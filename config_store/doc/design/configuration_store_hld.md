# Configuration Store High Level Design
Author: Simon Hughes

# Revision History
20160127: first version.

# Definition of Terms

##### Storage Area
This is an area in non-volatile storage medium used for persistent 
storage of secure data.  

##### Storage Chunk
A chunk is a mininum storage quantum on the NV device e.g. for the K64F 
on-chip NV store the chunk size is 128bits. When a chunk on backing store
has to be changes, the old chunk is erased and the updated data written to
a newly allocated chunk.


# Overview

The configuration store is an associative store for managing (key, value) 
pairs in persistent storage media.


# Use Cases

The design addresses the requirements of the following use cases:
- CS Initialisation and Factory Initialisation 
- FOTA

 
# System Logical High Level Design

## Storage Areas 
- There are 3 storage areas in the system:
    - 1 volatile swap area in memory (area_0) for caching client 
      CS changes.
    - 2 NV storage areas (area_1 and area_2)
- The structure of the 3 storages areas is the same, and is shown 
  schematically in the following diagram:

```C
   ===================
    SWAP_AREA (area_0)
    +-+-+-+-+-+-+-+-+
    |      H_0      |
    +-+-+-+-+-+-+-+-+
    |    ..KV..     |
    +-+-+-+-+-+-+-+-+
    |      T_0      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_1)
    +-+-+-+-+-+-+-+-+
    |      H_1      |
    +-+-+-+-+-+-+-+-+
    |    ..KV..     |
    +-+-+-+-+-+-+-+-+
    |      T_1      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_2)
    +-+-+-+-+-+-+-+-+
    |      H_2      |
    +-+-+-+-+-+-+-+-+
    |    ..KV..     |
    +-+-+-+-+-+-+-+-+
    |      T_2      |
    +-+-+-+-+-+-+-+-+
   ===================
   
   Schematic Representation of 
  
   H_0      : Header structure in area_0. Similarly H_i is the header 
              structure in the i-th area.
   ..KV..   : N (key, value) pairs in the the area
   T_0      : Tail structure in area_0. Similarly T_i is the tail 
              structure in the i-th area.
  
```

Note the following form the above diagram:
- Each area begins with a header structure including a version field.
- The header is followed by n (Key, Value) pairs where each Key, Value are of 
  arbitrary length.
- The area ends with a tail structure.


## Use Case: Factory Initialisation (Empty Store)

The initialisation sequence is as follows:
- area_0 is created with H_0:version = random_number, no (key, value) pair 
  entries and a valid tail structure 
- area_0 is stored to nv area_1
- area_0 H_0:version is incremented
- area_0 is stored to nv area_2

The configuration of the system can be represented by the figure below:

```C
   ===================
    SWAP_AREA (area_0)
    +-+-+-+-+-+-+-+-+
    |      H_0      |
    +-+-+-+-+-+-+-+-+
    |      T_0      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_1)
    +-+-+-+-+-+-+-+-+
    |      H_1      |
    +-+-+-+-+-+-+-+-+
    |      T_1      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_2)
    +-+-+-+-+-+-+-+-+
    |      H_2      |
    +-+-+-+-+-+-+-+-+
    |      T_2      |
    +-+-+-+-+-+-+-+-+
   ===================
   
   Area Configuration During Factory Initialisation (Empty Store)
```

The setting of the factory (key,value) pairs will then begin. See the 
Config-Store Client Storing (key, value) Pairs Call Flow
diagram below:

```C
--- CUT_HERE------------------------------------------------------------------
title Config-Store Client Storing (key, value) Pairs Call Flow

cfstore_Client->Config-Store: cfstore_open(keyname_1, o_create)
Config-Store->cfstore_Client: OK 
cfstore_Client->Config-Store: cfstore_write(value_1)
Config-Store->cfstore_Client: OK 
cfstore_Client->Config-Store: cfstore_close()
Config-Store->cfstore_Client: OK 
cfstore_Client->Config-Store: cfstore_open(keyname_i, o_create)
Config-Store->cfstore_Client: OK 
cfstore_Client->Config-Store: cfstore_write(value_i)
Config-Store->cfstore_Client: OK 
cfstore_Client->Config-Store: cfstore_close()
Config-Store->cfstore_Client: OK 
cfstore_Client->Config-Store: cfstore_flush()
Config-Store->cfstore_Client: OK 
--- CUT_HERE------------------------------------------------------------------
```

The following is the procedure for implementing the 
Config-Store Client Storing (key, value) Pairs Call Flow:
- on the creation of the new key, H_0:version is incremented to indicate the
  swap area_0 has been updated relative to the backing store.
- subsequent write(), open(), close(), etc. operations further update area_0 
  data structures but the H_0:version is not further incremented.
- the flush() operation finalises the area_0 and causes the area to be written
  to nv store, as described below:
	- the header and tail structures are updated as required. 
    - T_1 and T_2 are read from nv store and (e.g.) both areas found to be valid.    
    - H_1:version and H_2:version are read from nv store, inspected to find  
      H_1:version < H_2:version and therefore the area_1 is selected. 
     - area_0 is written (flushed) to selected area_1

The above is know as the 'Config-Store Update Procedure'.
The configuration of the system can now be represented by the figure below:

```C
   ===================
    SWAP_AREA (area_0)
    +-+-+-+-+-+-+-+-+
    |      H_0      |
    +-+-+-+-+-+-+-+-+
    |  K_0,1 V_0,1  |
    +-+-+-+-+-+-+-+-+
    |  K_0,2 V_0,2  |
    +-+-+-+-+-+-+-+-+
    |  K_0,3 V_0,3  |
    +-+-+-+-+-+-+-+-+
    |      T_0      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_1)
    +-+-+-+-+-+-+-+-+
    |      H_1      |
    +-+-+-+-+-+-+-+-+
    |      T_1      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_2)
    +-+-+-+-+-+-+-+-+
    |      H_2      |
    +-+-+-+-+-+-+-+-+
    |  K_0,1 V_0,1  |
    +-+-+-+-+-+-+-+-+
    |  K_0,2 V_0,2  |
    +-+-+-+-+-+-+-+-+
    |  K_0,3 V_0,3  |
    +-+-+-+-+-+-+-+-+
    |      T_2      |
    +-+-+-+-+-+-+-+-+
   ===================
  
   Area Configuration after Factory Initialisation (Non-Empty Store)
```

If the 'Config-Store Update Procedure' is repeated a number of times, then 
the sytem can represented in the following general way:

```C
   ===================
    SWAP_AREA (area_0)
    +-+-+-+-+-+-+-+-+
    |      H_0      |
    +-+-+-+-+-+-+-+-+
    |      K_0,0    |
    +-+-+-+-+-+-+-+-+
    |      V_0,0    |
    +-+-+-+-+-+-+-+-+
    |      K_0,1    |
    +-+-+-+-+-+-+-+-+
    |      V_0,1    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_0,j    |
    +-+-+-+-+-+-+-+-+
    |      V_0,j    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_0,n-1  |
    +-+-+-+-+-+-+-+-+
    |      V_0,n-1  |
    +-+-+-+-+-+-+-+-+
    |      T_0      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_1)
    +-+-+-+-+-+-+-+-+
    |      H_1      |
    +-+-+-+-+-+-+-+-+
    |      K_1,0    |
    +-+-+-+-+-+-+-+-+
    |      V_1,0    |
    +-+-+-+-+-+-+-+-+
    |      K_1,1    |
    +-+-+-+-+-+-+-+-+
    |      V_1,1    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_1,j    |
    +-+-+-+-+-+-+-+-+
    |      V_1,j    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_1,n-1  |
    +-+-+-+-+-+-+-+-+
    |      V_1,n-1  |
    +-+-+-+-+-+-+-+-+
    |      T_1      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_2)
    +-+-+-+-+-+-+-+-+
    |      H_2      |
    +-+-+-+-+-+-+-+-+
    |      K_2,0    |
    +-+-+-+-+-+-+-+-+
    |      V_2,0    |
    +-+-+-+-+-+-+-+-+
    |      K_2,1    |
    +-+-+-+-+-+-+-+-+
    |      V_2,1    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_2,j    |
    +-+-+-+-+-+-+-+-+
    |      V_2,j    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_2,m-1  |
    +-+-+-+-+-+-+-+-+
    |      V_2,m-1  |
    +-+-+-+-+-+-+-+-+
    |      T_2      |
    +-+-+-+-+-+-+-+-+
   ===================

   System Area Configuration after a Number of Config-Store Update Procedures 
```


## Use Case: Subsequent Initialisation (Non-Empty Store).
After factory configuration, at the start of initialisation CS finds the 
following general situation 
(see System Area Configuration after a Number of Config-Store Update 
Procedures):  

```C
   ===================
    SWAP_AREA (area_0)
    +-+-+-+-+-+-+-+-+
    |    Empty      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_1)
    +-+-+-+-+-+-+-+-+
    |      H_1      |
    +-+-+-+-+-+-+-+-+
    |      K_1,0    |
    +-+-+-+-+-+-+-+-+
    |      V_1,0    |
    +-+-+-+-+-+-+-+-+
    |      K_1,1    |
    +-+-+-+-+-+-+-+-+
    |      V_1,1    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_1,j    |
    +-+-+-+-+-+-+-+-+
    |      V_1,j    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_1,n-1  |
    +-+-+-+-+-+-+-+-+
    |      V_1,n-1  |
    +-+-+-+-+-+-+-+-+
    |      T_1      |
    +-+-+-+-+-+-+-+-+
   ===================
    NV_AREA (area_2)
    +-+-+-+-+-+-+-+-+
    |      H_2      |
    +-+-+-+-+-+-+-+-+
    |      K_2,0    |
    +-+-+-+-+-+-+-+-+
    |      V_2,0    |
    +-+-+-+-+-+-+-+-+
    |      K_2,1    |
    +-+-+-+-+-+-+-+-+
    |      V_2,1    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_2,j    |
    +-+-+-+-+-+-+-+-+
    |      V_2,j    |
    +-+-+-+-+-+-+-+-+
    |     ....      |
    +-+-+-+-+-+-+-+-+
    |      K_2,m-1  |
    +-+-+-+-+-+-+-+-+
    |      V_2,m-1  |
    +-+-+-+-+-+-+-+-+
    |      T_2      |
    +-+-+-+-+-+-+-+-+
   ===================

   System Area Configuration At Start of Initialisation 
```
The CS initialises swap area_0 in the following way:
- T_1 and T_2 are read from nv store and (e.g.) both areas found to be valid.    
- H_1:version and H_2:version are read from nv store, inspected to find  
  H_1:version < H_2:version and therefore the area_1 is selected. 
- The selected area_1 is loaded into area_0
- CS initialisation is then complete.

After initialisation, the system would look the same as the figure
System Area Configuration after a Number of Config-Store Update Procedures
where swap area_0 is an identical copy of area_1

## Keys


