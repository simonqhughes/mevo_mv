# Configuration Store Requirements
Author: Simon Hughes
Document Version: 0.01


# Overview

This document captures the Configuration Store (CFSTORE) Requirements


# Product Requirements

### General Requirements

`REQ_CFSTORE_PROD_GEN_0001`: Persistent Data Storage. CFSTORE MUST provide persistent storage of data 
e.g. using on-chip flash, off-chip flash, battery backed SRAM, EEPROM, etc. 

`REQ_CFSTORE_PROD_GEN_0002`: Off-chip Storage: CFSTORE MUST be able to store data off-chip in cases
where suitable off-chip storage is available.

`REQ_CFSTORE_PROD_GEN_0003`: On-chip Storage: CFSTORE MUST be able to store data on-chip in cases
where suitable on-chip storage is available. 

`REQ_CFSTORE_PROD_GEN_0004`: Stored Data Minimum Size. CFSTORE MUST be capable of storing a certificate chain and
keying information required for IoT type devices. This is a minimum of 4kB of data.

`REQ_CFSTORE_PROD_GEN_0005`: Stored Data Maximum Size. CFSTORE MAY be capable of storing application 
data upto to 1MB data. 

`REQ_CFSTORE_PROD_GEN_0006`: CFSTORE Feature Configuration: CFSTORE MUST implement configuration 
switches so CFSTORE features can be turned on or off by default. CFSTORE 
features incompatible with the platform OS or another subsystems features MAY then be disabled. 
The switches SHOULD be set at compile time.  


### Security Requirements

`REQ_CFSTORE_PROD_SEC_0001`: Secure Data Storage. CFSTORE MUST provide secure NV storage of data.  
The CFSTORE SHOULD enforce an Access Control List describing the permissions required by a 
system process to read/write/execute CFSTORE stored data. CFSTORE MUST prevent an 
unauthorised entity from reading, modifying or executing stored data. 

`REQ_CFSTORE_PROD_SEC_0002`: Security Primitives. CFSTORE SHOULD use security primitives and features
available from the operating environment to enhance the security of stored data (e.g. MCU 
fuses, flash bank security features, PlatformOS security primitives, etc should be employed).

`REQ_CFSTORE_PROD_SEC_0003`: Security Model - Transactional Atomicity. When committing data to 
storage, CFSTORE MUST perform the commit operation atomically i.e. there is no possibility that
NV data is left in an inconsistent state.     

`REQ_CFSTORE_PROD_SEC_0004`: Roll-back Protection. CFSTORE MUST be secure against attacks intended
to revert stored data to a state at a previous point in time (e.g. to factory settings).   

### mbed Cloud Support (Portability) Requirements 

`REQ_CFSTORE_PROD_PORT_0001`: mbed Cloud Client Platform OS Portability: The mbed Cloud client
is portable software and therefore the CFSTORE software stack MUST be 
portable to multiple platform operating systems (e.g. mbedOS, Zephyr, FreeRTOS). This
means the use of platform dependent primitives (e.g. semaphore, mutex, thread, timer) 
SHOULD be isolated to specific code modules (e.g. CFSTORE wrappers for OS integration) 
accompanied by porting guides and documentation.

`REQ_CFSTORE_PROD_PORT_0002`: mbed Cloud Client NV Storage: CFSTORE MUST support the NV storage requirements 
of mbed Cloud Client software subsystems. This includes but is not limited to the use of CFSTORE with the
following subsystems: 

- The Thread Stack.
- The Provisioning Client.
- The Connector Client.
- The Update Client.
 
`REQ_CFSTORE_PROD_PORT_0003`: Mbed Cloud and CFSTORE Interoperability: CFSTORE features incompatible
with the mbed Cloud client features SHOULD be disabled by default. For example, the CFSTORE 
"Use on-chip NV storage" feature SHOULD be disabled by default when the mbed Cloud Client 
"Use Thread Stack" feature is enabled.

`REQ_CFSTORE_PROD_PORT_0004`: Platform OS Wrappers: CFSTORE and its subcomponents SHOULD be capable of 
being encapsulated for multiple platform OSs to expose a platform OS specific APIs. The 
design and implementation of the CFSTORE OS wrappers will be determined by
the OS maintainers. However, CFSTORE SHOULD facilitate this process by minimizing the 
effort required to implement the wrappers.  

`REQ_CFSTORE_PROD_PORT_0005`: MCU Support. CFSTORE SHOULD support as wide range of MCUs as possible.  

`REQ_CFSTORE_PROD_PORT_0006`: Efficiency - Code Size. The CFSTORE code size SHOULD be small so 
it can be targeted on a wide range of MCUs. The target code size is less than 20kB. 

`REQ_CFSTORE_PROD_PORT_0007`: Efficiency - SRAM Size. The CFSTORE SRAM footprint SHOULD support be
small e.g. the size of 1-2 NV storage sectors (typically 4-8kB in size).
 
`REQ_CFSTORE_PROD_PORT_0008`: Reliability (Wear Levelling). CFSTORE MUST employ strategies to 
mitigate limited NV storage write/erase endurance (number of cycles before failure). This is 
required so devices can achieve acceptable product lifetimes at the expense of increased
NV storage footprints. 

`REQ_CFSTORE_PROD_PORT_0009`: Partner Port 1 Storage Driver Model: Partners MUST only be
required to port one storage (device) driver for both Kiel RTX and mbedOS.

   
# Engineering Requirements (Consolidated Requirements)

This section contains:

- Engineering requirements decomposed from the product requirements, given the current
  software architecture.
- New engineering requirements from CFSTORE clients. 


```

                         Portable mbed Cloud                                     Platform OS 
                           Software Stack                                        (e.g. mbedOS)
                         ==================                                      Integration
                                                                                 ============= 

    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | mbed Cloud Client                                                 |
    |  +-+-+-+-+-+-+-+-+-+-+-++-+  +-+-+-+-+-+-+-+-+                    |
    |  |  Provisioning Client   |  |  mbed Client  |                    |
    |  +-+-+-+-+-+-+-+-+-+-+-++-+  +-+-+-+-+-+-+-+-+                    |
    |                                                                   |
    |  +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+          |    
    |  | Thread Stack  |  |  Update Service |  | mbedTLS     |          |                               
    |  +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+     (20) |    
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    
      
                                --- CFSTORE C-HAL3 Interface/PAL (18) ---     -- OS CFSTORE API (19) --
                                                                            
                                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+-+-+-+-+-+-+
                                |    Security Layer (uvisor) (16)       |    | Platform-OS CFSTORE   |
                                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    | Wrapper (17)          |  
                                                                             +-+-+-+-+-+-+-+-+-+-+-+-+
                                                                            
    ------------------- CFSTORE C-HAL2 Interface (15) ------------------------------------------------ 
                                                                            
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  
    |             Configuration Store (CFSTORE) Mux/Demux (14)          |  
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  
                                                                            
    -------------------- CFSTORE CMSIS C-HAL Interface (13) -------------  
                                                                           
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  
    |                      Configuration Store (12)                     |  
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  

    -- Storage_VM.h API (9) ---   ---- Flash_Journal.h API (10) ---------    --- OS SVM/FJ API (11) --
     
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                      +-+-+-+-+-+-+-+-+-+-+-+-+
    | Storage Volume Manager (SVM) (7)|                                      |Platform-OS SVM Wrap   | (8)
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                      +-+-+-+-+-+-+-+-+-+-+-+-+

    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+-+-+-+-+-+-+
    | Flash Journal (FJ) (5)                                            |    | Platform-OS FJ Wrapper| (6)   
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+-+-+-+-+-+-+

    ------ Storage Driver API (CMSIS Storage Driver Interface) (3) ------    --- OS Storage API (4) --
    
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+-+-+-+-+-+-+
    | Storarge_Driver (1) e.g.                                          |    | Platform-OS           |
    |  - ARM_Driver_Storage_MTD_K64F                                    |    | Storage Driver        |
    |  - ARM_Driver_Storage_MTD_SDCard                                  |    | Wrapper (2)           |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+-+-+-+-+-+-+

    SW
    -----------------------------------------------------------------------------------------------------
    HW

```

The above figure is used to help describe the CFSTORE engineering requirements arising 
from the product requirements. Each of the following sections corresponds to one 
of the entities in the diagram, and describes the requirements relating to that entity.


### General Engineering Requirements

`REQ_CFSTORE_ENG_GEN_0001`: CMSIS Driver Model. The lowest level of the CFSTORE software stack includes a 
NV storage driver. The CFSTORE Storage Driver API MUST conform to the CMSIS Driver API so that Partners
are only required to port one storage driver for both Kiel RTX and mbedOS.

`REQ_CFSTORE_ENG_GEN_0002`: Portable C Components. The following portable components MUST be written in C:

- Storage Driver (1)
- Storage Driver API (CMSIS Storage Driver Interface) (3)  
- Flash Journal (FJ) (5)
- Platform OS Flash Journal Wrapper (6)
- Storage Volume Manager (7)
- Storage Volume Manager API(Storage_VM.h) (9)
- Flash Journal (Flash_Journal.h) API (10)
- Configuration Store (12)
- CFSTORE CMSIS C-HAL Interface (13)
- Configuration Store (CFSTORE) Mux/Demux (14)
- CFSTORE C-HAL2 Mux/Demux Interface (15)
- Security Layer (uvisor) (16)
- CFSTORE C-HAL3 Interface (18)
- mbed Cloud Client (20)


`REQ_CFSTORE_ENG_GEN_0003`: Platform OS Components. The following components MAY be implemented in a language selected by the OS maintainers:

- Platform OS Storage Driver Wrapper (2) 
- Platform OS Storage API (4)
- Platform OS Storage Volume Manager Wrapper (8)
- Platform OS Storage Volume Manager/Flash Journal Wrapper API (11)
- Platform-OS CFSTORE Wrapper (17)
- OS CFSTORE API (19)



### Storage Driver (1)

This entity is the implementation of the NV storage device driver.


`REQ_CFSTORE_THREAD_20160811_02`: Multi-platform support: Other SOCs Support
K64F is currently the only supported platform. Should the platform support be extended to other SOCs? Which platforms? Which families?

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments: SDH: todo: discuss with MJS. Suggest changing this requirement to "ARM MUST port to reference platforms, partners MAY port to their own platforms". 


`REQ_CFSTORE_THREAD_20160811_03`: Multi-platform support: K64 family support
16.12: MUST: generalize storage driver to K64 family. (MJS)

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments: SDH: todo: discuss with MJS. Suggest changing this requirement to "ARM MUST port to reference platforms, partners MAY port to their own platforms". 


`REQ_CFSTORE_THREAD_20160811_04`: Multi-platform support: New Thread Platform Support
Marcus S, Simon F both advocate multi-target support , 16.09: MUST - Implement storage drivers for all 6LP/Thread boards (based on product requirement). (MJS)

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments: SDH: todo: discuss with MJS. Suggest changing this requirement to "ARM MUST port to reference platforms, partners MAY port to their own platforms". 


### Platform OS Storage Driver Wrapper (2)

This entity encapsulates the Storage Driver for integration within a Platform OS.


`REQ_CFSTORE_MBEDOS_20161012_01`: Storage Drivers/Driver_Storage.h API requires mbedOS C++ wrapper

- Who needs it:  TBD
- Why do they need it:  TBD    
- When do they need it: TDB
- Who is proposing it: TBD
- Design suggestions:  TDB 
- Comments: 
    - SDH todo: Raise question for SamG: Do you want this wrapper? if yes then please detail requirements 


### Storage Driver API (CMSIS Storage Driver Interface) (3)

This entity is the portable storage driver API equating to the CMSIS Storage Driver Interface agreed with Kiel. 


`REQ_CFSTORE_UPDATE_SRV_20161012_10`: Abstract away a wide range of underlying storage systems.

- Who needs it:PAL team. mbed OS users.
- Why do they need it: To minimise porting effort required to adapt to different storage hardware.  To provide a consistent programmers model over a wide range of storage hardware, so that users dont need to know a lot about the hardware.  
- When do they need it:  Ask Simon F and Sam G
- Who is proposing it: Amyas, SDH,  
- Design suggestions: Appear and behave the same whether backed by on-chip, dual-bank or external Flash, EEPROM or RAM
- Comment: 
    - SDH todo: I propose restating this as a general requirement for the presence of the CMSIS Storage Driver API.
 

`REQ_CFSTORE_MBEDOS_20161012_04`: Storage Drivers/Driver_Storage.h API mbedOS C++ wrapper API supports both synchronous and asynchronous modes of operation.

- Who needs it:  TDB
- Why do they need it:  TDB   
- When do they need it: TDB
- Who is proposing it: TBD
- Design suggestions:  TDB 
    - API should be synchronous only? Asynchronous interface should not be exposed?
- Comments: Question for SamG: Does this API exist in mbedOS? If yes the please detail requirements. 

`REQ_CFSTORE_MBEDOS_20160810_07`: 16.09`: SHOULD - Discuss dropping SYNC only mode in cmsis-driver storage API with Kiel. (MJS)

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments:
	- SDH todo: suggest converting this into mbedOS requirement to only accept storage drivers
	  with both sync and async support.  
 

### Platform OS Storage API (4)

This entity is the Platform OS storage driver API.


`REQ_CFSTORE_MBEDOS_20160810_03`: Storage CMSIS-Driver API. Consistent with mbed-os practices? Keep/modify/change/encapsulate?

- Who needs it: Partners  
- Why do they need it: Partners MUST be required to port at most 1 storage driver per platform to support both mbedOS and Kiel RTX.  
- When do they need it: 20160810
- Who is proposing it: Marcus Shawcroft  
- Design suggestions:
- Comments:
    - SDH todo: can this requirement be removed? Its up to the platform OS how they want to encapsulate the storage API.  
    - It has been adopted by the mbedOS code base and released.
    - This requirement has been copied from 16Q3 planning spreadsheet (see CFSTORE roadmap doc for reference).


### Flash Journal (FJ) (5)

This entity is the Flash Journal implementation.


`REQ_CFSTORE_PROV_CLIENT_20160811_02`: Provide a wear-levelled, reliable key-value store.

- Who needs it: OpenAIS and other mbed OS users.
- Why do they need it: They would like to store configuration data e.g. current config of the device.
- When do they need it:  Firmware encryption is road-mapped for R1.2 (15 Feb 2017).  
- Who is proposing it: Amyas, provisioning client team. 
- Design suggestions:  The OpenAIS use case would be on the order of 10 updates a day for up to 20 years.  
  This would probably belong in the Flash driver not the CFSTORE. It is possibly a nice-to-have as in 
  most systems it does not matter too much if a device forgets its recent states.  
- Comments: 


### Platform OS Flash Journal Wrapper (6)

This entity is the platform OS Flash Journal wrapper implementation.

`REQ_CFSTORE_MBEDOS_20161012_02`: flash_journal.h API mbedOS C++ requires wrapper

- Who needs it:  TDB
- Why do they need it:  TDB   
- When do they need it: TDB
- Who is proposing it: TBD
- Design suggestions:  TDB
    - API should be synchronous only? Asynchronous interface should not be exposed?
- Comments: SDH todo: Question for SamG: Does this API exist in mbedOS? If yes the please detail requirements. 


### Storage Volume Manager (7)

This entity is the storage volume manager which creates virtual partitions from a physical storage device
so higher layer entities can share the device. 


`REQ_CFSTORE_SVM_20161013_01`: The Storage Volume Manager must be able to create multiple partitions from an underlying 
physical storage device for use by higher layers.  

- Who needs it:  TDB
- Why do they need it:  TDB   
- When do they need it: TDB
- Who is proposing it: Rohit
- Design suggestions:  TDB 
- Comments: SDH todo: Question for Rohit: please state the requirements here.


### Platform OS Storage Volume Manager Wrapper (8)

This entity is the platform OS encapsulation of the storage volume manager.


`REQ_CFSTORE_MBEDOS_20161012_03`: `storage_volume_manager.h` API mbedOS C++ wrapper

- Who needs it:  TDB
- Why do they need it:  TDB   
- When do they need it: TDB
- Who is proposing it: TBD
- Design suggestions:  TDB 
    - API should be synchronous only. Asynchronous interface should not be exposed.
- Comments: Question for SamG: Does this API exist in mbedOS? If yes the please detail requirements.


### Storage Volume Manager API(`Storage_VM.h`) (9) 

This entity is the portable API for the Storage Volume Manager. 


### Flash Journal (`Flash_Journal.h`) API (10) 

This entity is the portable API for the Flash Journal.


### Platform OS Storage Volume Manager/Flash Journal Wrapper API (11) 

This entity is the platform OS encapsulation of the storage volume manager and flash journal APIs.


### Configuration Store (12)  

This entity is the implementation in C of the configuration store. 


`REQ_CFSTORE_MBEDOS_20160810_11`: CFSTORE/Storage Configurability: CFSTORE must have a `DEVICE_STORAGE_CONFIG_HARDWARE_MTD_ASYNC_OPS` compiler switch to select between 
the synchronous or asynchronous modes of the CFSTORE software stack.

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Simon Hughes
- Design suggestions:   
- Comments:   


`REQ_CFSTORE_MBEDOS_20160810_12`: KV Paging (Remove SRAM Limitation)
Implement scheme so that the size of RW CFSTORE managed flash is not limited by the available heap SRAM. 
Current implementation has realloc()-ed heap slab for all KVs present in memory

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Simon Ford, Sam Grove, Simon Hughes, Milosch Meriac 
- Design suggestions:   
- Comments:   


`REQ_CFSTORE_THREAD_20160811_01`: CFSTORE supports requirements for Interrupt Latency Less ~50us

- Who needs it: Kevin Bracey, Thread Team, mbed Cloud Client  
- Why do they need it: to overcome flash Read While Write Limitation, and write/erase times 
- When do they need it: 
- Who is proposing it: 
- Design suggestions:   
	- Solution is the use off-chip storage e.g. SPI SDCard. 
- Comments:   
    - SDCARD_PRIORITY++.


`REQ_CFSTORE_UPDATE_SRV_20161012_03`:  Store large firmware objects (50kB - 1MB) 

- Who needs it:  Update client.
- Why do they need it: Update client needs to store and read firmware objects.  Bootloader needs to read and write firmware images.  
- When do they need it:  R1.1 when Update is launched
- Who is proposing it: Marcus C
- Design suggestions: Out-of-order write capability would be useful, for e.g. broadcast updates.  
  Ability to search for an object and see available objects is necessary.  Ability to write over 
  the main application is essential, which means this solution needs to be available to the bootloader.  
- Comments:   
	- Solution is the use off-chip storage e.g. SPI SDCard. SDCARD_PRIORITY++.


`REQ_CFSTORE_PROV_CLIENT_20161018_03`: Factory-Reset Support (Non-Deletable, Read-Only Data Attributes)  

- What is the requirement: Back-to-factory-reset support – keep a copy of certain CFSTORE entries in a way 
that allows going back to them upon request. Request should be protected so as only specific entities 
can ask for it. However, not all CFSTORE entries should be restored – some should persist this operation 
(most notably, those that are roll-back protected – otherwise, you get a bricked device).
- Who needs it: mbed Cloud Client (Provisioning)
- Why do they need it: Factory reset is a required operation on any device.
- When do they need it:  As soon as possible.
- Who is proposing it: Nimrod
- Design suggestions: Keep a shadow of certain CFSTORE entries in a secure manner (rollback protected itself). Restore from it as needed. uVisor for access control.



### CFSTORE CMSIS C-HAL Interface (13)

This entity is the portable CFSTORE interface (CMSIS aligned C-HAL).


`REQ_CFSTORE_MBEDOS_20160810_04`: CFSTORE CMSIS-Driver API. Consistent with mbed-os practices? Keep/modify/change/encapsulate?
drop alignment with CMSIS API specification?

- Who needs it: TBD  
- Why do they need it:    
- When do they need it: TDB
- Who is proposing it: Milosch Meriac
- Design suggestions:   
	- Simon Hughes: The API hasnt been accepted by Kiel. A requirement for a mux/demux layer exists. The need for the mux/demux layer
	  can be removed if CMSIS alignment is relaxed and each method has a context argument. This will simplify the
	  portable software stack.
- Comments:   


`REQ_CFSTORE_MBEDOS_20160810_09`: CFSTORE/Storage Configurability: Flash Volume/Partition Configuration
Currently system configuration is for K64F using first flash bank for code image, second for CFSTORE data. This should be abstracted/generalised (i.e. being able to apportion flash storage areas to code and data irrespective of underlying flash components) and made configurable at a system level, or at least at a higher level than the storage driver.

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments:   

  
### Configuration Store (CFSTORE) Mux/Demux (14)

This entity multiplexes/demultiplexes the calls from multiple overlying CFSTORE clients 
to the single user context of the underlying CMSIS layer. 
  

### CFSTORE C-HAL2 Mux/Demux Interface (15)

This entity is the portable API to the CFSTORE Mux/Demux.

`REQ_ENG_MUX_DEMUX_0001`: The C-HAL2 API MUST provide the C-HAL API (single client
no context, CMSIS aligned API) to a number of overlying clients. The mbed Cloud client 
subsystems MUST either all use the synchronous mode of the API, or the asynchronous mode 
of the API. The possibility of different modes for different subsystems
operating concurrently is not supported.


`REQ_CFSTORE_CHAL2_20161012_01`:  Support multiple, mutually-unaware users.  

- Who needs it:  Update client.  mbed OS users who want to use the storage abstraction and also use mbed Cloud Client,
- Why do they need it: Update Client, Provisioning Client, Connector Client, Thread stack and potentially the user application all want to use the storage system, and they cant reasonably be expected to coordinate their use of it at design time.
- When do they need it:  Update Client needs it when Provisioning launches its asset-provisioning capability in R1.2 (15 Feb 2017) so that it can access Provisioned keys.
- Design suggestions: In CFSTORE this could mean adding support for multiple users of the asynchronous API.


`REQ_CFSTORE_CHAL2_20161012_02`:  An asynchronous API.  

- Who needs it: mbed Cloud Client. 
- Why do they need it: So that read and write operations dont block execution in single-threaded environments.
- When do they need it:  Whenever mbed Cloud Client needs to run in single-threaded environments (Roni Ds "constrained" devices)
- Who is proposing it: Marcus C
- Design suggestions: 


`REQ_CFSTORE_CHAL2_20161012_08`: Provide a portable key-value store abstraction.

- Who needs it:PAL team.
- Why do they need it: So that environments with a key-vale store can supported by PAL with minimal porting work  / So that they do not need to further abstract the mbed OS storage system API.  
- When do they need it:  When they port mbed Client to non-mbed OS environments.  R1.2. 
- Who is proposing it: Amyas 
- Design suggestions:  


### `REQ_CFSTORE_CHAL2_20161012_07`: Provide a portable key-value store.

- Who needs it:PAL team.
- Why do they need it: So that environments without a key-vale store can easily import this one.
- When do they need it:  When they port mbed Client to non-mbed OS environments.  R1.2. 
- Who is proposing it: Amyas 
- Design suggestions:  
- Comment: accept requirement. 

                                                                       
### Security Layer (uvisor) (16)

This entity is used to provide security for lower layers of the software stack.

`REQ_CFSTORE_MBED_CLIENT_20160810_01`: mbed Connector Client MUST use provided secured functionality (of mbed OS)
 for certificate storage.


`REQ_CFSTORE_PROV_CLIENT_20160811_03`: Secure Config Store
Provisioning + PAL: Secured (encrypted) CFSTORE using device RoT

- Who needs it: PAL, Provisioning Team  
- Why do they need it:   
- When do they need it:
- Who is proposing it: 
- Design suggestions:   
- Comments:   


`REQ_CFSTORE_PROV_CLIENT_20161018_01`: Granualar & Controlled Access to Secure Data  

- What is the requirement: Security. Information written to CFSTORE should not be 
accessible by anyone aside of the entity that wrote it (or, more granular control, 
but that’s not required for Provisioning), even if an attacker gained access to the 
device, or gained physical control over the device. [this requirement is covered in 
the links, but I decided to mention it anyway because it is really cardinal]
- Who needs it: mbed Cloud Client (Provisioning)
- Why do they need it: Provisioning stores sensitive assets on the device, that shouldn’t leak.
- When do they need it:  Today.
- Who is proposing it: Nimrod
- Design suggestions: uVisor + cryptography + a good way to secretly store a device-generated key.


`REQ_CFSTORE_PROV_CLIENT_20161018_02`: Per-Data Attribute and Per-Operation Roll-back Protection  

- What is the requirement: Roll-back protection per entity and per operation. 
It should be possible to ask for a specific file/key to be roll-back protected, 
only for a specific write operation (that is, in general, writes aren’t roll-back protected, but this specific write is).
- Who needs it: mbed Cloud Client (Provisioning)
- Why do they need it: This is useful because roll-back protection is expensive (burns a fuse), 
and not all data written is created equal. Sometimes, it may be desirable to update a certain 
asset not caring that the value be rolled-back later (an upgrade is performed, but a down-grade 
isn’t a security or otherwise issue), and sometimes a roll-back should be prohibited (this is a 
security update, a rollback would expose the device to attacks).
- When do they need it:  As soon as possible.
- Who is proposing it: Nimrod
- Design suggestions: -



### Platform-OS CFSTORE Wrapper (17)  

This entity provides the CFSTORE integration with the Platform OS. 


`REQ_CFSTORE_MBEDOS_20160810_01`: CFSTORE mbedOS C++ wrapper support

- Who needs it: mbedOS
- Why do they need it: CFSTORE functionality is presented seamlessly in mbedOS for consumption by partners. 
- When do they need it: TBD 
- Who is proposing it:  Sam Grove, Simon Hughes, Marcus Shawcroft 
- Design suggestions: 
    - API should be synchronous only. The CFSTORE C-HAL asynchronous interface should not be exposed.
    - The CFSTORE should be represented as a file system.
- Comments: This requirement has been copied from 16Q3 planning spreadsheet (see CFSTORE roadmap doc for reference).


`REQ_CFSTORE_MBEDOS_20160810_05`: File system support

- Who needs it: mbedOS  
- Why do they need it: TBD   
- When do they need it: TBD
- Who is proposing it: Sam Grove
- Design suggestions:   
- Comments: This requirement needs further definition.


`REQ_CFSTORE_MBEDOS_20160810_06`: 16.07: MUST Establish internal policy that we only accept ASYNC capable storage drivers into mbed-os (MJS)

- Who needs it: mbedOS, mbed Cloud (for portability of software stack).  
- Why do they need it: composability of system. If one client uses async mode then it has to be present in all underlying drivers.  
- When do they need it: TBD
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments:   

### CFSTORE C-HAL3 Interface/PAL (18)

This entity is the portable interface to the secure CFSTORE. It is thought to be synonymous with the 
Portable Abstraction Layer (PAL)


`REQ_CFSTORE_PROV_CLIENT_20160811_04`: PAL (Portability Abstraction Layer) Support
Is CFSTORE going to be part of the PAL? Will Provisioning Team implement their own "portable" version 
of CFSTORE?

- Who needs it: Provisioning,   
- Why do they need it: to port to multiple platform OSs
- When do they need it:
- Who is proposing it: 
- Design suggestions:   
- Comments:  


### OS CFSTORE API (19)

This is the platform OS encapsulation of CFSTORE.


### mbed Cloud Client (20)

This entity is the integration of the provisioning client, mbed client and the update service, each sharing a single 
thread using the CFSTORE async callback programming model using C. 

`REQ_CFSTORE_MBEDTLS_20160811_01`: mbed Cloud Client Supports NV Storage of mbedTLS Entropy Seeds

- Who needs it: mbedTLS  
- Why do they need it:  to store entropy seeds  
- When do they need it: TBD
- Who is proposing it: Simon Butcher
- Design suggestions: 
- Comments:   


`REQ_CFSTORE_PROV_CLIENT_20160811_01`: Image sizes must be larger than 512kB (SPI SDCARD Support)

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: 
- Design suggestions:   
- Comments:   

`REQ_CFSTORE_UPDATE_SRV_20161012_04`: Store certificates (~1kB)

- Who needs it: Update client.
- Why do they need it: Update needs to store certificates with which to validate signatures of firmware.
- When do they need it: Update Client needs it when Provisioning launches its asset-provisioning capability 
  in R1.2 (15 Feb 2017) so that users can store certificates directly in the same place that Provisioning 
  would keep them, so that Client only has to look in one place..
- Who is proposing it: Marcus C
- Design suggestions: Certificates do not have to be kept secret, but in a uvisor-enabled environment 
  they should be writable by only the storage system.
- Comment: suggest deleting as covered by other requirements


`REQ_CFSTORE_UPDATE_SRV_20161012_05`: Store secrets securely (16B - 1kB)

- Who needs it: Update client.
- Why do they need it: Proposed mechanisms for delivering encrypted firmware, and for encrypting firmware that is stored on external Flash, use symmetric keys.
- When do they need it:  Firmware encryption is road-mapped for R1.2 (15 Feb 2017).  
- Who is proposing it: Marcus C.
- Design suggestions: Security in this case means a uvisor-enabled environment that does not allow other parts of the application than the mbed Cloud Client to access the secrets.  
- Comment: suggest deleting as covered by other requirements


# Rejected Requirements

`REQ_CFSTORE_MBEDOS_20160810_08`: 16.09: MUST/SHOULD Work on SW stack size reduction. (MJS)

- Who needs it:  
- Why do they need it:   
- When do they need it:
- Who is proposing it: Marcus Shawcroft
- Design suggestions:   
- Comments: SDH todo: discuss with Marcus.   


`REQ_CFSTORE_UPDATE_SRV_20161012_09`: Provide a portable filesystem abstraction.

- Who needs it:PAL team.
- Why do they need it: So that environments with a filesystem can be supported by PAL with minimal porting work / So that they do not need to further abstract the mbed OS storage system API.  
- When do they need it:  When they port mbed Client to non-mbed OS environments.  R1.2. 
- Who is proposing it: Amyas 
- Design suggestions:  This is only necessary if it is decided that a filesystem is the best solution to storing firmware objects. 
- Comments: SDH todo: discuss with Amyas. CFSTORE portable APIs can be used to implement filesystem abstractions but this is conceptually part of the platform OS wrappers.
  covered by `REQ_CFSTORE_MBEDOS_20160810_05` for example.   



# Notes for action at next arc meeting:

- `REQ_CFSTORE_THREAD_20160811_02`. requirement not specificly a storage requirement. Propose deleting or respecifying into specific requirement.

- `REQ_CFSTORE_THREAD_20160811_03`. requirement not specificly a storage requirement. Propose deleting or respecifying into specific requirement.

- `REQ_CFSTORE_THREAD_20160811_04`. requirement not specificly a storage requirement. Propose deleting or respecifying into specific requirement.

- `REQ_CFSTORE_MBEDOS_20161012_01`. Ask SamG. If he doesnt want this wrapper then remove requirement. 

- `REQ_CFSTORE_UPDATE_SRV_20161012_10` accept this as a general engineering requirement.

- `REQ_CFSTORE_MBEDOS_20161012_04`. accept this as as a general engineering requirement.

- `REQ_CFSTORE_MBEDOS_20160810_07`. consequence of `REQ_CFSTORE_MBEDOS_20161012_04` and not specifically a requirement.
 hence, propose removing.

- `REQ_CFSTORE_MBEDOS_20160810_03`. Ask SamG. what do you want to do here? 

- `REQ_CFSTORE_PROV_CLIENT_20160811_02`. Ask SimonF. Propose accepting as general product requirement. 

- `REQ_CFSTORE_MBEDOS_20161012_02` Ask SamG for mbedOS. Ask MarcusS for other platform OSs. Equally applicable to Zephyr or a.n.other platformOS.

- `REQ_CFSTORE_SVM_20161013_01`. Ask RohitG/MarcusS? propose accepting as SVM requirement. 

- `REQ_CFSTORE_MBEDOS_20161012_03`: Ask SamG for mbedOS. Ask MarcusS for other platform OSs. Equally applicable to Zephyr or a.n.other platformOS.

- `REQ_CFSTORE_MBEDOS_20160810_11`. Ask SamG/RohitG/SimonH/MarcusS/. suggest removing this requirement as should be superceded by requirement that all stroage drivers support async mode and there isnt a sync mode that can be switched on via compilation.

- `REQ_CFSTORE_MBEDOS_20160810_12`. propose accepting as general engineering requirement for cfstore.

- `REQ_CFSTORE_THREAD_20160811_01`. Ask all other stakeholders and MarcusS/SimonF to arbitrate to resolution. propose accepting this requirement and progressing with off-chip storage solutions.

- `REQ_CFSTORE_UPDATE_SRV_20161012_03`. propose remove. covered by `REQ_CFSTORE_PROD_GEN_0005`.

- `REQ_CFSTORE_PROV_CLIENT_20161018_03`. propose accepting in part. Make engineering requirements for 
 Non-Deletable KVs, Read-Only Data KVs, rollback protected KVs in the CFSTORE i.e. CFSTORE needs to provide primitives which permit something built on-top of cfstore to implement the factory reset behavior. Partly covered by `REQ_CFSTORE_PROD_SEC_0004`, which should be enhanced with discussion and usecase information. 

- `REQ_CFSTORE_MBEDOS_20160810_04`. propose removing this requirement i.e. CFSTORE-CHAL no longer has to conform to CMSIS alignment.

- `REQ_CFSTORE_MBEDOS_20160810_09`. Ask stakeholders. propose accepting as engineering requirement for general configurability of 
 portable software stack.

- `REQ_ENG_MUX_DEMUX_0001` propose accept this requirement.

- `REQ_CFSTORE_CHAL2_20161012_01`. duplicate. merge with `REQ_ENG_MUX_DEMUX_0001` 

- `REQ_CFSTORE_CHAL2_20161012_02`. duplicate. merge in with superceded requirement of `REQ_CFSTORE_MBEDOS_20160810_11`.
 
