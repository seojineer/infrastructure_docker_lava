# Copyright (C) 2015 Linaro Limited
#
# Author: Senthil Kumaran S <senthil.kumaran@linaro.org>
#
# This file is part of LAVA Dispatcher.
#
# LAVA Dispatcher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LAVA Dispatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along
# with this program; if not, see <http://www.gnu.org/licenses>.

import os
from lava_dispatcher.logical import Deployment
from lava_dispatcher.connections.serial import ConnectDevice
from lava_dispatcher.power import ResetDevice, PrePower
from lava_common.exceptions import InfrastructureError
from lava_dispatcher.action import (
    Pipeline,
    Action,
)
from lava_dispatcher.actions.deploy import DeployAction
from lava_dispatcher.actions.deploy.environment import DeployDeviceEnvironment
from lava_dispatcher.actions.deploy.overlay import OverlayAction
from lava_dispatcher.actions.deploy.apply_overlay import (
    ApplyOverlaySparseImage,
    ApplyOverlayImage,
)
from lava_dispatcher.actions.deploy.download import (
    DownloaderAction,
    HttpDownloadAction,
)
from lava_dispatcher.utils.filesystem import copy_to_lxc
from lava_dispatcher.utils.lxc import is_lxc_requested, lxc_cmd_prefix
from lava_dispatcher.actions.boot.fastboot import EnterFastbootAction
from lava_dispatcher.actions.boot.u_boot import UBootEnterFastbootAction
from lava_dispatcher.power import PDUReboot, ReadFeedback
# Nexell extension
from lava_dispatcher.actions.deploy.apply_overlay import ApplyNexellOverlay
import urllib.parse as lavaurl
from lava_dispatcher.utils.compression import (
    compress_file,
    decompress_file,
)

# pylint: disable=too-many-return-statements,too-many-instance-attributes,missing-docstring


class Fastboot(Deployment):
    """
    Strategy class for a fastboot deployment.
    Downloads the relevant parts, copies to the locations using fastboot.
    """
    compatibility = 1
    name = 'fastboot'

    def __init__(self, parent, parameters):
        super().__init__(parent)
        self.action = FastbootAction()
        self.action.section = self.action_type
        self.action.job = self.job
        parent.add_action(self.action, parameters)

    @classmethod
    def accepts(cls, device, parameters):
        if 'to' not in parameters:
            return False, '"to" is not in deploy parameters'
        if parameters['to'] != 'fastboot':
            return False, '"to" parameter is not "fastboot"'
        if 'deploy' not in device['actions']:
            return False, '"deploy" is not in the device configuration actions'
        if 'adb_serial_number' not in device:
            return False, '"adb_serial_number" is not in the device configuration'
        if 'fastboot_serial_number' not in device:
            return False, '"fastboot_serial_number" is not in the device configuration'
        if 'fastboot_options' not in device:
            return False, '"fastboot_options" is not in the device configuration'
        if 'fastboot' in device['actions']['deploy']['methods']:
            return True, 'accepted'
        return False, '"fastboot" was not in the device configuration deploy methods"'


class FastbootAction(DeployAction):  # pylint:disable=too-many-instance-attributes

    name = "fastboot-deploy"
    description = "download files and deploy using fastboot"
    summary = "fastboot deployment"

    def __init__(self):
        super().__init__()
        self.force_prompt = False

    def validate(self):
        super().validate()
        if not self.test_needs_deployment(self.parameters):
            return

    def populate(self, parameters):
        self.internal_pipeline = Pipeline(parent=self, job=self.job, parameters=parameters)
        image_keys = list(parameters['images'].keys())
        if self.test_needs_overlay(parameters):
            self.logger.debug("[SEOJI] add OverlayAction")
            self.internal_pipeline.add_action(OverlayAction())
        # Check if the device has a power command such as HiKey, Dragonboard,
        # etc. against device that doesn't like Nexus, etc.
        if self.job.device.get('fastboot_via_uboot', False):
            self.internal_pipeline.add_action(ConnectDevice())
            self.internal_pipeline.add_action(UBootEnterFastbootAction())
        elif self.job.device.hard_reset_command:
            self.force_prompt = True
            self.internal_pipeline.add_action(ConnectDevice())
            if not is_lxc_requested(self.job):
                self.internal_pipeline.add_action(PrePower())
            self.internal_pipeline.add_action(ResetDevice())
        elif 'nexell_ext' in image_keys:
            # Nexell extension
            #self.internal_pipeline.add_action(OverlayAction())

            # download build result
            if 'url' in parameters['images']['nexell_ext']:
                self.logger.debug("[SEOJI] url:" + str(parameters['images']['nexell_ext']['url']))
                self.path = '/opt/share'
                self.internal_pipeline.add_action(DownloaderAction('nexell_ext', self.path))
                #if 'compression' in parameters['images']['nexell_ext]:
                   #self.logger.debug("[SEOJI] yes compression param exist") 
                    

            self.logger.debug("SUKER: parameters in deploy/fastboot.py : " + str(parameters))
            self.internal_pipeline.add_action(EnterNexellFastbootAction(parameters,'deploy_script','deploy_command1','dir_name'))
            self.internal_pipeline.add_action(ApplyNexellDeployAction(parameters,'deploy_script','deploy_command2','dir_name'))
        else:
            self.internal_pipeline.add_action(EnterFastbootAction())

        fastboot_dir = self.mkdtemp()
        image_keys = sorted(parameters['images'].keys())
        # Nexell extension
        if 'nexell_ext' in image_keys:
            self.logger.debug("[SEOJI] pass adding DownloaderAction")
            #self.internal_pipeline.add_action(DeployDeviceEnvironment())
        else:
            for image in image_keys:
                if image != 'yaml_line':
                    self.internal_pipeline.add_action(DownloaderAction(image, fastboot_dir))
                    if parameters['images'][image].get('apply-overlay', False):
                        if self.test_needs_overlay(parameters):
                            if parameters['images'][image].get('sparse', True):
                                self.internal_pipeline.add_action(
                                    ApplyOverlaySparseImage(image))
                            else:
                                self.internal_pipeline.add_action(
                                    ApplyOverlayImage(image, use_root_partition=False))
                    if self.test_needs_overlay(parameters) and \
                       self.test_needs_deployment(parameters):
                        self.internal_pipeline.add_action(
                            DeployDeviceEnvironment())
            self.internal_pipeline.add_action(FastbootFlashOrderAction())
        '''
        for image in image_keys:
            if image != 'yaml_line':
                self.internal_pipeline.add_action(DownloaderAction(image, fastboot_dir))
                if parameters['images'][image].get('apply-overlay', False):
                    if self.test_needs_overlay(parameters):
                        if parameters['images'][image].get('sparse', True):
                            self.internal_pipeline.add_action(
                                ApplyOverlaySparseImage(image))
                        else:
                            self.internal_pipeline.add_action(
                                ApplyOverlayImage(image, use_root_partition=False))
                if self.test_needs_overlay(parameters) and \
                   self.test_needs_deployment(parameters):
                    self.internal_pipeline.add_action(
                        DeployDeviceEnvironment())
        self.internal_pipeline.add_action(FastbootFlashOrderAction())
        '''

class EnterNexellFastbootAction(DeployAction):
    """
    Enters fastboot bootloader.
    """

    def __init__(self,parameters, key1, key2, key3):
        super(EnterNexellFastbootAction, self).__init__()
        self.name = "enter-nexell-fastboot-action"
        self.description = "enter fastboot bootloader"
        self.summary = "enter fastboot"
        self.retries = 10
        self.sleep = 10
        self.cmd = parameters['images']['nexell_ext'][key1]
        self.param1 = parameters['images']['nexell_ext'][key2]
        self.param2 = parameters['images']['nexell_ext'][key3]
        self.device_path = parameters['images']['nexell_ext']['device_path']

    def validate(self):
        super(EnterNexellFastbootAction, self).validate()

    def run(self, connection, args=None):
        connection = super(EnterNexellFastbootAction, self).run(connection, args)        
        self.logger.debug("[SEOJI] param1: %s, param2: %s", self.param1, self.param2)
        self.logger.debug("[SEOJI] param: %s", self.job.device)
        test_path = self.device_path
        self.logger.debug("test_path:%s",test_path)
        telnet_cmd = [self.cmd, self.param1, self.param2, test_path]
        self.logger.debug("SUKER: telnet_cmd " + str(telnet_cmd))
        command_output = self.run_command(telnet_cmd)
        self.logger.debug("SUKER: self.errors " + str(self.errors))
        self.results = {'status': 'finished'}
        return connection


class ApplyNexellDeployAction(DeployAction):
    """
    Fastboot deploy Nexell image.
    """
    def __init__(self,parameters, key1, key2, key3):
        super(ApplyNexellDeployAction, self).__init__()
        self.name = "fastboot-apply-nexell-action1"
        self.description = "fastboot apply nexell image"
        self.summary = "fastboot apply nexell"
        self.retries = 1
        self.sleep = 3
        self.cmd_script = parameters['images']['nexell_ext'][key1]
        self.cmd_param1 = parameters['images']['nexell_ext'][key2]
        self.cmd_param2 = parameters['images']['nexell_ext'][key3]
        self.device_path = parameters['images']['nexell_ext']['device_path']
        self.parameters = parameters

    def validate(self):
        super(ApplyNexellDeployAction, self).validate()
        
    def run(self, connection, args=None):
        connection = super(ApplyNexellDeployAction, self).run(connection, args)
        if 'partial_name' not in self.parameters['images']['nexell_ext']:
            # fuse all
            self.logger.debug("test_path:%s", self.device_path)
            fastboot_cmd = [self.cmd_script, self.cmd_param1, self.cmd_param2, self.device_path]
            self.logger.debug("SUKER: fastboot cmd %s %s", self.cmd_param1, self.cmd_param2)
            command_output = self.run_command(fastboot_cmd)        
        else:
            self.logger.debug("[SEOJI] partial update")
            # fuse partial
            filename = os.path.basename(self.parameters['images']['nexell_ext']['url'])

            self.logger.debug("test_path:%s", self.device_path)
            fastboot_cmd = [self.cmd_script, self.cmd_param1, self.cmd_param2, self.device_path, self.parameters['images']['nexell_ext']['partial_name']]
            self.logger.debug("SUKER: fastboot cmd %s %s", self.cmd_param1, self.cmd_param2)
            command_output = self.run_command(fastboot_cmd)        

        # if type(command_output) == bool :
        #     self.logger.debug("SUKER: command_output type %s", type(command_output))
        # else :
        #     if command_output and 'error' in command_output:
        #         raise JobError("Unable to apply ptable image using fastboot: %s" %
        #                        command_output)  # FIXME: JobError needs a unit test

        return connection


class ApplyNexellAfterDeployAction(DeployAction):
    def __init__(self,parameters,key):
        super(ApplyNexellAfterDeployAction, self).__init__()
        self.name = "fastboot-apply-nexell-action-after-deploy"
        self.description = "fastboot apply nexell image"
        self.summary = "fastboot apply nexell"
        self.retries = 1
        self.sleep = 5
        self.cmd = parameters['images']['nexell_ext'][key]
        self.key = key

    def validate(self):
        super(ApplyNexellAfterDeployAction, self).validate()

    def run(self, connection, args=None):
        connection = super(ApplyNexellAfterDeployAction, self).run(connection, args)
        cmd = ['echo', self.cmd]
        command_output = self.run_command(cmd, True)
        
        return connection

class FastbootFlashOrderAction(DeployAction):
    """
    Fastboot flash image.
    """

    name = "fastboot-flash-order-action"
    description = "Determine support for each flash operation"
    summary = "Handle reset and options for each flash url."

    def __init__(self):
        super().__init__()
        self.retries = 3
        self.sleep = 10
        self.interrupt_prompt = None
        self.interrupt_string = None
        self.reboot = None

    def populate(self, parameters):
        self.internal_pipeline = Pipeline(parent=self, job=self.job, parameters=parameters)
        flash_cmds_order = self.job.device['flash_cmds_order']
        userlist = list(parameters['images'].keys())
        userlist.remove('yaml_line')
        flash_cmds = set(userlist).difference(set(flash_cmds_order))
        flash_cmds = flash_cmds_order + list(flash_cmds)
        self.internal_pipeline.add_action(ReadFeedback(repeat=True))
        for flash_cmd in flash_cmds:
            if flash_cmd not in parameters['images']:
                continue
            self.internal_pipeline.add_action(FastbootFlashAction(cmd=flash_cmd))
            self.reboot = parameters['images'][flash_cmd].get('reboot')
            if self.reboot == 'fastboot-reboot':
                self.internal_pipeline.add_action(FastbootReboot())
                self.internal_pipeline.add_action(ReadFeedback(repeat=True))
            elif self.reboot == 'fastboot-reboot-bootloader':
                self.internal_pipeline.add_action(FastbootRebootBootloader())
                self.internal_pipeline.add_action(ReadFeedback(repeat=True))
            elif self.reboot == 'hard-reset':
                self.internal_pipeline.add_action(PDUReboot())
                self.internal_pipeline.add_action(ReadFeedback(repeat=True))

    def validate(self):
        super().validate()
        self.set_namespace_data(
            action=FastbootFlashAction.name, label='interrupt',
            key='reboot', value=self.reboot)
        if 'fastboot_serial_number' not in self.job.device:
            self.errors = "device fastboot serial number missing"
        elif self.job.device['fastboot_serial_number'] == '0000000000':
            self.errors = "device fastboot serial number unset"
        if 'flash_cmds_order' not in self.job.device:
            self.errors = "device flash commands order missing"
        if 'fastboot_options' not in self.job.device:
            self.errors = "device fastboot options missing"
        elif not isinstance(self.job.device['fastboot_options'], list):
            self.errors = "device fastboot options is not a list"


class FastbootFlashAction(Action):

    """
    Fastboot flash image.
    """

    name = "fastboot-flash-action"
    description = "Run a specified flash command"
    summary = "Execute fastboot flash command"
    timeout_exception = InfrastructureError

    def __init__(self, cmd=None):
        super().__init__()
        self.retries = 3
        self.sleep = 10
        self.command = cmd
        self.interrupt_prompt = None
        self.interrupt_string = None

    def validate(self):
        super().validate()
        if not self.command:
            self.errors = "Invalid configuration - missing flash command"
        device_methods = self.job.device['actions']['deploy']['methods']
        if isinstance(device_methods.get('fastboot'), dict):
            self.interrupt_prompt = device_methods['fastboot'].get('interrupt_prompt')
            self.interrupt_string = device_methods['fastboot'].get('interrupt_string')

    def run(self, connection, max_end_time):  # pylint: disable=too-many-locals
        connection = super().run(connection, max_end_time)

        src = self.get_namespace_data(action='download-action', label=self.command, key='file')
        if not src:
            return connection
        self.logger.debug("%s bytes", os.stat(src)[6])
        lxc_name = is_lxc_requested(self.job)
        if lxc_name:
            src = copy_to_lxc(lxc_name, src, self.job.parameters['dispatcher'])
        sequence = self.job.device['actions']['boot']['methods'].get(
            'fastboot', [])
        if 'no-flash-boot' in sequence and self.command in ['boot']:
            return connection

        # if a reboot is requested, will need to wait for the prompt
        # if not, continue in the existing mode.
        reboot = self.get_namespace_data(
            action=self.name, label='interrupt', key='reboot')
        if self.interrupt_prompt and reboot:
            connection.prompt_str = self.interrupt_prompt
            self.logger.debug("Changing prompt to '%s'", connection.prompt_str)
            self.wait(connection)

        serial_number = self.job.device['fastboot_serial_number']
        fastboot_opts = self.job.device['fastboot_options']
        fastboot_cmd = lxc_cmd_prefix(self.job) + [
            'fastboot', '-s', serial_number, 'flash', self.command, src
        ] + fastboot_opts
        self.logger.info("Handling %s", self.command)
        # needs to move to self.run_cmd with support for raising InfrastructureError
        command_output = self.run_command(fastboot_cmd)
        if not command_output:
            raise InfrastructureError("Unable to flash %s using fastboot" %
                                      self.command)
        self.results = {'label': self.command}
        return connection


class FastbootReboot(Action):

    name = 'fastboot-reboot'
    description = 'Reset a device between flash operations using fastboot reboot.'
    summary = 'execute a reboot using fastboot'

    def run(self, connection, max_end_time):  # pylint: disable=too-many-locals
        connection = super().run(connection, max_end_time)

        serial_number = self.job.device['fastboot_serial_number']
        fastboot_opts = self.job.device['fastboot_options']

        self.logger.info("fastboot rebooting device.")
        fastboot_cmd = lxc_cmd_prefix(self.job) + ['fastboot', '-s', serial_number,
                                                   'reboot'] + fastboot_opts
        # needs to move to self.run_cmd with support
        command_output = self.run_command(fastboot_cmd)
        if not command_output:
            raise InfrastructureError("Unable to reboot")
        return connection


class FastbootRebootBootloader(Action):

    name = 'fastboot-reboot-bootloader'
    description = 'Reset a device between flash operations using fastboot reboot-bootloader.'
    summary = 'execute a reboot to bootloader using fastboot'

    def run(self, connection, max_end_time):  # pylint: disable=too-many-locals
        connection = super().run(connection, max_end_time)

        serial_number = self.job.device['fastboot_serial_number']
        fastboot_opts = self.job.device['fastboot_options']

        self.logger.info("fastboot reboot device to bootloader.")
        fastboot_cmd = lxc_cmd_prefix(self.job) + [
            'fastboot', '-s', serial_number, 'reboot-bootloader'
        ] + fastboot_opts
        # needs to move to self.run_cmd with support
        command_output = self.run_command(fastboot_cmd)
        if not command_output:
            raise InfrastructureError("Unable to reboot to bootloader")
        return connection
