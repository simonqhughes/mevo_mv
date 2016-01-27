# REQUIREMENTS

## Defintion of Terms
CS = Configuration Store
KV = Key Value Pair. {key, value}
NV = Non Volatile 

## Secure Key Value Storage\Rationale (REQ-1.xx-SKVS-R) Requirements

##### REQ-1.01-SKVS-R:
The CS must provide a non-volatile, hardware-independent secure storage
service that can be used by CS API clients for storing data owned
by a client security context (uvisor box).

##### REQ-1.02-SKVS-R:
Clients of the CS API must be security contexts (boxes) so that security
policies can be enforced.

##### REQ-1.03-SKVS-R:
The CS design values simplicity over complexity to promote security by
minimizing the attack surface to secure data.

##### REQ-1.04-SKVS-R:
The CS must be implemented as a uvisor secure box.

##### REQ-1.05-SKVS-R:
The CS must support the use of Access Control Lists for policing access to
secure data.

##### REQ-1.06-SKVS-R:
The CS must support the storage of a {key, value} tuples where
- the key is a zero terminated string of arbitrary length.
- the value is a binary blob of data of arbitrary length
The {key, value} tuple is a CS object.

##### REQ-1.07-SKVS-R: CS Stores Binary Blobs
The CS must support services so that other components can implement
more complex storage types other than a binary blob e.g. by
wrapping the underlying CS {key, value} tuple with additional
type information.

##### REQ-1.08-SKVS-R: CS Key Structure as Name Strings
CS must support keys having the format of a null terminated string.

##### REQ-1.09-SKVS-R: Key Creation and Ownership Part 1
CS keys must be owned by the security context . A security context (box)
is identified by a unique security_name_prefix and this identifier
must be used when the key is created. CS must support the use of the
security_name_prefix as the leading substring of the CS key string, in which
case the key_name_prefix is the security_name_prefix and identifies the
owner of the key.

##### REQ-1.10-SKVS-R: Security Context
In order to create objects in the CS, a security context (box) must have
a security_name_prefix.

##### REQ-1.11-SKVS-R: CS object
In order to create objects in the CS, a security context (box) must have
a security_name_prefix.


## Secure Key Value Storage High Level Design (REQ-1.2.xx-SKVS-HLD) Requirements

##### REQ-1.2.01-SKVS-HLD:
The CS must be able to detect the available types of storage media
available in the system and report associated storage media attributes.

##### REQ-1.2.02-SKVS-HLD:
The CS may report the following storage media data retention level attribute,
when available:
- only during device activity
- during sleep
- during deep-sleep
- battery-backed, device can be powered off
- internal nonvolatile memory
- external nonvolatile memory

##### REQ-1.2.03-SKVS-HLD:
For a particular storage medium, the CS may report the following device
data security protection features, when available:
- no security, just safety
- write-once-read-only-memory (WORM)
- against internal software attacks using ACLs
- roll-back protection
- immovable (for internal memory mapping, to stop relocated block to move).
  This attribute must only be set provided:
  -- the device memory is mapped into the CPU address space
  -- access is only granted to specific CS API system clients e.g. FOTA,
     DMA.
- hardening against device software (malware running on the device)
- hardening against board level attacks (debug probes, copy protection
  fuses)
- hardening against chip level attacks (tamper-protection)
- hardening against side channel attacks
- tamper-proof memory (will be deleted on tamper-attempts using board level
  or chip level sensors)

##### REQ-1.2.04-SKVS-HLD:
The CS may be used to implement KV storage protection services
(e.g. flash image roll-back protection, confidentiality) for off-chip
(external) storage media (e.g. SPI/I2C/NAND Flash).

##### REQ-1.2.05-SKVS-HLD:
The device data security protection immovable attribute may only be set


## Secure Key Value Storage\High Level API Description\Key Value Storage (REQ-3.1.xx-SKVS-HLAPID-KVS) Requirements.

##### REQ-3.1.01-SKVS-HLAPID-KVS: CS Global Key Namespace
The CS must implement a system global hierarchical tree name-space for
keys. The namespace is shared by all software components operating within
the system. Examples of key names include the following:
 - 'com.arm.mbed.wifi.accesspoint[5].essid'
 - 'com.arm.mbed.wifi.accesspoint[home].essid'
 - 'yotta.your-yotta-registry-module-name.your-value'
 - 'yotta.hello-world.animal[dog][foot][3]'
 The key name string forms a path where 'Path Directory Entries' are
 separated by the '.' character.

##### REQ-3.1.02-SKVS-HLAPID-KVS: CS Key Name String Format Max Length
For CS keys The maximum length of a CS key is 220 characters excluding
the terminating null.

##### REQ-3.1.03-SKVS-HLAPID-KVS: CS Key Name String Allowed Characters
CS key name strings must only contain the following characters:
- [a-zA-Z0-9.]
- '-'

##### REQ-3.1.04-SKVS-HLAPID-KVS: Key Name Path Directory Entry List []
Path Directory Entries may have list indicators designated by []. For
example,
 - 'com.arm.mbed.wifi.accesspoint[5].essid'
 - 'com.arm.mbed.wifi.accesspoint[home].essid'
 - 'yotta.hello-world.animal[dog][foot][3]'
In the above the list item specifiers are respectively:
 - '5'
 - 'home'
 - 'dog', 'foot, '3'
As list item specifiers are part of the key name string, the list item
substring must be composed of allowable characters.

##### REQ-3.1.05-SKVS-HLAPID-KVS: CS Global Key Yotta Namespace
The key name prefix 'yotta' is reserved for use by the yotta module. Other
prefixes may be reserved.


## Secure Key Value Storage\High Level API Description\Access Control Security (REQ-3.2.xx-SKVS-HLAPID-ACS) Requirements.

##### REQ-3.2.01-SKVS-HLAPID-KACS:
The CS must enforce security policies as defined by Access Control Lists.

##### REQ-3.2.02-SKVS-HLAPID-KACS: CS Key Creation Part 2
The CS objects must be created with an ACL. The ACL is attached to the object
so that access permissions to the KV data can be enforced.

##### REQ-3.2.03-SKVS-HLAPID-KACS:
The CS Access Control Lists must support the groups for 'owner' and 'other',
with optional permissions read, write and executable. The owner group
permissions describe the access permissions of the owner of the object. The
other group permissions describe the access permissions for entities other
than the owner. The writable and executable permissions are mutually
exclusive.

##### REQ-3.2.04-SKVS-HLAPID-KACS:
A CS API client must be able to query the CS for a list of KV pairs provided
the KV pair ACL permissions allow the client access. The query result must
contain all client owner KVs. The query results may include non-client
owned KVs provided the other group permissions grant access.


## Secure Key Value Storage\API Logic\Finding Keys (REQ-5.1.xx-SKVS-APIL-FK) Requirements.

##### REQ-5.1.01-SKVS-APIL-FK: Key Searching/Finding Scoped by ACL
The CS must provide an interface to query for active keys in the global
storage. The query must:
- return results based on the ACL provided by the client
- support wild card searches using the '*' character. The '*' character
  can occur at most once any point in the search string. For example:
  -- 'com.arm.mbed.wifi.accesspoint*.essid'
  -- 'yotta.your-yotta-registry-module-name.*'
  -- 'yotta.hello-world.animal[dog][foot][*]'
  -- 'yotta.hello-world.animal[dog][foot]*'
  -- 'yotta.hello-world.animal[dog*3]'

##### REQ-5.1.02-SKVS-APIL-FK: CS Global Key Namespace Reserves Character '*'
The character '*' is reserved in the CS global key namespace. The current
functions of this character as as follows:
- a wild card character in searches.
- a wild card character used in the delete operation.


##### REQ-5.1.03-SKVS-APIL-FK: Key Searching/Finding Resume
In order to support the return of a large list of key query results (perhaps
exceeding the ability of the caller to consume in a single operation), the
query interface must support the ability to restart/resume the query to
retrieve a subsequent set of records to those already received.

##### REQ-5.1.04-SKVS-APIL-FK: Key Searching/Finding Internals (key versions)
The CS must be robust against incomplete, corrupted or aborted write 
operations to NV store caused for example, by loss of power during the 
write. 


## Secure Key Value Storage\API Logic\Get Storage Information (REQ-5.2.xx-SKVS-APIL-GSI) Requirements.

##### REQ-5.2.01-SKVS-APIL-GSI: storage_detect
The CS must provide an API so that clients can discover the CS storage
capabilities. Storage capabilities may include:
- write-block sizes for O_BLOCK_WRITE mode (sequence of writes into the
  same value)
- supported Data Retention Levels
- supported Device Data Security Protection Features

##### REQ-5.2.02-SKVS-APIL-GSI: Minimal Storage Support
The CS must provide minimal storage media services including the following:
- SRAM/SDRAM memory with no security guarantees.


## Secure Key Value Storage\API Logic\Creating & Opening Keys for Writing (REQ-5.3.xx-SKVS-APIL-COKFW) Requirements.

##### REQ-5.3.01-SKVS-APIL-COKFW: storage_key_create with O_CREATE
CS keys must be explicitly created using 'storage_key_create' with the following
parameters:
- security ACLs (owner & others)
- the intended retention levels (bit mask to allow caching if needed)
- indicating the expected Device Data Security Protection Features
- the key pointer (zero-terminated)
- the value size
- optionally the offset address (restricted feature, ideally only granted
  to the FOTA security context) (todo: how does the offset-address work?)
- alignment bits of the value hardware address (only for O_CONTINUOUS).
  The structure start is aligned accordingly to ensure that the value
  blob is aligned on a multiple of the 2alignment_bits
- mode flags (O_CREATE, O_CONTINUOUS, O_LAZY_FLUSH, O_BLOCK_WRITE,
  O_ALLOCATE_AT_OFFEST).
  -- O_CREATE. The call will create the KV pair. If a
     pre-existing KV with the same name is present in CS then the
     storage_key_create will fail with FILE_EXISTS.
  -- O_CONTINUOUS. The KV value will be stored in a continuous range
     of hardware addresses.
  -- O_LAZY_FLUSH ? (todo: define)
  -- O_BLOCK_WRITE ? (todo: define)
  -- O_ALLOCATE_AT_OFFEST ? (todo: define)

##### REQ-5.3.02-SKVS-APIL-COKFW: storage_key_create without O_CREATE
Pre-existing CS objects can be updated by calling the storage_key_create
API with the O_CREATE not set.
(todo: understand this requirement more fully:)
In case a pre-existing key is updated (O_CREATE not set) and the previous
ACL allows writing to the caller:
(todo: which previous ACL?)
- all key-value fragments of the previous key are set as inactive
  (todo: delete? fragmentation are not exposed to the API client)
- the new key is allocated (in fragments if permitted)
  (todo: are we internally creating a new copy of the key?)
- all permissions and settings are copied from the previous key
- the version number is incremented compared to the previous key
  (todo: delete? updating of version numbers is an CS internal
  implementation detail)

##### REQ-5.3.03-SKVS-APIL-COKFW: O_CONTINUOUS for executable objects
CS will manage an executable KV as though the mode O_CONTINUOUS flag
is set.

##### REQ-5.3.04-SKVS-APIL-COKFW: O_CONTINUOUS for non-executable objects
A CS client may specify the mode O_CONTINUOUS flag for non-executable
objects.


## Secure Key Value Storage\Updating and Settings and Permissions (REQ-6.1.xx-SKVS-USP) Requirements.

##### REQ-6.1.01-SKVS-USP:
CS does not permit the updating of KV pair permissions or settings. This is to promote security.


## Secure Key Value Storage\Updating and Settings and Permissions\Deleting Keys (REQ-6.2.xx-SKVS-USP-DK) Requirements.

##### REQ-6.2.01-SKVS-USP-DK:
Only the owner of the CS KV pair can delete the object. The wildcard
'*' character can be specified to delete an owned subtree of the CS
global key namespace.

##### REQ-6.2.02-SKVS-USP-DK:
To change the value of a CS KV pair, the owner must:
- delete the KV pair
- create a new KV pair with the new value/attributes.


## Secure Key Value Storage\Updating and Settings and Permissions\Opening Keys for Reading (REQ-6.2.xx-SKVS-USP-OKFR) Requirements.

##### REQ-6.3.xx-SKVS-USP-OKFR storage_key_open_read
CS objects must be explicitly opened with storage_key_open_read(key_name)
before operations on the KV pair can be performed. The KV must
pre-exist in the store before it can be opened.


## Secure Key Value Storage\Updating and Settings and Permissions\Seeking in Key Values (REQ-6.3.xx-SKVS-USP-SIKV) Requirements.

##### REQ-6.4.01-SKVS-USP-SIKV storage_value_rseek
The function storage_value_rseek can be used on a file handle
to change the read position inside a value. Changing the write
position is intentionally not supported

##### REQ-6.4.02-SKVS-USP-SIKV
CS does not support the changing of the write position of an object
value attribute.


## Secure Key Value Storage\Updating and Settings and Permissions\Writing Keys (REQ-6.4.xx-SKVS-USP-WK) Requirements.

##### REQ-6.5.01-SKVS-USP-WK
CS KV values can be written in one or more operation.
todo: are there any requirements arising from these statements?
They appear to refer to CS internal implementation details.
- The CRC block including the activation is set after the last value
  byte is written to finalize the key.
- The write position is kept in SRAM only and is lost on reboots
- non-finalized values can be finalized on reboot.
- Each value-fragment is independently finalised.

##### REQ-6.5.01-SKVS-USP-WK
CS KV write interface has the following semantics:
- Writing to a non-finalised object is only allowed by the owner.
- Closing of a written object results in the finalisation of the object.
- Flushing of the CS results in the finalisation of the store.
- Non-finalised object can't be read.


## Secure Key Value Storage\Updating and Settings and Permissions\Executable Keys and Firmware Updates (REQ-6.6.xx-SKVS-USP-EKFU)
Requirements.

##### REQ-6.6.xx-SKVS-USP-EKFU
todo 


## Secure Key Value Storage\Miscellaneous (REQ-7.1.xx-SKVS-M)Requirements.

##### REQ-7.1.01-SKVS-M
The CS will implement a C Language interface.

##### REQ-7.1.02-SKVS-M
The CS does not support hot-pluggable storage devices which SD flash. 




