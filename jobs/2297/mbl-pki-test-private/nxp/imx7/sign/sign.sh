#!/bin/bash

# set -x

TOOLS=${TOOLS:-"$PWD"}

# Path to CST Tool
CST_TOOLS_DIR="$PWD/../../../../mbl-nxp-private/tools/"
CST_TOOLS_PATH=${CST_TOOLS_DIR}"/cst-2.3.2"

# PATH to keys and certs directories
CST_PATH="$PWD/../boards/400766-1401-000899-1717/"

IMG=${IMG:="mbl-console-image-test-imx7s-warp-mbl.wic.gz"}
IMAGE=${IMAGE:="$PWD/../../../../../build-mbl/tmp-mbl-glibc/deploy/images/imx7s-warp-mbl/$IMG"}


echo "IMG:            $IMG"
echo "TOOLS:          $TOOLS"
echo "CST_PATH:       $CST_PATH"
echo "CST_TOOLS_PATH: $CST_TOOLS_PATH"
echo "IMAGE:          $IMAGE"
echo "IMG:            $IMG"

export CST_PATH
export CST_TOOLS_PATH
#export UBOOT_MKIMAGE=/usr/bin/mkimage


# Unroll the NXP CST tarball so can use CST
tar -C ${CST_TOOLS_DIR} -xvzf ${CST_TOOLS_DIR}/cst-2.3.2.tar.gz

# Copy image to CWD
cp $IMAGE .


# setup the CSF file to be used
pushd csf-templates
ln -s 2048-boot_scr_sign.csf boot_scr_sign.csf 
ln -s 2048-dtb_sign.csf dtb_sign.csf
ln -s 2048-optee_sign.csf optee_sign.csf
ln -s 2048-u-boot-recover_sign.csf u-boot-recover_sign.csf
ln -s 2048-u-boot_sign.csf u-boot_sign.csf
ln -s 2048-zimage_sign.csf zimage_sign.csf
popd


make -f $TOOLS/Makefile dirs-clean
make -f $TOOLS/Makefile dirs
make -f $TOOLS/Makefile u-boot-fetch-checkout
make -f $TOOLS/Makefile u-boot-build-tools
sudo $TOOLS/scripts/extract-unsigned-images.sh -i $IMG
make -f $TOOLS/Makefile all $CST_PATH
sudo $TOOLS/scripts/add-signed-images.sh -i $IMG

