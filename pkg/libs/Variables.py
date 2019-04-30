# Copyright (C) 2012-2018 Jonathan Vasquez <jon@xyinn.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see<https://www.gnu.org/licenses/>.

import os
import subprocess
import sys
import random

# Application Info
name = "Bliss Initramfs"
author = "Jonathan Vasquez"
email = "jon@xyinn.org"
contact = author + " <" + email + ">"
version = "7.1.4"
<<<<<<< HEAD
license = "2-BSD"
=======
license = "GPLv3+"
>>>>>>> 26579dbb3fd60547b07c446367483f0419c42172

# Locations
home = os.getcwd()

# Kernel and Menu Choice
kernel = ""
modules = ""
lmodules = ""
initrd = "initrd"
features = ""

rstring = str(random.randint(100000000, 999999999))

# Temporary directory will now be in 'home' rather than
# in /tmp since people may have executed their /tmp with 'noexec'
# which would cause bliss-initramfs to fail to execute any binaries
# in the temp dir.
temp = home + "/bi-" + rstring

# Directory of Program
phome = os.path.dirname(os.path.realpath(sys.argv[0]))

# Files Directory
files_dir = phome + "/files"

# System Directories
bin = "/bin"
sbin = "/sbin"
lib = "/lib"
lib64 = "/lib64"
etc = "/etc"

# Paths in Temp (Local)
lbin = temp + bin
lsbin = temp + sbin
llib = temp + lib
llib64 = temp + lib64
letc = temp + etc

# CPU Architecture
arch = subprocess.check_output(["uname", "-m"], universal_newlines=True).strip()

# Preliminary binaries needed for the success of creating the initrd
# but that are not needed to be placed inside the initrd
prel_bin = [
    "/bin/cpio",
    "/sbin/depmod",
]

# Firmware directory
firmwareDirectory = "/lib/firmware/"

# Layout of the initramfs
baselayout = [
    temp + "/etc",
    temp + "/etc/bash",
    temp + "/etc/zfs",
    temp + "/dev",
    temp + "/proc",
    temp + "/sys",
    temp + "/mnt",
    temp + "/mnt/root",
    temp + "/mnt/key",
    temp + "/lib",
    temp + "/lib/modules",
    temp + "/lib64",
    temp + "/bin",
    temp + "/sbin",
    temp + "/usr",
    temp + "/root",
    temp + "/run"
]

# Line numbers in the 'init' script where sed will substitute its values in
initrdVersionLine = "19"
addonModulesLine = "20"
useLuksLine = "21"
useRaidLine = "32"
useLvmLine = "23"
useZfsLine = "24"
useAddonLine = "25"
