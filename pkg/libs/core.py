# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil
import re

from subprocess import call
from subprocess import check_output
from subprocess import CalledProcessError

import pkg.libs.variables as var

from pkg.libs.toolkit import Toolkit as tools

from pkg.hooks.base import Base
from pkg.hooks.zfs import ZFS
from pkg.hooks.lvm import LVM
from pkg.hooks.raid import RAID
from pkg.hooks.luks import LUKS
from pkg.hooks.addon import Addon

# Contains the core of the application
class Core:
	def __init__(self):
		self.base = Base()
		self.zfs = ZFS()
		self.lvm = LVM()
		self.raid = RAID()
		self.luks = LUKS()
		self.addon = Addon()

		# List of binaries (That will be 'ldd'ed later)
		self.binset = set()

		# List of modules that will be compressed
		self.modset = set()

	# Prints the menu and accepts user choice
	def print_menu(self):
		# If the user didn't pass an option through the command line,
		# then ask them which initramfs they would like to generate.
		if not var.choice:
			print("Which initramfs would you like to generate:")
			tools.print_options()
			var.choice = tools.eqst("Current choice [1]: ")
			tools.eline()

		# Enable the addons if the addon has files (modules) listed
		if self.addon.get_files():
			self.addon.enable_use()

		if var.choice == "1" or not var.choice:
			self.zfs.enable_use()
			self.addon.enable_use()
			self.addon.add_to_files("zfs")
		elif var.choice == "2":
			self.lvm.enable_use()
		elif var.choice == "3":
			self.raid.enable_use()
		elif var.choice == "4":
			self.raid.enable_use()
			self.lvm.enable_use()
		elif var.choice == "5":
			pass
		elif var.choice == '6':
			self.luks.enable_use()
			self.zfs.enable_use()
			self.addon.enable_use()
			self.addon.add_to_files("zfs")
		elif var.choice == "7":
			self.luks.enable_use()
			self.lvm.enable_use()
		elif var.choice == "8":
			self.luks.enable_use()
			self.raid.enable_use()
		elif var.choice == "9":
			self.luks.enable_use()
			self.raid.enable_use()
			self.lvm.enable_use()
		elif var.choice == "10":
			self.luks.enable_use()
		elif var.choice == '11':
			tools.ewarn("Exiting.")
			quit(1)
		else:
			tools.ewarn("Invalid Option. Exiting.")
			quit(1)

	# Creates the base directory structure
	def create_baselayout(self):
		for b in var.baselayout:
			call(["mkdir", "-p", b])

		# Create a symlink to this temporary directory at the home dir.
		# This will help us debug if anything (since the dirs are randomly
		# generated...)
		os.symlink(var.temp, var.tlink)

	# Ask the user if they want to use their current kernel, or another one
	def do_kernel(self):
		if not var.kernel:
			current_kernel = check_output(["uname", "-r"], universal_newlines=True).strip()

			x = "Do you want to use the current kernel: " + current_kernel + " [Y/n]: "
			var.choice = tools.eqst(x)
			tools.eline()

			if var.choice == 'y' or var.choice == 'Y' or not var.choice:
				var.kernel = current_kernel
			elif var.choice == 'n' or var.choice == 'N':
				var.kernel = tools.eqst("Please enter the kernel name: ")
				tools.eline()

				if not var.kernel:
					tools.die("You didn't enter a kernel. Exiting...")
			else:
				tools.die("Invalid Option. Exiting.")

		# Set modules path to correct location and sets kernel name for initramfs
		var.modules = "/lib/modules/" + var.kernel + "/"
		var.lmodules = var.temp + "/" + var.modules
		var.initrd = "initrd-" + var.kernel

		# Check modules directory
		self.check_mods_dir()

	# Check to make sure the kernel modules directory exists
	def check_mods_dir(self):
		if not os.path.exists(var.modules):
			tools.die("The modules directory for " + var.modules + " doesn't exist!")

	# Make sure that the arch is x86_64
	def get_arch(self):
		if var.arch != "x86_64":
			tools.die("Your architecture isn't supported. Exiting.")

	# Checks to see if the preliminary binaries exist
	def check_prelim_binaries(self):
		tools.einfo("Checking preliminary binaries ...")

		# If the required binaries don't exist, then exit
		for x in var.prel_bin:
			if not os.path.isfile(x):
				tools.err_bin_dexi(x)

	# Compresses the kernel modules and generates modprobe table
	def do_modules(self):
		tools.einfo("Compressing kernel modules ...")

		cmd = "find " + var.lmodules + " -name " + "*.ko"
		results = check_output(cmd, shell=True, universal_newlines=True).strip()

		for x in results.split("\n"):
			cmd = "gzip -9 " + x
			cr = call(cmd, shell=True)

			if cr != 0:
				tools.die("Unable to compress " + x + " !")

	# Generates the modprobe information
	def gen_modinfo(self):
		tools.einfo("Generating modprobe information ...")

		# Copy modules.order and modules.builtin just so depmod doesn't spit out warnings. -_-
		tools.ecopy(var.modules + "/modules.order")
		tools.ecopy(var.modules + "/modules.builtin")

		result = call(["depmod", "-b", var.temp, var.kernel])

		if result != 0:
			tools.die("You've encountered an unknown problem!")

	# Create the required symlinks to it
	def create_links(self):
		tools.einfo("Creating symlinks ...")

		# Needs to be from this directory so that the links are relative
		os.chdir(var.lbin)

		# Create busybox links
		cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "cd /bin && /bin/busybox --install -s ."'

		cr = call(cmd, shell=True)

		if cr != 0:
			tools.die("Unable to create busybox links via chroot!")

		# Create 'sh' symlink to 'bash'
		os.remove(var.temp + "/bin/sh")
		os.symlink("bash", "sh")

		# Switch to the kmod directory, delete the corresponding busybox
		# symlink and create the symlinks pointing to kmod
		if os.path.isfile(var.lsbin + "/kmod"):
			os.chdir(var.lsbin)
		elif os.path.isfile(var.lbin + "/kmod"):
			os.chdir(var.lbin)

		for link in self.base.get_kmod_links():
			os.remove(var.temp + "/bin/" + link)
			os.symlink("kmod", link)

		# If 'lvm.static' exists, then make a 'lvm' symlink to it
		if os.path.isfile(var.lsbin + "/lvm.static"):
			os.symlink("lvm.static", "lvm")

	# This functions does any last minute steps like copying zfs.conf,
	# giving init execute permissions, setting up symlinks, etc
	def last_steps(self):
		tools.einfo("Performing finishing steps ...")

		# Create mtab file
		call(["touch", var.temp + "/etc/mtab"])

		if not os.path.isfile(var.temp + "/etc/mtab"):
			tools.die("Error creating the mtab file. Exiting.")

		# Set library symlinks
		if os.path.isdir(var.temp + "/usr/lib") and os.path.isdir(var.temp + "/lib64"):
			pcmd = 'find /usr/lib -iname "*.so.*" -exec ln -s "{}" /lib64 \;'
			cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
			call(cmd, shell=True)

		if os.path.isdir(var.temp + "/usr/lib32") and os.path.isdir(var.temp + "/lib32"):
			pcmd = 'find /usr/lib32 -iname "*.so.*" -exec ln -s "{}" /lib32 \;'
			cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
			call(cmd, shell=True)

		if os.path.isdir(var.temp + "/usr/lib64") and os.path.isdir(var.temp + "/lib64"):
			pcmd = 'find /usr/lib64 -iname "*.so.*" -exec ln -s "{}" /lib64 \;'
			cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
			call(cmd, shell=True)

		# Copy init functions
		shutil.copytree(var.phome + "/files/libs/", var.temp + "/libs")

		# Copy the init script
		shutil.copy(var.phome + "/files/init", var.temp)

		if not os.path.isfile(var.temp + "/init"):
			tools.die("Error creating the init file. Exiting.")

		# Give execute permissions to the script
		cr = call(["chmod", "u+x", var.temp + "/init"])

		if cr != 0:
			tools.die("Failed to give executive privileges to " + var.temp + "/init")

		# Fix 'poweroff, reboot' commands
		call("sed -i \"71a alias reboot='reboot -f' \" " + var.temp + "/etc/bash/bashrc", shell=True)
		call("sed -i \"71a alias poweroff='poweroff -f' \" " + var.temp + "/etc/bash/bashrc", shell=True)

		# Sets initramfs script version number
		call(["sed", "-i", "-e", "19s/0/" + var.version + "/", var.temp + "/init"])

		# Fix EDITOR/PAGER
		call(["sed", "-i", "-e", "12s:/bin/nano:/bin/vi:", var.temp + "/etc/profile"])
		call(["sed", "-i", "-e", "13s:/usr/bin/less:/bin/less:", var.temp + "/etc/profile"])

		# Any last substitutions or additions/modifications should be done here
		if self.zfs.get_use():
			# Enable ZFS in the init if ZFS is being used
			call(["sed", "-i", "-e", "13s/0/1/", var.temp + "/init"])

			# Copy the /etc/modprobe.d/zfs.conf file if it exists
			if os.path.isfile("/etc/modprobe.d/zfs.conf"):
				tools.ecopy("/etc/modprobe.d/zfs.conf")

			# Get the system's hostid now since it will default to 0
			# within the initramfs environment

			# source: https://bbs.archlinux.org/viewtopic.php?id=153868
			hostid = check_output(["hostid"], universal_newlines=True).strip()

			cmd = "printf $(echo -n " + hostid.upper() + " | " + \
			"sed 's/\(..\)\(..\)\(..\)\(..\)/\\\\x\\4\\\\x\\3\\\\x\\2\\\\x\\1/') " + \
			"> " + var.temp + "/etc/hostid"

			call(cmd, shell=True)

			# Copy zpool.cache into initramfs
			if os.path.isfile("/etc/zfs/zpool.cache"):
				tools.ewarn("Using your zpool.cache file ...")
				tools.ecopy("/etc/zfs/zpool.cache")
			else:
				tools.ewarn("No zpool.cache was found. It will not be used ...")

		# Enable RAID in the init if RAID is being used
		if self.raid.get_use():
			call(["sed", "-i", "-e", "14s/0/1/", var.temp + "/init"])

		# Enable LVM in the init if LVM is being used
		if self.lvm.get_use():
			call(["sed", "-i", "-e", "15s/0/1/", var.temp + "/init"])

		# Enable LUKS in the init if LUKS is being used
		if self.luks.get_use():
			call(["sed", "-i", "-e", "16s/0/1/", var.temp + "/init"])

		# Enable ADDON in the init and add our modules to the initramfs
		# if addon is being used
		if self.addon.get_use():
			call(["sed", "-i", "-e", "17s/0/1/", var.temp + "/init"])
			call(["sed", "-i", "-e", "20s/\"\"/\"" + " ".join(self.addon.get_files()) + "\"/", var.temp + "/libs/common.sh"])

	# Create the solution
	def create(self):
		tools.einfo("Creating the initramfs ...")

		# The find command must use the `find .` and not `find ${T}`
		# because if not, then the initramfs layout will be prefixed with
		# the ${T} path.
		os.chdir(var.temp)

		call(["find . -print0 | cpio -o --null --format=newc | gzip -9 > " +  var.home + "/" + var.initrd], shell=True)

		if not os.path.isfile(var.home + "/" + var.initrd):
			tools.die("Error creating the initramfs. Exiting.")

	# Checks to see if the binaries exist, if not then emerge
	def check_binaries(self):
		tools.einfo("Checking required files ...")

		# Check required base files
		for f in self.base.get_files():
			if not os.path.exists(f):
				tools.err_bin_dexi(f)

		# Check required zfs files
		if self.zfs.get_use():
			tools.eflag("Using ZFS")
			for f in self.zfs.get_files():
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

		# Check required lvm files
		if self.lvm.get_use():
			tools.eflag("Using LVM")
			for f in self.lvm.get_files():
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

		# Check required raid files
		if self.raid.get_use():
			tools.eflag("Using RAID")
			for f in self.raid.get_files():
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

		# Check required luks files
		if self.luks.get_use():
			tools.eflag("Using LUKS")
			for f in self.luks.get_files():
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

	# Installs the packages
	def install(self):
		tools.einfo("Copying required files ...")

		for f in self.base.get_files():
			self.emerge(f)

		if self.zfs.get_use():
			for f in self.zfs.get_files():
				self.emerge(f)

		if self.lvm.get_use():
			for f in self.lvm.get_files():
				self.emerge(f)

		if self.raid.get_use():
			for f in self.raid.get_files():
				self.emerge(f)

		if self.luks.get_use():
			for f in self.luks.get_files():
				self.emerge(f)

	# Filters and installs a package into the initramfs
	def emerge(self, afile):
		# If the application is a binary, add it to our binary set

		try:
			lcmd = check_output('file ' + afile.strip() + ' | grep "linked"', shell=True, universal_newlines=True).strip()
			self.binset.add(afile)
		except CalledProcessError:
			pass

		# Copy the file into the initramfs
		tools.ecopy(afile)

	# Copy modules and their dependencies
	def copy_modules(self):
		tools.einfo("Copying modules ...")

		moddeps = set()

		# Build the list of module dependencies
		if self.addon.get_use():
			# Checks to see if all the modules in the list exist
			for x in self.addon.get_files():
				try:
					cmd = 'find ' + var.modules + ' -iname "' + x + '.ko" | grep ' + x + '.ko'
					result = check_output(cmd, universal_newlines=True, shell=True).strip()
					self.modset.add(result)
				except CalledProcessError:
					tools.err_mod_dexi(x)

		# If a kernel has been set, try to update the module dependencies
		# database before searching it
		if var.kernel:
			result = call(["depmod", var.kernel])

			if result:
				tools.die("Error updating module dependency database!")

		# Get the dependencies for all the modules in our set
		for x in self.modset:
			# Get only the name of the module
			match = re.search('(?<=/)\w+.ko', x)

			if match:
				sx = match.group().split(".")[0]

				cmd = "modprobe -S " + var.kernel + " --show-depends " + sx + " | awk -F ' ' '{print $2}'"
				results = check_output(cmd, shell=True, universal_newlines=True).strip()

				for i in results.split("\n"):
					moddeps.add(i.strip())

		# Copy the modules/dependencies
		if moddeps:
			for x in moddeps:
				tools.ecopy(x)

			# Compress the modules and update module dependency database inside the initramfs
			self.do_modules()
			self.gen_modinfo()

	# Gets the library dependencies for all our binaries and copies them
	# into our initramfs.
	def copy_deps(self):
		tools.einfo("Copying library dependencies ...")

		bindeps = set()

		# Get the interpreter name that is on this system
		result = check_output("ls " + var.lib64 + "/ld-linux-x86-64.so*", shell=True, universal_newlines=True).strip()

		# Add intepreter to deps since everything will depend on it
		bindeps.add(result)

		# Get the dependencies for the binaries we've collected and add them to
		# our bindeps set. These will all be copied into the initramfs later.
		for b in self.binset:
			cmd = "ldd " + b + " | awk -F '=>' '{print $2}' | awk -F ' ' '{print $1}' | sed '/^ *$/d'"
			results = check_output(cmd, shell=True, universal_newlines=True).strip()

			if results:
				for j in results.split("\n"):
					bindeps.add(j)

		# Copy all the dependencies of the binary files into the initramfs
		for x in bindeps:
			tools.ecopy(x)

