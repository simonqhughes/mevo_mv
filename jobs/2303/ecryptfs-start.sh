#!/bin/bash
#
# TODO: copyright notice
#
# ecryptfs-start.sh
#  Script to setup blahs
#  TODO: more explanation.
#
# Document the configuration that needs to be present in the /etc/fstab
#
# /home/root/.secret /home/root/secret ecryptfs \
#   noauto,user,ecryptfs_sig=dd0a45455a291a98, \
#   ecryptfs_fnek_sig=dd0a45455a291a98, \
#   ecryptfs_cipher=aes,ecryptfs_key_bytes=16, \
#   key=passphrase:passphrase_passwd_file=/home/root/passphrase1.txt, \
#   ecryptfs_passthrough=n,ecryptfs_unlink_sigs 0 0
#
#
# Outstanding issue:
#  passphrase is generated and stored in the configuration dir.
#  this shouldnt be the case, as it should be in the keyring and 
#  referred to by its signature

# The upper and lower directory terminology originated with overlay 
# filesystems and is further described at [1].
#
# Notes:
# useful keyctl commands: 
#   keyctl list            # list keys
#   keyctl show            # list keys
#   keyctl revoke <id>     # make key for deletion
#   keyctl reap            # delete revoked keys
#
# References
# ==========
# [1] See the following document in the Linux kernel source code tree: 
#       <src/>/Documentation/filesystems/overlayfs.txt
#
# TODO: 
# - allow _UPPER dir to be configured by a command line arg that can be
#   specified to the script.
# - allow _LOWER to be specified as command line arg. check if this can be
#   supplied by ecryptfs.service file.


 


# TODO: remove next line
#set -x


###############################################################################
# Tools, required to be on the PATH 
###############################################################################
EFS_DAEMON="ecryptfsd"
EFS_INSERT_PASSPH="ecryptfs-insert-wrapped-passphrase-into-keyring"
EFS_WRAP_PASSPH="ecryptfs-wrap-passphrase"

###############################################################################
# Symbols
###############################################################################
# TODO: set this back when done testing on PC
#EFS_PREFIX="./"
EFS_PREFIX=""
EFS_FSTAB_PATH=${EFS_PREFIX}"/etc/fstab"
# todo: set EFS_HOME to empty
EFS_HOME=${EFS_PREFIX}"/home"
EFS_RANDOM="/dev/random"
# TODO: remove next line
#EFS_RANDOM="/dev/urandom"
EFS_USER="root"

# Directory to store configuration artifacts
EFS_CONFIG_DIR=".ecryptfs"
EFS_CONFIG_DIR_PATH=${EFS_HOME}/${EFS_USER}/${EFS_CONFIG_DIR}
EFS_CONFIG_FSTAB_PATH=${EFS_CONFIG_DIR_PATH}/"fstab.old"
EFS_CONFIG_KEY_FILENAME_PATH=${EFS_CONFIG_DIR_PATH}/"wrapped-passphrase.bin"
# TODO: remove this as not used
# EFS_CONFIG_KEY_SIG_FILE_PATH=${EFS_CONFIG_DIR_PATH}/"key_sig.txt"
EFS_CONFIG_PASSPHRASE_FILE_PATH=${EFS_CONFIG_DIR_PATH}/"passphrase.txt"

# This is the path to the encrypted storage directory on the underlying 
# filesystem.
EFS_CONFIG_LOWER_PATH=${EFS_HOME}/${EFS_USER}/".secret"

# This is the path to the unencrypted mounted directory.
EFS_CONFIG_UPPER_PATH=${EFS_HOME}/${EFS_USER}/"secret"

EFS_KEY_WIDTH="30"
EFS_SESSION_KEY_BYTES="16"

###############################################################################
# Global Variables
###############################################################################

# Error codes
EFS_SUCCESS_KEY_CREATED=1
EFS_SUCCESS=0
EFS_ERROR=-1
EFS_RET=${EFS_SUCCESS}

###############################################################################
# FUNCTION: efs_init_pc
#  Initialise on PC for testing purposes.
#  Can be removed from final version
###############################################################################
function efs_init_pc()
{
    if [ ! -d "${EFS_CONFIG_DIR_PATH}" ]; then
        mkdir -p ${EFS_PREFIX}/"etc"
    fi
}

###############################################################################
# FUNCTION: efs_sys_init()
#  Perform the first boot system initialisation. In summary:
#  - Generate the key.
#  - Gnerate the passphrase for potecting the key
#  - Wrap the key with the passphrase
#  - Insert the wrapped key into the keyring and recover the key signature.
#  - Update /etc/fstab 
###############################################################################
function efs_sys_init()
{
    local ret=${EFS_ERROR}
    local efs_fekek=""
    local efs_fekek_passphrase=""
    local efs_config_fstab_entry=""
    local sig=""
    
    # If the directory exists then the one-time system initialisation has already
    # been performed, and should not be run again.
    if [ -d "${EFS_CONFIG_DIR_PATH}" ]; then
        # setup has been run previously on first time startup  
        return ${EFS_SUCCESS}
    else
        mkdir -p ${EFS_CONFIG_DIR_PATH}
        mkdir -p ${EFS_CONFIG_LOWER_PATH}
        mkdir -p ${EFS_CONFIG_UPPER_PATH}
    fi
    
    # This is the File Encryption Key Encryption Key. It is intended to be stored
    # on the file system protected by the passphrase.
    efs_fekek=$(od -x --read-bytes=100 --width=${EFS_KEY_WIDTH} ${EFS_RANDOM} | head -n 1 | sed "s/^0000000//" | sed "s/\\s*//g")

    # The passphrase protects the FEKEK. It should be stored securely (e.g. in 
    # secure on-chip flash for key storage). One option if the secure boot to 
    # install it in the key ring and supply its signature to this script.
    efs_fekek_passphrase=$(od -x --read-bytes=100 --width=${EFS_KEY_WIDTH} ${EFS_RANDOM} | head -n 1 | sed "s/^0000000//" | sed "s/\\s*//g")
    
    # store key and passphrase in files for use later
    echo "passphrase_passwd=${efs_fekek_passphrase}" > ${EFS_CONFIG_PASSPHRASE_FILE_PATH} 
    
    # store the passphrase in the configuration area.
    # Note, this shouldnt be done. the passphrase should be
    # inserted into the keyring by secure boot and the 
    # signature supplied by to this script for use.

    # create the wrapped-passphrase file.
    printf "%s\n%s" ${efs_fekek} ${efs_fekek_passphrase} | ${EFS_WRAP_PASSPH} ${EFS_CONFIG_KEY_FILENAME_PATH} -

    # Install the wrapped key in the keyring for use by ecryptfs
    # cat "<passphrase>" | ecryptfs-insert-wrapped-passphrase-into-keyring /home/root/.ecryptfs/wrapped-passphrase - 
    sig=$(echo ${efs_fekek_passphrase} | ${EFS_INSERT_PASSPH} ${EFS_CONFIG_KEY_FILENAME_PATH} -)
    
    # Extract the key signature from within "[]" (e.g. "<some text> [dd0a45455a291a98] <other text> ").
    sig=${sig/*"["/""}
    sig=${sig/"]"*/""}
    
    # TODO: Is it really necessary to store this? as its stored in the fstab
    # store the signature of use later by xyx: 
    # echo "${sig}" > ${EFS_CONFIG_KEY_SIG_FILE_PATH}
    
    if [ -f "${EFS_FSTAB_PATH}" ]; then
        # Update /etc/fstab so can do mount operation.
        # This involves inserting the key so that the signature can be recovered
        # and therefore used in the fstab entry line.

        rm -f ${EFS_CONFIG_FSTAB_PATH}
        cp -f ${EFS_FSTAB_PATH} ${EFS_CONFIG_FSTAB_PATH}  

        # See the ecryptfs.7 manpage for the description of the options used here.
        # The options permit non-interactive mounting  i.e. a user doesn't
        # have to respond to prompts. Note the ecryptfs_unlink_sigs option causes 
        # umount to remove the key from the keyring.
        efs_config_fstab_entry="${EFS_CONFIG_LOWER_PATH} ${EFS_CONFIG_UPPER_PATH} ecryptfs "
        efs_config_fstab_entry+="noauto,user,"
        efs_config_fstab_entry+="ecryptfs_sig=${sig},"
        efs_config_fstab_entry+="ecryptfs_fnek_sig=${sig},"
        efs_config_fstab_entry+="ecryptfs_cipher=aes,ecryptfs_key_bytes=${EFS_SESSION_KEY_BYTES},"
        efs_config_fstab_entry+="key=passphrase:passphrase_passwd_file=${EFS_CONFIG_PASSPHRASE_FILE_PATH},"
        efs_config_fstab_entry+="ecryptfs_passthrough=n,ecryptfs_unlink_sigs,no_sig_cache 0 0"
        echo ${efs_config_fstab_entry} >> ${EFS_FSTAB_PATH}
    fi
    
    # everything successfully initialised. Report 
    return ${EFS_SUCCESS_KEY_CREATED}
}


###############################################################################
# FUNCTION: efs_init()
#  This function performs the following system startup initialisation:
#  - start the message dispatcher. 
#  - install the FEKEK in the keyring.
#  - mount the cipher directory
###############################################################################
function efs_init()
{
    local ret=${ERS_ERROR} 
    local efs_fekek_passphrase=""
    
    efs_sys_init
    ret=$?
    if [ $ret -lt ${EFS_SUCCESS} ]; then
        return $ret
    elif [ $ret -eq ${EFS_SUCCESS} ]; then
        # Extract the passphrase from the passphrase file which has type=value
        # format.
        efs_fekek_passphrase=$(cat ${EFS_CONFIG_PASSPHRASE_FILE_PATH})
        efs_fekek_passphrase=${efs_fekek_passphrase/passphrase_passwd=/""}
        echo ${efs_fekek_passphrase} | ${EFS_INSERT_PASSPH} ${EFS_CONFIG_KEY_FILENAME_PATH} -
    fi
    
    # Mount the encrypted directory using configuration in /etc/fstab
    mount ${EFS_CONFIG_UPPER_PATH}
}


###############################################################################
# FUNCTION: efs_deinit()
#  This function performs the following system startup de-initialisation:
###############################################################################
efs_deinit()
{
    # un-mount the encrypted directory
    umount ${EFS_CONFIG_UPPER_PATH}
}

###############################################################################
# FUNCTION: efs_main()
#  
###############################################################################
efs_main()
{
    # TODO: delete efs_init_pc() for final version
    #efs_init_pc
    efs_init
}

# Start the script at the main() function
efs_main

