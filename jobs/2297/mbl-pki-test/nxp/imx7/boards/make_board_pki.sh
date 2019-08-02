#!/bin/bash

############################################################################## 
# SPDX-License-Identifier:      Apache-2.0
#
# SCRIPT: Generate NXP Warp7 keying material using HAB tools 
##############################################################################

# Enable debug
# set -x


############################################################################## 
# DEFINES
##############################################################################
BOARD_ID=""
TIMESTAMP=$(date --utc +%Y%m%d_%H%M%S)


############################################################################## 
# FUNCTION: mkbrdpki_setup
#  Setup a temporary work directory
# ARGUMENTS:
#  $1   Board ID
##############################################################################
mkbrdpki_setup() 
{
    local WORKDIR=$1
    # create subdir 
    mkdir -p ${WORKDIR}

    # unroll cst archive there
    tar -C ${WORKDIR} -xvzf ../../../../mbl-nxp-private/tools/cst-2.3.2.tar.gz 
    cp serial ${WORKDIR}/cst-2.3.2/keys
    cp key_pass.txt  ${WORKDIR}/cst-2.3.2/keys
	return $?
}


############################################################################## 
# FUNCTION: mkbrdpki_make_keying_material
#  Make private keys and certificates containing public keys
# ARGUMENTS:
#  $1   Board ID
##############################################################################
mkbrdpki_make_keying_material() 
{

    local WORKDIR=$1
    local HABTOOL=`pwd`/${WORKDIR}/cst-2.3.2/keys/hab4_pki_tree.sh

    pushd ${WORKDIR}/cst-2.3.2/keys

    # make keys and certificates
    ${HABTOOL} <<-HABINPUT_1024_END
n
n
1024
10
4
y
HABINPUT_1024_END

    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: HAB tool failed to generate 1024 bit keying material"
        popd
        return $ret
    fi

    ${HABTOOL} <<-HABINPUT_2048_END
n
n
2048
10
4
y
HABINPUT_2048_END
    
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: HAB tool failed to generate 1024 bit keying material"
        popd
        return $ret
    fi

    ${HABTOOL} <<-HABINPUT_4096_END
n
n
4096
10
4
y
HABINPUT_4096_END
    
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: HAB tool failed to generate 1024 bit keying material"
        popd
        return $ret
    fi

    popd
    return $?
}
    

############################################################################## 
# FUNCTION: mkbrdpki_fuse_file
#  Use the srktool to create the SRK_1_2_3_4_xxx_fuse.bin and
#  SRK_1_2_3_4_xxx_table.bin files  
# ARGUMENTS:
#  $1   Board ID
##############################################################################
mkbrdpki_fuse_file() 
{
    local WORKDIR=$1
    local SRKTOOL=`pwd`/${WORKDIR}/cst-2.3.2/linux64/srktool
    
    local SRK1_1024=SRK1_sha256_1024_65537_v3_ca_crt.pem
    local SRK2_1024=SRK2_sha256_1024_65537_v3_ca_crt.pem
    local SRK3_1024=SRK3_sha256_1024_65537_v3_ca_crt.pem
    local SRK4_1024=SRK4_sha256_1024_65537_v3_ca_crt.pem
    local SRK1_2048=SRK1_sha256_2048_65537_v3_ca_crt.pem
    local SRK2_2048=SRK2_sha256_2048_65537_v3_ca_crt.pem
    local SRK3_2048=SRK3_sha256_2048_65537_v3_ca_crt.pem
    local SRK4_2048=SRK4_sha256_2048_65537_v3_ca_crt.pem
    local SRK1_4096=SRK1_sha256_4096_65537_v3_ca_crt.pem
    local SRK2_4096=SRK2_sha256_4096_65537_v3_ca_crt.pem
    local SRK3_4096=SRK3_sha256_4096_65537_v3_ca_crt.pem
    local SRK4_4096=SRK4_sha256_4096_65537_v3_ca_crt.pem
    local HAB_VER=4
    local SRK_FILE_HEAD=SRK_1_2_3_4_
    local SRK_TABLE_FILE_TAIL=_table.bin
    local SRK_FUSE_FILE_TAIL=_fuse.bin

    local SRK_FUSE_FILE_1024=${SRK_FILE_HEAD}1024${SRK_FUSE_FILE_TAIL}
    local SRK_TABLE_FILE_1024=${SRK_FILE_HEAD}1024${SRK_TABLE_FILE_TAIL}
    local SRK_FUSE_FILE_2048=${SRK_FILE_HEAD}2048${SRK_FUSE_FILE_TAIL}
    local SRK_TABLE_FILE_2048=${SRK_FILE_HEAD}2048${SRK_TABLE_FILE_TAIL}
    local SRK_FUSE_FILE_4096=${SRK_FILE_HEAD}4096${SRK_FUSE_FILE_TAIL}
    local SRK_TABLE_FILE_4096=${SRK_FILE_HEAD}4096${SRK_TABLE_FILE_TAIL}

    pushd ${WORKDIR}/cst-2.3.2/crts
    ${SRKTOOL} -h ${HAB_VER} -t ${SRK_FUSE_FILE_1024} -e ${SRK_TABLE_FILE_1024} -d sha256 -c ./${SRK1_1024},./${SRK2_1024},./${SRK3_1024},./${SRK4_1024} -f 1
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: srktool failed to generate 1024 bit fuse file."
        popd
        return $ret
    fi
    
    ${SRKTOOL} -h ${HAB_VER} -t ${SRK_FUSE_FILE_2048} -e ${SRK_TABLE_FILE_2048} -d sha256 -c ./${SRK1_2048},./${SRK2_2048},./${SRK3_2048},./${SRK4_2048} -f 1
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: srktool failed to generate 2048 bit fuse file."
        popd
        return $ret
    fi

    ${SRKTOOL} -h ${HAB_VER} -t ${SRK_FUSE_FILE_4096} -e ${SRK_TABLE_FILE_4096} -d sha256 -c ./${SRK1_4096},./${SRK2_4096},./${SRK3_4096},./${SRK4_4096} -f 1
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: srktool failed to generate 4096 bit fuse file."
        popd
        return $ret
    fi

    popd

    return $?
}


############################################################################## 
# FUNCTION: mkbrdpki_cleanup
#  cleanup ready for adding new keying material to repository by
#  removing unnecessary files.
# ARGUMENTS:
#  $1   Board ID
##############################################################################
mkbrdpki_cleanup() 
{
    local WORKDIR=$1

    # cleanup
    rm -fR ${WORKDIR}/cst-2.3.2/keys/add_key.bat
    rm -fR ${WORKDIR}/cst-2.3.2/keys/add_key.sh
    rm -fR ${WORKDIR}/cst-2.3.2/keys/hab3_pki_tree.bat
    rm -fR ${WORKDIR}/cst-2.3.2/keys/hab3_pki_tree.sh
    rm -fR ${WORKDIR}/cst-2.3.2/keys/hab4_pki_tree.bat
    rm -fR ${WORKDIR}/cst-2.3.2/keys/hab4_pki_tree.sh

    # The serial number will have been update by the HAB tool.
    # Update the managed copy
    mv serial serial.${TIMESTAMP}
    cp ${WORKDIR}/cst-2.3.2/keys/serial .

    mv ${WORKDIR}/cst-2.3.2/keys ${WORKDIR}/keys
    mv ${WORKDIR}/cst-2.3.2/crts ${WORKDIR}/crts
    rm -fR ${WORKDIR}/cst-2.3.2

    return $?
}


############################################################################## 
# FUNCTION: mkbrdpki_usage
#  Print a usage statement.
# ARGUMENTS:
#  $0   Name of script
##############################################################################
mkbrdpki_usage()
{
    echo "Usage : $0 -i <board_id>"
    echo ""
    echo "<baord_id>    unique board ID e.g. serial number"
    exit
}


############################################################################## 
# FUNCTION: mkbrdpki_command_line
#  Process the command line arguments.
# ARGUMENTS:
#  $@   All command line arguments for processing
##############################################################################
mkbrdpki_command_line()
{
    if [ "$#" -ne 2 ]
    then
      mkbrdpki_usage
    fi
    
    while [ "$1" != "" ]; do
        case $1 in
            -i )           shift
                           BOARD_ID=$1
                           ;;
            * )            mkbrdpki_usage
        esac
        shift
    done
    
    # extra validation suggested by @technosaurus
    if [ "$BOARD_ID" = "" ]
    then
        mkbrdpki_usage
    fi
}


############################################################################## 
# FUNCTION: mkbrdpki_main
#  This is the main script entrypoint.
# ARGUMENTS:
#  $@   All command line arguments for processing
##############################################################################
mkbrdpki_make_main() 
{
    local ret=0
    
    mkbrdpki_command_line $@
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: unable to parse command line arguments"
        exit $ret
    fi

    mkbrdpki_setup ${BOARD_ID}
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: unable to setup working directory"
        exit $ret
    fi

    mkbrdpki_make_keying_material ${BOARD_ID}
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: unable to generate keying material"
        exit $ret
    fi

    mkbrdpki_fuse_file ${BOARD_ID}
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: unable to generate fuse files"
        exit $ret
    fi

    mkbrdpki_cleanup ${BOARD_ID}
    ret=$?
    if [ ! $? -eq 0 ]; then
        echo "Error: unable to cleanup after generating keying material"
        exit $ret
    fi

    return $?
}


mkbrdpki_make_main $@
