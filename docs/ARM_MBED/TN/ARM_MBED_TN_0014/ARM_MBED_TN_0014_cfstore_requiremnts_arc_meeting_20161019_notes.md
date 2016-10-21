# Configuration Store Requirements ARC Meeting 21061019
Author: Simon Hughes
Document Version: 0.02
last updated: 20161021

# Overview

Notes/thoughts captured from:

- ARC meeting of 20161019
- follow up conversation with Rohit, Marcus, SimonF, SDH of 20161020 


# Conclusions

### Primary Conclusions:

- Decisions are required to decouple the multiple, interconnected CFSTORE problems into pieces that can be progressed independently. 
  The "decisions" tentatively agreed are as follows:
- Agree CMSIS storage driver simplifications with Kiel (async mode only, callback notifier invoked for API method invocation).
- Progress/standardize mbed-os block storage API so that multiple NV storage backends can be presented with a standardized
  interface within mbed-os.   
- Adopt NVStore concept for "Fixed Storage". Use it to store a key.
- CFSTORE is secure "Updatable Storage". 
- Decouple CFSTORE from the underlying CMSIS storage driver to make CFSTORE truly portable. Provide porting guide. Implement example on mbed-os 
- Bottom out important Provisioning use cases for secure storage of keys/certs.
- Implement CFSTORE C-HAL2 Mux/Demux API for supporting multiple overlying clients. API will be async as per C-HAL.
- Implement PlatformOS CFSTORE Wrapper (17) for mbed-os as FileSystemLike C++ API.
- CFSTORE Remove SRAM Limitation
- Iterate cfstore requirements doc to next version including all clarifications.
- Priorities for CFSTORE
    - multiuser support i.e. C-HAL2 Mux/Demux API implementation
    - removing SRAM limitation.
    - mbedOS C++ wrapper (filesystem interface).


### Secondary Conclusions:

- mbed-os File system mappable to CFSTORE C-HAL/C-HAL2/C-HAL3 APIs but not perfect fit. 
- POSIX file system API not easily mappable to CFSTORE C-HAL/C-HAL2/C-HAL3 APIs due to:
    - file size specified at create time, but can grow.
    - key security descriptor. 
- "Portable-Writable-Storage" entity in portable stack for "Writeable Storage". Will map to filesystems on mbedOS. 
- The CMSIS storage driver problems is a platformOS problem.
  
# Key Points

- CMSIS storage driver interface. 
 - a block type interface specialised for flash striving for portability/reusability benefits.
 - Conceptually, its desirable for an OS to have a unifrom, generic block interface to storage which 
   encapsulates the specifics of the storage back-end. If a well defined interface exists, an arbitrary 
   file system can be bound to it, for example. 
 - The concept works for on-chip flash storage i.e. the mcu vendor has to write a driver for it
 - The concept doesnt work so well for off-chip storage (see next point) 
 - The mtd-sdcard CMSIS storage driver implementation for off-chip SDCard
   depends on the bus technology (e.g. SPI) used to connect the external flash. Bus (SPI) driver is 
   provided by mcu vendor for platformOSs, and hence this creates an implicit binding between the 
   CMSIS storage driver and the bus driver. There is no standardized way of coupling the 2, inhibiting 
   portability. 
 - This is one of the main reasons the CMSIS Driver standardisation effort has largely been 
   unsuccessful, whereas the CMSIS Core standardisation effort has been more successful.
 - This suggests the CMSIS Storage Driver interface is insufficient but needs a richer, architected stack
   which allows different bus drivers to be bound to the storage driver.
 - Conclusion: the storage driver problem is a platformOS problem.
 - A clean storage driver interface doesnt exist in mbedOS at the moment. Explore sdcard, 
   usbhost and semi-hosting interfaces which appear to provide block storage.
   
- CFSTORE upper edge. the c-hal3 interface. 
    - This cant easily be a file system interface because
        - fopen() doesnt specify upfront the size that the file will be for the 
          rest of its life, and there is no easy way for the file interface
          to specify this. fioctl()-like thing may be able to specify size 
          after the fact, but this is unacceptbly clunky.
        - there isn't the concept of file security traits (key descriptor) with where the key 
          can have different security levels.
    - however, could me made to look similar e.g. optionally have a default KV size of 32 bytes but
      let the size be set by the size of the first write (permissible with a NULL buffer).
    - but, what about the kdesc?  
      
  
- CFSTORE lower edge (call it C-HAL0). Better define a bottom edge for CFSTORE because:  
 - can make it a block interface for simplicity (read, write, erase, commit, etc).
 - decouples CFSTORE from storage back end (i.e. flash journal and SVM) and the associated portability
   problems (which may be solved in time but not soon).
 - CFSTORE trusts that the storage is secure i.e. at the same of better Security Level (see later for 
   notion of Security Level).   
 - Portability. Everything above C-HAL0 is then portable and part of mbed cloud stack. Porters map this
   interface onto some block NV storage API available on their platform. 
 - simple and clean.
 - Consequence: CFSTORE needs a cypher layer for encrypting/decrypting blocks before passing to the storage driver.  
    
    
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
    |  | xxxxxxxxxxxx  |  |  Update Service |  | xxxxxxx     |          |                               
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
                                                                            
    ------ CFSTORE CMSIS C-HAL Interface (13) ---------------------------  
                                                                           
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  
    |          Configuration Store (12)                   |  
    |                                                     |  
    |                                                     |  
    |                                                     |  
    |-----------------------------------------------------|  
    |     Cypher Function to Encode/Decode Blocks         |  
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  

    ---- CFSTORE C-HAL0 API, Portable Block Storage Interface (21) ----------------------------------------------------    
                                                                             +-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+ 
                                                                             | Platform-OS           |    | NVStore   | 
                                                                             | Storage Wrapper       |    |           | 
                                                                             | (24)                  |    |           | 
                                                                             +-+-+-+-+-+-+-+-+-+-+-+-+    +-+-+-+-+-+-+ 

                                                                             -- OS Storage API (23) --

                                                                             +-+-+-+-+-+-+-+-+-+-+-+-+
                                                                             | Platform-OS           |
                                                                             | Storage Driver        |
                                                                             | (22)                  |
                                                                             +-+-+-+-+-+-+-+-+-+-+-+-+

    SW
    -------------------------------------------------------------------------------------------------------------------
    HW

```

    
    
Design Assumptions:

- There will be platforms where CFSTORE cannot use on-chip NV storage e.g.:
    - There is no on-chip NV storage
    - On-chip NV storage is present but ultra-limited e.g. only sufficient to store 128bits for a key.
    - On-chip NV storage is present but extremely-limited e.g. less than a sectors worth of 
      storage and/or has to be stored in part of the firmware image.
    - On-chip NV storage is present but very-limited e.g. can be stored independently of the 
      firmware image but the available storage is so small such that the CFSTORE code/data/SRAM 
      overhead of CFSTORE cannot be justified.
- In these circumstances, 
    - the system still needs to be able to store/recover data from on-chip flash e.g. 
      data from a firmware image. 
    - if used, CFSTORE needs to able to store data securely off-chip, and CFSTORE needs a cypher 
    key for this.
     
- New concept of the NVStore which always exists on every platform (mbedOS, zephyr, etc). 
  - NVStore for "fixed storage" data (fixed storage term defined by SF ppt P3 
    `mbedOSStorageRequirements_simon_ford_20161020.pdf`).
  - NVStore MAY contain provisioned data during manufacture/post-manufacture programming
    e.g. typically MAC address.
  - NVStore MAY contain a key. 
  - info: this NV store is very much like a data structure has exceptionally low overhead for access
  - info: this is where the key patched into the firmware image is stored and recoverable from
  - System Architecture has notion of different Security Levels (Security Levels (1, 2) defined on P6 & P7 
    `mbedOSStorageRequirements_simon_ford_20161020.pdf`).
        - Security Level 0: most secure level.
        - Security Level 1: next most secure level
        - Security Level i: the i-th security level
    - The system designer defines what the different security levels mean and associates them with a specific
      NVStore/CFSTORE usage model. 
        - example 1:  
            - Security Level 0: code/data contained within SoC boundary are at SL0. (used for NVStore).
            - Security Level 1: code/data visible outside of SoC boundary are at SL1 (used for a CFSTORE with offchip back-end).
        - example 2:
            - Security Level 0: key stored in fuse/TPM, are at SL0 (used for NVStore).
            - Security Level 1: code/data contained within TrustZone are at SL1 (security context used for CFSTORE code/implementation data structures with CFSTORE on-chip, unencrypted data back-end). 
            - Security Level 2: code/data contained within SoC boundary are at SL2.
            - Security Level 3: code/data visible outside of SoC boundary are at SL3 (used for a CFSTORE off-chip, encrypted data back-end).
            
    - The Security Level of the NVStore is greater than or equal to the security 
      level of the CFSTORE. 
        - let `SL_nvstore` = numeric value of security level for NVStore  
        - let `SL_cfstore` = numeric value of security level for CFSTORE
        - then   `SL_nvstore <= SL_cfstore` 
 - If the NVStore key is present (non-zero) CFSTORE will use the key to encrypt/decrypt
   blocks passed over the C-HAL0. 
 - CFSTORE now includes an internal cyphering function so that CFSTORE data can be encrypted 
   using the NVStore key (if present) and stored on external NV storage devices.   
 - CFSTORE is now for "Updateable" Data objects see SF ppt for definition.
 - CFSTORE NV Interface `nvstore_get_key()` is part of CFSTORE-C-HAL0. 
    
  
- CMSIS drivers and Kiel
   - look at CMSIS flash driver. keys design decisions:
        - stateless
        - no threading concept (single execution context)
        - exposes a capabilities interface which reports whether the driver is a sync or async mode driver.
   - revisit CMSIS storage driver
        - drivers should only expose 1 API which is an async API. Drivers can implement the asynchronous API
          with function methods that always complete synchronously (if the implementer so wishes), 
          by calling the callback notifier in the context of executing the original API call (rather than returning
          first) 
        - remove the sync bit in GetCapabilities CAPABILITIES structure.
        - clarify the interface so that the callback notifier is invoked even when the API call completes
          all processing synchronously.
        
- CFSTORE Remove SRAM Limitation
    - off-chip support will provide large storage areas (>> available SRAM). 
    - SRAM limitation means these cant be accessed with current SRAM limitation.     
    - hence remove SRAM limitation.
