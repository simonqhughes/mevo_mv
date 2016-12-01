# mbed Storage Product Requirements

Contributors: Simon Ford, Sam Grove, Simon Hughes, Erez Landau, Marcus Shawcroft

Author: Simon Hughes

Document Version: 0.01

Date: 20161201

Status: DRAFT

# <a name="introduction"></a> Introduction

This aim of this document is to articulate the mbed storage product requirements.

# Overview 

The mbed storage endpoint functionality is envisaged to be partitioned into to the following functional components:

- NVStore.
- Filesystem Store.

The feature cut between above components is described in the table below.

**Storage Component Feature Analysis**

<table>
<thead>
<tr>
  <th>Feature</th>
  <th>NVStore</th>
  <th>Filesystem Store</th>
</tr>
</thead>
<tbody>
<tr>
  <td>Security</td>
  <td>Is secure and must run in a security context (uvisor)</td>
  <td>Is secure and should run in a security context (uvisor)</td>
</tr>
<tr>
  <td>Security</td>
  <td>Stores root of trust key</td>
  <td>Does not store root of trust key</td>
</tr>
  <td>Security</td>
  <td>May not be encrypted.</td>
  <td>Must be encrypted if held on off-chip storage.</td>
</tr>
<tr>
  <td>Endurance</td>
  <td>Written 10-100 times during product lifetime (1 time/year-1 time/month)</td>
  <td>Written 10^5-10^6 times during product lifetime (10+ times/day)</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td>Should be on-chip</td>
  <td>Should be off-chip</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td>On-chip is NOR flash with 
  NAND like restrictions due to flash memory controller.</td>
  <td>A key use case is SPI NOR flash as the storage backend.</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td></td>
  <td>A key use case is SPI NAND flash as the storage backend.</td>
</tr>
<tr>
  <td>Physical Location</td>
  <td></td>
  <td>A key use case is SPI SDCard/MMC as the storage backend.</td>
</tr>
<tr>
  <td>Wear Levelling</td>
  <td>Not required due to 
  small number of write/erase operations</td>
  <td>Required due to large number of writes/erase operations</td>
</tr>
<tr>
  <td>EEC</td>
  <td>Error Correction Codes (ECC) not required 
  due to stability of storage</td>
  <td>Error Correction Codes (ECC)  required due to instability of NAND storage (NAND is a key use case).</td>
</tr>
<tr>
  <td>Bad Block management</td>
  <td>Required.</td>
  <td>Required.</td>
</tr>
<tr>
  <td>Robustness against power failures</td>
  <td>Required.</td>
  <td>Required.</td>
</tr>
<tr>
  <td>Journaling</td>
  <td>Required for robustness against power failures.</td>
  <td>Required for robustness against power failures.</td>
</tr>
<tr>
  <td>Sequential Writes</td>
  <td>NAND: sequential writing required 
  (no rewriting of previous journaled entries).</td>
  <td>NAND: sequential writing required (no rewriting of previous journaled entries).</td>
</tr>
<tr>
  <td>API</td>
  <td>API: Should be the POSIX file interface, may be something different.</td>
  <td>API: Must be the POSIX file interface.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may be invasive/disruptive to the system.</td>
  <td>Storage operations must not be invasive or disruptive to the system.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may disable interrupts (causing high interrupt latency).</td>
  <td>Storage operations must not disable interrupts.</tr>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may require a system reboot after an operation</td>
  <td>Storage operations must not require a reboot after an operation.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Storage operations may use in-application programming techniques (use of RAMFUNCS).</td>
  <td>Storage operations should not be use in-application programming techniques.</td>
</tr>
<tr>
  <td>System Impact</td>
  <td>Concurrent storage operations may have a very small number of file (or file equivalent) entities open concurrently e.g. maximum 2.</td>
  <td>Concurrent storage operations may have a small number of file (or file equivalent) entities open concurrently e.g. maximum 10 (configurable).</td>
</tr>
<tr>
  <td>Portability</td>
  <td>Required. Must be capable of being ported to 99% of all IoT devices.</td>
  <td>Required. Must be capable of being ported to 99% of all IoT devices.</td>
</tr>
  <td>Portability (Minimal Resources)</td>
  <td>Must need minimal system resources so NVSTORE can be implemented on the smallest of devices e.g. 2-4kB SRAM and 10-15kB code flash.</td>
  <td>May require more than minimal system resources e.g. >4kB SRAM, SRAM footprint scaling linearly with store size and number of files,  >>15kB code flash.</td>
</tr>
<tr>
  <td>mbedOS Native Support</td>
  <td>Required.</td>
  <td>?</td>
</tr>

</tbody>
</table>




