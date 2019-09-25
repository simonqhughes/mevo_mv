
# Makefile to make composite project of mbed-crypto and libpsastorage

TOPDIR = $(shell pwd)
JOBDIR = ${TOPDIR}/mevo/jobs/2303
MBED_CRYPTO_PATCH1 = ${JOBDIR}/0001-Add-psa_trusted_storage_linux-persistent-storage-sup.patch 
MBED_CRYPTO_PATCH2 = ${JOBDIR}/0002-PSA-Storage-Fix-tests-to-support-PSA_STORAGE_FLAG_NO.patch 
CFLAGS="-I${TOPDIR}/psa-storage/inc -I${TOPDIR}/psa-storage/configs -DMBEDTLS_CONFIG_FILE='<mbed_crypto_psa_storage_config.h>'"
LDFLAGS="-L${TOPDIR}/psa-storage/usr/local/lib -lpsastorage"
LD_LIBRARY_PATH=$(TOPDIR)/mbed-crypto/library/:$(TOPDIR)/psa-storage/usr/local/lib
TEST_DIR="${TOPDIR}/test/"
PSA_CFLAGS="-DPSA_STORAGE_FILE_C_STORAGE_PREFIX='\"${TEST_DIR}\"'"

.PHONY: all
all: psa-arch-tests-ps

.PHONY: mbed-crypto
mbed-crypto: psa-storage-install
	make -C mbed-crypto CFLAGS=${CFLAGS} LDFLAGS=${LDFLAGS}

.PHONY: psa-storage
psa-storage:
	make -C psa-storage CFLAGS=${PSA_CFLAGS} 

.PHONY: clean
clean: mbed-crypto-clean psa-storage-clean test-clean psa-arch-tests-ps-clean

.PHONY: install
install: psa-storage-install

.PHONY: mbed-crypto-clean
mbed-crypto-clean:
	make -C mbed-crypto clean

.PHONY: psa-storage-clean
psa-storage-clean:
	make -C psa-storage clean

.PHONY: psa-storage-install
psa-storage-install: psa-storage
	make -C psa-storage install prefix=$(TOPDIR)/psa-storage/usr/local

.PHONY: mbed-crypto-patch
mbed-crypto-patch:
	# The patch should be applied against the development branch
	# The patch can be created using: git format-patch -1 HEAD
	# where the changes have been checked into the last commit.
	cd mbed-crypto && git checkout aad3dab
	cd mbed-crypto && git am < ${MBED_CRYPTO_PATCH1} && cd ..
	cd mbed-crypto && git am < ${MBED_CRYPTO_PATCH2} && cd ..

test: test-mbed-crypto-app test-mbed-crypto-its test-mbed-crypto-key test-psa-storage-app

test-mbed-crypto-app: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/programs/test && ./mbl-crypto-storage-example-app && cd ../..

test-mbed-crypto-its: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_its && cd ../..

test-mbed-crypto-key: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_crypto_persistent_key && cd ../..

test-psa-storage-app: test-dir
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd psa-storage/app && ./psa-storage-example-app && cd ../..

test-dir:
	-mkdir $(TOPDIR)/test

.PHONY: test-clean
test-clean:
	rm -fR $(TOPDIR)/test

.PHONY: manifest
manifest:
	repo manifest -r -o psa-storage-pinned-manifest.xml

# create a workspace
ws-create:
	repo init -u https://github.com/armmbed/mbl-manifest
	git clone git@github.com:armmbed/mevo mevo_create_clone
	cp $(TOPDIR)/mevo_create_clone/jobs/2303/psa-storage-manifest.xml $(TOPDIR)/.repo/manifests
	repo init -m psa-storage-manifest.xml
	repo sync
	rm -IR $(TOPDIR)/mevo_create_clone

ws-create-pinned:
	repo init -u https://github.com/armmbed/mbl-manifest
	git clone git@github.com:armmbed/mevo mevo_create_clone
	cp $(TOPDIR)/mevo_create_clone/jobs/2303/psa-storage-pinned-manifest.xml $(TOPDIR)/.repo/manifests
	repo init -m psa-storage-pinned-manifest.xml
	repo sync
	rm -IR $(TOPDIR)/mevo_create_clone

# delete the workspace
ws-delete:
	rm -IR $(TOPDIR)/mevo
	rm -IR $(TOPDIR)/psa-storage
	rm -IR $(TOPDIR)/.repo
	rm -IR $(TOPDIR)/mbed-crypto


# working on new targets to build psa-arch-tests project

#TODO: rename psa-storage to psa_trusted_storage_linux
PSA_STORAGE_DIR=psa-storage
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

main.o:
	gcc -Wall -Werror -c -o ./$(PSA_ARCH_TEST_BOILERPATE_DIR)/resources/psa-arch-tests/main.o ./mbedtls-test/resources/psa-arch-tests/main.c


.PHONY: test-psa-arch-tests-ps
test-psa-arch-tests-ps:
	$(TOPDIR)/psa-arch-tests/api-tests/build-ps/psa-arch-tests-ps
