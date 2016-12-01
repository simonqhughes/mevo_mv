# mbed Storage Product Requirements

Contributors: Simon Ford, Sam Grove, Simon Hughes, Erez Landau, Marcus Shawcroft

Author: Simon Hughes

Document Version: 0.01

Date: 20161201

Status: DRAFT

# <a name="introduction"></a> Introduction

This document attempts to articulate the mbed storage product requirements.

# Product Requirements

This section captures the high level storage product requirements applicable across the mbed solution components.


## Portability

This section documents the requirements needed to ensure the IoT storage solution has wide applicability.

**PROD-REQ-PORT-0001:** The storage solution must be capable of being ported to 99% of available IoT Operating Systems.

**PROD-REQ-PORT-0002:** The storage solution must be capable of being implemented on 99% of available IoT devices.

**PROD-REQ-PORT-0003:** The storage solution must be configurable so features can be disabled/enabled and thereby decrease/increase the required system resources 
( e.g. SRAM, code size, flash storage requirements). The solution can then be targeted at a range of device capabilities e.g. M0, M1, M3, M4, M7 for ARM-Mv7, ARM-Mv8 etc).


## Storage Clients

- The mbed Cloud Client is a user of the storage solution and therefore the Cloud Client storage requirements must be supported by the storage solution. 
  They are documented in the [mbed Cloud Client section](#mbed-cloud-product-requirements).


## Stored Object Types, Locations and Security

**PROD-REQ-OBJTYPE-0001:** The storage solution must be capable storing a 128bit cypher key in on-chip storage. They key can then be used to secure other NV stored e.g. off-chip.

**PROD-REQ-OBJTYPE-0002:** The storage solution must be capable storing a firmware images off-chip. 


## Security



# NVStore Product Requirements

# Filesystem Product Requirements

# <a name="mbed-cloud-product-requirements"></a> mbed Cloud Product Requirements

### Product Requirement 1: NVStore 

The product must be able to persistently store a small set of data items (e.g. a 128bit cypher key, a certificate chain)
which are used to secure the rest of the system. This store will be called NVStore. The size of the NVStore must be 
no less than 16kB.


#### Informational

- An envisaged product scenario is that the SoC on-chip flash will be used for the NVStore. By virtue of this flash
  storage being internal to the SoC and flash read/write operations being conducted entirely withing the chip (no external visibility), 
  the key is relatively secure (compared to being stored in external media) and can be more easily securely managed 
  The existence of the NVStore containing the key is a prerequisite to encrypting data for external storage.
  

### Product Requirement 2: Filesystem Store.

The product must be able to persistently store large data objects (e.g. 


### Product Requirement 3: NVStore API: should be a POSIX file interface

may relax this requirement if Minimal Resource Requirement cannot be met.


### Product Requirement 4: NVStore API: Minimal Resource Requirements 

i.e. must be capable being implemented on approx. 99% of IoT devices consuming approx. <= 10% of system resources

### Product Requirement 5: NVStore RAM Footprint: must be less than 10% of available SRAM (~2kB) so that  



|             |          Grouping           ||
First Header  | Second Header | Third Header |
 ------------ | :-----------: | -----------: |
Content       |          *Long Cell*        ||
Content       |   **Cell**    |         Cell |

New section   |     More      |         Data |
And more      | With an escaped '\|'         ||  
[Prototype table]


\begin{array} {|r|r|}
\hline
1 &2 \\
\hline
3 &4 \\
\hline
\end{array}


<table>
<thead>
<tr>
  <th>First Header</th>
  <th>Second Header</th>
</tr>
</thead>
<tbody>
<tr>
  <td>Content Cell</td>
  <td>Content Cell</td>
</tr>
<tr>
  <td>Content Cell</td>
  <td>Content Cell</td>
</tr>
</tbody>
</table>

