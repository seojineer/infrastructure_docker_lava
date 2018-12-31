# Copyright (C) 2016 Linaro Limited
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

from lava_dispatcher.utils.shell import which
from lava_dispatcher.action import (
    Action,
    JobError,
)
from lava_dispatcher.shell import ShellCommand, ShellSession

# pylint: disable=too-many-public-methods


class LxcSession(ShellSession):
    """Extends a ShellSession to include the ability to disconnect and finalise
    cleanly.
    """

    name = "LxcSession"

    def finalise(self):
        self.disconnect("closing")
        super().finalise()

    def disconnect(self, reason=''):
        self.sendline('exit', disconnecting=True)
        self.connected = False


class ConnectLxc(Action):
    """
    Class to make a lxc shell connection to the container.
    """

    name = "connect-lxc"
    description = "connect to the lxc container"
    summary = "run connection command"

    def __init__(self):
        super().__init__()
        self.session_class = LxcSession
        self.shell_class = ShellCommand

    def validate(self):
        if 'lxc' not in self.job.device['actions']['boot']['methods']:
            return
        super().validate()
        which('lxc-attach')

    def run(self, connection, max_end_time):
        lxc_name = self.get_namespace_data(
            action='lxc-create-action',
            label='lxc',
            key='name'
        )
        if not lxc_name:
            self.logger.debug("No LXC device requested")
            return connection

        connection = self.get_namespace_data(action='shared', label='shared', key='connection', deepcopy=False)
        if connection:
            return connection

        cmd = "lxc-attach -n {0}".format(lxc_name)
        self.logger.info("%s Connecting to device using '%s'", self.name, cmd)
        # ShellCommand executes the connection command
        shell = self.shell_class(
            "%s\n" % cmd, self.timeout, logger=self.logger,
            window=self.job.device.get_constant('spawn_maxread'))
        if shell.exitstatus:
            raise JobError(
                "%s command exited %d: %s" % (
                    cmd, shell.exitstatus, shell.readlines()))
        # LxcSession monitors the pexpect
        connection = self.session_class(self.job, shell)
        connection.connected = True
        connection = super().run(connection, max_end_time)
        connection.prompt_str = self.parameters['prompts']
        self.set_namespace_data(action='shared', label='shared', key='connection', value=connection)
        return connection

# Nexell extension
class ConnectNexell(Action):
    """
    Class to make a lxc shell connection to the container.
    """
    def __init__(self):
        super(ConnectNexell, self).__init__()
        self.name = "connect-nexell-device"
        self.summary = "run connection command"
        self.description = "connect to the nexell device"
        self.session_class = ShellSession
        self.shell_class = ShellCommand

    def validate(self):
        super(ConnectNexell, self).validate()

    def run(self, connection, args=None):
        # Attach usb device to lxc
        if 'device_path' in list(self.job.device.keys()):
            device_path = self.job.device['device_path']
            if not isinstance(device_path, list):
                raise JobError("device_path should be a list")

            if device_path:
                # Wait USB_SHOW_UP_TIMEOUT seconds for usb device to show up
                self.logger.info("Wait %d seconds for usb device to show up",
                                 USB_SHOW_UP_TIMEOUT)
                sleep(USB_SHOW_UP_TIMEOUT)
                # for path in device_path:
                #     path = os.path.realpath(path)
                #     if os.path.isdir(path):
                #         devices = os.listdir(path)
                #     else:
                #         devices = [path]

                #     for device in devices:
                #         device = os.path.join(path, device)
                #         lxc_cmd = ['lxc-device', '-n', lxc_name, 'add', device]
                #         self.run_command(lxc_cmd)
                #         self.logger.debug("%s: devices added from %s", lxc_name,
                #                           path)
            else:
                self.logger.debug("device_path is None")

        cmd = str(self.parameters['nexell_ext']['cmd']) + ' ' + str(self.parameters['nexell_ext']['param'])
        self.logger.info("%s Connecting to device using '%s'", self.name, cmd)
        signal.alarm(0)  # clear the timeouts used without connections.
        # ShellCommand executes the connection command
        shell = self.shell_class("%s\n" % cmd, self.timeout,
                                 logger=self.logger)
        if shell.exitstatus:
            raise JobError("%s command exited %d: %s" % (cmd,
                                                         shell.exitstatus,
                                                         shell.readlines()))
        # ShellSession monitors the pexpect
        connection = self.session_class(self.job, shell)
        connection.connected = True
        connection = super(ConnectNexell, self).run(connection, args)
        connection.prompt_str = self.parameters['prompts']
        self.data['boot-result'] = 'failed' if self.errors else 'success'
        return connection

