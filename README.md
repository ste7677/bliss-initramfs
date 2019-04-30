# Bliss Initramfs 7.1.5
#### Maintained fork of Bliss Initramfs 
#### originally designed by Jonathan Vasquez (fearedbliss) for Gentoo Linux

## Description

This script generates an initramfs image with all the included files and
dependencies needed to mount your filesystem.

It was designed primarily to be a simple alternative to genkernel or dracut 
for booting Gentoo Linux on Native ZFS (Not FUSE) and supports a few
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

## Gentoo Ebuilds

sys-kernel/bliss-initramfs: Updated gentoo ebuilds are available at the overlay [ste7677/gentoo-overlay-ste76](https://github.com/ste7677/gentoo-overlay-ste76). 
