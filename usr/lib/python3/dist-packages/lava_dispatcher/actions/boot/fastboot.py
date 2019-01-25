# Copyright (C) 2015-2018 Linaro Limited
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
from lava_dispatcher.action import Action, Pipeline
from lava_common.exceptions import InfrastructureError, JobError, LAVABug
from lava_dispatcher.logical import Boot
from lava_dispatcher.actions.boot import (
    BootAction,
    AutoLoginAction,
    OverlayUnpack,
    AdbOverlayUnpack,
)
# Nexell extension
from lava_dispatcher.connections.telnet import ConnectTelnet
from lava_dispatcher.power import ResetDevice, PreOs
from lava_common.constants import LAVA_LXC_HOME
from lava_dispatcher.utils.lxc import is_lxc_requested, lxc_cmd_prefix
from lava_dispatcher.connections.serial import ConnectDevice
from lava_dispatcher.connections.adb import ConnectAdb
from lava_dispatcher.actions.boot.environment import ExportDeviceEnvironment
from lava_dispatcher.shell import ExpectShellSession
from lava_dispatcher.actions.boot.u_boot import UBootEnterFastbootAction
from lava_dispatcher.actions.deploy.apply_overlay import ApplyNexellOverlay


def _fastboot_sequence_map(sequence):
    """Maps fastboot sequence with corresponding class."""
    sequence_map = {'boot': (FastbootBootAction, None),
                    'reboot': (FastbootRebootAction, None),
                    'no-flash-boot': (FastbootBootAction, None),
                    'auto-login': (AutoLoginAction, None),
                    'overlay-unpack': (OverlayUnpack, None),
                    'shell-session': (ExpectShellSession, None),
                    'export-env': (ExportDeviceEnvironment, None), }
    return sequence_map.get(sequence, (None, None))


class BootFastboot(Boot):
    """
    Expects fastboot bootloader, and boots.
    """

    compatibility = 1

    def __init__(self, parent, parameters):
        super().__init__(parent)
        self.action = BootFastbootAction()
        self.action.section = self.action_type
        self.action.job = self.job
        parent.add_action(self.action, parameters)

    @classmethod
    def accepts(cls, device, parameters):
        if 'method' in parameters:
            if parameters['method'] == 'fastboot':
                return True, 'accepted'
        return False, 'boot "method" was not "fastboot"'


class BootFastbootCommands(Action):

    name = "fastboot-boot-commands"
    description = "Run custom fastboot commands before boot"
    summary = "Run fastboot boot commands"

    def run(self, connection, max_end_time):
        serial_number = self.job.device['fastboot_serial_number']
        self.logger.info("Running custom fastboot boot commands....")
        for command in self.parameters.get("commands"):
            pre_cmd = (
                lxc_cmd_prefix(self.job)
                + ["fastboot", "-s", serial_number, command]
                + self.job.device["fastboot_options"]
            )
            self.run_command(pre_cmd)


class BootFastbootAction(BootAction):
    """
    Provide for auto_login parameters in this boot stanza and re-establish the
    connection after boot.
    """

    name = "fastboot-boot"
    description = "fastboot boot into the system"
    summary = "fastboot boot"

    def validate(self):
        super().validate()
        self.logger.debug("[SEOJI] BootFastbootAction validate()")
        self.logger.debug("[SEOJI] self.job.device: %s", self.job.device)
        self.logger.debug("[SEOJI] param: %s", self.job.device['actions']['boot']['methods'])
        sequences = self.job.device['actions']['boot']['methods'].get(
            'fastboot', [])
        if sequences is not None:
            for sequence in sequences:
                if not _fastboot_sequence_map(sequence):
                    self.errors = "Unknown boot sequence '%s'" % sequence
        else:
            self.logger.debug("[SEOJI] fastboot_sequence undefined")
            self.errors = "fastboot_sequence undefined"

    def populate(self, parameters):
        self.internal_pipeline = Pipeline(parent=self, job=self.job,
                                          parameters=parameters)

        # Nexell Extension
        if 'nexell_ext' in parameters:
            self.logger.debug("[SEOJI] ****** parameters: %s", parameters)
            self.internal_pipeline.add_action(NexellFastbootBootAction(parameters))
            # SEOJI 190116 add for adb push overlay files to DUT
            self.internal_pipeline.add_action(WaitForAdbDeviceForNexell())
            self.internal_pipeline.add_action(ApplyNexellOverlay())
            self.internal_pipeline.add_action(ConnectDevice())
            #self.internal_pipeline.add_action(ConnectTelnet(parameters))
            #self.internal_pipeline.add_action(WaitForPromptForNexell(parameters))
            self.internal_pipeline.add_action(ExpectShellSession())
        else:
            if parameters.get("commands"):
                self.logger.debug("[SEOJI] boot - add BootFastbootCommands()")
                self.internal_pipeline.add_action(BootFastbootCommands())

            # Always ensure the device is in fastboot mode before trying to boot.
            # Check if the device has a power command such as HiKey, Dragonboard,
            # etc. against device that doesn't like Nexus, etc.
            if self.job.device.get('fastboot_via_uboot', False):
                self.internal_pipeline.add_action(ConnectDevice())
                self.internal_pipeline.add_action(UBootEnterFastbootAction())
            elif self.job.device.hard_reset_command:
                self.force_prompt = True
                self.internal_pipeline.add_action(ConnectDevice())
                self.internal_pipeline.add_action(ResetDevice())
            else:
                self.logger.debug("[SEOJI] boot - add EnterFastbootAction")
                self.internal_pipeline.add_action(EnterFastbootAction())

            # Based on the boot sequence defined in the device configuration, add
            # the required pipeline actions.
            self.logger.debug("[SEOJI] get sequences")
            sequences = self.job.device['actions']['boot']['methods'].get(
                'fastboot', [])
            self.logger.debug("[SEOJI] sequences" + str(sequences))
            for sequence in sequences:
                mapped = _fastboot_sequence_map(sequence)
                if mapped[1]:
                    self.internal_pipeline.add_action(
                        mapped[0](device_actions=mapped[1]))
                elif mapped[0]:
                    self.internal_pipeline.add_action(mapped[0]())
            if self.job.device.hard_reset_command:
                if not is_lxc_requested(self.job):
                    self.internal_pipeline.add_action(PreOs())
                if self.has_prompts(parameters):
                    self.internal_pipeline.add_action(AutoLoginAction())
                    if self.test_has_shell(parameters):
                        self.internal_pipeline.add_action(ExpectShellSession())
                        if 'transfer_overlay' in parameters:
                            self.internal_pipeline.add_action(OverlayUnpack())
                        self.internal_pipeline.add_action(ExportDeviceEnvironment())
            else:
                if not is_lxc_requested(self.job):
                    self.internal_pipeline.add_action(ConnectAdb())
                    self.internal_pipeline.add_action(AdbOverlayUnpack())

# Nexell extension
class NexellFastbootBootAction(Action):
    """
    This action calls fastboot to boot into the system.
    """
    def __init__(self,parameters):
        super(NexellFastbootBootAction, self).__init__()
        self.name = "nexell-boot-on-uboot"
        self.summary = "attempt to boot"
        self.description = "nexell boot into system"
        self.command = ''
        self.dir_name = parameters['nexell_ext']['dir_name']
        self.cmd_script = parameters['nexell_ext']['command']
        self.cmd_param = parameters['nexell_ext']['command_param']
        self.device_path = parameters['nexell_ext']['device_path']

    def validate(self):
        super(NexellFastbootBootAction, self).validate()

    def run(self, connection, args=None):
        connection = super(NexellFastbootBootAction, self).run(connection, args)
        #test_path = self.job.device['device_path']
        # get device_path from job file
        test_path = self.device_path
        self.logger.debug("test_path:%s",test_path)
        cmd = [self.cmd_script, self.cmd_param, self.dir_name, test_path]
        self.logger.debug("[SEOJI] cmd" + str(cmd))
        command_output = self.run_command(cmd)
        # Nexell extension
        self.logger.debug("[SEOJI] not save boot-result for test action.")
        #self.data['boot-result'] = 'failed' if self.errors else 'success'
        return connection

# Nexell extension
class WaitForPromptForNexell(Action):
    """
    This action calls fastboot to boot into the system.
    """
    def __init__(self,parameters):
        super(WaitForPromptForNexell, self).__init__()
        self.name = "nexell-wait-prompt"
        self.summary = "wait prompt"
        self.description = "nexell wait prompt"
        self.command = ''
        self.dir_name2 = parameters['nexell_ext']['dir_name']
        self.prompts = parameters['prompts']
        self.cmd_script = parameters['nexell_ext']['command']
        self.cmd_param = parameters['nexell_ext']['command_param2']
        self.device_path = parameters['nexell_ext']['device_path']

    def validate(self):
        super(WaitForPromptForNexell, self).validate()

    def run(self, connection, args=None):
        connection = super(WaitForPromptForNexell, self).run(connection, args)
        #test_path = self.job.device['device_path']
        test_path = self.device_path
        self.logger.debug("test_path:%s",test_path)
        cmd = [self.cmd_script, self.cmd_param, self.dir_name2, test_path]
        command_output = self.run_command(cmd)
        connection.prompt_str = self.prompts
        self.wait(connection)
        return connection

# Nexell extension
class WaitForAdbDeviceForNexell(Action):
    """
    Waits for device that gets connected using adb.
    """

    def __init__(self):
        super(WaitForAdbDeviceForNexell, self).__init__()
        self.name = "wait-for-adb-device-by-nexell"
        self.summary = "Waits for adb device"
        self.description = "Waits for availability of adb device"
        self.prompts = []

    def validate(self):
        super(WaitForAdbDeviceForNexell, self).validate()
        if 'adb_serial_number' not in self.job.device:
            self.errors = "device adb serial number missing"
            if self.job.device['adb_serial_number'] == '0000000000':
                self.errors = "device adb serial number unset"
                
    def run(self, connection, args=None):
        connection = super(WaitForAdbDeviceForNexell, self).run(connection, args)
        #adb_cmd = ['/opt/android-sdk-linux/platform-tools/adb', 'start-server']
        adb_cmd = ['adb', 'start-server']
        serial_number = self.job.device['adb_serial_number']
        self.logger.debug("Starting adb daemon")
        self.run_command(adb_cmd)

        adb_cmd = ['adb', 'root']
        self.run_command(adb_cmd)

        adb_cmd = ['adb', '-s', serial_number, 'wait-for-device']
        self.logger.debug("%s: Nexell Waiting for device", serial_number)
        self.run_command(adb_cmd)
        
        return connection

class WaitFastBootInterrupt(Action):
    """
    Interrupts fastboot to access the next bootloader
    Relies on fastboot-flash-action setting the prompt and string
    from the deployment parameters.
    """

    name = 'wait-fastboot-interrupt'
    description = "Check for prompt and pass the interrupt string to exit fastboot."
    summary = "watch output and try to interrupt fastboot"

    def __init__(self, itype):
        super().__init__()
        self.type = itype
        self.prompt = None
        self.string = None

    def validate(self):
        super().validate()
        if 'fastboot_serial_number' not in self.job.device:
            self.errors = "device fastboot serial number missing"
        elif self.job.device['fastboot_serial_number'] == '0000000000':
            self.errors = "device fastboot serial number unset"
        if 'fastboot_options' not in self.job.device:
            self.errors = "device fastboot options missing"
        elif not isinstance(self.job.device['fastboot_options'], list):
            self.errors = "device fastboot options is not a list"
        device_methods = self.job.device['actions']['deploy']['methods']
        if isinstance(device_methods.get('fastboot'), dict):
            self.prompt = device_methods['fastboot'].get('interrupt_prompt')
            self.string = device_methods['fastboot'].get('interrupt_string')
        if not self.prompt or not self.string:
            self.errors = "Missing interrupt configuration for device."

    def run(self, connection, max_end_time):
        if not connection:
            raise LAVABug("%s started without a connection already in use" % self.name)
        connection = super().run(connection, max_end_time)
        # device is to be put into a reset state, either by issuing 'reboot' or power-cycle
        connection.prompt_str = self.prompt
        self.logger.debug("Changing prompt to '%s'", connection.prompt_str)
        self.wait(connection)
        self.logger.debug("Sending '%s' to interrupt fastboot.", self.string)
        connection.sendline(self.string)
        return connection


class FastbootBootAction(Action):
    """
    This action calls fastboot to boot into the system.
    """

    name = "boot-fastboot"
    description = "fastboot boot into system"
    summary = "attempt to fastboot boot"

    def validate(self):
        super().validate()
        if 'fastboot_serial_number' not in self.job.device:
            self.errors = "device fastboot serial number missing"
        elif self.job.device['fastboot_serial_number'] == '0000000000':
            self.errors = "device fastboot serial number unset"
        if 'fastboot_options' not in self.job.device:
            self.errors = "device fastboot options missing"
        elif not isinstance(self.job.device['fastboot_options'], list):
            self.errors = "device fastboot options is not a list"

    def run(self, connection, max_end_time):
        connection = super().run(connection, max_end_time)
        lxc_name = is_lxc_requested(self.job)
        serial_number = self.job.device['fastboot_serial_number']
        boot_img = self.get_namespace_data(action='download-action',
                                           label='boot', key='file')
        if not boot_img:
            raise JobError("Boot image not found, unable to boot")
        else:
            if lxc_name:
                boot_img = os.path.join(LAVA_LXC_HOME,
                                        os.path.basename(boot_img))
        fastboot_cmd = lxc_cmd_prefix(self.job) + [
            'fastboot', '-s', serial_number, 'boot', boot_img
        ] + self.job.device['fastboot_options']
        command_output = self.parsed_command(fastboot_cmd, allow_fail=True)
        if command_output and 'booting' not in command_output.lower():
            raise JobError("Unable to boot with fastboot: %s" % command_output)
        else:
            lines = [status for status in command_output.split(
                '\n') if 'finished' in status.lower()]
            if lines:
                self.results = {'status': lines[0].strip()}
            else:
                self.results = {'fail': self.name}
        self.set_namespace_data(action='shared', label='shared', key='connection', value=connection)
        return connection


class FastbootRebootAction(Action):
    """
    This action calls fastboot to reboot into the system.
    """

    name = "fastboot-reboot"
    description = "fastboot reboot into system"
    summary = "attempt to fastboot reboot"

    def validate(self):
        super().validate()
        if 'fastboot_serial_number' not in self.job.device:
            self.errors = "device fastboot serial number missing"
        elif self.job.device['fastboot_serial_number'] == '0000000000':
            self.errors = "device fastboot serial number unset"
        if 'fastboot_options' not in self.job.device:
            self.errors = "device fastboot options missing"
        elif not isinstance(self.job.device['fastboot_options'], list):
            self.errors = "device fastboot options is not a list"

    def run(self, connection, max_end_time):
        connection = super().run(connection, max_end_time)
        serial_number = self.job.device['fastboot_serial_number']
        fastboot_opts = self.job.device['fastboot_options']
        fastboot_cmd = lxc_cmd_prefix(self.job) + ['fastboot', '-s', serial_number,
                                                   'reboot'] + fastboot_opts
        command_output = self.parsed_command(fastboot_cmd, allow_fail=True)
        if command_output and 'rebooting' not in command_output.lower():
            raise JobError("Unable to fastboot reboot: %s" % command_output)
        else:
            lines = [status for status in command_output.split(
                '\n') if 'finished' in status.lower()]
            if lines:
                self.results = {'status': lines[0].strip()}
            else:
                self.results = {'fail': self.name}
        self.set_namespace_data(action='shared', label='shared', key='connection', value=connection)
        return connection


class EnterFastbootAction(Action):
    """
    Enters fastboot bootloader.
    """

    name = "enter-fastboot-action"
    description = "enter fastboot bootloader"
    summary = "enter fastboot"
    command_exception = InfrastructureError

    def validate(self):
        super().validate()
        if 'adb_serial_number' not in self.job.device:
            self.errors = "device adb serial number missing"
        elif self.job.device['adb_serial_number'] == '0000000000':
            self.errors = "device adb serial number unset"
        if 'fastboot_serial_number' not in self.job.device:
            self.errors = "device fastboot serial number missing"
        elif self.job.device['fastboot_serial_number'] == '0000000000':
            self.errors = "device fastboot serial number unset"
        if 'fastboot_options' not in self.job.device:
            self.errors = "device fastboot options missing"
        elif not isinstance(self.job.device['fastboot_options'], list):
            self.errors = "device fastboot options is not a list"

    def run(self, connection, max_end_time):
        connection = super().run(connection, max_end_time)

        cmd_prefix = lxc_cmd_prefix(self.job)
        # Try to enter fastboot mode with adb.
        adb_serial_number = self.job.device['adb_serial_number']
        # start the adb daemon
        adb_cmd = cmd_prefix + ['adb', 'start-server']
        command_output = self.parsed_command(adb_cmd, allow_fail=True)
        if command_output and 'successfully' in command_output:
            self.logger.debug("adb daemon started: %s", command_output)
        adb_cmd = cmd_prefix + ['adb', '-s', adb_serial_number, 'devices']
        command_output = self.parsed_command(adb_cmd, allow_fail=True)
        if command_output and adb_serial_number in command_output:
            self.logger.debug("Device is in adb: %s", command_output)
            adb_cmd = cmd_prefix + ['adb', '-s', adb_serial_number,
                                    'reboot-bootloader']
            self.run_command(adb_cmd)
            return connection

        # Enter fastboot mode with fastboot.
        fastboot_serial_number = self.job.device['fastboot_serial_number']
        fastboot_opts = self.job.device['fastboot_options']
        fastboot_cmd = cmd_prefix + ['fastboot', '-s', fastboot_serial_number,
                                     'devices'] + fastboot_opts
        command_output = self.parsed_command(fastboot_cmd)
        if command_output and fastboot_serial_number in command_output:
            self.logger.debug("Device is in fastboot: %s", command_output)
            # Nexell extension
            #fastboot_cmd = cmd_prefix + [
                #'fastboot', '-s', fastboot_serial_number, 'reboot-bootloader'
            #] + fastboot_opts
            fastboot_cmd = cmd_prefix + [
                'fastboot', '-s', fastboot_serial_number, 'reboot'
            ] + fastboot_opts
            self.logger.debug("[SEOJI] chage 'reboot-bootloader' to 'reboot' because of version issue.")
            self.logger.debug("[SEOJI] fastboot_cmd:" + str(fastboot_cmd))

            command_output = self.parsed_command(fastboot_cmd)
            self.logger.debug("[SEOJI] command_output: %s", command_output)
            '''
            if command_output and 'okay' not in command_output.lower():
                raise InfrastructureError("Unable to enter fastboot: %s" %
                                          command_output)
            else:
                lines = [status for status in command_output.split(
                    '\n') if 'finished' in status.lower()]
                if lines:
                    self.results = {'status': lines[0].strip()}
                else:
                    self.results = {'fail': self.name}
            '''
            lines = [status for status in command_output.split(
                '\n') if 'finished' in status.lower()]
            if lines:
                self.results = {'status': lines[0].strip()}
            else:
                self.results = {'fail': self.name}
        return connection
