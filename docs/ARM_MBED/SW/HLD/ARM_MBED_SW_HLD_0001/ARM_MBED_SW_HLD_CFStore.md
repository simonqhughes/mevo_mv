# Configuration Store High Level Design For Removing SRAM Limitation

Author: Simon Hughes

Document Version: 0.01

Date 20161110

# Introduction

## Overview

This document describes the CFSTORE high level design to remove the SRAM Limitation.

- The current CFSTORE has a HLD. This document is a delta to that document.
- The current design uses a heap, which is too impactful wrt to SRAM usages.
- Cant take full advantage of the available flash storage because of SRAM usage.


## Goals of design:

- to reduce the SRAM footprint to 2-4kB
- for SRAM usage to be bounded, i.e. statically allocated data structures rather than using the heap.
- to make the implementation capable using a large flash store without increasing 
- to be robust against failures i.e. the stored data should always be left in a recoverable state should
  power be lost or a software reset occurs during a flash write operation.

## Document Structure and Layout

The layout of the document is as follows:


  
## Terminology

Refer to terminology document.


# Overview of Basic Design 

## KVs are stored Using Modified Flash Journal

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig1.jpg "unseen title text")
*Figure 1. Flash Journal (modified) is used to support slots of different types and sizes.*

- The design uses a new Flash Journal alogorithm (strategy) (insert picture from jpg for 20161109_1):
    - KVs are stored as TLVs (Linked List) within a slot. (todo: consider inserting flash journal slot picture).
    - Algorithm will have N slots e.g. 4 slots.
    - Slots are of 2 types:
        - Snapshot Slot. This slot contains a complete record of all the KVs in a TLV array
          (linked list).
        - Delta Slot. This slot contains a record of TLVs that have been modified since the creation 
          of the last snapshot. Modifications include:
            - Writing new data to the KV.
            - Changing the size of the KV.
            - Deleting the KV.
        
    - Slot boundaries are aligned to sector boundaries.
    - Slots can be of different sizes. It's advantageous for snapshot slots to be larger than
      delta slots (e.g. snapshot slot = 256kB, delta slots = 16kB) because:
        - the mapping of this scheme is better for devices with mixed block sizes e.g. STM devices with 4x16kB, 3x64kB, 1x128kB, 1x256kB.
          as small sectors can be used for the deltas, and the large sectors can be used to store the entirety of the snapshot data.
        - its desireable that the snapshot slots use the large sectors so the total amount of stored data can be large e.g. 256kB.

        
## KVs Storage Format

### TLV Structure

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_tlv_structure_overview.jpg "unseen title text")
*Figure 1. TLV storage format for KV data.*

The above figure shows the format of the KV TLVs representation. This is composed of the following elements:

- Header of fixed size, padded so the last byte aligns with a program unit boundary. The header can  be written to flash independently of writing payload data.
- A data payload, padded so the last byte aligns with a program unit boundary. The payload can be written to flash independently of writing tail data.
- A tail of fixed size, padded so the last byte aligns with a program unit boundary. This permits the next header to be written on adjacent to the tail independently of the tail.

Note also the following:

- TLVs are of variable length.
- TLVs can be of different types, as indicated by the header type field.


### KV TLV Generic Header

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_generic_header.jpg "unseen title text")
*Figure 2. TLV generic header format.*


The above figure shows the TLV generic header format fields as described below:

- Version field (~4 bits) indicating the version of TLV header and data format. This document describes version 1.
- Reserved field (~4 bits).
- Type field (~2 bits) 
    - Type 1 indicates a full TLV which includes the key name and the value data. These TLVs appear in snapshot and delta slots.
    - Type 2 indicates a TLV for additional features and functionality. See later for details.
- Flags field (~16 bits). This field includes permissions, for example.
- Additional fields are present depending on the value of the Type field.
- Pad. The header is padded so the last byte aligns with a program unit boundary. 


### KV TLV Tail

![alt text](pics/ARM_MBED_SW_HLD_0001_cfstore_lld_fig_tail.jpg "unseen title text")
*Figure 3. TLV tail format.*

The above figure shows the TLV tail format including the following fields:

- Valid field (~8 bits). A value of 0xff indicates the TLV is valid (provided the CRC is correct). A value of 0x00 indicates the TLV is invalid. The delete operation sets the Valid field to 0.
- Reserved1 field (~24 bits). 
- Reserved2 field (~32n bits). This is padding so the Valid field sits within a program unit size block of NV store. 
- CRC field (32 bits). This is the CRC of the TCV.
- Reserved3 field (~32n bits). This is padding so the CRC field sits within a program unit size block of NV store. 


### KV TLV Header Type 1: Full TLVs

![alt text](pics/ARM_MBED_SW_HLD_0001_header_type1.jpg "unseen title text")
*Figure 4. TLV type 1 header format.*

The fields of the KV header include the following:

- The generic header fields.
- HLEN field (8 bits) specifies the length of the header.
- KLEN field (8 bits) specifies the length of the key name field in the TLV payload. This is padded with 0's so the last byte aligns with a program unit boundary.
- Reserved1 field (~16 bits). 
- VLEN field (32 bits) specifies the length of the KV value data field in the TLV payload.

- Length (32 bits). Length of the data payload that follows the header. 
    - For a Delta TLV Add operation, this is the length of the key name string (max 220 chars).
    - For a Delta TLV Delete operation, this is 0.
    - For a Delta TLV Write operation, this is the length of the value data
- Offset (32 bits). Present for Delta TLV Write operation, otherise set to 0. This is the write location offset from the start of the KV value data.
- KVID (32 bits). A unique indentifier bound to the the key name specified in this TLV. The KVID can be used in alternative TLV types to identify a TLV without having to include the KV key name.
- Sequence Number (32 bits). This is the KV version number which is incremented each time a new version of the KV is written.
- Pad. The header is padded so the last byte aligns with a program unit boundary. 


## Requirement for KVBUFs to Support Transaction Queueing


## CFSTORE Transactions Implementation

### Creating a New KV

![alt text](pics/ARM_MBED_SW_HLD_0001_kv_create.jpg "unseen title text")
*Figure 5. Creating a New KV.*

- todo:  insert pic of creating new KV
- todo: describe pic
- read/write locations stored in cfstore_file_t in hkey.


### Deleting a  KV

![alt text](pics/ARM_MBED_SW_HLD_0001_kv_delete.jpg "unseen title text")
*Figure 6. Deleting a  KV.*

### Opening an Existing KV for Reading

- todo:  insert pic and describe

### Opening an Existing KV for Reading/Writing

![alt text](pics/ARM_MBED_SW_HLD_0001_kv_open.jpg "unseen title text")
*Figure 5. Opening an existing KV for reading/writing.*

- todo:  insert pic and describe


### Reference Counting: Support for Multiple Readers/Writers


### Storage of KV Read/Write Locations

- locations are on a per KV descriptor basic i.e. each open KV descriptor has rlocation and wlocation.
- the values are stored in the hkey buffer.


### Error Handling


### Asynchronous Mode of Operation

The async KV read operation would proceed as follows:

- On a KV open for read-only access, a KVBUF is attached to the KV file descriptor.
- The KV is found in the lastest snapshot and the value data read into the KVBUF.
- The delta snapshots subsequent to latest snapshot are searched and applied to the KVBUF to yield the current state of the KV value data.
 



### Synchronous Mode of Operation.


### Static SRAM Buffers (KVBUFs)

update these notes:

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
  

# Additional Features For Enhanced Design

## Micro-Deltas

- have TLV Type n for different types of operation.
- Delta TLVs. This records a change (delta) to an existing KV or the addition/deletion of a TLV, for example. The TLV data incluedes:
    - Header including the unique KV identifier KVID.
    - The delta operation being performed:
        - Add KV.
        - Delete KV.
        - Rseek read location.
        - Write KV.
        - Open KV.
        - Close KV.
    - Optionally, write data for a write operation.

    
- Header Flags (n bits) for supporting Micro deltas (could be different TLV types too) . The flags can indicate the following properties
    - rwx permissions of the attribute.
    - Delta TLV Add bit. If set, this is a delta TLV for adding a new KV, and the TLV data contains the key name.
    - Delta TLV Delete bit. If set, this is a delta TLV for deleting a pre-existing KV. The KV is indentified using the KV ID field. This operation decrements the KV reference count. 
    - Delta TLV Open bit. If set, this is a delta TLV for opening a pre-existing KV. The KV is indentified using the KV ID field. This operation increments the KV reference count. 
    - Delta TLV Rseek bit. If set, this is a delta TLV for seeking the read location on a pre-existing KV. The KV is indentified using the KV ID field. 
    - Delta TLV Write bit. If set, this is a delta TLV for writing the value data of a pre-existing KV. The KV is indentified using the KV ID field.
    - Delta TLV Wseek bit. If set, this is a delta TLV for seeking the write location on a pre-existing KV. The KV is indentified using the KV ID field. 
    - Delta TLV First bit. If set, this is the first delta TLV to be written in a delta slot. See later for further details.
    - (check for other flags in the pre-existing implementation).

- The scheme permits the current state of an open KV to be recreated in memory when required to do so e.g. when a KV 


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


