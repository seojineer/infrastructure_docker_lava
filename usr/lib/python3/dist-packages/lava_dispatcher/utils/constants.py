# Copyright (C) 2014 Linaro Limited
#
# Author: Remi Duraffort <remi.duraffort@linaro.org>
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

# Overrides are only supported when and as declared in the comments for
# each constant.

# pylint: disable=anomalous-backslash-in-string

# Delay between each character sent to the shell. This is required for some
# slow serial consoles.
SHELL_SEND_DELAY = 0.05

# Default timeout for shell operations
SHELL_DEFAULT_TIMEOUT = 60

# Default timeout when downloading over http/https
HTTP_DOWNLOAD_TIMEOUT = 15

# Retry at most 5 times
MAX_RETRY = 5

# u-boot auto boot prompt
UBOOT_AUTOBOOT_PROMPT = "Hit any key to stop autoboot"

# u-boot default timeout for commands
UBOOT_DEFAULT_CMD_TIMEOUT = 90

# Ramdisk default filenames
RAMDISK_FNAME = 'ramdisk.cpio'

# Size of the chunks when copying file
FILE_DOWNLOAD_CHUNK_SIZE = 32768

# Size of the chunks when downloading over http
HTTP_DOWNLOAD_CHUNK_SIZE = 32768

# Size of the chunks when downloading over scp
SCP_DOWNLOAD_CHUNK_SIZE = 32768

# Clamp on the maximum timeout allowed for overrides
OVERRIDE_CLAMP_DURATION = 300

# Auto-login prompt timeout default
AUTOLOGIN_DEFAULT_TIMEOUT = 120

# dispatcher temporary directory
# This is distinct from the TFTP daemon directory
# Files here are for download using the Apache /tmp alias.
DISPATCHER_DOWNLOAD_DIR = "/var/lib/lava/dispatcher/tmp"

# OS shutdown message
# Override: set as the shutdown-message parameter of an Action.
SHUTDOWN_MESSAGE = 'The system is going down for reboot NOW'

# Kernel starting message
BOOT_MESSAGE = 'Booting Linux'

# Default shell prompt for AutoLogin
DEFAULT_SHELL_PROMPT = 'lava-test: # '

# Distinctive prompt characters which can
# help distinguish status messages from shell prompts.
DISTINCTIVE_PROMPT_CHARACTERS = "\\:"

# LAVA Coordinator setup and finalize timeout
LAVA_MULTINODE_SYSTEM_TIMEOUT = 90

# Default Action timeout
ACTION_TIMEOUT = 30

# Android tmp directory
ANDROID_TMP_DIR = '/data/local/tmp'

# Default timeout for fastboot reboot
FASTBOOT_REBOOT_TIMEOUT = 10

# LXC container path
LXC_PATH = "/var/lib/lxc"

# Nexell extension
NEXELL_PATH = "/var/lib/nexell"

# LXC finalize timeout
LAVA_LXC_TIMEOUT = 30

# LXC templates with mirror option
LXC_TEMPLATE_WITH_MIRROR = ['debian', 'ubuntu']

# Timeout used by the vland protocol when waiting for vland to
# respond to the api.create_vlan request, in seconds.
VLAND_DEPLOY_TIMEOUT = 120

# ipxe boot interrupting
IPXE_BOOT_PROMPT = "Press Ctrl-B for the iPXE command line"

# bootloader default timeout for commands
BOOTLOADER_DEFAULT_CMD_TIMEOUT = 90

GRUB_BOOT_PROMPT = "Press enter to boot the selected OS"

# Timeout for USB devices to settle and show up
USB_SHOW_UP_TIMEOUT = 20

# kernel boot monitoring
# Some successful kernel builds end the boot with this string
KERNEL_FREE_UNUSED_MSG = 'Freeing unused kernel memory'
# Some successful kernel builds end the boot with this string
KERNEL_FREE_INIT_MSG = 'Freeing init memory'
# exception
KERNEL_EXCEPTION_MSG = '-+\[ cut here \]-+\s+(.*\s+-+\[ end trace (\w*) \]-+)'
# unhandled fault
KERNEL_FAULT_MSG = '(Unhandled fault.*)\r\n'
# panic
KERNEL_PANIC_MSG = "Kernel panic - (.*) end Kernel panic"
# init dropping to a shell - often needs a sendline
KERNEL_INIT_ALERT = 'ALERT! .* does not exist.\s+Dropping to a shell!'

# qemu installer size limit in Mb
# (i.e. size * 1024 * 1024)
INSTALLER_IMAGE_MAX_SIZE = 8 * 1024  # 8Gb
INSTALLER_QUIET_MSG = 'Loading initial ramdisk'

# V1 compatibility
DEFAULT_V1_PATTERN = "(?P<test_case_id>.*-*)\\s+:\\s+(?P<result>(PASS|pass|FAIL|fail|SKIP|skip|UNKNOWN|unknown))"
DEFAULT_V1_FIXUP = {'PASS': 'pass', 'FAIL': 'fail', 'SKIP': 'skip', 'UNKNOWN': 'unknown'}

# Message for notifying completion of secondary deployment
SECONDARY_DEPLOYMENT_MSG = "Secondary media deployment complete"
