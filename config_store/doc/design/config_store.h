/*
 * mbed config store API
 * v0.03
 * 20160125
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
 *      'com.arm.mbed.wifi.accesspoint[5].essid'
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
 *    owner = cfstore_open_ctx(security_prefix_name)
 *
 *    // create the key
 *    status = cfstore_create_key(owner, key_name, O_CREATE, &key_handle)
 *
 *    // use key handle to perform operations
 *    ???
 *
 *    // close the CS context handle
 *    cfstore_close_ctx(owner)
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
 * REQ-1.2.04-SKVS-HLD:
 * The CS may be used to implement object storage protection services
 * (e.g. flash image roll-back protection, confidentiality) for off-chip
 * (external) storage media (e.g. SPI/I2C/NAND Flash).
 *
 * REQ-1.2.05-SKVS-HLD:
 * The device data security protection immovable attribute may only be set
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
 *  - 'yotta.your-yotta-registry-module-name.your-value'
 *  - 'yotta.hello-world.animal[dog][foot][3]'
 *  The key name string forms a path where 'Path Directory Entries' are
 *  separated by the '.' character.
 *
 * REQ-3.1.02-SKVS-HLAPID-KVS: CS Key Name String Format Max Length
 * For CS keys The maximum length of a CS key is 220 characters excluding
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
 *  - 'yotta.hello-world.animal[dog][foot][3]'
 * In the above the list item specifiers are respectively:
 *  - '5'
 *  - 'home'
 *  - 'dog', 'foot, '3'
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
 * Secure Key Value Storage\API Logic\Finding Keys
 * (REQ-5.1.xx-SKVS-APIL-FK) Requirements.
 *
 * REQ-5.1.01-SKVS-APIL-FK: Key Searching/Finding Scoped by ACL
 * The CS must provide an interface to query for active keys in the global
 * storage. The query must:
 * - return results based on the ACL provided by the client
 * - support wild card searches using the '*' character. The '*' character
 *   can occur at most once any point in the search string. For example:
 *   -- 'com.arm.mbed.wifi.accesspoint*.essid'
 *   -- 'yotta.your-yotta-registry-module-name.*'
 *   -- 'yotta.hello-world.animal[dog][foot][*]'
 *   -- 'yotta.hello-world.animal[dog][foot]*'
 *   -- 'yotta.hello-world.animal[dog*3]'
 *
 * REQ-5.1.02-SKVS-APIL-FK: CS Global Key Namespace Reserves Character '*'
 * The character '*' is reserved in the CS global key namespace. The current
 * functions of this character as as follows:
 * - a wild card character in searches.
 * - a wild card character used in object delete operation.
 *
 *
 * REQ-5.1.03-SKVS-APIL-FK: Key Searching/Finding Resume
 * In order to support the return of a large list of key query results (perhaps
 * exceeding the ability of the caller to consume in a single operation), the
 * query interface must support the ability to restart/resume the query to
 * retrieve a subsequent set of records to those already received.
 *
 * REQ-5.1.04-SKVS-APIL-FK: Key Searching/Finding Internals (key versions)
 * (todo: resolve problems as this mixed a requirement)
 * Internally, CS stores objects with a version number.
 * - todo: define what is the role of this version number?
 * - todo: define what is the role of this version number in querying for
 *   keys?
 *
 * Secure Key Value Storage\API Logic\Get Storage Information
 * (REQ-5.2.xx-SKVS-APIL-GSI) Requirements.
 *
 * REQ-5.2.01-SKVS-APIL-GSI: storage_detect
 * The CS must provide an API so that clients can discover the CS storage
 * capabilities. Storage capabilities may include:
 * - write-block sizes for O_BLOCK_WRITE mode (sequence of writes into the
 *   same value)
 * - supported Data Retention Levels
 * - supported Device Data Security Protection Features
 *
 * REQ-5.2.02-SKVS-APIL-GSI: Minimal Storage Support
 * The CS must provide minimal storage media services including the following:
 * - SRAM/SDRAM memory with no security guarantees.
 *
 *
 * Secure Key Value Storage\API Logic\Creating & Opening Keys for Writing
 * (REQ-5.3.xx-SKVS-APIL-COKFW) Requirements.
 *
 * REQ-5.3.01-SKVS-APIL-COKFW: storage_key_create with O_CREATE
 * CS keys must be explicitly created using 'storage_key_create' with the following
 * parameters:
 * - security ACLs (owner & others)
 * - the intended retention levels (bit mask to allow caching if needed)
 * - indicating the expected Device Data Security Protection Features
 * - the key pointer (zero-terminated)
 * - the value size
 * - optionally the offset address (restricted feature, ideally only granted
 *   to the FOTA security context) (todo: how does the offset-address work?)
 * - alignment bits of the value hardware address (only for O_CONTINUOUS).
 *   The structure start is aligned accordingly to ensure that the value
 *   blob is aligned on a multiple of the 2alignment_bits
 * - mode flags (O_CREATE, O_CONTINUOUS, O_LAZY_FLUSH, O_BLOCK_WRITE,
 *   O_ALLOCATE_AT_OFFEST).
 *   -- O_CREATE. The call will create the {key,value} object. If a
 *      pre-existing object with the same name is present in CS then the
 *      storage_key_create will fail with FILE_EXISTS.
 *   -- O_CONTINUOUS. The object value will be stored in a continuous range
 *      of hardware addresses.
 *   -- O_LAZY_FLUSH ? (todo: define)
 *   -- O_BLOCK_WRITE ? (todo: define)
 *   -- O_ALLOCATE_AT_OFFEST ? (todo: define)
 *
 * REQ-5.3.02-SKVS-APIL-COKFW: storage_key_create without O_CREATE
 * Pre-existing CS objects can be updated by calling the storage_key_create
 * API with the O_CREATE not set.
 * (todo: understand this requirement more fully:)
 * In case a pre-existing key is updated (O_CREATE not set) and the previous
 * ACL allows writing to the caller:
 * (todo: which previous ACL?)
 * - all key-value fragments of the previous key are set as inactive
 *   (todo: delete? fragmentation are not exposed to the API client)
 * - the new key is allocated (in fragments if permitted)
 *   (todo: are we internally creating a new copy of the key?)
 * - all permissions and settings are copied from the previous key
 * - the version number is incremented compared to the previous key
 *   (todo: delete? updating of version numbers is an CS internal
 *   implementation detail)
 *
 * REQ-5.3.03-SKVS-APIL-COKFW: O_CONTINUOUS for executable objects
 * CS will manage an executable object as though the mode O_CONTINUOUS flag
 * is set.
 *
 * REQ-5.3.04-SKVS-APIL-COKFW: O_CONTINUOUS for non-executable objects
 * A CS client may specify the mode O_CONTINUOUS flag for non-executable
 * objects.
 *
 *
 * Secure Key Value Storage\Updating and Settings and Permissions
 * (REQ-6.1.xx-SKVS-USP) Requirements.
 *
 * REQ-6.1.01-SKVS-USP:
 * CS does not permit the updating of object {key, value} permissions
 * or settings. This is to promote security.
 *
 *
 * Secure Key Value Storage\Updating and Settings and Permissions\
 * Deleting Keys (REQ-6.2.xx-SKVS-USP-DK) Requirements.
 *
 * REQ-6.2.01-SKVS-USP-DK:
 * Only the owner of the CS object can delete the object. The wildcard
 * '*' character can be specified to delete an owned subtree of the CS
 * global key namespace.
 *
 * REQ-6.2.02-SKVS-USP-DK:
 * To change the value of a CS object, the owner must:
 * - delete the object
 * - create the object with the new attributes.
 *
 *
 * Secure Key Value Storage\Updating and Settings and Permissions\
 * Opening Keys for Reading (REQ-6.2.xx-SKVS-USP-OKFR) Requirements.
 *
 * REQ-6.3.xx-SKVS-USP-OKFR storage_key_open_read
 * CS objects must be explicitly opened storage_key_open_read(key_name)
 * before operations on the object can be performed. The object must
 * pre-exist in the store before it can be opened.
 *
 *
 * Secure Key Value Storage\Updating and Settings and Permissions\
 * Seeking in Key Values (REQ-6.3.xx-SKVS-USP-SIKV) Requirements.
 *
 * REQ-6.4.01-SKVS-USP-SIKV storage_value_rseek
 * The function storage_value_rseek can be used on a file handle
 * to change the read position inside a value. Changing the write
 * position is intentionally not supported
 *
 * REQ-6.4.02-SKVS-USP-SIKV
 * CS does not support the changing of the write position of an object
 * value attribute.
 *
 *
 * Secure Key Value Storage\Updating and Settings and Permissions\
 * Writing Keys (REQ-6.4.xx-SKVS-USP-WK) Requirements.
 *
 * REQ-6.5.01-SKVS-USP-WK
 * CS object values can be written in one or more operation.
 * todo: are there any requirements arising from these statements?
 * They appear to refer to CS internal implementation details.
 * - The CRC block including the activation is set after the last value
 *   byte is written to finalize the key.
 * - The write position is kept in SRAM only and is lost on reboots
 * - non-finalized values can be finalized on reboot.
 * - Each value-fragment is independently finalised.
 *
 * REQ-6.5.01-SKVS-USP-WK
 * CS object write interface has the following semantics:
 * - Writing to a non-finalised object is only allowed to the owner.
 * - Closing of a written object results in the finalisation of the object.
 * - Non-finalised object can't be read.
 *
 *
 * Secure Key Value Storage\Updating and Settings and Permissions\
 * Executable Keys and Firmware Updates (REQ-6.6.xx-SKVS-USP-EKFU)
 * Requirements.
 *
 * REQ-6.6.xx-SKVS-USP-EKFU
 *
 *
 *
 *

/*  Config-Store Client API Usage Call Flow Web Sequence Diagram data
 *
 * The following can be pasted into Web Sequence Diagram tool here:
 *   https://www.websequencediagrams.com/
 * This will generate a picture of the typicall call flow between a Config-Store
 * Client and the Config-Store API.


--- CUT_HERE-----------------------------------------------------------------------
title Config-Store Client API Usage Call Flow

cfstore_Client->Config-Store: cfstore_open_ctx(security_key_prefix)
Config-Store->cfstore_Client: returns hOwner

note left of cfstore_Client: Client find
cfstore_Client->Config-Store: cfstore_handle cfstore_find(cfstore_handle owner, const char* key_name_query, cfstore_handle previous=NULL)
Config-Store->cfstore_Client: returns key_handle to matching key_name

note left of cfstore_Client: Client uses key_handle as prev argument
cfstore_Client->Config-Store: cfstore_handle cfstore_find(cfstore_handle owner, const char* key_name_query, cfstore_handle previous=key_handle)
Config-Store->cfstore_Client: returns key handle to matching key_name

note over cfstore_Client,Config-Store: client iterates to get complete find list

note left of cfstore_Client: cfstore_Client create new object
cfstore_Client->Config-Store: cfstore_open(hOwner, key_name, valueL, kdesc with O_CREATE)
Config-Store->cfstore_Client: returns hObj

note left of cfstore_Client: cfstore_Client performs operations if required

note left of cfstore_Client: cfstore_Client close new object hObj
cfstore_Client->Config-Store: cfstore_close(hObj)
Config-Store->cfstore_Client: OK


note left of cfstore_Client: cfstore_Client opens pre-existing object
cfstore_Client->Config-Store: cfstore_open(hOwner, key_name, NULL, NULL)
Config-Store->cfstore_Client: returns hObj

note left of cfstore_Client: cfstore_Client seeks in pre-existing object
cfstore_Client->Config-Store: cfstore_rseek(hObj, ... )
Config-Store->cfstore_Client: returns data

note left of cfstore_Client: cfstore_Client reads pre-existing object
cfstore_Client->Config-Store: cfstore_read(hObj, ... )
Config-Store->cfstore_Client: returns data

note left of cfstore_Client: cfstore_Client closes pre-existing object
cfstore_Client->Config-Store: cfstore_close(hObj)
Config-Store->cfstore_Client: OK


note left of cfstore_Client: cfstore_Client closes security context with Config-Store
cfstore_Client->Config-Store: cfstore_close_ctx(hOwner)
Config-Store->cfstore_Client: OK
--- CUT_HERE-----------------------------------------------------------------------

 */


typedef int int32_t;
typedef unsigned int uint32_t;
typedef uint32_t* cfstore_handle;

/* Defines
 *
 * CFSTORE_KEY_NAME_MAX_LENTH
 *   The maximum length of the null terminated character string used as a
 *   key name string.
 *
 */
#define CFSTORE_KEY_NAME_MAX_LENTH      220


/* other bits in 32bit word reserved for future use */
#define CFSTORE_ACL_PERM_OWNER_READ         (1<<0)
#define CFSTORE_ACL_PERM_OWNER_WRITE        (1<<1)
#define CFSTORE_ACL_PERM_OWNER_EXE          (1<<2)
#define CFSTORE_ACL_PERM_OTHER_READ         (1<<3)
#define CFSTORE_ACL_PERM_OTHER_WRITE        (1<<4)
#define CFSTORE_ACL_PERM_OTHER_EXE          (1<<5)

typedef struct cfstore_access_control_list_t
{
    unit32_t acl;
} cfstore_access_control_list_t;


/* supported volatility values of different storage mediums */
typedef enum cfstore_data_retention_level_e
{
    drl_volatile,
    drl_volatile_sleep,
    drl_volatile_deep_sleep,
    drl_non_volatile_battery_backed,
    drl_non_volatile_internal,
    drl_non_volatile_external,
    drl_max
} cfstore_data_retention_level_e;


/* other bits in 32bit word reserved for future use */
#define CFSTORE_MODE_CREATE            (1<<0)
#define CFSTORE_MODE_CONTINUOUS        (1<<1)
#define CFSTORE_MODE_LAZY_FLUSH        (1<<2)
#define CFSTORE_MODE_BLOCK_WRITE       (1<<3)
#define CFSTORE_MODE_ALLOC_AT_OFFSET        (1<<4)


typedef struct cfstore_key_mode_t
{
    uint32_t mode;
} cfstore_key_mode_t;


/*bitfield with the following attributes */
#define CFSTORE_DDSP_NONE                                (1<<0)
#define CFSTORE_DDSP_WRITE_ONCE_READ_ONLY_MEMORY         (1<<1)
#define CFSTORE_DDSP_ACCESS_CONTROL_LIST                 (1<<2)
#define CFSTORE_DDSP_ROLL_BACK_PROTECTION                (1<<3)
#define CFSTORE_DDSP_IMMOVABLE                           (1<<4)
#define CFSTORE_DDSP_HARDENED_MALWARE                    (1<<5)
#define CFSTORE_DDSP_HARDENED_BOARD_LEVEL                (1<<6)
#define CFSTORE_DDSP_HARDENED_CHIP_LEVEL                 (1<<7)
#define CFSTORE_DDSP_HARDENED_SIDE_CHANNEL               (1<<8)
#define CFSTORE_DDSP_TAMPER_PROOF                        (1<<9)

typedef struct cfstore_device_data_security_protection_t
{
    uint32_t ddsp;
} cfstore_device_data_security_protection_t;


/*****************************************************************************
 * STRUCTURE: cfstore_key_desc_t
 *  descriptor used to create keys
 *****************************************************************************/
typedef struct cfstore_key_desc_t
{
    /*key descriptor attributes */
    cfstore_access_control_list_t acl;
    cfstore_data_retention_level_e drl;
    cfstore_device_data_security_protection_t ddsp;
    uint32_t offset_address;                        /*? todo: define exact purpose */
    uint32_t properties;                            /* include alignment bits in lower 5 bits and reserve other for future use */
    cfstore_key_mode_t mode;
} cfstore_key_desc_t;


/*****************************************************************************
 * STRUCTURE: cfstore_storage_desc_t
 *  descriptor used to report the details of a specific storage media
 *
 * ATTRIBUTES:
 * id
 *   a unique identifier associated with a specific instance of a detect
 *   storage media type
 * drl
 *   data retention level for this storage media device/service
 * ddsp
 *   device data security protection for this particular storage media device/
 *   service.
 *
 *****************************************************************************/
typedef struct cfstore_storage_desc_t
{
    uint32_t id;
    cfstore_data_retention_level_e drl;
    cfstore_device_data_security_protection_t ddsp;
} cfstore_storage_desc_t;

/*****************************************************************************
 * FUNCTION: cfstore_open_ctx
 *  A CS client uses this function to get a CS context for performing
 *  operations with the CS API
 *****************************************************************************
 * ARGUMENTS:
 *  security_name_prefix
 *   uvisor registered security name prefix.
 *****************************************************************************
 * RETURN:
 *  SUCCESS: A non-null cfstore_handle for performing operations with CS. This is
 *  known as the owner handle.
 *  FAILURE: A NULL handle.
 ****************************************************************************/
cfstore_handle cfstore_open_ctx(const char* security_name_prefix);

/*****************************************************************************
 * FUNCTION: cfstore_close_ctx
 *  A CS client uses this function to close a CS context previously returned
 *  from cfstore_open_ctx()
 *****************************************************************************
 * ARGUMENTS:
 *  IN owner
 *  the owner handle previously returned form the cfstore_open_ctx() call.
 *  uvisor registered security name prefix.
 *****************************************************************************
 * RETURN:
 *  None
 ****************************************************************************/
void cfstore_close_ctx(cfstore_handle owner);

/*****************************************************************************
 * FUNCTION: cfstore_storage_detect
 *  This function reports the information on the underlying storage media
 *****************************************************************************
 * ARGUMENTS:
 *  IN owner
 *    handle to owner context (todo: may be NULL? always null and therefore
 *    this arg can be removed?)
 *  IN OUT sdesc
 *    on input, a pointer to a storage descriptor is supplied to take the
 *    data reported by CS.
 *    on output, if the call is successfully the sdesc will contain data for
 *    a detect storage medium/service.
 *  IN prev
 *    on the first call to this function prev is null.
 *    on the second and subsequent calls to this function, a previously
 *    supplied sdesc pointer can be supplied, and the
 *****************************************************************************
 * RETURN:
 *  SUCCESS 0, when the last storage media/service descriptor is returned
 *  ERROR < 0, an internal error occurred
 *  MORE = 1,  the returned data as sdesc is valid, and more descriptors are
 *             available.
 ****************************************************************************/
int32_t cfstore_storage_detect(cfstore_handle owner, cfstore_storage_desc_t* sdesc, cfstore_storage_desc_t* prev);

/*****************************************************************************
 * FUNCTION: cfstore_find
 *  find a list of pre-existing keys according to a particular pattern. The
 *  search pattern can have the following formats
 *  - 'com.arm.mbed.wifi.accesspoint.essid'. Find whether an object exists
 *    that has a key matching 'com.arm.mbed.wifi.accesspoint.essid'
 *  - 'com.arm.mbed.wifi.accesspoint*.essid'. Find all keys that start with
 *    the substring 'com.arm.mbed.wifi.accesspoint' and end with the substring
 *    '.essid'
 *  - 'yotta.your-yotta-registry-module-name.*'. Find all key_name strings that
 *     begin with the substring 'yotta.your-yotta-registry-module-name.'
 *  - 'yotta.hello-world.animal[dog][foot][*]'. Find all key_name strings
 *    beginning yotta.hello-world.animal[dog][foot]
 *  - 'yotta.hello-world.animal[dog][foot]*'
 *  - 'yotta.hello-world.animal[dog*3]'
 *
 *****************************************************************************
 * ARGUMENTS:
 *  IN owner
 *   a previously returned handle from cfstore_open_ctx()
 *  IN key_name_query
 *   a search string to find. This can include the wildcard '*' character
 *  IN previous
 *   On the first call to cfstore_find then previous is set to NULL.
 *   On the subsequent calls to cfstore_find, a previously returned key handle
 *   can be supplied as the previous argument. The next available search result
 *   will be returned. If no further search results are available then
 *   cfstore_find will return NULL.
 *****************************************************************************
 * RETURN:
 *  SUCCESS     non-null valid handle to a CS key is returned
 *  ERROR       NULL
 ****************************************************************************/
cfstore_handle cfstore_find(cfstore_handle owner, const char* key_name_query, cfstore_handle previous);

/*****************************************************************************
 * FUNCTION: cfstore_strerror
 *  A CS client uses this function get an error string associated with a
 *  returned error code
 *****************************************************************************
 * ARGUMENTS:
 * IN errno  A previously returned error code from a CS API call.
 *
 *****************************************************************************
 * RETURN:
 *  SUCCESS  a null terminated string for a valid error code.
 *  ERROR    a null terminated emtpy string.
 ****************************************************************************/
const char* cfstore_strerror(uint32_t errno);

/*****************************************************************************
 * FUNCTION: cfstore_open
 *  open a {key, value} object for future operations.
 *  - if the kdesc->mode |= CFSTORE_MODE_CREATE, then the object will be created
 *    if it does not already exist. A handle will be returned to the newly
 *    created object.
 *  - if kdesc->mode &= ~CFSTORE_MODE_CREATE and an object exists in with the
 *    key_name then a handle will be returned to the object. There must be a
 *    unique match of the key_name
 *
 *****************************************************************************
 * ARGUMENTS:
 *  IN owner
 *   CS handle returned from cfstore_open_ctx() call made be owner
 *  IN key_name
 *   zero terminated string specifying the key name.
 * IN data
 *   a pointer to a data buffer supplied by the caller for CS to write as the
 *   binary blob value data
 *   (todo: remove? as this is available in _write())
 * IN OUT len
 *   on input, the client specifies the length of the buffer available at data
 *   on output, the CS specifies how many bytes have been stored in the CS.
 *   Note that fewer bytes may be stored than the input len depending on the
 *   CS internal representation of the value.
 *   (todo: remove? as this is available in _write())
 *  IN kdesc
 *   key descriptor, specifying how the details of the key create operations
 *
 *****************************************************************************
 * RETURN:
 *  NULL upon failure
 *  Non-NULL CS object handle on success, used to perform object operations
 ****************************************************************************/
cfstore_handle cfstore_open(cfstore_handle owner, const char* key_name, char* data, size_t* len, cfstore_key_desc_t* kdesc);

/*****************************************************************************
 * FUNCTION: cfstore_close
 *  Close the key_handle context previously recovered from CS.
 *  If an object has been written then it is finalised when the key is closed.
 *****************************************************************************
 * ARGUMENTS:
 *  IN key_handle
 *   a previously returned handle from cfstore_open()
 *****************************************************************************
 * RETURN: None
 ****************************************************************************/
void cfstore_close(cfstore_handle key_handle);

/*****************************************************************************
 * FUNCTION: cfstore_read
 *  this function allows the client to read the value data associated with
 *  a specified key.
 *****************************************************************************
 * ARGUMENTS:
 *  IN key_handle
 *   the handle returned from a previous call to cfstore_open() to get a handle
 *   to the key
 * IN data
 *  a pointer to a data buffer supplied by the caller for CS to fill with
 *  value data
 * IN OUT len
 *  on input, the client specifies the length of the buffer available at data
 *  on output, the CS specifies how many bytes have been written into the data
 *  buffer.
 *****************************************************************************
 * RETURN:
 *  SUCCESS  when all the data has been read and there is no more key_data to
 *           read
 *  ERROR    when an error occurred reading the value data.
 *  MORE     the read operation occurred successfully and there is more data
 *           to read
 ****************************************************************************/
int32_t cfstore_read(cfstore_handle key_handle, char* data, size_t* len);

/*****************************************************************************
 * FUNCTION: cfstore_write
 *  This function allows a client to write the value data associated with
 *  a specified key
 *****************************************************************************
 * ARGUMENTS:
 * IN key_handle
 *   the key for which value data will be written
 * IN data
 *   a pointer to a data buffer supplied by the caller for CS to write as the
 *   binary blob value data
 * IN OUT len
 *   on input, the client specifies the length of the buffer available at data
 *   on output, the CS specifies how many bytes have been stored in the CS.
 *   Note that fewer bytes may be stored than the input len depending on the
 *   CS internal representation of the value.
 * IN offset
 *  The offset from the start of the CS stored value at which supplied data
 *  should be written.
 *****************************************************************************
 * RETURN:
 *  SUCCESS  the supplied data was successfully written to the CS key.
 *  ERROR    the supplied data was not successfully written
 ****************************************************************************/
int32_t cfstore_write(cfstore_handle key_handle, char* data, size_t* len, uint32_t offset);

/*****************************************************************************
 * FUNCTION: cfstore_rseek
 *  move the position of the read pointer within a value
 *****************************************************************************
 * ARGUMENTS:
 *  IN key_handle
 *   the key referencing the value data for which the read location should be
 *   updated.
 *  IN offset
 *   the new offset position from the start of the value data
 *  IN whence
 *    CFSTORE_RSEEK_SET_OFFSET
 *      the location is set to offset bytes
 *    CFSTORE_RSEEK_SET_CUR
 *      the location is set current location plus offset bytes
 *    CFSTORE_RSEEK_SET_END
 *      the location is set to the end of the value plus offset bytes
 *
 *****************************************************************************
 * RETURN:
 *  SUCCESS, current read location >= 0
 *    upon success, the function returns the current read location measured
 *    from the beginning of the data value.
 *  ERROR
 *   on failure, the function returns an error code < 0
 ****************************************************************************/
int32_t cfstore_rseek(cfstore_handle key_handle, uint32_t offset, uint32_t whence);



/* Questions to resolve wrt sdh_20160106_1
 *
 * (1) todo:
 * - What distrusts what?
 * - Alternatively, what trust what?
 * - How is a secure box created and how to do you refer to it? the api?
 * - what is the data type supplied by the security context to the
 *   cfstore_open_ctx()
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
 *
 *  (18)
 *  resuming key queries: is this an iterator that can get partial sets of
 *  results, e.g. based on supplied buffer length for results, which may be
 *  too small to hold all results?
 *
 *  (21) offset_address; how does this work?
 *
 *  (24)
 *  why is there specific reference to storage mediums here. AFAIK the storage
 *  medium is an attribute of the object.
 *
 *  (50)
 *   -- 'a.b.c[d][e][*]'
 *   -- 'a.b.c[d][e]*'
 *
 *   whats the difference between the above 2 search strings?
 *   Consider the case where the CS contains the following keys
 *   a) 'a.b.c[d][e]'
 *   b) 'a.b.c[d][e].f'
 *   c) 'a.b.c[d][e][1]'
 *   d) 'a.b.c[d][e][2]'
 *   e) 'a.b.c[d][e][1].f'
 *   f) 'a.b.c[d][e][2].f'
 *
 *   search results for 'a.b.c[d][e][*]':
 *   a) 'a.b.c[d][e]'       (should this not be returned?)
 *   b) 'a.b.c[d][e].f'     (should this not be returned?)
 *   c) 'a.b.c[d][e][1]'
 *   d) 'a.b.c[d][e][2]'
 *   e) 'a.b.c[d][e][1].f'
 *   f) 'a.b.c[d][e][2].f'
 *
 *   search results for 'a.b.c[d][e]*':
 *   a) 'a.b.c[d][e]'
 *   b) 'a.b.c[d][e].f'
 *   c) 'a.b.c[d][e][1]'
 *   d) 'a.b.c[d][e][2]'
 *   e) 'a.b.c[d][e][1].f'
 *   f) 'a.b.c[d][e][2].f'
 *
 */
