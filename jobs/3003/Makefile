
# Makefile to make composite project of mbed-crypto and libpsastorage

TOPDIR = $(shell pwd)
CFLAGS="-I${TOPDIR}/psa-storage/inc -I${TOPDIR}/psa-storage/configs -DMBEDTLS_CONFIG_FILE='<psa_storage_config.h>'"
LDFLAGS="-L${TOPDIR}/psa-storage/usr/local/lib -lpsastorage"
LD_LIBRARY_PATH=$(TOPDIR)/mbed-crypto/library/:$(TOPDIR)/psa-storage/usr/local/lib

.PHONY: all
all: mbed-crypto 

.PHONY: mbed-crypto
mbed-crypto: psa-storage-install
	make -C mbed-crypto CFLAGS=${CFLAGS} LDFLAGS=${LDFLAGS}

.PHONY: psa-storage
psa-storage:
	make -C psa-storage

.PHONY: clean
clean: mbed-crypto-clean psa-storage-clean

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
	make -C psa-storage install PREFIX_DEFAULT=$(TOPDIR)/psa-storage/usr/local


test:
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_crypto_persistent_key && cd ../..
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/programs/test && ./mbl-crypto-storage-example-app && cd ../..

manifest: psa-storage-pinned-manifest.xml
	repo manifest -r -o psa-storage-pinned-manifest.xml
