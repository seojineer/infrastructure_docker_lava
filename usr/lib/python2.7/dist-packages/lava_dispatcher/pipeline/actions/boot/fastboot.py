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


from lava_dispatcher.pipeline.action import (
    Pipeline,
    Action,
    JobError,
)
from lava_dispatcher.pipeline.logical import Boot
from lava_dispatcher.pipeline.actions.boot import BootAction
from lava_dispatcher.pipeline.connections.lxc import ConnectLxc
# Nexell extension
from lava_dispatcher.pipeline.connections.telnet import ConnectTelnet

class BootFastboot(Boot):
    """
    Expects fastboot bootloader, and boots.
    """
    compatibility = 1

    def __init__(self, parent, parameters):
        super(BootFastboot, self).__init__(parent)
        self.action = BootFastbootAction()
        self.action.section = self.action_type
        self.action.job = self.job
        parent.add_action(self.action, parameters)

    @classmethod
    def accepts(cls, device, parameters):
        if 'method' in parameters:
            if parameters['method'] == 'fastboot':
                return True
        return False


class BootFastbootAction(BootAction):
    """
    Provide for auto_login parameters in this boot stanza and re-establish the
    connection after boot.
    """
    def __init__(self):
        super(BootFastbootAction, self).__init__()
        self.name = "fastboot_boot"
        self.summary = "fastboot boot"
        self.description = "fastboot boot into the system"

    def populate(self, parameters):
        self.internal_pipeline = Pipeline(parent=self, job=self.job, parameters=parameters)

        # Nexell Extension
        if len(parameters['nexell_ext']) > 0:
            self.internal_pipeline.add_action(NexellFastbootBootAction(parameters))
            #self.internal_pipeline.add_action(ConnectTelnet(parameters))
            #self.internal_pipeline.add_action(WaitForAdbDeviceForNexell())
            self.internal_pipeline.add_action(ConnectTelnet(parameters))
            self.internal_pipeline.add_action(WaitForPromptForNexell(parameters))
        else:    
            self.internal_pipeline.add_action(FastbootBootAction())
            self.internal_pipeline.add_action(ConnectLxc())
            self.internal_pipeline.add_action(WaitForAdbDevice())

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

    def validate(self):
        super(NexellFastbootBootAction, self).validate()

    def run(self, connection, args=None):
        connection = super(NexellFastbootBootAction, self).run(connection, args)
        test_path = self.job.device['device_path']
        self.logger.debug("test_path:%s",test_path[0])
        cmd = [self.cmd_script, self.cmd_param, self.dir_name, test_path[0]]
        command_output = self.run_command(cmd)
        self.data['boot-result'] = 'failed' if self.errors else 'success'
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

    def validate(self):
        super(WaitForPromptForNexell, self).validate()

    def run(self, connection, args=None):
        connection = super(WaitForPromptForNexell, self).run(connection, args)
        test_path = self.job.device['device_path']
        self.logger.debug("test_path:%s",test_path[0])
        cmd = [self.cmd_script, self.cmd_param, self.dir_name2, test_path[0]]
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
        adb_cmd = ['/opt/android-sdk-linux/platform-tools/adb', 'start-server']
        serial_number = self.job.device['adb_serial_number']
        self.logger.debug("Starting adb daemon")
        self.run_command(adb_cmd)
        adb_cmd = ['/opt/android-sdk-linux/platform-tools/adb', '-s', serial_number, 'wait-for-device']
        self.logger.debug("%s: Nexell Waiting for device", serial_number)
        self.run_command(adb_cmd)
        
        return connection
    
    
class FastbootBootAction(Action):
    """
    This action calls fastboot to boot into the system.
    """

    def __init__(self):
        super(FastbootBootAction, self).__init__()
        self.name = "boot-fastboot"
        self.summary = "attempt to fastboot boot"
        self.description = "fastboot boot into system"
        self.command = ''

    def validate(self):
        super(FastbootBootAction, self).validate()
        if 'fastboot_serial_number' not in self.job.device:
            self.errors = "device fastboot serial number missing"
            if self.job.device['fastboot_serial_number'] == '0000000000':
                self.errors = "device fastboot serial number unset"

    def run(self, connection, args=None):
        connection = super(FastbootBootAction, self).run(connection, args)
        lxc_name = self.get_common_data('lxc', 'name')
        serial_number = self.job.device['fastboot_serial_number']
        fastboot_cmd = ['lxc-attach', '-n', lxc_name, '--', 'fastboot',
                        '-s', serial_number, 'reboot']
        command_output = self.run_command(fastboot_cmd)
        if command_output and 'rebooting' not in command_output:
            raise JobError("Unable to boot with fastboot: %s" % command_output)
        else:
            status = [status.strip() for status in command_output.split(
                '\n') if 'finished' in status][0]
            self.results = {'status': status}
        self.data['boot-result'] = 'failed' if self.errors else 'success'
        return connection


class WaitForAdbDevice(Action):
    """
    Waits for device that gets connected using adb.
    """

    def __init__(self):
        super(WaitForAdbDevice, self).__init__()
        self.name = "wait-for-adb-device"
        self.summary = "Waits for adb device"
        self.description = "Waits for availability of adb device"
        self.prompts = []

    def validate(self):
        super(WaitForAdbDevice, self).validate()
        if 'adb_serial_number' not in self.job.device:
            self.errors = "device adb serial number missing"
            if self.job.device['adb_serial_number'] == '0000000000':
                self.errors = "device adb serial number unset"

    def run(self, connection, args=None):
        connection = super(WaitForAdbDevice, self).run(connection, args)
        lxc_name = self.get_common_data('lxc', 'name')
        serial_number = self.job.device['adb_serial_number']
        adb_cmd = ['lxc-attach', '-n', lxc_name, '--', 'adb', 'start-server']
        self.logger.debug("Starting adb daemon")
        self.run_command(adb_cmd)
        adb_cmd = ['lxc-attach', '-n', lxc_name, '--', 'adb',
                   '-s', serial_number, 'wait-for-device']
        self.logger.debug("%s: Waiting for device", serial_number)
        self.run_command(adb_cmd)
        return connection
