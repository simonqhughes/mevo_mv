# Copyright (c) 2018 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: MIT

###############################################################################
# Packages added irrespective of the MACHINE
#     - runc-opencontainers. Open Container Initiative (oci) containerised 
#       environment for secure application execution.
#     - kernel-modules. Required by iptables related modules (e.g. netfilter
#       connection tracking.
#     - optee-os. If the machine supports optee include the os.
#     - optee-client. If the machine supports optee include the client.
###############################################################################
RDEPENDS_remove_packagegroup-mbl-production = "avahi-autoipd"
RDEPENDS_remove_packagegroup-mbl-production = "ca-certificates"
RDEPENDS_remove_packagegroup-mbl-production = "runc-opencontainers"
RDEPENDS_remove_packagegroup-mbl-production = "iptables"
RDEPENDS_remove_packagegroup-mbl-production = "kernel-modules"
RDEPENDS_remove_packagegroup-mbl-production = "rng-tools"
RDEPENDS_remove_packagegroup-mbl-production = "opkg"
RDEPENDS_remove_packagegroup-mbl-production = "mbl-app-manager"
RDEPENDS_remove_packagegroup-mbl-production = "mbl-app-lifecycle-manager"
RDEPENDS_remove_packagegroup-mbl-production = "mbl-app-update-manager"
RDEPENDS_remove_packagegroup-mbl-production = "mbl-firmware-update-manager"
RDEPENDS_remove_packagegroup-mbl-production = "python3-core"
# pyhton3-debugger and python3-doctest are included because Pytest is
# dependent on them.
RDEPENDS_remove_packagegroup-mbl-production = "python3-debugger"
RDEPENDS_remove_packagegroup-mbl-production = "python3-doctest"
RDEPENDS_remove_packagegroup-mbl-production = "python3-logging"
# See meta-mbl/recipes-devtools/python/python3_%.bbappend for information
# on why python3-ntpath is included in the package group.
RDEPENDS_remove_packagegroup-mbl-production = "python3-ntpath"
RDEPENDS_remove_packagegroup-mbl-production = "python3-pip"
RDEPENDS_remove_packagegroup-mbl-production = "python3-runpy"
RDEPENDS_remove_packagegroup-mbl-production = "python3-shell"
RDEPENDS_remove_packagegroup-mbl-production = "python3-venv"
RDEPENDS_remove_packagegroup-mbl-production = "mbl-cloud-client"
RDEPENDS_remove_packagegroup-mbl-production = "usbgadget"
RDEPENDS_remove_packagegroup-mbl-production = "usbinit"

