#!/bin/bash

# This script aims to document some useful command of managing 
#
#

CERT_CREATE=../../cert_create
TMPDIR=../


# In summary, this command:
#   - takes as input the image bins.
#   - outputs new certs
#   - outputs new files containing private keys generated
# In detail, these are the input files:
#
# --rot-key "$TMPDIR"/keys/rot.pem: INPUT FILE: ROT private key to use to generate certificate chains.
# --save-keys: causes the private keys to be saved in the following files (which must be specified):
#   --scp-fw-key "$TMPDIR"/fip/scp-fw-key-content-cert.bin: OUTPUT FILE: SCP Firmware Content Certificate (private) key output file name
#   --soc-fw-key "$TMPDIR"/fip/soc-fw-key-content-cert.bin: OUTPUT FILE: BL31 SoC Firmware Content Certificate (private) key output file
#   --tos-fw-key "$TMPDIR"/fip/tos-fw-key-content-cert.bin: OUTPUT FILE: BL32 Trusted OS Firmware Content Certificate (private) key output file
#   --nt-fw-key "$TMPDIR"/fip/nt-fw-key-content-cert.bin: OUTPUT FILE: BL33 Non-Trusted Firmware Content Certificate (private) key output file
# --tfw-nvctr 0: INPUT COUNTER: NV Counter value to be included in trusted world certificate chain content certificates (e.g. SOC FW content cert) 
# --ntfw-nvctr 0: INPUT COUNTER: NV Counter value to be included in non-trusted world certificate chain content certificates (e.g. Non-Trusted FW content cert)
# --tb-fw "$TMPDIR"/fip/tb-fw.bin: INPUT FILE: BL2 trusted boot FW binary. Needed to generate hash and for Trusted Boot FW Content Cert.
# --soc-fw "$TMPDIR"/fip/soc-fw.bin: INPUT FILE: BL31 SOC FW binary. 
# --tos-fw "$TMPDIR"/fip/tos-fw.bin: INPUT FILE: BL32 Trusted OS FW binary.
# --tos-fw-extra1 "$TMPDIR"/fip/tos-fw-extra1.bin: INPUT FILE: BL32 Trusted OS FW binary extra1.
# --tos-fw-extra2 "$TMPDIR"/fip/tos-fw-extra2.bin: INPUT FILE: BL32 Trusted OS FW binary extra2.
# --nt-fw "$TMPDIR"/fip/nt-fw.bin: INPUT FILE: BL33 Non-Trusted OS FW binary extra1.
# --trusted-key-cert "$TMPDIR"/fip/trusted-key-cert.bin: OUTPUT FILE: cert in DER format.
# --soc-fw-key-cert "$TMPDIR"/fip/soc-fw-key-cert.bin OUTPUT FILE: cert in DER format.
# --tos-fw-key-cert "$TMPDIR"/fip/tos-fw-key-cert.bin OUTPUT FILE: cert in DER format.
# --nt-fw-key-cert "$TMPDIR"/fip/nt-fw-key-cert.bin OUTPUT FILE: cert in DER format.
# --tb-fw-cert "$TMPDIR"/fip/tb-fw-cert.bin OUTPUT FILE: cert in DER format.
# --soc-fw-cert "$TMPDIR"/fip/soc-fw-cert.bin OUTPUT FILE: cert in DER format.
# --tos-fw-cert "$TMPDIR"/fip/tos-fw-cert.bin OUTPUT FILE: cert in DER format.
# --nt-fw-cert "$TMPDIR"/fip/nt-fw-cert.bin OUTPUT FILE: cert in DER format.
# --trusted-world-key "$TMPDIR"/fip/trusted-world-key.bin: OUTPUT FILE: contains private key of trusted_world_pk (see Julians TBBR chain of trust diagram)
# --non-trusted-world-key "$TMPDIR"/fip/non-trusted-world-key.bin: OUTPUT FILE:  contains private key of non_trusted_world_pk (see Julians TBBR chain of trust diagram)
# --scp-fw-key "$TMPDIR"/fip/scp-fw-key-content-cert.bin: OUTPUT FILE:  contains private key of scp_fw_content_pk  (see Julians TBBR chain of trust diagram)
# --soc-fw-key "$TMPDIR"/fip/soc-fw-key-content-cert.bin: OUTPUT FILE:  contains private key of soc_fw_content_pk  (see Julians TBBR chain of trust diagram)
# --tos-fw-key "$TMPDIR"/fip/tos-fw-key-content-cert.bin: OUTPUT FILE:  contains private key of tos_fw_content_pk  (see Julians TBBR chain of trust diagram)
# --nt-fw-key "$TMPDIR"/fip/nt-fw-key-content-cert.bin: OUTPUT FILE:  contains private key of nt_fw_content_pk  (see Julians TBBR chain of trust diagram)

"$CERT_CREATE" -n \
	       --rot-key "$TMPDIR"/keys/rot.pem \
	       --save-keys \
	       --tfw-nvctr 0 \
	       --ntfw-nvctr 0 \
	       --tb-fw "$TMPDIR"/fip/tb-fw.bin \
	       --soc-fw "$TMPDIR"/fip/soc-fw.bin \
	       --tos-fw "$TMPDIR"/fip/tos-fw.bin \
	       --tos-fw-extra1 "$TMPDIR"/fip/tos-fw-extra1.bin \
	       --tos-fw-extra2 "$TMPDIR"/fip/tos-fw-extra2.bin \
	       --nt-fw "$TMPDIR"/fip/nt-fw.bin \
	       --trusted-key-cert "$TMPDIR"/fip/trusted-key-cert.bin \
	       --soc-fw-key-cert "$TMPDIR"/fip/soc-fw-key-cert.bin \
	       --tos-fw-key-cert "$TMPDIR"/fip/tos-fw-key-cert.bin \
	       --nt-fw-key-cert "$TMPDIR"/fip/nt-fw-key-cert.bin \
	       --tb-fw-cert "$TMPDIR"/fip/tb-fw-cert.bin \
	       --soc-fw-cert "$TMPDIR"/fip/soc-fw-cert.bin \
	       --tos-fw-cert "$TMPDIR"/fip/tos-fw-cert.bin \
	       --nt-fw-cert "$TMPDIR"/fip/nt-fw-cert.bin \
	       --trusted-world-key "$TMPDIR"/fip/trusted-world-key.bin \
	       --non-trusted-world-key "$TMPDIR"/fip/non-trusted-world-key.bin \
	       --scp-fw-key "$TMPDIR"/fip/scp-fw-key-content-cert.bin \
	       --soc-fw-key "$TMPDIR"/fip/soc-fw-key-content-cert.bin \
	       --tos-fw-key "$TMPDIR"/fip/tos-fw-key-content-cert.bin \
	       --nt-fw-key "$TMPDIR"/fip/nt-fw-key-content-cert.bin 

# This command can be used to generate a new soc-fw content certificate (BL31)
# for example after rebuilding and BL31 has a new hash. This is more what we 
# want because we want to generate a new content certs without generating new
# key certs for the certificate chains, or a new ROT everytime we get a new
# set of BL3x's.
#
# ARGUMENTS:
# --rot-key ../keys/rot_key.pem: INPUT FILE: required, but is shouldn't be necessary to use as the only private key needed is the private key for tos_fw_content_pk.
# --trusted-world-key trusted-world-key.bin: INPUT FILE: private key of trusted_world_pk
# --non-trusted-world-key non-trusted-world-key.bin: INPUT FILE: private key of non_trusted_world_pk 
# --scp-fw-key scp-fw-key-content-cert.bin: INPUT FILE: private key of scp_fw_content_pk
# --soc-fw-key soc-fw-key-content-cert.bin: INPUT FILE: private key of soc_fw_content_pk
# --tos-fw-key tos-fw-key-content-cert.bin: INPUT FILE: private key of tos_fw_content_pk
# --soc-fw soc-fw.bin: INPUT FILE: the binary for which to generate a new content certificate for.
# --print-cert: INPUT OPTION: pretty print the output certificate to console
# --tfw-nvctr 0: INPUT COUNTER: NV counter to include in new content cert
# --soc-fw-cert soc-fw-cert_new.bin: OUTPUT FILE: new BL31 content cert filename to generate
#    
# Here is the command trace:
#    simhug01@e113506-lin:/data/2284/test/to_delete/20181018/pr239/work_20181109/fip$ ../../cert_create  --trusted-world-key trusted-world-key.bin --non-trusted-world-key non-trusted-world-key.bin --scp-fw-key scp-fw-key-content-cert.bin --soc-fw-key soc-fw-key-content-cert.bin --tos-fw-key tos-fw-key-content-cert.bin --nt-fw-key nt-fw-key-content-cert.bin --soc-fw soc-fw.bin -p --tfw-nvctr 0 --soc-fw-cert soc-fw-cert_new.bin --rot-key ../keys/rot_key.pem 
#    NOTICE:  CoT Generation Tool: Built : 16:24:14, Oct 18 2018
#    NOTICE:  Target platform: TBBR Generic
#    =====================================
#    
#    Certificate:
#        Data:
#            Version: 3 (0x2)
#            Serial Number: 11925470483941105960 (0xa57fc838a6b72128)
#        Signature Algorithm: rsassaPss
#             Hash Algorithm: sha256
#             Mask Algorithm: mgf1 with sha256
#             Salt Length: 0x20
#             Trailer Field: 0xBC (default)
#            Issuer: CN=SoC Firmware Content Certificate
#            Validity
#                Not Before: Nov  9 15:57:20 2018 GMT
#                Not After : Nov  4 15:57:20 2038 GMT
#            Subject: CN=SoC Firmware Content Certificate
#            Subject Public Key Info:
#                Public Key Algorithm: rsaEncryption
#                    Public-Key: (2048 bit)
#                    Modulus:
#                        00:e6:c3:dc:fb:70:ee:74:79:56:1a:fb:0f:a2:c4:
#                        6d:5b:c4:a7:66:c5:ac:08:ee:e2:c1:db:4e:dd:8a:
#                        a1:0a:b5:d9:1a:b1:a8:cf:7d:8c:6b:40:6a:d1:6d:
#                        71:6e:b5:09:e1:44:ee:f7:98:01:d1:ea:3e:92:b4:
#                        54:ea:ac:d7:54:f6:3e:fb:89:d0:dd:49:42:d2:a1:
#                        f8:70:1f:66:01:f1:89:0f:a3:f9:d8:57:8d:dd:c1:
#                        c6:4b:63:2a:31:bf:ed:ad:43:18:8a:3f:68:5a:2e:
#                        69:36:2c:b2:ef:cb:eb:5f:ac:56:94:99:97:9b:66:
#                        4b:1b:f7:d5:bf:84:ee:25:02:ec:87:6b:59:58:f0:
#                        22:7d:dc:1a:45:18:cd:9a:21:2e:bd:29:3f:89:f4:
#                        46:c1:db:dd:09:31:19:9f:ba:da:1b:df:b8:7f:cf:
#                        a8:48:4d:81:5d:43:a3:52:b6:96:dd:31:2f:fb:33:
#                        46:69:f2:5b:24:2b:60:4c:38:a3:92:fe:e0:fe:b7:
#                        1a:37:3c:b4:14:0c:9c:36:c6:13:80:df:89:51:48:
#                        ea:29:d5:6c:5e:a4:81:b0:4b:7c:bd:5d:8c:63:dc:
#                        f0:e6:77:76:68:ac:e4:44:d7:f9:8b:34:3c:32:78:
#                        cb:32:c1:9c:35:04:05:94:09:75:3a:fc:45:02:54:
#                        20:77
#                    Exponent: 65537 (0x10001)
#            X509v3 extensions:
#                X509v3 Subject Key Identifier: 
#                    1A:AB:69:6F:61:18:6B:EC:49:4A:87:14:FE:1F:8A:F0:AD:7F:BD:8B
#                X509v3 Authority Key Identifier: 
#                    keyid:1A:AB:69:6F:61:18:6B:EC:49:4A:87:14:FE:1F:8A:F0:AD:7F:BD:8B
#    
#                X509v3 Basic Constraints: 
#                    CA:FALSE
#                Trusted World Non-Volatile counter: critical
#                    0
#                SoC AP Firmware hash (SHA256): critical
#    ..`.H.e....... .n..(l...;..u..b....^.>.......l9
#                SoC Firmware Config hash: critical
#    ..`.H.e....... ................................
#        Signature Algorithm: rsassaPss
#             Hash Algorithm: sha256
#             Mask Algorithm: mgf1 with sha256
#             Salt Length: 0x20
#             Trailer Field: 0xBC (default)
#    
#             27:40:5f:f8:d7:6a:d2:51:db:db:fc:3b:1b:c8:3b:2f:eb:dc:
#             a5:5e:68:5c:01:f0:8e:a6:d7:31:ee:84:1a:18:2e:99:c6:c3:
#             85:34:bd:b2:b4:ba:87:0c:a3:37:8c:03:11:e0:15:8f:1b:e4:
#             77:85:af:a2:34:15:c8:da:ec:ee:42:f4:b9:c5:37:7a:4a:3a:
#             14:76:8a:46:8a:00:c5:58:34:07:f1:c8:0f:1a:d8:e1:2e:45:
#             ee:30:bd:56:a5:f5:3a:6e:82:50:19:bc:1a:e2:96:48:c7:76:
#             c2:d5:e8:0d:8f:b1:4c:fa:ce:91:73:84:d7:57:cb:10:b9:6a:
#             d5:52:84:e6:6b:f3:1d:8a:6c:e6:71:54:85:dd:12:b8:3b:f7:
#             00:bf:b5:d5:11:a8:62:f4:4a:35:47:59:0c:57:cd:fb:1e:a4:
#             98:19:d3:c6:57:be:f8:6b:85:98:d4:ef:d2:60:30:ce:bc:9c:
#             88:3c:0b:ef:21:74:cf:6c:15:53:e2:c0:40:51:20:d5:d1:21:
#             cd:7e:4e:9e:e1:ba:04:2b:0f:b4:20:d2:1f:ec:07:15:19:30:
#             4f:2f:a8:2b:33:39:15:4a:8a:a6:70:7c:52:4a:19:b7:30:39:
#             7b:30:1a:09:33:bd:d5:7a:e7:7d:b4:c3:40:a1:54:51:39:73:
#             8e:ea:2a:67
   
cert_create  \
	--rot-key ../keys/rot_key.pem \ 
	--trusted-world-key trusted-world-key.bin \
	--non-trusted-world-key non-trusted-world-key.bin \
	--scp-fw-key scp-fw-key-content-cert.bin \
	--soc-fw-key soc-fw-key-content-cert.bin \
	--tos-fw-key tos-fw-key-content-cert.bin  \
	--soc-fw soc-fw.bin \
	--print-cert \
	--tfw-nvctr 0 \
	--soc-fw-cert soc-fw-cert_new.bin  

# the newly generated soc-fw-cert_new.bin is in DER format. The contents of this cert can be viewed
# using openssl using the following commands:
# First, convert cert in DER format to PEM:
# 
# 	simhug01@e113506-lin:/data/2284/test/to_delete/20181018/pr239/work_20181109/fip$ openssl x509 -inform der -in soc-fw-cert_new.bin -out soc-fw-cert_new.pem
#
# Then inspect the contents of the cert:
#
# 	simhug01@e113506-lin:/data/2284/test/to_delete/20181018/pr239/work_20181109/fip$ openssl x509 -in soc-fw-cert_new.pem -text -nooutCertificate:
# 	    Data:
# 	        Version: 3 (0x2)
# 	        Serial Number: 11925470483941105960 (0xa57fc838a6b72128)
# 	    Signature Algorithm: rsassaPss
# 	         Hash Algorithm: sha256
# 	         Mask Algorithm: mgf1 with sha256
# 	         Salt Length: 0x20
# 	         Trailer Field: 0xBC (default)
# 	        Issuer: CN=SoC Firmware Content Certificate
# 	        Validity
# 	            Not Before: Nov  9 15:57:20 2018 GMT
# 	            Not After : Nov  4 15:57:20 2038 GMT
# 	        Subject: CN=SoC Firmware Content Certificate
# 	        Subject Public Key Info:
# 	            Public Key Algorithm: rsaEncryption
# 	                Public-Key: (2048 bit)
# 	                Modulus:
# 	                    00:e6:c3:dc:fb:70:ee:74:79:56:1a:fb:0f:a2:c4:
# 	                    6d:5b:c4:a7:66:c5:ac:08:ee:e2:c1:db:4e:dd:8a:
# 	                    a1:0a:b5:d9:1a:b1:a8:cf:7d:8c:6b:40:6a:d1:6d:
# 	                    71:6e:b5:09:e1:44:ee:f7:98:01:d1:ea:3e:92:b4:
# 	                    54:ea:ac:d7:54:f6:3e:fb:89:d0:dd:49:42:d2:a1:
# 	                    f8:70:1f:66:01:f1:89:0f:a3:f9:d8:57:8d:dd:c1:
# 	                    c6:4b:63:2a:31:bf:ed:ad:43:18:8a:3f:68:5a:2e:
# 	                    69:36:2c:b2:ef:cb:eb:5f:ac:56:94:99:97:9b:66:
# 	                    4b:1b:f7:d5:bf:84:ee:25:02:ec:87:6b:59:58:f0:
# 	                    22:7d:dc:1a:45:18:cd:9a:21:2e:bd:29:3f:89:f4:
# 	                    46:c1:db:dd:09:31:19:9f:ba:da:1b:df:b8:7f:cf:
# 	                    a8:48:4d:81:5d:43:a3:52:b6:96:dd:31:2f:fb:33:
# 	                    46:69:f2:5b:24:2b:60:4c:38:a3:92:fe:e0:fe:b7:
# 	                    1a:37:3c:b4:14:0c:9c:36:c6:13:80:df:89:51:48:
# 	                    ea:29:d5:6c:5e:a4:81:b0:4b:7c:bd:5d:8c:63:dc:
# 	                    f0:e6:77:76:68:ac:e4:44:d7:f9:8b:34:3c:32:78:
# 	                    cb:32:c1:9c:35:04:05:94:09:75:3a:fc:45:02:54:
# 	                    20:77
# 	                Exponent: 65537 (0x10001)
# 	        X509v3 extensions:
# 	            X509v3 Subject Key Identifier: 
# 	                1A:AB:69:6F:61:18:6B:EC:49:4A:87:14:FE:1F:8A:F0:AD:7F:BD:8B
# 	            X509v3 Authority Key Identifier: 
# 	                keyid:1A:AB:69:6F:61:18:6B:EC:49:4A:87:14:FE:1F:8A:F0:AD:7F:BD:8B
# 	
# 	            X509v3 Basic Constraints: 
# 	                CA:FALSE
# 	            1.3.6.1.4.1.4128.2100.1: critical
# 	                ...
# 	            1.3.6.1.4.1.4128.2100.603: critical
# 	..`.H.e....... .n..(l...;..u..b....^.>.......l9
# 	            1.3.6.1.4.1.4128.2100.604: critical
# 	..`.H.e....... ................................
# 	    Signature Algorithm: rsassaPss
# 	         Hash Algorithm: sha256
# 	         Mask Algorithm: mgf1 with sha256
# 	         Salt Length: 0x20
# 	         Trailer Field: 0xBC (default)
# 	
# 	         27:40:5f:f8:d7:6a:d2:51:db:db:fc:3b:1b:c8:3b:2f:eb:dc:
# 	         a5:5e:68:5c:01:f0:8e:a6:d7:31:ee:84:1a:18:2e:99:c6:c3:
# 	         85:34:bd:b2:b4:ba:87:0c:a3:37:8c:03:11:e0:15:8f:1b:e4:
# 	         77:85:af:a2:34:15:c8:da:ec:ee:42:f4:b9:c5:37:7a:4a:3a:
# 	         14:76:8a:46:8a:00:c5:58:34:07:f1:c8:0f:1a:d8:e1:2e:45:
# 	         ee:30:bd:56:a5:f5:3a:6e:82:50:19:bc:1a:e2:96:48:c7:76:
# 	         c2:d5:e8:0d:8f:b1:4c:fa:ce:91:73:84:d7:57:cb:10:b9:6a:
# 	         d5:52:84:e6:6b:f3:1d:8a:6c:e6:71:54:85:dd:12:b8:3b:f7:
# 	         00:bf:b5:d5:11:a8:62:f4:4a:35:47:59:0c:57:cd:fb:1e:a4:
# 	         98:19:d3:c6:57:be:f8:6b:85:98:d4:ef:d2:60:30:ce:bc:9c:
# 	         88:3c:0b:ef:21:74:cf:6c:15:53:e2:c0:40:51:20:d5:d1:21:
# 	         cd:7e:4e:9e:e1:ba:04:2b:0f:b4:20:d2:1f:ec:07:15:19:30:
# 	         4f:2f:a8:2b:33:39:15:4a:8a:a6:70:7c:52:4a:19:b7:30:39:
# 	         7b:30:1a:09:33:bd:d5:7a:e7:7d:b4:c3:40:a1:54:51:39:73:
# 	         8e:ea:2a:67
	       