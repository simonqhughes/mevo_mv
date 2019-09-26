###############################################################################
# Copyright (c) 2019 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
###############################################################################
#
# <topdir>/test/Makefile
#  Makefile to build the PSA storage x86 test binaries.
#
# This makefile provides support for building the x86 PSA storage tests:
#  - psa-arch-test-ps, a test binary generated from the PSA Compliance project
#    psa-arch-test.
#  - psa_trusted_storage_linux test binaries (derived from the mbed-crypto
#    tests)
#
# (WARNING: Public users will be unable to use this makefile to generate
# psa-arch-test-ps due to repo access restrictions. However, other test
# binaries can be generated. See later for more details.)
#
# In order to run the above, use this makefile in the following way:
#  1. Copy this makefile into a new top level workspace directory TOPDIR.
#  2. cd into TOPDIR and invoke the following commands.
#  3. make ws-create-pinned
#  4. make
#  5. make test
#
# Item 3 above git clones the relevant repositories at compatible pinned versions.
# The projects of interest are:
#  - https://github.com/ARMmbed/psa_trusted_storage_linux.
#  - https://github.com/ARMmbed/mbed-crypto.
#  - A private fork of https://github.com/ARM-software/psa-arch-tests. The private
#    fork contains patches against upstream so that psa-arch-tests-ps can be built.
#    The fork is accessible to ARM stakeholders for internal development. In time,
#    the patches will be upstreamed and become publicly availble.
#    **** WARNING ****
# 
# Item 4 above builds test binaries. ARM developers can build all test binaries
# including psa-arch-tests-ps by using the following command:
#  - make all-arm
#
# Item 5 above runs the test binaries and outputs the test trace to the console.
#
# The following tools are required on the host and available on the path:
# - git
# - repo
# - host gcc compiler.
###############################################################################

TOPDIR = $(shell pwd)
# TODO: replace jobdir with path into psa_trusted_storage_linux
JOBDIR = ${TOPDIR}/mevo/jobs/2303
# todo: store patches in psa_trusted_storage_linux
MBED_CRYPTO_PATCH1_NAME = 0001-Add-psa_trusted_storage_linux-persistent-storage-sup.patch
MBED_CRYPTO_PATCH2_NAME = 0002-PSA-Storage-Fix-tests-to-support-PSA_STORAGE_FLAG_NO.patch
MBED_CRYPTO_PATCH1 = ${JOBDIR}/${MBED_CRYPTO_PATCH1_NAME}
MBED_CRYPTO_PATCH2 = ${JOBDIR}/${MBED_CRYPTO_PATCH2_NAME}
CFLAGS="-I${TOPDIR}/psa-storage/inc -I${TOPDIR}/psa-storage/configs -DMBEDTLS_CONFIG_FILE='<mbed_crypto_psa_storage_config.h>'"
LDFLAGS="-L${TOPDIR}/psa-storage/usr/local/lib -lpsastorage"
LD_LIBRARY_PATH=$(TOPDIR)/mbed-crypto/library/:$(TOPDIR)/psa-storage/usr/local/lib
TEST_DIR="${TOPDIR}/test/"
PSA_CFLAGS="-DPSA_STORAGE_FILE_C_STORAGE_PREFIX='\"${TEST_DIR}\"'"

###############################################################################
# Standard targets
###############################################################################
.PHONY: all
all: mbed-crypto

.PHONY: all-arm
all-arm: psa-arch-tests-ps

.PHONY: clean
clean: mbed-crypto-clean psa-storage-clean test-clean psa-arch-tests-ps-clean test-clean

.PHONY: install
install: psa-storage-install

.PHONY: test
test: test-mbed-crypto-app test-mbed-crypto-its test-mbed-crypto-key test-psa-storage-app test-psa-arch-tests-ps

.PHONY: test-clean
test-clean:
	rm -fR $(TOPDIR)/test

###############################################################################
# mbed-crypto targets
###############################################################################
#.PHONY: mbed-crypto
mbed-crypto: psa-storage-install mbed-crypto/${MBED_CRYPTO_PATCH1_NAME}
	make -C mbed-crypto CFLAGS=${CFLAGS} LDFLAGS=${LDFLAGS}

.PHONY: mbed-crypto-clean
mbed-crypto-clean:
	make -C mbed-crypto clean
	rm -fR mbed-crypto/${MBED_CRYPTO_PATCH1_NAME}

# The mbed-crypto project test framework is used to test PSA storage lib.
# However, patches must be applied against a specific revision for this to 
# work.
mbed-crypto/${MBED_CRYPTO_PATCH1_NAME}:
	# The patch should be applied against the development branch
	# The patch can be created using: git format-patch -1 HEAD
	# where the changes have been checked into the last commit.
	cd mbed-crypto && git checkout aad3dab
	cd mbed-crypto && git am < ${MBED_CRYPTO_PATCH1} && cd ..
	cd mbed-crypto && git am < ${MBED_CRYPTO_PATCH2} && cd ..
	cp ${MBED_CRYPTO_PATCH1} mbed-crypto
	touch mbed-crypto

# Target to run the mbed-crypto-app test binary
test-mbed-crypto-app: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/programs/test && ./mbl-crypto-storage-example-app && cd ../..

# Target to run the mbed-crypto-its test binary
test-mbed-crypto-its: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_its && cd ../..

# Target to run the mbed-crypto-key test binary
test-mbed-crypto-key: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_crypto_persistent_key && cd ../..

# Directory to contain files generated by testing.
.PHONY: test-dir
test-dir:
	-mkdir $(TOPDIR)/test

###############################################################################
# psa-storage targets
###############################################################################
.PHONY: psa-storage
psa-storage:
	make -C psa-storage CFLAGS=${PSA_CFLAGS} 

.PHONY: psa-storage-clean
psa-storage-clean:
	make -C psa-storage clean

.PHONY: psa-storage-install
psa-storage-install: psa-storage
	make -C psa-storage install prefix=$(TOPDIR)/psa-storage/usr/local

.PHONY: test-psa-storage-app
test-psa-storage-app: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd psa-storage/app && ./psa-storage-example-app && cd ../..

###############################################################################
# Workspace management targets
###############################################################################

# Target to create a pinned manifest from the workspace
.PHONY: ws-manifest
ws-manifest:
	repo manifest -r -o psa-storage-pinned-manifest.xml

# Target to create a workspace for development (from the unpinned manifest)
ws-create:
	repo init -u https://github.com/armmbed/mbl-manifest
	git clone git@github.com:armmbed/mevo mevo_create_clone
	cp $(TOPDIR)/mevo_create_clone/jobs/2303/psa-storage-manifest.xml $(TOPDIR)/.repo/manifests
	repo init -m psa-storage-manifest.xml
	repo sync
	rm -IR $(TOPDIR)/mevo_create_clone

# Target to create a workspace for testing latest known good version (pinned manifest)
ws-create-pinned:
	repo init -u https://github.com/armmbed/mbl-manifest
	git clone git@github.com:armmbed/mevo mevo_create_clone
	cp $(TOPDIR)/mevo_create_clone/jobs/2303/psa-storage-pinned-manifest.xml $(TOPDIR)/.repo/manifests
	repo init -m psa-storage-pinned-manifest.xml
	repo sync
	rm -IR $(TOPDIR)/mevo_create_clone

# Target t delete the workspace.
ws-delete:
	rm -IR $(TOPDIR)/mevo
	rm -IR $(TOPDIR)/psa-storage
	rm -IR $(TOPDIR)/.repo
	rm -IR $(TOPDIR)/mbed-crypto

###############################################################################
# PSA Compliance psa-arch-tests-ps protected storage test binary targets
###############################################################################

#TODO: rename psa-storage to psa_trusted_storage_linux
PSA_STORAGE_DIR=psa-storage

# TODO: remove this from the makefile and the manifest.
PSA_ARCH_TEST_BOILERPATE_DIR=mbedtls-test

.PHONY: psa-arch-tests-ps
psa-arch-tests-ps: mbed-crypto psa-storage-install $(TOPDIR)/psa-arch-tests/api-tests/build-ps $(TOPDIR)/psa-arch-tests/api-tests/build-ps/CMakeFiles main.o 
	cd psa-arch-tests/api-tests/build-ps && cmake --build .
	cd psa-arch-tests/api-tests/build-ps && gcc -o psa-arch-tests-ps $(TOPDIR)/mbedtls-test/resources/psa-arch-tests/main.o ./dev_apis/protected_storage/test_combine.a ./val/val_nspe.a ./platform/pal_nspe.a ./dev_apis/protected_storage/test_combine.a $(TOPDIR)/$(PSA_STORAGE_DIR)/usr/local/lib/libpsastorage.so

$(TOPDIR)/psa-arch-tests/api-tests/build-ps:
	mkdir $(TOPDIR)/psa-arch-tests/api-tests/build-ps

$(TOPDIR)/psa-arch-tests/api-tests/build-ps/CMakeFiles:
	cd psa-arch-tests/api-tests/build-ps && cmake ../ -DTOOLCHAIN=HOST_GCC -DTARGET=tgt_dev_apis_stdc -DSUITE=PROTECTED_STORAGE -DPSA_INCLUDE_PATHS=$(TOPDIR)/$(PSA_STORAGE_DIR)/inc -DCPU_ARCH=armv7m

psa-arch-tests-ps-build:
	cd $(TOPDIR)/psa-arch-tests/api-tests/build-ps && cmake --build .

# delete the psa-arch-tests-ps test binary
psa-arch-tests-ps-clean:
	rm -fR $(TOPDIR)/psa-arch-tests/api-tests/build-ps

# TODO: move main.c into psa storage repo
main.o:
	gcc -Wall -Werror -c -o ./$(PSA_ARCH_TEST_BOILERPATE_DIR)/resources/psa-arch-tests/main.o ./mbedtls-test/resources/psa-arch-tests/main.c

.PHONY: test-psa-arch-tests-ps
test-psa-arch-tests-ps:
	$(TOPDIR)/psa-arch-tests/api-tests/build-ps/psa-arch-tests-ps

###############################################################################
# PSA Compliance psa-arch-tests-crypto crypto test binary targets
# Note the binary has to be generated from a non-patched version of mbed-crypto
# TODO: setup another patch target to capture this version
###############################################################################

.PHONY: psa-arch-tests-crypto
psa-arch-tests-crypto: mbed-crypto $(TOPDIR)/psa-arch-tests/api-tests/build-crypto $(TOPDIR)/psa-arch-tests/api-tests/build-crypto/CMakeFiles main.o 
	cd psa-arch-tests/api-tests/build-crypto && cmake --build .
	cd psa-arch-tests/api-tests/build-crypto && gcc -o psa-arch-tests-crypto $(TOPDIR)/mbedtls-test/resources/psa-arch-tests/main.o ./dev_apis/crypto/test_combine.a ./val/val_nspe.a ./platform/pal_nspe.a ./dev_apis/crypto/test_combine.a $(TOPDIR)/mbed-crypto/library/libmbedcrypto.a $(TOPDIR)/$(PSA_STORAGE_DIR)/usr/local/lib/libpsastorage.so

$(TOPDIR)/psa-arch-tests/api-tests/build-crypto:
	mkdir $(TOPDIR)/psa-arch-tests/api-tests/build-crypto

$(TOPDIR)/psa-arch-tests/api-tests/build-crypto/CMakeFiles:
	cd psa-arch-tests/api-tests/build-crypto && cmake ../ -DTOOLCHAIN=HOST_GCC -DTARGET=tgt_dev_apis_stdc -DSUITE=CRYPTO -DPSA_INCLUDE_PATHS=$(TOPDIR)/mbed-crypto/include -DCPU_ARCH=armv7m

psa-arch-tests-crypto-build:
	cd $(TOPDIR)/psa-arch-tests/api-tests/build-crypto && cmake --build .

# delete the psa-arch-tests-crypto test binary
psa-arch-tests-crypto-clean:
	rm -fR $(TOPDIR)/psa-arch-tests/api-tests/build-crypto

.PHONY: test-psa-arch-tests-crypto
test-psa-arch-tests-crypto:
	$(TOPDIR)/psa-arch-tests/api-tests/build-crypto/psa-arch-tests-crypto
