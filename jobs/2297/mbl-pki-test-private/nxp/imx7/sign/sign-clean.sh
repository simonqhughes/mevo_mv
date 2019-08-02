#!/bin/bash

rm -fR signed-binaries
rm -fR temp
rm -fR mbl-u-boot
rm -fR mbl-console-image*
rm -fR signed-mbl-console-image*
rm -f csf-templates/boot_scr_sign.csf
rm -f csf-templates/dtb_sign.csf
rm -f csf-templates/optee_sign.csf
rm -f csf-templates/u-boot-recover_sign.csf
rm -f csf-templates/u-boot_sign.csf
rm -f csf-templates/zimage_sign.csf
