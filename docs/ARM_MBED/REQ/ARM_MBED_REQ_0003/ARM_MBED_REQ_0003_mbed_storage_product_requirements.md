# mbed Storage Product Requirements

Contributors: Daniel Benor, Marcus Chang, Simon Ford, Sam Grove, Simon Hughes, Erez Landau, Marcus Shawcroft

Author: Simon Hughes

Document Version: 0.03

Date: 20161209

Status: DRAFT

# <a name="introduction"></a> Introduction

This aim of this document is to articulate the mbed storage product requirements.

# Overview 

The mbed storage endpoint functionality is envisaged to be partitioned into to the following functional components:

- RoTStore. This is an "updatable", internal (on-chip, ~16kB data) storage facility for the (128bit) root of trust key, and other minimal functionality that can be implemented on 99% of IoT devices.
- Filesystem Store (FAT32). This is a "read-write" general purpose storage facility on external SDCards, for example.
- High Integrity Filesystem (HIFS). This is a "read-write" general purpose storage facility with robustness enhancements principally for SPI-NOR and SPI-NAND support, for example.
- SMARTFS. This is a lightweight read-write restricted-use storage facility e.g. for certificates, keys and state data held on internal flash.

The feature cut between above components is described in the table below.

**Storage Component Feature Analysis**

<table>
<thead>
<tr>
  <th>Feature</th>
  <th>RoTStore</th>
  <th>FAT32 FS</th>
  <th>High Integrity FS (HIFS)</th>
</tr>
</thead>
<tbody>
<tr>
  <td>Security</td>
  <td>Is secure and may run in a security context (uvisor)</td>
  <td>Insecure</td>
  <td>Is secure and should run in a security context (uvisor)</td>
</tr>
<tr>
  <td>Security</td>
  <td>Stores root of trust key</td>
  <td>Does not store root of trust key</td>
  <td>Does not store root of trust key</td>
</tr>
  <td>Security</td>
  <td>May not be encrypted e.g. when stored in internal flash.</td>
  <td>Must not be encrypted.</td>
  <td>May be encrypted if held on off-chip storage.</td>
</tr>
<tr>
  <td>Endurance</td>
  <td>Written 10-100 times during product lifetime (1 time/year-1 time/month)</td>
  <td>Written 10^5-10^6 times during product lifetime (10+ times/day)</td>
  <td>Written 10^5-10^6 times during product lifetime (10+ times/day)</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td>Should be on-chip</td>
  <td>Should be off-chip</td>
  <td>Should be off-chip</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td>On-chip is NOR flash with 
  NAND like restrictions due to flash memory controller.</td>
  <td>A key use case is SPI NOR flash as the storage backend.</td>
  <td>A key use case is SPI NOR flash as the storage backend.</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td></td>
  <td>A key use case is SPI NAND flash as the storage backend.</td>
  <td>A key use case is SPI NAND flash as the storage backend.</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td></td>
  <td>A key use case is SPI SDCard/MMC as the storage backend.</td>
  <td></td>
</tr>
<tr>
  <td>Wear Levelling</td>
  <td>Not required due to small number of write/erase operations</td>
  <td>Not required due to transparent implementation on SDCard</td>
  <td>Required due to large number of writes/erase operations</td>
</tr>
<tr>
  <td>EEC</td>
  <td>Error Correction Codes (ECC) not required due to stability of storage</td>
  <td>Not required due to transparent implementation on SDCard</td>
  <td>Error Correction Codes (ECC)  required due to instability of NAND storage (NAND is a key use case).</td>
</tr>
<tr>
  <td>Bad Block management</td>
  <td>Required.</td>
  <td>Not required due to transparent implementation on SDCard</td>
  <td>Required.</td>
</tr>
<tr>
  <td>Robustness against power failures</td>
  <td>Required.</td>
  <td>Not required as difficult/impossible to implement</td>
  <td>Required.</td>
</tr>
<tr>
  <td>Journaling</td>
  <td>May be required for robustness against power failures.</td>
  <td>Not required as should use HIFS for robustness features</td>
  <td>Required for robustness against power failures.</td>
</tr>
<tr>
  <td>Sequential Writes</td>
  <td>NAND: sequential writing may be required (no rewriting of previous journaled entries).</td>
  <td>Not required due to transparent implementation on SDCard</td>
  <td>NAND: sequential writing required (no rewriting of previous journaled entries).</td>
</tr>
<tr>
  <td>API</td>
  <td>API: May be get()/set() interface, or create_key()/encrypt()/decrypt().</td>
  <td>API: Must be the POSIX file interface.</td>
  <td>API: Must be the POSIX file interface.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may be invasive/disruptive to the system.</td>
  <td>Storage operations must not be invasive or disruptive to the system.</td>
  <td>Storage operations must not be invasive or disruptive to the system.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may disable interrupts (causing high interrupt latency).</td>
  <td>Storage operations must not disable interrupts.</td>
  <td>Storage operations must not disable interrupts.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may require a system reboot after an operation</td>
  <td>Storage operations must not require a reboot after an operation.</td>
  <td>Storage operations must not require a reboot after an operation.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may use in-application programming techniques (use of RAMFUNCS).</td>
  <td>Storage operations should not be use in-application programming techniques.</td>
  <td>Storage operations should not be use in-application programming techniques.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Concurrent storage operations may have a very small number of file (or file equivalent) entities open concurrently e.g. maximum 2.</td>
  <td>Concurrent storage operations may have a small number of file (or file equivalent) entities open concurrently e.g. maximum 10 (configurable).</td>
  <td>Concurrent storage operations may have a small number of file (or file equivalent) entities open concurrently e.g. maximum 10 (configurable).</td>
</tr>
<tr>
  <td>Portability</td>
  <td>Required. Must be capable of being ported to 99% of all IoT devices.</td>
  <td>Required. Must be capable of being ported to 99% of all IoT devices.</td>
  <td>Required. Must be capable of being ported to 99% of all IoT devices.</td>
</tr>
  <td>Portability (Minimal Resources)</td>
  <td>Must need minimal system resources so can be implemented on the smallest of devices e.g. 2-4kB SRAM and 10-15kB code flash.</td>
  <td>May require more than minimal system resources e.g. >4kB SRAM, SRAM footprint scaling linearly with store size and number of files,  >>15kB code flash.</td>
  <td>May require more than minimal system resources e.g. >4kB SRAM, SRAM footprint scaling linearly with store size and number of files,  >>15kB code flash.</td>
</tr>
<tr>
  <td>mbedOS Native Support</td>
  <td>Required.</td>
  <td>Required.</td>
  <td>Required.</td>
</tr>

</tbody>
</table>


# Product Requirements On OS Driver Architecture

## Background Information 

This section contains explanatory information for the purposes of communicating the product requirements later in the document. It's not intended to define the solution architecture. 

The following terminology/acronyms will be used:

- ARM-SW. Software component implemented by ARM, and an API specified by ARM.
- SiP-SW. Software component implemented by Silicon Partner.
- FMPV-SW. Software component implemented by Flash Memory Part Vendor.
- OTHER-SW. Software component implemented by mbed community, or 3rd party ecosystem vendor.

![alt text](pics/ARM_MBED_REQ_0003_product_requirements_on_os_components.jpg "unseen title text")
**Figure 1. OS Driver Architecture for describing product requirements on silicon partner and flash memory vendor contributed software components.**


The figure above shows the following entities :

- (1) RoTStore API (ARM-SW). This is the Root of Trust (RoT) storage interface to RoTStore and other RoT related functionality. 
    - The API is supported by mbedOS and is part of the Platform Abstraction Layer (PAL) specification. 
    - The API may be a get()/set() interface allowing key retrieval, or it may provide a block encrypt()/decrypt() interface so once a key has been generated/provisioned, the key is never provided to clients.
- (2) POSIX File System API (ARM-SW). This is the general purpose POSIX file system API (or a subset thereof) which will be used for accessing the file system components.
- (3) RoTStore (ARM-SW). This is the component for storing the root of trust key and implementing the RoTStore API (1). 
- (4) FAT32 Filesystem (ARM-SW). This is the "read-write" filesystem for mounting of SDCard backends (with transparent bad block management, wear-levelling and ECC).
- (5) High Integrity Filesystem (ARM-SW). This is the "read-write" filesystem for mounting on SPI-NOR or SPI-NAND backends. The FS includes robustness features, bad block management, wear-levelling and ECC for example.
- (6) Filesystem Encryption/Decryption Layer. 
    - This takes blocks from the overlying filesystem and encrypts them before storing the same size block on the flash. 
    - This component retrieves requested (encrypted) blocks from the flash, decrypts and forwards them to the filesystem. 
    - This component will use a key in the RoTStore for cryptographic operations.
- (7) Block Store API(ARM-SW). This API is the same as (9) Block Store API but appears here as the top edge of the Filesystem Encryption/Decryption Layer. See (9) and [Appendix A] for more details.
    - `blkstr_write_page_fn` encrypts the block and forwards to the underlying Block Store API `blkstr_write_page_fn` for storing on flash.
    - `blkstr_read_page_fn` retrieves the encrypted block using the underlying Block Store API `blkstr_read_page_fn` method, decrypts and forwards to the overlying filesystem.
- (8) Other Filesystem (Community)(OTHER-SW). This is another filesystem that can be implemented by the mbedOS community, or ported by an ecosystem FS provider. 
- (9) Block Store API (ARM-SW). This provides a unifying interface for the underlying internal flash driver and SPI protocol drivers. See [Appendix A] for more details.
- (10) OS Block Store Glue Code (ARM-SW). This component provides the unifying block store interface over:
    - The internal flash storage driver (~CMSIS-Flash or CMSIS-Driver).
    - The SPI Flash Memory Protocol Driver.
    - The SDCard Protocol Driver.
- (11) Flash Driver/Storage Driver for SoC internal flash (SiP-SW). This may be the CMSIS-Flash or CMSIS-Storage driver, or an alternative driver model. 
    - Typically internal flash is memory mapped for reading, with a page write/sector erase sematic.
    - The driver will have a method to program (write) a supplied data buffer to a memory address in flash e.g.  `int32_t (*flshdrv_program_data_fn)(uint64_t addr, const void *data, uint32_t size)`. This method is
      used by the bootloader to program a new firmware image into flash, for example.
- (12) SPI Flash Memory Protocol Driver from Company A (FMPV-SW). This driver encapsulates the command specific protocol for the flash hardware part at (18). The driver implement the read/write/erase commands.
- (13) SPI Flash Memory Protocol Driver from Company i (FMPV-SW). The same as (12) but for a different vendor with a different command protocol.
- (14) SDCard Protocol Driver from Company i (FMPV-SW). The same as (12) but for a vendor of SDCard flash hardware parts.
- (15) SPI Bus Virtualisation (ARM-SW). This component owns the SPI bus MISO, MOSI, SCLK and all CS's for devices attached to the SPI bus(es). It virtualises the bus by performing queueing, locking, 
   muxing/demuxing so each of the SPI clients (e.g. (12), (13), (14), (22)) can be virtual SPI masters. The information about the device-tree configuration owned by the SPI bus (i.e. the pins used 
   for the SPI bus, mapping of CS pins to specific devices) is provided by the configuration subsystem. 
- (16) SoC SPI Driver (SiP-SW). This is the SPI bus driver provided by the silicon partner for driving the SoC SPI engines.
- (17) SoC Internal Flash Hardware. This is the on-chip internal flash, used to store firmware image(s) and optionally data.
    - The Bootloader (4) uses internal flash to begin the execution of the active firmware image, and to write a new firmware image (as an Update Client (34) delegate).
    - The internal flash is used by SMARTFS, ConfigFS (EREZFS) and ConfigFS Block Store (EREZBlockStore) ((31), (32), (33)) for file (data) storage.
- (18) Company A SPI NOR/NAND Flash Memory Part Hardware. This is a vendor specific SPI-NOR/NAND part.
- (19) Company B SPI NOR/NAND Flash Memory Part Hardware. This is a vendor specific SPI-NOR/NAND part.
- (20) Company i SPI NOR/NAND Flash Memory Part Hardware. This is a vendor specific SPI-NOR/NAND part.
- (21) A.N.Other SPI Device of arbitrary type sharing the SPI bus with the NOR/NAND flash memory parts. This device may be accessed by the SPI RAW API (22) for example.
- (22) RAW SPI Interface (ARM-SW). This is a direct programmatic interface to a SPI device.
- (23) Board/SoC/Device Configuration System interface (ARM-SW). This provides an API to query the system configuration e.g. which devices are connected to which SoC buses.
- (24) Configuration Subsystem (ARM-SW). This is the OS equivalent of the Linux device tree or Windows device registry which stores the target specific board/bus/device pin configuration and mapping information for (dynamic) bindings.
- (25) SDCard Hardware. This is a vendor specific SDCard part.
- (26)-(29) Unused identifiers.
- (30) mbed Client (ARM-SW). This is the collection of portable components for implementing the provisioning and update services on the user endpoint. The diagram shows the Update Client and the SMARTFS sub-components.
- (31) SMARTFS (ARM-SW). This component contains the mbed Client required functionality not supported by the platform OS standard file system. 
    - It may include encryption, access control and factory reset awareness.
    - It may present a POSIX file system API with overloaded fopen flags for permissions, for example, but other APIs may also be required.
    - It should use features in ConfigFS (EREZFS) (32) if available.
    - It must use the POSIX File API, but it may restrict use of operations to a subset supported by ConfigFS (EREZFS) (e.g. no write seek operation).
- (32) ConfigFS (EREZFS) (ARM-SW). This component contains the mbed Client required functionality not supported by the platform OS standard file system. 
    - It may include key-value store management primitives, and a lightweight in-memory file index directory/cache hash to speed up retrieval of data objects from flash.
    - It should use features in ConfigFS Block Store (EREZBlockStore) (33) if available.
- (33) ConfigFS Block Store (EREZBlockStore) (ARM-SW). This provides an interface with functionality not supported by the platform OS standard Block Store API. 
    - This functionality may include variable length logical storage buffers with transparent wear-levelling, EEC and journaling, for example.
    - The upper interface has been referred to as the i-node API.
- (34) Update Client (ARM-SW). This component manages the downloading of firmware images and their storage in SPI flash ready for the bootloader to program into SoC internal flash.
- (35)-(39) Unused identifiers.
- (40) Bootloader (ARM-SW). Upon power up the bootloader runs the currently active firmware image, and also manages the copying of a new firmware image from SPI flash into SoC internal flash.
    - The internal flash will typically contain a firmware image located at an address known to the bootloader (e.g. `image1_start_addr`).
    - The bootloader uses the POSIX file interface to read a new firmware image from SPI flash.
    - The bootloader writes the new firmware image to internal flash using the Flash/Storage Driver (CMSIS-Flash or CMSIS-Storage?) (11) API method 
      `int32_t (*flshdrv_program_data_fn)(uint64_t addr, const void *data, uint32_t size)`. Note this method allows the bootloader to write the image to a specific address i.e. `image1_start_addr`.
    - As the bootloader is portable across supported platforms then the following must be present on all supported platforms:
        - The Flash/Storage Driver (CMSIS-Flash or CMSIS-Storage?) (11) API.
        - The POSIX File API.
- (41) Soc Core. The core is initialised by the bootloader and then set running the currently active firmware image.

## The Requirements 

Figure 1 is informational to help communicate the following requirements.

- The mbed storage solution must provide a framework so that ARM, silicon partners and flash memory part vendors can contribute software components that work together to provide a complete solution.
- Silicon Partners should provide:
    - A Storage driver for the internal flash. 
    - A SPI bus driver. 
- Flash Memory Part Vendors should provide SPI Flash Memory protocol drivers for their parts.
- SDCard Part Vendors should provide SDCard protocol drivers for their parts.
- ARM should provide the following components and interfaces:
    - RoTStore.
    - Filesystem components e.g.FAT32, HIFS.
    - Filesystem Encryption/Decryption Layer for block storage.
    - Block Store API.
    - SPI Bus virtualisation API.
    - RAW SPI API.
    - Configuration Subsystem component and API.
    - SMARTFS, ConfigFS (EREZFS) and ConfigFS Block Store (EREZBlockStore).
    - Update Client.
    - Bootloader.
- The ecosystem may provide:
    - Alternative file system components. 
    - Alternative file system encryption/decryption components.
    - POSIX File System API.
- The SiP partner or Flash Memory Part Vendor must be able to implement their components (e.g. the internal flash storage driver) with the subset of knowledge known to them. For the internal flash storage driver example, 
  the SiP will not know exactly how the OEM will partition internal flash for use, but rather the driver model must permit this flexibility. 
- The driver model must constrain the environment for implementation e.g. a portable, single thread of execution, no locking or synchronisation primitives used inside the driver.
- Where relevant, the driver models must alignment with other important ARM standards e.g. CMSIS-Driver specifications, so that SiPs/FMPVs are required to implement only one driver for mbedOS and CMSIS-RTOS, for example.
- SMARTFS, ConfigFS (EREZFS) and ConfigFS Block Store (EREZBlockStore) are required to store the data items with the sizes and update frequencies documented in [Appendix B](#appendix-b-smartfs-storage-requirements)

# Appendices

## <a name="appendix-a-sketch-of-block-store-api"></a> Appendix A: Sketch of Block Store API

A typical block store API would include the following operations:

- `int (*blkstr_write_page_fn)(struct dev_t *dev, int pageId, char* data, size_t len, other params)`. Write a page (chunk of data e.g. 512bytes) within a block (e.g.4kB sector) where the offset is specified by the pageId.
- `int (*blkstr_read_page_fn)(struct dev_t *dev, int pageId, char* data, size_t len, other params)`. Read a page (e.g. 512bytes) from a block where the offset is specified by the pageId.
- `int (*blkstr_erase_block_fn)(struct dev_t *dev, int blockId)`. Erase the block i.e. the sector.
- `int (*blkstr_mark_bad_block_fn)(struct dev_t *dev, int blockId)`. Mark the whole block (i.e. sector) identified by the blockId as bad i.e. put identifying code in sector or OOB area.
- `int (*blkstr_init_fn)(struct dev_t *dev)`. Initialise use of device.
- `int (*blkstr_deinit_fn)(struct dev_t *dev)`. Deinitialise use of device.


## <a name="appendix-b-smartfs-storage-requirements"></a> Appendix B: SMARTFS Storage Requirements

The SMARTFS storage requirements can be enumerated as follows:

- Certificates. 
    - The individual certificates are ~700-1400 bytes long.
    - A chain of certificates is typically 4kB in size.
    - The system is required to store ~40 certificates and hence given the certificate sizes above, approximately 64kB of storage is required.
    - The certificates will be updated infrequently, ~1-3 times/year. This places a low endurance requirement on flash storage.
- Keys.
    - The system is required to store ~10 keys of 16-64 bytes in length, and therefore ~640 bytes of storage is required.
    - The keys will be updated periodically, approximately every 12-24hrs (7-14 times per week).
- State Data.
    - State data is used to speed up warm starts by caching application configuration data (e.g. recently discovered mesh network neighbour node addresses).
    - The system is required store ~4-16 bytes of data every 8 hours (~1000 times per year).


