# Configuration Store High Level Design: Design For Removing SRAM Limitation

Author: Simon Hughes

Document Version: 0.01

Date 20161110

# Introduction

## Overview

This document describes the CFSTORE high level design to remove the SRAM Limitation.

- There is a pre-existing CFSTORE [HLD for the API design][CFSTORE_HLD]. Please refer to that document before reading this document.
- The current document describes a new HLD for the implmentation of the API with minimal SRAM footprint.
    



## Goals of New Design:

The implementation uses the system heap to store a full SRAM image of all stored KV attributes prior to committing to NV store. 

- When the CFSTORE Flush() operation is performed, the SRAM image is copied to NV store.
- When the CFSTORE Initialize() operation is performed, the NV store KV data image is loaded into to SRAM heap memory which is allocated when the size of the NV store image is determined.
- When the CFSTORE Uninitialize() operation is performed, the SRAM heap memory is deallocated back to the system.
- When the CFSTORE Read() operation is performed, KV data is read from the SRAM image.
- When the CFSTORE Write() operation is performed, KV data is written to the SRAM image.
- Changes to the KV SRAM image (e.g. through write() operations) must be persisted to the NV store using the flush() operation prior to the calling of Uninitialize(), otherwise the changes will be lost.

The limitations of the above scheme are as follows:
- System heap usage is unbounded, and will continue to grow until the system runs out of memory. 
- System heap usage grows as the total size of stored data grows.
- The size of flash store used is limited to the available SRAM that can be dedicated to CFSTORE usage. For example, if 32kB of SRAM is dedicated to CFSTORE KV image use, then only 32kB of the NV store can be used.
  (Note, a larger NV store footprint will occur as Flash Journal uses additional NV storage to maintain multiple versions of attributes).


  The goals of the new design and implementation are as follows:

- To reduce the SRAM footprint to 2-4kB.
- For SRAM usage to be bounded, i.e. the implemtation should use statically allocated data buffers rather than using the heap.
- To be capable of using a large flash store without being restricted by the amount of SRAM dedicated to CFSTORE.
- To be robust against failures i.e. the stored data should always be left in a recoverable state should
  power be lost or a software reset occurs during a flash write operation.

## Document Structure and Layout

The layout of the document is as follows:

(todo: write the layout section)

  
## Terminology

Please refer to CFSTORE [terminology document][CFSTORE_TERM] for definitions of terminology. For reference, the following terms are used extensively throughout this document.

- CFSTORE: Configuration Store.
- HLD: High Level Design.
- KV: Key Value.
- PU: Program Unit. This is the minimum size data block write that can be programmed into a sector (e.g. the K64F PU size = 8 bytes).
- TLV: Type Length Value.


# Basic Design Overview

## KVs are stored Using Modified Flash Journal

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig1.jpg "unseen title text")
**Figure 1. Flash Journal (modified) is used to support slots of different types and sizes.**

- The design uses a new Flash Journal alogorithm (strategy) (see the above figure):
    - KVs are stored as TLVs (similar to a linked list structure) within a slot.
    - The algorithm will have N slots e.g. 4 slots.
    - Slots are of 2 types:
        - Snapshot Slot. This slot contains a complete record of all the KVs in a TLV array. The TLVs used to represent the KVs are called use a TLV format that includes both the key name and value data in the TLV payload.
        - Delta Slot. This slot contains TLVs that have been modified since the creation 
          of the last snapshot. Modified KVs are recorded using the full TLV format for the specifically modified KVs. KVs that have not been modified are not represented in the delta slot.
    - Slot boundaries are aligned to sector boundaries.
    - Slots can be of different sizes. It's advantageous for snapshot slots to be larger than
      delta slots (e.g. snapshot slot = 256kB, delta slots = 16kB) because:
        - the mapping of this scheme is better for devices with mixed block sizes e.g. STM devices with 4x16kB, 3x64kB, 1x128kB, 1x256kB.
          as small sectors can be used for the deltas, and the large sectors can be used to store the entirety of the snapshot data.
        - its desireable that the snapshot slots use the large sectors so the total amount of stored data can be large e.g. 256kB.
    - Slots can be made up of multiple smaller sectors. For example, on the K64F which has a 2kB sector size, a 256kB snapshot slot may be composed of 128x2kB sectors. In the case that a slot is composed of a 
    - Slots can be made up of 1 large sector. For exmaple, the STM 42x (todo find data), has a 128kB sector which may be used for a snapshot slot.
    
todo find link to Rohits spreadsheet.
        
## KVs Storage Format

### TLV Structure

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_tlv_structure_overview.jpg "unseen title text")
**Figure 2. Full TLV storage format for KV data.**

The above figure shows the format of the KV full TLV representation i.e. the format that includes both the key name and value data. This is composed of the following elements:

- Header of fixed size, padded so the last byte aligns with a program unit boundary. The header can  be written to flash independently of writing the preceding tail (if a prior TLV exists in the slot) and the following payload data.
- A data payload, padded so the last byte aligns with a program unit boundary. The payload can be written to flash independently of writing the preceding header and following tail. In the above figure, the payload is composed of:
    - Key name. This is the name of the KV attribute.
    - Value data. This is the value data bound to the key name.
- A tail of fixed size, padded so the last byte aligns with a program unit boundary. The tal can be written to flash independently of writing the preceding payload, and the following header of the next TLV (space permitting). 

Note also the following:

- TLVs are of variable length.
- TLVs can be of different types, as indicated by the header TYPE field.
- TLV fields for data types larger than a byte are written in big endian format (network byte order).
- TLVs may cross sector boundaries so that CFSTORE can support KV sizes larger than sector sizes.
- The start of the header, key name, value data and tail data structures on NV store must be aligned with PU boundaries, to facilitate the writing of the TLV components independently of one another.


### <a name="kv-tlv-generic-header"></a> KV TLV Generic Header

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_generic_header.jpg "unseen title text")
**Figure 3. TLV generic header format.**


The above figure shows the generic structure of the TLV header common to all KV TLV representations. The structure and field definitions are described in the following: 

- VERSION field (~4 bits). This field indicates the version of TLV header and data format (version 1 is described in this document).
- RESERVED field (~4 bits). This field is reserved for future use.
- TYPE field (~8 bits). Type = 1 indicates a full TLV representation which includes the key name and the value data. These TLVs may appear in snapshot and delta slots.
- FLAGS field (~16 bits). This field includes permissions, for example, and the definition of the flags is determined by the TLV Type.
- Additional fields are present depending on the value of the Type field.
- PAD. The header is padded so the last byte aligns with a program unit boundary, so that the header can be written to flash independently of writing the preceeding and following journal entries. 


### KV TLV Tail

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_tail.jpg "unseen title text")
**Figure 4. KV TLV tail format.**

The above figure shows the TLV tail format including the following fields:

- Valid field (~8 bits). A value of 0xff (and the correct CRC for the TLV) indicates the TLV is valid. A value of 0x00 indicates the TLV is invalid irrespective of the CRC. The delete operation sets the Valid field to 0. 
  TLVs with the Valid field set to 0 are ignored.
- Reserved1 field (~24 bits). 
- Reserved2 field (~32n bits, for n >=0). This is padding so the Valid field sits within a program unit size block of NV store. 
- CRC field (32 bits). This is the CRC of the TLV.
- Reserved3 field (~32n bits). This is padding so the CRC field sits within a program unit size block of NV store. 


### <a name="kv-tlv-header-type-1"></a> KV TLV Header Type 1: Full TLVs

![alt text](pics/ARM_MBED_SW_HLD_0001_header_type1.jpg "unseen title text")
**Figure 5. TLV type 1 header format for the full TLV representation. Note that figure incorrectly shows Type = 0. **

The fields of the KV header include the following:

- The generic header fields as previousl described in the [KV TLV Generic Header](#kv-tlv-generic-header) section.
- FLAGS field (16 bits). This field is to be specified.
- HLEN field (8 bits). This field specifies the length of the header.
- KLEN field (8 bits). This field specifies the length of the key name field in the TLV payload. It is padded with 0's so the last byte aligns with a program unit boundary, 
  allowing the first part of the TLV (header and key name) to be written in NV store when created/opened for writing independently of the following payload.
- Reserved1 field (~16 bits). 
- VLEN field (32 bits) specifies the length of the KV value data field in the TLV payload.
- KVID (32 bits). This field reports the unique identifier bound to the key name specified in TLV key name part of the payload. The KVID is used in other TLV types to identify a TLV without including the key name.
  The KVID is selected at create time and is unique within the store.
- SEQUENCE_NUMBER (32 bits). This is the KV version number which is incremented each time a new version of the KV is written. The implementation must take into account the possibility that 
  the sequence number counter can wrap. See the next section.
- Pad. The header is padded so the last byte aligns with a program unit boundary. 


#### Wrapping of the SEQUENCE_NUMBER

todo: describe how the sequence number wraps.


## CFSTORE Operations

### Storage of KV Read/Write Locations

For each open KV descriptor (hkey buffer), the cfstore_file_t data structure stores the following data:

- The file read location rlocation.
- The file write location wlocation.

todo: describe the reference counting.


### Creating a New KV

![alt text](pics/ARM_MBED_SW_HLD_0001_kv_create.jpg "unseen title text")
**Figure 6. Creating a New KV.**

- todo:  insert pic of creating new KV
- todo: describe pic
- read/write locations stored in cfstore_file_t in hkey.


### Deleting a  KV

![alt text](pics/ARM_MBED_SW_HLD_0001_kv_delete.jpg "unseen title text")
**Figure 7. Deleting a  KV.**

### Opening an Existing KV for Reading

- todo:  insert pic and describe

### Opening an Existing KV for Reading/Writing

![alt text](pics/ARM_MBED_SW_HLD_0001_kv_open.jpg "unseen title text")
**Figure 8. Opening an existing KV for reading/writing.**

- todo:  insert pic and describe


### Reference Counting: Support for Multiple Readers/Writers



### Error Handling


### Asynchronous Mode of Operation

The async KV read operation would proceed as follows:

- On a KV open for read-only access, a KVBUF is attached to the KV file descriptor.
- The KV is found in the lastest snapshot and the value data read into the KVBUF.
- The delta snapshots subsequent to latest snapshot are searched and applied to the KVBUF to yield the current state of the KV value data.
 



### Synchronous Mode of Operation.


### Static SRAM Buffers (KVBUFs)

update these notes:

- Requirement for KVBUFs to Support Transaction Queueing (old section title, delete?)
- sram buffers used for queueing for the simultaneous rw access of n clients to the same KV.
- read buffer supplied by client is owned by cfstore until either the read data is returned, or an error is returned. The buffer is used as a scratch pad for internal operations prior to return of the read data.
  The buffer (or a part thereof) will be passed to the storage driver f  space may be reserved so the underlying storage driver is 

- For an open KV, there is an associated statically allocated SRAM staging buffer (KVBUF). The KVBUF is needed for queue-buffering read/write transactions.
  CMSIS storage driver transactions have to be serialised i.e. an outstanding transaction has to 
  completed before another transaction can be requested. The KVBUF is therefore used to buffer context data for a pending storage driver transaction until it can be 
  issued/completed with the the storage driver.
- For example, the KV SRAM buffer (KVBUF) may be ~256bytes, and there may be ~8 buffers (limiting the maximum number pending transaction to 8).
  So the typical SRAM footprint is ~2kB. Dimensioning of the SRAM buffer should take into account:
- the size of the flash optimal program unit (1024 bytes on K64F)
- the size of the flash program unit (8 bytes on K64F) i.e. the KVBUF size should be a multiple of the program unit.
- The total SRAM footprint.
- The maximum number of concurrently open KVs (this doesnt have to be the case if all data is stored on flash necessary to re-create the open KV state).
  The number of KVBUFs then just restricts the number of concurrent accesses from clients.
- Each KV SRAM buffer has the following associated data items:
  - read location.
  - write location.
  - reference count (no, this has to be bound to *the* one and only representation of the KV value data).
  

# Enhanced Design Features

This section describes features that can be added to the basic design to enhance operation and performance. Additional features includes:

- Write location seek support for setting the write location within a file.


## Write Location Seek Support

The CFSTORE API specification has the limitation that the write locaion does not support seeking:

- When a file is opened for writing, the write location (wlocation) is set to 0, i.e. to the beginning of the KV value data.
- As data is written to the KV value data field, wlocation is incrementally updated reflecting data that has been written. No Wseek() method exists in the CFSTORE API, so wlocation cannot be changed i
  independently of write operations.
- When a file is opened for reading, the read location (rlocation) is set to 0, i.e. to the beginning of the KV value data.
- As datat is read from the KV value data field, rlocation is incrementally updated reflecting data that has been read. 
- rlocation can be set to a new offset using the Rseek() method in the CFSTORE API. 

This inability to seek the wlocation means there is a mismatch between the CFSTORE API and the behaviour of a traditional POSIX file API, 
which the feature described in this section seeks to address. 

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_incremental_write_header.jpg "unseen title text")
**Figure 9. Type 2 TLV Header format incremental write operations.**


Seeking wlocation is implemented by defining a new TLV type for incremental writes (Type = 2 header). Figure 9 shows the fields in the header, where the definition of the following 
fields has been defined previously in the [KV TLV Header Type 1](#kv-tlv-header-type-1) section:

- Version field (~4 bits). 
- Reserved field (~4 bits). 
- Type field (~8 bits).  
- Flags field (~16 bits).  
- VLEN (32 bits). 
- KVID (32 bits).
- SEQUENCE_NUMBER (32 bits).
- PAD.

The wlocation field is defined as follows:

- WLOCATION (32 bits). The first byts of the incremental write payload data is written at offset WLOCATION from the start of the KV value data.


![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_incremental_write_ops.jpg "unseen title text")
**Figure 10. Sequence of incremental write operations.**


Figure 10 illustrates how the incremental write TLV is used in conjunction with the full TLV to support seeking wlocation:

- When a KV is opened for reading and writing, space for a new full TLV representation of the KV is reserved in the delta slot. See (1) in the figure. 
    - Upon opening, the header fields, key name and size of the KV are known, so these data can be created and stored in flash. The setting of the 
      header TLV length fields means the TLV can be "walked over" to the next TLV's (e.g. the incremental write TLVs) so that new TLVs can be written
      in the journal, before the full TLV tail CRC has been written.
    - The header SEQUENCE_NUMBER is set to i.  
- The subsequent write operations are recorded in the delta slot with incremental write TLVs. 
    - The incremental write TLVs (write deltas) are stored after the full TLV described in the previous point.
    - The header SEQUENCE_NUMBER is set to j where j > i.  
    - The cfstore_file_t::wlocation variable is updated accordingly after each incremental write.
    - The above figure shows the 3 incremental write operations at (2), (3) and (4). The sequence numbers are ordered such that j4 > j3 > j2 > i.
    - Multiple writers can be writing data to the same KV. Each writer contributes incremental writes independently, but they are all used to create a new version of the full TLV data.
- Read operations first read the original KV TLV snapshot data into the client receive buffer. The delta write operations for this KV are then applied ontop of the original TLV data into the client receive buffer. 
  This re-creates the current version of the value data, which is returned to the client.
- When the TLV is closed ((see (6) in the above figure, no more writes to be made), the new state of the TLV is recorded in the space allocated for the full TLV. In a loop:
    - A data window (e.g. 256 bytes, a multiple of the PU size) is read from the snapshot TLV into an SRAM buffer, the first data window being read from the start of the TLV data.
    - The incrementatal writes updating value data inside the data window are applied to the buffer.
    - The buffer is then written to the full TLV.
    - The loop is repeated for the next data window worth of data until the full TLV data payload has been written.
    - Once the payload has been written, the full TLV tail is written committing the new version of the TLV. The incremental write TLVs are then deleted.
- With reference to the above figure, events (6), (7) and (8) show the incremental write data being recorded in the full TLV. The CRC is then written  
  for the full TLV (9) committing the data. The incremental TLVs are then deleted by setting the VALID field in the tails to 0x00 (see events (10), (11) and (12)).
  
The above operation has been specified such that if device experienced a power failure at any point during the sequence of operations then the KV data stored in flash remains in a consistent state
from which the device software can recover the data. 

If the power fails during the above operation then upon restarting the system falls back to the latest version of the full TLV representing the KV data. 
The latest version is the one with the most recent sequence number. 

- If the power fails prior to event (9) then the system will fallback to the previous full TLV version e.g. the version stored in the last snapshot slot. 
  The incremental write TLVs will be ignored (they may be deleted on CFSTORE initialisation) and the 3 data incremental write operation will be lost.
- If the power fails after event (9) but prior to deleting the incremental write TLVs, then the system will fallback to using the new full TLV version created with the incremental write deltas. The 
  undeleted incremental write TLVs will be ignores (they may be deleted on CFSTORE initialisation).

Note that at initialisation, undeleted incremental write TLVs in a delta slot may be deleted.


## Slots as Ring Buffers

- starting at variable location.
- finding the first TLV in a slot
- wrapping 

todo: in next revision relax this constraint e.g. with the following changes:

- relax the constraint that the delta TLV is fixed size of 256 bytes.
- the delta TLV is of minimum of program unit bytes in size.
- have a cookie field in the header.
- the delta slot is used as a ring buffer.
- rather than the first delta TLV start at a random location selected from one of the (sizeof delta slot)/(sizeof fixed delta TLV block ~256bytes) locations, 
  have N~(sizeof delta slot)/(sizeof KVBUF) so N~64 predefined possible locations.
- one subslot position is selected at random when writing the first KV to a delta slot. 
- The location of the first TLV in a delta slot is caches in 
  to find the first delta TLV 
  
- the first delta block writing in a slot is written at a random location within the slot so as not to excessively wear the 
  flash at the start of the associated sector. To do this: 
    - delta blocks have a flag indicating this is the first one to be written in the delta slot.
    - delta blocks are of fixed size e.g. KVBUF, multiple of the program unit. They delta slot can be searched 
      from the start of the slot by looking for the looking for the first delta TLV flag at the 
      boundaries which 


#### Delta TLV First bit

todo: this section describes the operation of the Delta TLV First bit

- A Scheme for minimizing wear at the start of a slot.
- delta slot used as a ring buffer of delta TLVs.



# References 

* The [CFSTORE Product Requirements][CFSTORE_PRODREQ]
* The [CFSTORE Engineering Requirements][CFSTORE_ENGREQ]
* The [CFSTORE High Level Design Document][CFSTORE_HLD]
* The [CFSTORE Low Level Design Document][CFSTORE_LLD]
* The [CFSTORE Terminology for definition of terms used in CFSTORE documents][CFSTORE_TERM]

[CFSTORE_PRODREQ]: doc/design/configuration_store_product_requirements.md
[CFSTORE_ENGREQ]: doc/design/configuration_store_requirements.md
[CFSTORE_LLD]: doc/design/configuration_store_lld.md
[CFSTORE_HLD]: doc/design/configuration_store_hld.md
[CFSTORE_TERM]: doc/design/configuration_store_terminology.md
[KEIL_CMSIS_DRIVER]: http://www.keil.com/pack/doc/CMSIS/Driver/html/index.html