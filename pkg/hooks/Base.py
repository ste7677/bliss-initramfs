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

from pkg.hooks.Hook import Hook
from pkg.libs.Tools import Tools

class Base(Hook):
    @classmethod
    # Returns the kmod links
    def GetKmodLinks(cls):
        return cls._kmod_links

    _files = [
        # sys-apps/busybox
        "/bin/busybox",

        # sys-apps/kmod
        Tools.GetProgramPath("kmod"),

        # app-shells/bash
        "/bin/bash",

        # sys-apps/grep
        "/bin/egrep",
        "/bin/fgrep",
        "/bin/grep",

        # sys-apps/kbd,
        "/usr/bin/loadkeys",

        # udev
        Tools.GetUdevPath(),
        Tools.GetProgramPath("udevadm"),
    ]

    _kmod_links = [
        "depmod",
        "insmod",
        "lsmod",
        "modinfo",
        "modprobe",
        "rmmod",
    ]
