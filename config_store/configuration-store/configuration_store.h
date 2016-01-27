/* configure-store.h
 *
 * interface
 * */


/*
 * opaque cfstore handle for manipulating cfstore data objects e.g. KV pairs.
 */
typedef void* cfstore_handle;


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
 * FUNCTION: cfstore_storage_detect
 *  This function reports the information on the underlying storage media
 *****************************************************************************
 * ARGUMENTS:
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
int32_t cfstore_storage_detect(cfstore_storage_desc_t* sdesc, cfstore_storage_desc_t* prev);

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
cfstore_handle cfstore_find(const char* key_name_query, cfstore_handle previous);

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
cfstore_handle cfstore_open(const char* key_name, char* data, size_t* len, cfstore_key_desc_t* kdesc);

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


/*****************************************************************************
 * FUNCTION: cfstore_flush
 *  move the position of the read pointer within a value
 *****************************************************************************
 * ARGUMENTS:
 *  reserverd   reserved for future use.
 *****************************************************************************
 * RETURN:
 *  SUCCESS, current read location >= 0
 *    upon success, the function returns the current read location measured
 *    from the beginning of the data value.
 *  ERROR
 *   on failure, the function returns an error code < 0
 ****************************************************************************/
int32_t cfstore_flush(cfstore_handle reserverd);



