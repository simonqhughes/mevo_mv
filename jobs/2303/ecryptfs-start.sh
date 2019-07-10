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
EFS_PREFIX="./"
EFS_FSTAB_PATH=${EFS_PREFIX}"/etc/fstab"
# todo: set EFS_HOME to empty
EFS_HOME=${EFS_PREFIX}"/home"
EFS_RANDOM="/dev/random"
# TODO: remove next line
EFS_RANDOM="/dev/urandom"
EFS_USER="root"

# Directory to store configuration artifacts
EFS_CONFIG_DIR=".ecryptfs"
EFS_CONFIG_DIR_PATH=${EFS_HOME}/${EFS_USER}/${EFS_CONFIG_DIR}
EFS_CONFIG_KEY_FILENAME_PATH=${EFS_CONFIG_DIR_PATH}/"wrapped-passphrase.bin"
EFS_CONFIG_KEY_SIG_FILE_PATH=${EFS_CONFIG_DIR_PATH}/"key_sig.txt"
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


###############################################################################
# FUNCTION: efs_init_pc
#  Initialise on PC for testing purposes.
#  Can be removed from final version
###############################################################################
efs_init_pc()
{
    mkdir -p ${EFS_PREFIX}/"etc"  
}

###############################################################################
# FUNCTION: efs_generate_keys()
#  Generate keys used for x and y.
###############################################################################
efs_generate_keys()
{
    local ret=0
    local efs_fekek=""
    local efs_fekek_passphrase=""
    local efs_config_fstab_entry=""
    local sig=""
    
    # If the directory exists then this has been run before and should not be
    # run again.
    if [ -d "${EFS_CONFIG_DIR_PATH}" ]; then
        # setup has been run previously on first time startup  
        return $ret
    fi
    
    mkdir -p ${EFS_CONFIG_DIR_PATH}

    # This is the File Encryption Key Encryption Key. It is intended to be stored
    # on the file system protected by the passphrase.
    efs_fekek=$(od -x --read-bytes=100 --width=${EFS_KEY_WIDTH} ${EFS_RANDOM} | head -n 1 | sed "s/^0000000//" | sed "s/\\s*//g")

    # The passphrase protects the FEKEK. It should be stored securely (e.g. in 
    # secure on-chip flash for key storage). One option if the secure boot to 
    # install it in the key ring and supply its signature to this script.
    efs_fekek_passphrase=$(od -x --read-bytes=100 --width=${EFS_KEY_WIDTH} ${EFS_RANDOM} | head -n 1 | sed "s/^0000000//" | sed "s/\\s*//g")
    
    # store key and passphrase in files for use later
    echo ${efs_fekek_passphrase} > ${EFS_CONFIG_PASSPHRASE_FILE_PATH} 
    
    # store the passphrase in the configuration area.
    # Note, this shouldnt be done. the passphrase should be
    # inserted into the keyring by secure boot and the 
    # signature supplied by to this script for use.

    # create the wrapped-passphrase file.
    printf "%s\n%s" ${efs_fekek} ${efs_fekek_passphrase} | ${EFS_WRAP_PASSPH} ${EFS_CONFIG_KEY_FILENAME_PATH} -

    # install the wrapped key in the keyring
    # cat /home/root/passphrase.txt | ecryptfs-insert-wrapped-passphrase-into-keyring /home/root/.ecryptfs/wrapped-passphrase - 
    sig=$(cat ${EFS_CONFIG_PASSPHRASE_FILE_PATH} | ${EFS_INSERT_PASSPH} ${EFS_CONFIG_KEY_FILENAME_PATH} -)
    
    # Extract the key signature from within square branckets (e.g. "<some text> [dd0a45455a291a98] <other text> ").
    sig=${sig/*"["/""}
    sig=${sig/"]"*/""}
    
    # check that everything is as expected by removing the key from the keyring
    key_id=$(keyctl search @u user $sig)
    keyctl revoke ${key_id}
    keyctl reap 
    
    # TODO: Is it really necessary to store this? as its stored in the fstab
    # store the signature of use later by xyx: TODO: say what its used for.
    echo ${sig} > ${EFS_CONFIG_KEY_SIG_FILE_PATH}

    # update /etc/fstab so can do mount operation
    # this involves inserting the key so that the signature can be recovered
    # and therefore used in the fstab entry line.
    efs_config_fstab_entry="${EFS_CONFIG_LOWER_PATH} ${EFS_CONFIG_UPPER_PATH} ecryptfs "
    efs_config_fstab_entry+="noauto,user,"
    efs_config_fstab_entry+="ecryptfs_sig=${sig},"
    efs_config_fstab_entry+="ecryptfs_fnek_sig=${sig},"
    efs_config_fstab_entry+="ecryptfs_cipher=aes,ecryptfs_key_bytes=${EFS_SESSION_KEY_BYTES},"
    efs_config_fstab_entry+="key=passphrase:passphrase_passwd_file=${EFS_CONFIG_PASSPHRASE_FILE_PATH},"
    efs_config_fstab_entry+="ecryptfs_passthrough=n,ecryptfs_unlink_sigs 0 0"
    
    # TODO: check if rm -f works even when no file present
    rm -f ${EFS_FSTAB_PATH}".old"
    if [ -f "${EFS_FSTAB_PATH}" ]; then
        cp -f ${EFS_FSTAB_PATH} ${EFS_FSTAB_PATH}".old"  
    fi
    echo ${efs_config_fstab_entry} >> ${EFS_FSTAB_PATH}
    
    return $ret
}

# FUNCTION: efs_setup()
#  setup ecryptfs config the first time the system boots
#
efs_setup_config()
{
    
    # check whether the configuration exists.
    # If yes, return. otherwise configure the system
    
    # make the .ecryptfs dir to hold the files, the ciphered dir, the decyphered dir (can these be refered to as upper and lower?)
    
    # create secret.conf? may not be necessary
    
    # store secret.sig? have to extract this
    
    # generate key and passphrase
    
    # store passphrase for use in fstab entry
    
    return 0    
}

###############################################################################
# FUNCTION: efs_init()
#  This function performs the following system startup initialisation:
#  - start the message dispatcher. 
#  - install the FEKEK in the keyring.
#  - mount the cipher directory
###############################################################################
efs_init()
{
    # start the ecryptfs message dispatcher
    /usr/bin/ecryptfsd -f

    # install the wrapped key in the keyring
    # cat /home/root/passphrase.txt | ecryptfs-insert-wrapped-passphrase-into-keyring /home/root/.ecryptfs/wrapped-passphrase - 
    sig=$(cat ${EFS_CONFIG_PASSPHRASE_FILE_PATH} | ${EFS_INSERT_PASSPH} ${EFS_CONFIG_KEY_FILENAME_PATH} -)
    
    # todo: check its the same signature as the one in EFS_CONFIG_KEY_SIG_FILE_PATH 
    
    # Mount the encrypted directory using configuration in /etc/fstab
    mount ${EFS_CONFIG_UPPER_PATH}
}


###############################################################################
# FUNCTION: efs_deinit()
#  This function performs the following system startup de-initialisation:
###############################################################################
efs_deinit()
{
    # Mount the encrypted directory using configuration in /etc/fstab
    umount ${EFS_CONFIG_UPPER_PATH}

    # start the ecryptfs message dispatcher
    # todo: kill `pidof ecryptfsd`
}


test()
{
    search="["
    string="Inserted auth tok with sig [dd0a45455a291a98] into the user session keyring"
    x=${string##*$search}
    echo "x=$x"

    #pattern="[A-z0-9 ]*[a-f0-9]"
    pattern="["
    x=${string/*$pattern/""}
    echo "x=$x"

    pattern="]"
    y=${x/$pattern*/""}
    echo "y=$y"
    
    x=${string/*"["/""}
    x=${x/"]"*/""}
    echo "x=$x"
    
}

efs_init_pc
efs_generate_keys

