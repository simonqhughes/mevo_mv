#!/usr/bin/env python

"""
##############################################################################
# mbl_tool.py
#  mbl tool to help with build automation 
#
# DEPENDENCIES  
# - Depends on repo tool being installed and on the path.
# - Github ssh keys installed for user so repo can use git ssh transport
#   and authentication.
##############################################################################
# Versions
# 0.0.1  20171005 Prototyping and investigation of problems. 
##############################################################################
"""

import subprocess
import time
import datetime
import argparse
import sys
import os               # getenv()
import shutil           # for rmtree()
import re
import cmd


# error codes are positive numbers because sys.exit() returns a +ve number to the env
MBL_SUCCESS = 0
MBL_FAILURE = 1
MBL_ERROR_MAX = 2


WS_NAME="sdh_dev_mx1001"
TEST_MANIFEST_NAME="default_test_01.xml"
BUILD_SCRIPT="do_build.sh"

##############################################################################
# mbl_tool
#   tool for automating mbed linux distro builds to help locate commits 
#   that break builds/working images. 
##############################################################################
class mbl_tool:
    
    def do_bash_cmd(self, strBashCommand):
        ret = subprocess.call(strBashCommand.split(), shell=False)
        return ret



if __name__ == "__main__":

    ret = MBL_FAILURE
    app = mbl_tool()

    # command line argment setup and parsing
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    bashCommand = """echo Hello"""
    ret = app.do_bash_cmd(bashCommand)
    
    # create new dir for workspace with sdh_dev_mx as root
    ret = app.do_bash_cmd("mkdir " + WS_NAME)
    
    # cd into ws and  repo init using ssh
    cmd = "cd " + WS_NAME + " && repo init -u ssh://git@github.com/armmbed/mbl-manifest.git -b master -m default.xml"
    subprocess.call(cmd, shell=True)
    
    # cp new manifest.xml with revisions for testing
    cmd = "cp " + TEST_MANIFEST_NAME + " " + WS_NAME + "/.repo/manifests"
    ret = app.do_bash_cmd(cmd)

    # repo init with new manifest
    cmd = "cd " + WS_NAME + " && repo init -m " + TEST_MANIFEST_NAME
    #ret = app.do_bash_cmd(cmd)
    subprocess.call(cmd, shell=True)

    # repo sync
    cmd = "cd " + WS_NAME + " && repo sync"
    #ret = app.do_bash_cmd(cmd)
    subprocess.call(cmd, shell=True)

    # source the environment && bitbake
    cmd = "cd " + WS_NAME + " && ln -s /data/2284/shared_downloads downloads"
    subprocess.call(cmd, shell=True)
    
    # cp the do_build.sh to the top level dir
    cmd = "cp " + BUILD_SCRIPT + " " + WS_NAME + "/"
    #ret = app.do_bash_cmd(cmd)
    subprocess.call(cmd, shell=True)

    cmd = "cd " + WS_NAME  + " && ./do_build.sh"
    print cmd
    #ret = app.do_bash_cmd(WS_NAME + "do_build.sh")
    subprocess.call(cmd, shell=True)

    sys.exit(ret)
    
