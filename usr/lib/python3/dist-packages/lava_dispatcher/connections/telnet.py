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

import os
import signal
from time import sleep
from lava_common.exceptions import (
    InfrastructureError,
    JobError,
    LAVABug,
)
from lava_dispatcher.test.utils import infrastructure_error
from lava_dispatcher.action import (
    Action,
    JobError,
)
from lava_dispatcher.shell import ShellCommand, ShellSession
from lava_dispatcher.utils.constants import USB_SHOW_UP_TIMEOUT

# pylint: disable=too-many-public-methods


class ConnectTelnet(Action):
    """
    Class to make a telnet shell connection
    """
    def __init__(self,parameters):
        super(ConnectTelnet, self).__init__()
        self.name = "connect-telnet"
        self.summary = "run connection command"
        self.description = "connect to the telnet container"
        self.session_class = ShellSession
        self.shell_class = ShellCommand
        self.params = parameters
        
    def validate(self):
        super(ConnectTelnet, self).validate()
        self.errors = infrastructure_error('telnet')
        if 'prompts' not in self.parameters:
            self.errors = "Unable to identify test image prompts from parameters."

    def run(self, connection, args=None):
        self.logger.debug("SUKER: connection/telnet.py: " + str(self.parameters))
        self.device_path = self.parameters['nexell_ext']['device_path']

        # Attach usb device to telnet
        if 'device_path' in list(self.job.device.keys()):
            device_path = self.job.device['device_path']
            if not isinstance(device_path, list):
                raise JobError("device_path should be a list")

            if device_path:
                # Wait USB_SHOW_UP_TIMEOUT seconds for usb device to show up
                self.logger.info("Wait %d seconds for usb device to show up",
                                 USB_SHOW_UP_TIMEOUT)
                sleep(USB_SHOW_UP_TIMEOUT)

                for path in device_path:
                    path = os.path.realpath(path)
                    if os.path.isdir(path):
                        devices = os.listdir(path)
                    else:
                        devices = [path]
            else:
                self.logger.debug("device_path is None")

        # Nexell extension
        elif self.device_path is not None:
            device_path = self.device_path

            if device_path:
                # Wait USB_SHOW_UP_TIMEOUT seconds for usb device to show up
                self.logger.info("Wait %d seconds for usb device to show up",
                                 USB_SHOW_UP_TIMEOUT)
                sleep(USB_SHOW_UP_TIMEOUT)

                devices =[device_path]

	# Nexell extension
        #cmd = "telnet 192.168.1.19 4001"
        self.logger.debug("devices:%s",devices[0])
        cmd = self.job.device['commands']['connect']
        #cmd_str = ['cat',devices[0]]
        #cmd = ' '.join(cmd_str)
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
        connection = super(ConnectTelnet, self).run(connection, args)
        connection.prompt_str = self.parameters['prompts']
        self.data['boot-result'] = 'failed' if self.errors else 'success'
        return connection
