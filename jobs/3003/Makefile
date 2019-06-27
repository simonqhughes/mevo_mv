
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
	make -C psa-storage install prefix=$(TOPDIR)/psa-storage/usr/local


test:
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_crypto_persistent_key && cd ../..
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/tests && ./test_suite_psa_its && cd ../..
	export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) && cd mbed-crypto/programs/test && ./mbl-crypto-storage-example-app && cd ../..

.PHONY: manifest
manifest:
	repo manifest -r -o psa-storage-pinned-manifest.xml

# create a workspace
ws_create:
	repo init -u https://github.com/armmbed/mbl-manifest
	git clone git@github.com:armmbed/mevo mevo_create_clone
	cp $(TOPDIR)/mevo_create_clone/jobs/3003/psa-storage-manifest.xml $(TOPDIR)/.repo/manifests
	repo init -m psa-storage-manifest.xml
	repo sync
	rm -IR $(TOPDIR)/mevo_create_clone

# delete the workspace
ws_delete:
	rm -IR $(TOPDIR)/mevo
	rm -IR $(TOPDIR)/psa-storage
	rm -IR $(TOPDIR)/.repo
	rm -IR $(TOPDIR)/mbed-crypto
