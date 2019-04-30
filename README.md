## Maintained fork of Bliss Initramfs

# Bliss Initramfs 7.1.4
#### Jonathan Vasquez (fearedbliss)
#### Designed for Gentoo Linux

## Description

This script generates an initramfs image with all the included files and
dependencies needed to mount your filesystem.

It was designed primarily to be a simple alternative to genkernel
for booting Gentoo Linux on Native ZFS (Not FUSE), but it supports a few
other combinations such as LUKS, ZFS on LUKS, RAID, and LVM.

All you need to do is run "./mkinitrd", select the options you want "a-la-carte",
and then tell the initramfs via your bootloader parameters in what order you
want those features to be trigerred in. Check the USAGE file for examples.

## License

Released under the GNU General Public License v3 or Later.

## Dependencies

Please have the following installed:

- dev-lang/python 3.3 or greater
- app-arch/cpio
- app-shells/bash
- sys-apps/kmod
- sys-apps/grep
- sys-fs/udev OR sys-fs/eudev OR sys-apps/systemd (UUIDs, Labels, etc)
- sys-apps/kbd (Keymap support)
- sys-fs/zfs (ZFS support)
- sys-fs/mdadm (RAID support)
- sys-fs/lvm2 (LVM support)
- sys-fs/cryptsetup (LUKS support)
- app-crypt/gnupg (LUKS support)

For more information/instructions check the USAGE file.
