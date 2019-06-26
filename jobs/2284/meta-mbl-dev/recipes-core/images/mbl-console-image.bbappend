# Copyright (c) 2018 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: MIT

###############################################################################
# mbl-console-image.bbappend
###############################################################################
SUMMARY = "Mbed Linux Development Modifications to Basic Minimal Image"


# No GPLv3 allowed in this image
IMAGE_LICENSE_CHECKER_BLACKLIST = ""
inherit image-license-checker
