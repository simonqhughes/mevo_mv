/*
 * mbed config store API
 *
 * This is the interface to config store that clients use to access config
 * store services.
 *
 * Notes:
 * - this is intended to include a requirements capture document.
 * - this is intended to be include a high level design document.
 *
 * This is for information purposes only.
 *
 *
 * DEFINTIONS OF TERMS
 *
 * Access Control List (ACL)
 * A data descriptor defining which system defined groups (e.g. owner,
 * other) has read, write of executable access permissions for a data object.
 *
 * Access Control List Group 'owner'
 *
 *
 * CS = Config Store
 *
 * CS Key
 *  A null terminated string composed of [a-zA-Z0-9'-']* characters. The key
 *  is used to reference a CS stored binary blob.
 *
 * CS Object
 *  A CS stored {key, value} tuple is known as a CS object.
 *
 * CS Key Name Path Directory Entry (PDE)
 *  Path Directory Entry are the key name substrings separated by the '.'
 *  character. For example, in:
 * 	    'com.arm.mbed.wifi.accesspoint[5].essid'
 *  the PDE's are 'com', 'arm', 'mbed', 'wifi', 'accesspoint[5]' and 'essid'.
 *
 * CS Key Name Prefix (key_name_prefix)
 *  When a CS object is created with a security_prefix_name, then this
 *  ownership identifier becomes the first part of the key name, and is
 *  referred to as the key_name_prefix. For example, the key creation
 *  idion is illustrated in the following pseudo-code
 *
 *    owner = none               // CS context owner handle
 *    key_handle = none          // CS context key handle
 *    security_prefix_name = 'com.arm.med.tls'
 *    key_name = security_prefix_name + '.cert[5].key'
 *
 *    // bind the security_prefix_name to a CS context handle for performing CS
 *    // operations
 *    owner = cs_open(security_prefix_name)
 *
 *    // create the key
 *    status = cs_create_key(owner, key_name, O_CREATE, &key_handle)
 *
 *    // use key handle to perform operations
 *    ???
 *
 *    // close the CS context handle
 *    cs_close(owner)
 *
 * Security Context (uvisor box)
 *  The Security Context is a computational entity for providing OS code,
 *  OS data, App code, App data security services. It is identified by a
 *  registered name globally unique within the system, known as the
 *  Security Prefix Name.
 *
 * Security Prefix Name (security_prefix_name)
 *  A system unique character string composed of [a-zA-Z0-9.\-] characters
 *  which identifies the security context (box). Other system objects (e.g.
 *  CS keys) are 'owned' by tagging them with the security_prefex_name label.
 *  An example of a security_prefex_name may be 'com.arm.med.tls'.
 *
 *
 * REQUIREMENTS
 *
 * Secure Key Value Storage Rationale (REQ-1.xx-SKVS-R) Requirements
 *
 * REQ-1.01-SKVS-R:
 * The CS must provide a non-volatile, hardware-independent secure storage
 * service that can be used by CS API clients for storing data owned
 * by a client security context (uvisor box).
 *
 * REQ-1.02-SKVS-R:
 * Clients of the CS API must be security contexts (boxes) so that security
 * policies can be enforced.
 *
 * REQ-1.03-SKVS-R:
 * The CS design values simplicity over complexity to promote security by
 * minimizing the attack surface to secure data.
 *
 * REQ-1.04-SKVS-R:
 * The CS must be implemented as a uvisor secure box.
 *
 * REQ-1.05-SKVS-R:
 * The CS must support the use of Access Control Lists for policing access to
 * secure data.
 *
 * REQ-1.06-SKVS-R:
 * The CS must support the storage of a {key, value} tuples where
 * - the key is a zero terminated string of arbitrary length.
 * - the value is a binary blob of data of arbitrary length
 * The {key, value} tuple is a CS object.
 *
 * REQ-1.07-SKVS-R: CS Stores Binary Blobs
 * The CS must support services so that other components can implement
 * more complex storage types other than a binary blob e.g. by
 * wrapping the underlying CS {key, value} tuple object with addition
 * type information.
 *
 * REQ-1.08-SKVS-R: CS Key Structure as Name Strings
 * CS must support keys having the format of a null terminated string.
 *
 * REQ-1.09-SKVS-R: Key Creation and Ownership Part 1
 * CS keys must be owned by the security context . A security context (box)
 * is identified by a unique security_name_prefix and this identifier
 * must be used when the key is created. CS must support the use of the
 * security_name_prefix as the leading substring of the CS key string, in which
 * case the key_name_prefix is the security_name_prefix and identifies the
 * owner of the key.
 *
 * REQ-1.10-SKVS-R: Security Context
 * In order to create objects in the CS, a security context (box) must have
 * a security_name_prefix.
 *
 * REQ-1.11-SKVS-R: CS object
 * In order to create objects in the CS, a security context (box) must have
 * a security_name_prefix.
 *
 *
 * Secure Key Value Storage High Level Design (REQ-1.2.xx-SKVS-HLD) Reqs
 *
 * REQ-1.2.01-SKVS-HLD:
 * The CS must be able to detect the available types of storage media
 * available in the system and report associated storage media attributes.
 *
 * REQ-1.2.02-SKVS-HLD:
 * The CS may report the following storage media data retention level attribute,
 * when available:
 * - only during device activity
 * - during sleep
 * - during deep-sleep
 * - battery-backed, device can be powered off
 * - internal nonvolatile memory
 * - external nonvolatile memory
 *
 * REQ-1.2.03-SKVS-HLD:
 * For a particular storage medium, the CS may report the following device
 * data security protection features, when available:
 * - no security, just safety
 * - write-once-read-only-memory (WORM)
 * - against internal software attacks using ACLs
 * - roll-back protection
 * - immovable (for internal memory mapping, to stop relocated block to move).
 *   This attribute must only be set provided:
 *   -- the device memory is mapped into the CPU address space
 *   -- access is only granted to specific CS API system clients e.g. FOTA,
 *      DMA.
 * - hardening against device software (malware running on the device)
 * - hardening against board level attacks (debug probes, copy protection
 *   fuses)
 * - hardening against chip level attacks (tamper-protection)
 * - hardening against side channel attacks
 * - tamper-proof memory (will be deleted on tamper-attempts using board level
 *   or chip level sensors)
 *
 *  REQ-1.2.04-SKVS-HLD:
 *  The CS may be used to implement object storage protection services
 *  (e.g. flash image roll-back protection, confidentiality) for off-chip
 *  (external) storage media (e.g. SPI/I2C/NAND Flash).
 *
 *  REQ-1.2.05-SKVS-HLD:
 *  The device data security protection immovable attribute may only be set
 *
 *
 * Secure Key Value Storage\High Level API Description\Key Value Storage
 * (REQ-3.1.xx-SKVS-HLAPID-KVS) Requirements.
 *
 * REQ-3.1.01-SKVS-HLAPID-KVS: CS Global Key Namespace
 * The CS must implement a system global hierarchical tree name-space for
 * keys. The namespace is shared by all software components operating within
 * the system. Examples of key names include the following:
 *  - 'com.arm.mbed.wifi.accesspoint[5].essid'
 *  - 'com.arm.mbed.wifi.accesspoint[home].essid'
 *	- 'yotta.your-yotta-registry-module-name.your-value'
 *	- 'yotta.hello-world.animal[dog][foot][3]'
 *	The key name string forms a path where 'Path Directory Entries' are
 *	separated by the '.' character.
 *
 * REQ-3.1.02-SKVS-HLAPID-KVS: CS Key Name String Format Max Length
 * For CS keys The maximum length of a CS key is 221 characters including
 * the terminating null.
 *
 * REQ-3.1.03-SKVS-HLAPID-KVS: CS Key Name String Allowed Characters
 * CS key name strings must only contain the following characters:
 * - [a-zA-Z0-9.]
 * - '-'
 *
 * REQ-3.1.04-SKVS-HLAPID-KVS: Key Name Path Directory Entry List []
 * Path Directory Entries may have list indicators designated by []. For
 * example,
 *  - 'com.arm.mbed.wifi.accesspoint[5].essid'
 *  - 'com.arm.mbed.wifi.accesspoint[home].essid'
 *	- 'yotta.hello-world.animal[dog][foot][3]'
 * In the above the list item specifiers are respectively:
 *  - '5'
 *  - 'home'
 *	- 'dog', 'foot, '3'
 * As list item specifiers are part of the key name string, the list item
 * substring must be composed of allowable characters.
 *
 * REQ-3.1.05-SKVS-HLAPID-KVS: CS Global Key Yotta Namespace
 * The key name prefix 'yotta' is reserved for use by the yotta module. Other
 * prefixes may be reserved.
 *
 *
 * Secure Key Value Storage\High Level API Description\Access Control Security
 * (REQ-3.2.xx-SKVS-HLAPID-ACS) Requirements.
 *
 * REQ-3.2.01-SKVS-HLAPID-KACS:
 * The CS must enforce security policies as defined by Access Control Lists.
 *
 * REQ-3.2.02-SKVS-HLAPID-KACS: CS Key Creation Part 2
 * The CS objects must be created with an ACL. The ACL is attached to the object
 * so that access permissions to the object can be enforced.
 *
 * REQ-3.2.03-SKVS-HLAPID-KACS:
 * The CS Access Control Lists must support the groups for 'owner' and 'other',
 * with optional permissions read, write and executable. The owner group
 * permissions describe the access permissions of the owner of the object. The
 * other group permissions describe the access permissions for entities other
 * than the owner. The writable and executable permissions are mutually
 * exclusive.
 *
 * REQ-3.2.04-SKVS-HLAPID-KACS:
 * A CS API client must be able to query the CS for a list of objects provided
 * the object ACL permissions allow the client access. The query result must
 * contain all client owner object. The query results may include non-client
 * owned objects provided the other group permissions grant access.
 *
 *
 * Secure Key Value Storage\API Logic (REQ-5.1.xx-SKVS-APIL) Requirements.
 *
 */


typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef uint32_t* cs_handle;


/* other bits in 32bit word reserved for future use */
#define CS_ACL_PERM_OWNER_READ         (1<<0)
#define CS_ACL_PERM_OWNER_WRITE        (1<<1)
#define CS_ACL_PERM_OWNER_EXE          (1<<2)
#define CS_ACL_PERM_OTHER_READ         (1<<3)
#define CS_ACL_PERM_OTHER_WRITE        (1<<4)
#define CS_ACL_PERM_OTHER_EXE          (1<<5)

typedef struct cs_access_control_list_t
{
    unit32_t acl;
} cs_access_control_list_t;


/* supported volatility values of different storage mediums */
typedef enum cs_data_retention_level_e
{
    drl_volatile,
    drl_volatile_sleep,
    drl_volatile_deep_sleep,
    drl_non_volatile_battery_backed,
    drl_non_volatile_internal,
    drl_non_volatile_external,
    drl_max
} cs_data_retention_level_e;


/* other bits in 32bit word reserved for future use */
#define CS_MODE_CREATE            (1<<0)
#define CS_MODE_CONTINUOUS        (1<<1)
#define CS_MODE_LAZY_FLUSH        (1<<2)
#define CS_MODE_BLOCK_WRITE       (1<<3)
#define CS_ALLOC_AT_OFFSET        (1<<4)


typedef struct cs_key_mode_t
{
    uint32_t mode;
} cs_key_mode_t;


/*bitfield with the following setable attributes */
#define CS_DDSP_NONE                                (1<<0)
#define CS_DDSP_WRITE_ONCE_READ_ONLY_MEMORY         (1<<1)
#define CS_DDSP_ACCESS_CONTROL_LIST                 (1<<2)
#define CS_DDSP_ROLL_BACK_PROTECTION                (1<<3)
#define CS_DDSP_IMMOVABLE                           (1<<4)
#define CS_DDSP_HARDENED_MALWARE                    (1<<5)
#define CS_DDSP_HARDENED_BOARD_LEVEL                (1<<6)
#define CS_DDSP_HARDENED_CHIP_LEVEL                 (1<<7)
#define CS_DDSP_HARDENED_SIDE_CHANNEL               (1<<8)
#define CS_DDSP_TAMPER_PROOF                        (1<<9)

typedef struct cs_device_data_security_protection_t
{
    uint32_t ddsp;
} cs_device_data_security_protection_t;



/*****************************************************************************
 * STRUCTURE: cs_key_desc_t
 *  descriptor used to create/update keys
 *
 *
 *****************************************************************************/
typedef struct cs_key_desc_t
{
	/*key descriptor attributes */
	cs_access_control_list_t acl;
	cs_data_retention_level_e drl;
	cs_device_data_security_protection_t ddsp;
	uint32_t offset_address; 						/*? todo: define exact purpose */
	uint32_t properties; 							/* include alignment bits in lower 5 bits and reserve other for future use */
	cs_key_mode_t mode;
} cs_key_desc_t;


/*****************************************************************************
 * FUNCTION: cs_open
 *  A CS client uses this function to get a CS context for performing
 *  operations with the CS API
 *****************************************************************************
 * ARGUMENTS:
 *  security_name_prefix
 *   uvisor registered security name prefix.
 *****************************************************************************
 * RETURN:
 *  SUCCESS: A non-null cs_handle for performing operations with CS. This is
 *  known as the owner handle.
 *  FAILURE: A NULL handle.
 ****************************************************************************/
cs_handle cs_open(uint8_t* security_name_prefix);

/*****************************************************************************
 * FUNCTION: cs_close
 *  A CS client uses this function to close a CS context previously returned
 *  from cs_open()
 *****************************************************************************
 * ARGUMENTS:
 *  the owner handle previously returned form the cs_open() call.
 *   uvisor registered security name prefix.
 *****************************************************************************
 * RETURN:
 *  None
 ****************************************************************************/
void cs_close(cs_handle owner);


/*****************************************************************************
 * FUNCTION: cs_obj_create
 *  open a {key, value} object for future operations.
 *  - if the kdesc->mode |= CS_MODE_CREATE, then the object will be created
 *    if it does not already exist. A handle will be returned to the newly
 *    created object.
 *  - if kdesc->mode &= ~CS_MODE_CREATE and an object exists in with the
 *    key_name then a handle will be returned to the object. There must be a
 *    unique match of the key_name
 *
 *****************************************************************************
 * ARGUMENTS:
 *  IN key_name
 *   zero terminated string specifying the key name.
 *  IN value
 *   the binary blob value data to be created, or NULL when opening a
 *   pre-existing object specified by key_name
 *  IN value_len
 *   length of the binary blob
 *  IN kdesc
 *   key descriptor, specifying how the details of the key create operations
 *
 *****************************************************************************
 * RETURN:
 *  NULL upon failure
 *  Non-NULL object handle on success.
 ****************************************************************************/
cs_handle cs_obj_open(cs_handle owner, uint8_t* key_name, uint8_t* value, uint32_t value_len, cs_key_desc_t* kdesc);

/*****************************************************************************
 * FUNCTION: cs_obj_close
 *  Close the key_handle context previously recovered from CS
 *****************************************************************************
 * ARGUMENTS:
 *  IN key_handle
 *   a previously returned handle from cs_obj_open()
 *****************************************************************************
 * RETURN: None
 ****************************************************************************/
void cs_obj_close(cs_handle key_handle);



/* DEFINTIONS
 *
 * SECURITY PREFIX NAME
 * todo: define what it is...
 *
 * */


/*
 */


/* Questions to resolve wrt sdh_20160106_1
 *
 * (1) todo:
 * - What distrusts what?
 * - Alternatively, what trust what?
 * - How is a secure box created and how to do you refer to it? the api?
 *
 * (2): todo:
 * - what does the software stack look like?
 * - is the pic on P4 of notes approximately correct?
 *
 * (3): todo:
 * - Check this: the CS supports...
 *
 * (4)
 *  >>
 *  The ownership of a key is tied to its name. A mandatory key name
 *  prefix is listed in each box security context in case the context is
 *  allowed to create values. For key creation the security prefix name
 *  is enforced for created values.
 *  <<
 *
 *  - what is the security prefix name
 */
