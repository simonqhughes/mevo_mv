#!/bin/bash

nohup bitbake mbl-image-production 2>&1 | tee build_`date "+%Y%m%d-%H%M%S"`.txt
rm -fR tmp-mbl-glibc ../sstate-cache cache 

