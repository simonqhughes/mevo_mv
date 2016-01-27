/** @file configuration_store_prv.h
 *
 * component private header file.
 */


/*
 * Defines
 *
 * CFSTORE_FLASH_CHUNK_SIZE_BYTES
 * Number of bytes forming 1 chunk in the non-volatile storage
 * For the K64F, the chunk size is 128bits = 16 bytes
 */
#define CFSTORE_NV_CHUNK_SIZE_BYTES 16

/** structure of a flash area
 *
 */


/** @brief
 *
 * @param hdr_crc
 *         CRC32 of the following data up to the start offset of 'value'
 * @param size0
 *         total structure size including padding to support 128 bit
 *         granularity, 0xFFFFFFFF for invalid entry
 * @param version
 *         monotonic version increment for this key-value, the highest
 *         version number wins
 * @param frag_next_kvp
 *         pointer to next value fragment structure, 0xFFFFFFFF for
 *         last entry in chain, only present if fragmentation bit is supported
 * @param key_permissions
 *         bottom 6 bits contain the ACLs-bits (owner read/write/execute,
 *         other read/write/execute). The remaining bits in this field are
 *         used for the Device Data Security Protection Features bit field,
 *         bits are low-active
 * @param vlength
 *         this value fragment length
 * @param klength
 *         key name size including zero-padding
 * @param reserved0
 *         padding (zeroed) to align with chunk boundary
 */
typedef struct cfstore_area_header_t
{
    uint32_t hdr_crc;
    uint32_t size0;
    uint32_t version;
    uint32_t frag_next_kvp;
    uint32_t key_permissions;
    uint32_t vlength;
    uint8_t klength;
    uint8_t reserved0[3];
} cfstore_area_header_t;

/** @brief A key is made up of 1..n cfstore_area_key_t chunks.
 *
 * @param key
 *         ASCII value name byte array, always zero terminated - padded with
 *         zeros to align value end to 128 bit boundary
 */
typedef struct cfstore_area_key_t
{
    uint8_t key[CFSTORE_NV_CHUNK_SIZE_BYTES];
} cfstore_area_key_t;

/** @brief A value is made up of 1..n cfstore_area_value_t chunks.
 *
 * @param value
 *         opaque value blob byte array
 */
typedef struct cfstore_area_value_t
{
    uint8_t value[CFSTORE_NV_CHUNK_SIZE_BYTES];

} cfstore_area_value_t;

/** @brief
 *
 * @param flags
 *         CRC32 of the following data up to the start offset of 'value'
 * @param reserved0
 *         reserved for future use, set to 0.
 * @param size1
 *         total structure size including padding to support 128 bit
 *         granularity, 0xFFFFFFFF for invalid entry i.e. same as size0
 *         in cfstore_area_header_t, used for recovery from memory corruption.
 * @param final_crc
 *         CRC32 of complete entry including the hdr_crc, without the final_crc
 */
typedef struct cfstore_area_tail_t
{
    uint32_t flags;
    uint32_t reserved0;
    uint32_t size1;
    uint32_t final_crc;
} cfstore_area_tail_t;
