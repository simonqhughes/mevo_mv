#!/usr/bin/env python

"""
##############################################################################
# mbed_jenkins.py
#  jenkins Automation Testworks (mAT) python script for automating mbedmicro 
#  builds.
#
#
# Jenkins dependencies:
#  CMake is on the path
#  arm-none-eabi-gcc is on the path
#
# This is how the windows path looks at the present time:
# /h/bin:.:/usr/local/bin:/mingw/bin:/bin:/c/windows/system32:
# /c/windows:/c/windows/System32/Wbem:
# /c/windows/System32/WindowsPowerShell/v1.0/:
# /c/Program Files (x86)/GnuWin32/bin:
# /c/mbed_tools/Python27:
# /c/mbed_tools/Python27/Scripts:
# /bin:
# /c/mbed_tools/ARMCompiler_5.03_117_Windows/bin:
# /c/mbed_tools/scripts:/c/mbed_tools/CMake/bin:
# /c/mbed_tools/GnuWin32/bin:
# /c/mbed_tools/gcc-arm-none-eabi-4_9-2014q4-20141203-win32/bin
#
# windows pexpect
# ===============
# working to get pexpect installed.
#  pip install resource
# need to install xunitparser with:
#  pip install xunitparser
# for nordic nrf51822 singletest.py which invokes 
#   <src_root>/workspace_tools\targets.py
# need to install intelhex
#  pip install intelhex
#
##############################################################################
# Versions
# 0.0.1  20150320 SDH first version that works. 
# 0.0.2  20150409 add junit xml support to check for failures.
# 0.0.3  20150410 correcting errors, adding correct error processing 
# 0.0.4  20150410 enhancing trace, first version working with arm_cc 
# 0.0.5  20150413 added html tracing to jobs, open(..., "w+"), uARM support 
# 0.0.6  20150414 version upto 1251. 
# 0.0.7  20150414 ARMCompiler_5.03_117_Windows support
# 0.0.8  20150512 add removal of test_spec.json and muts_all.json if present to
#                 clean operation 
# 0.0.9  20150609 integrating with mbed_usb.py
#                  
# todo: check for failures in junit xml as well as errors.
#
# todo:
# - document functions/classes
# - configure arm_cc
# - configure ublox, seed and F091 with muts/test_spec
##############################################################################
"""

import subprocess
import time
import datetime
import argparse
import sys
import xunitparser
import os               # getenv()
import shutil           # for rmtree()
import re
import mbed_usb


# error codes are positive numbers because sys.exit() returns a +ve number to the env
MBED_SUCCESS = 0
MBED_FAILURE = 1
MBED_ERROR_MAX = 2

# terminology
#
# mAT   mbed Automation Testworks

KEIL_PATH = "c:/mbed_tools/ARMCompiler_5.03_117_Windows/bin" 
# note no /bin on the end of the ARM_PATH
#ARM_PATH = "c:/mbed_tools/DS-5"
#ARM_PATH_2 = "C:/mbed_tools/ARMCompiler_5.03_117_Windows"
ARM_PATH = "C:/mbed_tools/ARMCompiler_5.03_117_Windows"

GCC_ARM_PATH = "c:/mbed_tools/gcc-arm-none-eabi-4_9-2014q4-20141203-win32/bin"

# GCC CodeSourcery
# todo: remove
#GCC_CS_PATH = "C:/Program Files (x86)/CodeSourcery/Sourcery_CodeBench_Lite_for_ARM_EABI/bin"
GCC_CS_PATH = "C:/mbed_tools/CodeSourcery/Sourcery_CodeBench_Lite_for_ARM_EABI/bin"


# GCC CodeRed
# todo: remove
#GCC_CR_PATH = "C:/LPCXpresso_7.1.1_125/lpcxpresso/tools/bin"
GCC_CR_PATH = "C:/mbed_tools/nxp/LPCXpresso_7.1.1_125/lpcxpresso/tools/bin"

# IAR
# todo: remove
#IAR_PATH = "C:/Program Files (x86)/IAR Systems/Embedded Workbench 7.0/arm"
IAR_PATH = "C:/mbed_tools/IAR Systems/Embedded Workbench 7.0/arm"

WRKSPC_TOOLS_DIR="workspace_tools"
TEST_SPC_JSN_PATHNAME = WRKSPC_TOOLS_DIR + "/test_spec.json"
MUTS_ALL_JSN_PATHNAME = WRKSPC_TOOLS_DIR + "/muts_all.json"
 

g_debug = True

# a debug trace function
#def dbg(str):
#    if g_debug is True:
#        print str
#    return

def dbg(str):
    print str
    return


# todo:
# code to get drive letter of mbedls K64 device
# $ mbedls | grep K64F | awk '{print $2}' | sed 's/^.\(.*\).$/\1/'
# code to get the com port of mbedls K64 device
# mbedls | grep K64F | awk '{print $3}' | sed 's/^.//'

# s091 id: 075002000750051938359374
# get the com port: mbedls | grep 075002000750051938359374 | awk '{print $3}' | sed 's/^.//'
# get the mds: mbedls | grep 075002000750051938359374 | awk '{print $2}' | sed 's/^.//'

# exception for breaking out of loops
class BreakInnerLoop(Exception): pass

##############################################################################
# jenkins
##############################################################################
class mbed_jenkins:
    """A class to manage jenkins builds/test"""
    TARGET_ID_DEF = '000000000000000000000000'

    #def __init__(self):

    # function to execute a bash command

    def dbg(self, str):
        print str
        return

    def doBashCmd(self, strBashCommand):
        ret = subprocess.call(strBashCommand.split(), shell=True)
        return ret

    def build20(self, toolchain, target):
        # do the build:
        # python.exe build.py -t GCC_ARM -m LPC1768

        dbg(sys._getframe().f_code.co_name + ":entered.")
        ret = MBED_SUCCESS 
        if args.build is True:
            if args.jenkins is True: 
                bashCommand = "python ./workspace_tools/" + "build.py -t " + toolchain + " -m " + target
            else:
                # cmdline
                bashCommand = "python " + args.project + "/workspace_tools/" + "build.py -t " + toolchain + " -m " + target
            ret = self.doBashCmd(bashCommand)
        return ret    

    def clone20(self):
        dbg(sys._getframe().f_code.co_name + ":entered.")
        ret = MBED_SUCCESS 
        if args.clone is True:
            if args.jenkins is True: 
                bashCommand = "git clone https://github.com/mbedmicro/mbed.git"
            else:
                # cmdline
                # clone the repository into a folder called args.project
                bashCommand = "git clone https://github.com/mbedmicro/mbed.git " + args.project
            ret = self.doBashCmd(bashCommand)
        return ret    

    def make_private_settings20(self, args):
        dbg(sys._getframe().f_code.co_name + ":entered.") 
        if args.jenkins is True: 
            if args.toolchain == "GCC_ARM": 
                with open("./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("GCC_ARM_PATH = \"" + GCC_ARM_PATH + "\"")
                    
            if args.toolchain == "ARM": 
                with open("./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("from os.path import join\n")
                    text_file.write("\n")
                    text_file.write("ARM_PATH = \"" + ARM_PATH + "\"\n")
                    text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
                    text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
                    text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
                    text_file.write("ARM_CPPLIB = join(ARM_LIB, \"cpplib\")\n")
                    text_file.write("\n")
                    
            if args.toolchain == "uARM": 
                with open("./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("from os.path import join\n")
                    text_file.write("\n")
                    text_file.write("ARM_PATH = \"" + ARM_PATH + "\"\n")
                    text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
                    text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
                    text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
                    text_file.write("ARM_CLIB = join(ARM_PATH, \"lib\", \"microlib\")\n")
                    text_file.write("\n")
                   
            if args.toolchain == "uARM2": 
                with open("./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("from os.path import join\n")
                    text_file.write("\n")
                    text_file.write("ARM_PATH = \"" + ARM_PATH_2 + "\"\n")
                    text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
                    text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
                    text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
                    text_file.write("ARM_CLIB = join(ARM_PATH, \"lib\", \"microlib\")\n")
                    text_file.write("\n")
                   
        else:
            # cmdline
            if args.toolchain == "GCC_ARM": 
                with open(args.project + "/workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("GCC_ARM_PATH = \"" + GCC_ARM_PATH + "\"")

            if args.toolchain == "ARM": 
                with open(args.project + "./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("from os.path import join\n")
                    text_file.write("\n")
                    text_file.write("ARM_PATH = \"" + ARM_PATH + "\"\n")
                    text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
                    text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
                    text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
                    text_file.write("ARM_CPPLIB = join(ARM_LIB, \"cpplib\")\n")
                    text_file.write("\n")

            if args.toolchain == "uARM": 
                with open(args.project + "./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("from os.path import join\n")
                    text_file.write("\n")
                    text_file.write("ARM_PATH = \"" + ARM_PATH + "\"\n")
                    text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
                    text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
                    text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
                    text_file.write("ARM_CLIB = join(ARM_PATH, \"lib\", \"microlib\")\n")
                    text_file.write("\n")

            if args.toolchain == "uARM2": 
                with open(args.project + "./workspace_tools/private_settings.py", "w+") as text_file:
                    text_file.write("from os.path import join\n")
                    text_file.write("\n")
                    text_file.write("ARM_PATH = \"" + ARM_PATH_2 + "\"\n")
                    text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
                    text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
                    text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
                    text_file.write("ARM_CLIB = join(ARM_PATH, \"lib\", \"microlib\")\n")
                    text_file.write("\n")

        return MBED_SUCCESS       

    def print_test_header(self):
        """ 
        function to print useful test related information e.g.
            - command line arguments of invoking function
            - PATH settings
        """
        print os.environ.get('KEY_THAT_MIGHT_EXIST') 


    def mbed20_clean(self, args):
        """
        Clean the build directory from project directory. Note the singletest.py --clean doesnt work at present
        
        args.project        used for the top level subdirectory
        """
        ret1 = MBED_FAILURE
        ret2 = MBED_FAILURE
        
        filepath = ""
        
        
        if args.clean is True:
            if args.jenkins is True:
                filepath = "./"
            else:
                filepath = args.project + "/"
        
            filepath += "build"
            if os.path.exists(filepath):
                shutil.rmtree(filepath)
                
            ret1 = self.mbed20_test_spec_json_del(args)
            ret2 = self.mbed20_muts_all_json_del(args)
                
            if ret1 == MBED_SUCCESS:
                if ret2 == MBED_SUCCESS:
                    return MBED_SUCCESS
                else:
                    return ret2
            else:
                return ret1

        return MBED_FAILURE

    def mbed20_generate_json_test_spec_files(self, args):
        """
        """
        self.dbg(sys._getframe().f_code.co_name + ":entered.") 
        
        ret = MBED_FAILURE
        filepath = ""
        if args.jenkins is True:
            filepath = "./workspace_tools/"
        else:
            filepath = args.project + "/workspace_tools/"
    
        # todo: remove print args.target_id

        print "args.comport=" + args.comport
        print "args.disk=" + args.disk

        if args.target_id != self.TARGET_ID_DEF:
            name = ""
            comport = ""
            disk = ""
            target_id = 0
            
            # now make json files:
            ret = self.mbed20_test_spec_json_add(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to create test_spec.json.") 
                return ret

            # use regex to find platform identified with target_is in mbedls output, and parse for comport and disk 
            mbedls_cmd = "mbedls > " + filepath + "mbedls_output.txt"
            ret = self.doBashCmd(mbedls_cmd)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to get mbedls output.") 
                return ret

            # find the target id in the mbedls output
            # note: this isnt working as I expected. todo: investigate
            pattern = re.compile(str(args.target_id))
            
            # search the mbedls output to find the line with the target_id, so the comport and disk can
            # be extracted
            try:
                for i, line in enumerate(open(filepath + "mbedls_output.txt")):
    
                    for match in re.finditer(pattern, line):
                        print 'Found on line %s: %s' % (i+1, match.groups())
                        print line
                        # s= "| 'TOMATOES_PICKED'                                  |       914 |       1397 |"
                        # |unknown              |G:                 |COM18              |075002000750051938359374                |                        
                        pattern = re.compile(r"""\|\s*                 # opening bar and whitespace
                                                 (?P<name>.*?)       # name
                                                 \s*\|\s*(?P<disk>.*?)   # whitespace, next bar, n1
                                                 \s*\|\s*(?P<comport>.*?)      # whitespace, next bar, n2
                                                 \s*\|\s*(?P<target_id>.*?)      # whitespace, next bar, n2
                                                 \s*\|""", re.VERBOSE)
                        match = pattern.match(line)
                    
                        name = match.group("name")
                        comport = match.group("comport")
                        disk = match.group("disk")
                        target_id = match.group("target_id")
                        
                        if args.target_id == target_id:
                            # found the target_id 
                            raise BreakInnerLoop
    
                        dbg(sys._getframe().f_code.co_name + ": comport=" + comport) 
                        dbg(sys._getframe().f_code.co_name + ": disk=" + disk) 

            except BreakInnerLoop:
                pass
           
            if comport == "":
                dbg(sys._getframe().f_code.co_name + ": failed to find valid values for comport.") 
                return MBED_FAILURE;
            
            if disk == "":
                dbg(sys._getframe().f_code.co_name + ": failed to find valid values for disk.") 
                return MBED_FAILURE;
            
            ret = self.mbed20_muts_all_json_add(args, comport, disk)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to create muts_all.json.") 
                return ret;
 
        elif args.comport != "" and args.disk != "":

            # now make json files:
            ret = self.mbed20_test_spec_json_add(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to create test_spec.json.") 
                return ret

            ret = self.mbed20_muts_all_json_add(args, args.comport, args.disk)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to create muts_all.json.") 
                return ret;
    
        return ret            
    
    def singletest(self, args):
        """
        Supported target list is stated in workspace_tools/targets.py and as of 20150410 the list is as follows:
        ['APPNEARME_MICRONFCBOARD', 'ARCH_BLE', 'ARCH_GPRS', 'ARCH_MAX', 'ARCH_PRO', 'ARM_MPS2', 'ARM_MPS2_M0', 
        'ARM_MPS2_M0P', 'ARM_MPS2_M1', 'ARM_MPS2_M3', 'ARM_MPS2_M4', 'ARM_MPS2_M7', 'DELTA_DFCM_NNN40', 
        'DELTA_DFCM_NNN40_OTA', 'DISCO_F051R8', 'DISCO_F100RB', 'DISCO_F303VC', 'DISCO_F334C8', 
        'DISCO_F401VC', 'DISCO_F407VG', 'DISCO_F429ZI', 'DISCO_L053C8', 'HRM1017', 'K20D50M', 
        'K22F', 'K64F', 'KL05Z', 'KL25Z', 'KL43Z', 'KL46Z', 'LPC1114', 'LPC11C24', 'LPC11U24', 
        'LPC11U24_301', 'LPC11U34_421', 'LPC11U35_401', 'LPC11U35_501', 'LPC11U35_Y5_MBUG', 
        'LPC11U37H_401', 'LPC11U37_501', 'LPC11U68', 'LPC1347', 'LPC1549', 'LPC1768', 'LPC2368', 
        'LPC4088', 'LPC4088_DM', 'LPC4330_M0', 'LPC4330_M4', 'LPC4337', 'LPC810', 'LPC812', 
        'LPC824', 'LPCCAPPUCCINO', 'MAXWSNENV', 'MTS_DRAGONFLY_F411RE', 'MTS_GAMBIT', 
        'MTS_MDOT_F405RG', 'MTS_MDOT_F411RE', 'NRF51822', 'NRF51822_BOOT', 'NRF51822_OTA', 
        'NRF51822_Y5_MBUG', 'NRF51_DK', 'NRF51_DK_BOOT', 'NRF51_DK_OTA', 'NRF51_DONGLE', 
        'NUCLEO_F030R8', 'NUCLEO_F070RB', 'NUCLEO_F072RB', 'NUCLEO_F091RC', 'NUCLEO_F103RB', 
        'NUCLEO_F302R8', 'NUCLEO_F303RE', 'NUCLEO_F334R8', 'NUCLEO_F401RE', 'NUCLEO_F411RE', 
        'NUCLEO_L053R8', 'NUCLEO_L073RZ', 'NUCLEO_L152RE', 'OC_MBUINO', 'RBLAB_BLENANO', 
        'RBLAB_NRF51822', 'RZ_A1H', 'SEEED_TINY_BLE', 'SEEED_TINY_BLE_BOOT', 
        'SEEED_TINY_BLE_OTA', 'SSCI824', 'STM32F3XX', 'STM32F407', 'TEENSY3_1', 
        'UBLOX_C027', 'UBLOX_C029', 'WALLBOT_BLE', 'XADOW_M0']
        """
        dbg(sys._getframe().f_code.co_name + ":entered.")

        # run singletest
        filepath = ""
        comport = ""
        disk = ""
        cmd = "python "
        if args.test is True:
        
            if args.jenkins is True:
                filepath = "./workspace_tools/"
            else:
                # cmdline
                filepath = args.project + "/workspace_tools/"
                
            cmd += filepath + "singletest.py "
            #cmd += "-f " + args.target + " --tc=" + args.toolchain + " -j 8 -v --report-junit " + args.target + "_junit_report.xml" + " --report-html " + args.target + "_html_report.html -c cp "
            # windows prefers copy
            cmd += "-f " + args.target + " --tc=" + args.toolchain + " -j 8 -v --report-junit " + args.target + "_junit_report.xml" + " --report-html " + args.target + "_html_report.html -c copy --global-loops 5 -W "
            
            if args.target_id != self.TARGET_ID_DEF:
                cmd += "-i " + filepath + "test_spec.json -M  " + filepath + "muts_all.json "
                
                # now make json files:
                ret = self.mbed20_generate_json_test_spec_files(args)
                if ret != MBED_SUCCESS:
                    dbg(sys._getframe().f_code.co_name + ": failed to create test_spec.json and muts_all.json files.") 
                    return ret
            elif args.comport != "" and args.disk != "":
                cmd += "-i " + filepath + "test_spec.json -M  " + filepath + "muts_all.json "
                
                # now make json files:
                ret = self.mbed20_generate_json_test_spec_files(args)
                if ret != MBED_SUCCESS:
                    dbg(sys._getframe().f_code.co_name + ": failed to create test_spec.json and muts_all.json files.") 
                    return ret
            
            else:
                cmd += "--auto "
            

            dbg(sys._getframe().f_code.co_name + ": running:" + cmd) 
            ret = self.doBashCmd(cmd)

        return ret    

    def singletest_working_version(self, toolchain, target):
        """
        Supported target list is stated in workspace_tools/targets.py and as of 20150410 the list is as follows:
        ['APPNEARME_MICRONFCBOARD', 'ARCH_BLE', 'ARCH_GPRS', 'ARCH_MAX', 'ARCH_PRO', 'ARM_MPS2', 'ARM_MPS2_M0', 
        'ARM_MPS2_M0P', 'ARM_MPS2_M1', 'ARM_MPS2_M3', 'ARM_MPS2_M4', 'ARM_MPS2_M7', 'DELTA_DFCM_NNN40', 
        'DELTA_DFCM_NNN40_OTA', 'DISCO_F051R8', 'DISCO_F100RB', 'DISCO_F303VC', 'DISCO_F334C8', 
        'DISCO_F401VC', 'DISCO_F407VG', 'DISCO_F429ZI', 'DISCO_L053C8', 'HRM1017', 'K20D50M', 
        'K22F', 'K64F', 'KL05Z', 'KL25Z', 'KL43Z', 'KL46Z', 'LPC1114', 'LPC11C24', 'LPC11U24', 
        'LPC11U24_301', 'LPC11U34_421', 'LPC11U35_401', 'LPC11U35_501', 'LPC11U35_Y5_MBUG', 
        'LPC11U37H_401', 'LPC11U37_501', 'LPC11U68', 'LPC1347', 'LPC1549', 'LPC1768', 'LPC2368', 
        'LPC4088', 'LPC4088_DM', 'LPC4330_M0', 'LPC4330_M4', 'LPC4337', 'LPC810', 'LPC812', 
        'LPC824', 'LPCCAPPUCCINO', 'MAXWSNENV', 'MTS_DRAGONFLY_F411RE', 'MTS_GAMBIT', 
        'MTS_MDOT_F405RG', 'MTS_MDOT_F411RE', 'NRF51822', 'NRF51822_BOOT', 'NRF51822_OTA', 
        'NRF51822_Y5_MBUG', 'NRF51_DK', 'NRF51_DK_BOOT', 'NRF51_DK_OTA', 'NRF51_DONGLE', 
        'NUCLEO_F030R8', 'NUCLEO_F070RB', 'NUCLEO_F072RB', 'NUCLEO_F091RC', 'NUCLEO_F103RB', 
        'NUCLEO_F302R8', 'NUCLEO_F303RE', 'NUCLEO_F334R8', 'NUCLEO_F401RE', 'NUCLEO_F411RE', 
        'NUCLEO_L053R8', 'NUCLEO_L073RZ', 'NUCLEO_L152RE', 'OC_MBUINO', 'RBLAB_BLENANO', 
        'RBLAB_NRF51822', 'RZ_A1H', 'SEEED_TINY_BLE', 'SEEED_TINY_BLE_BOOT', 
        'SEEED_TINY_BLE_OTA', 'SSCI824', 'STM32F3XX', 'STM32F407', 'TEENSY3_1', 
        'UBLOX_C027', 'UBLOX_C029', 'WALLBOT_BLE', 'XADOW_M0']
        """
        dbg(sys._getframe().f_code.co_name + ":entered.")

        # run singletest
        filepath = ""
        comport = ""
        disk = ""
        cmd = "python "
        if args.test is True:
        
            if args.jenkins is True:
                filepath = "./workspace_tools/"
            else:
                # cmdline
                filepath = args.project + "/workspace_tools/"
                
            cmd += filepath + "singletest.py "
            cmd += "-f " + target + " --tc=" + toolchain + " -j 8 -v --report-junit " + target + "_junit_report.xml" + " --report-html " + target + "_html_report.html -c cp "
            
            print args.target_id
            if args.target_id != self.TARGET_ID_DEF:
                cmd += "-i " + filepath + "test_spec.json -M  " + filepath + "muts_all.json "
                
                # now make json files:
                ret = self.mbed20_test_spec_json_add(args)
                if ret != MBED_SUCCESS:
                    dbg(sys._getframe().f_code.co_name + ": failed to create test_spec.json.") 
                    return ret

                # doesnt work: python rc
                mbedls_cmd = "mbedls > " + filepath + "mbedls_output.txt"
                dbg(sys._getframe().f_code.co_name + ": mbedls_cmd=" + mbedls_cmd) 
                #print comport_cmd

                ret = self.doBashCmd(mbedls_cmd)
                if ret != MBED_SUCCESS:
                    dbg(sys._getframe().f_code.co_name + ": failed to get mbedls output.") 
                    return ret

                pattern = re.compile(args.target_id)
                
                for i, line in enumerate(open(filepath + "mbedls_output.txt")):

                    for match in re.finditer(pattern, line):
                        print 'Found on line %s: %s' % (i+1, match.groups())
                        print line
                        # s= "| 'TOMATOES_PICKED'                                  |       914 |       1397 |"
                        # |unknown              |G:                 |COM18              |075002000750051938359374                |                        
                        pattern = re.compile(r"""\|\s*                 # opening bar and whitespace
                                                 (?P<name>.*?)       # name
                                                 \s*\|\s*(?P<disk>.*?)   # whitespace, next bar, n1
                                                 \s*\|\s*(?P<comport>.*?)      # whitespace, next bar, n2
                                                 \s*\|\s*(?P<target_id>.*?)      # whitespace, next bar, n2
                                                 \s*\|""", re.VERBOSE)
                        match = pattern.match(line)
                    
                        comport = match.group("comport")
                        disk = match.group("disk")

                        dbg(sys._getframe().f_code.co_name + ": comport=" + comport) 
                        dbg(sys._getframe().f_code.co_name + ": disk=" + disk) 
                
                ret = self.mbed20_muts_all_json_add(args, comport, disk)
                if ret != MBED_SUCCESS:
                    dbg(sys._getframe().f_code.co_name + ": failed to create muts_all.json.") 
                    return ret;
                
            else:
                cmd += "--auto "
            

            dbg(sys._getframe().f_code.co_name + ": running:" + cmd) 
            ret = self.doBashCmd(cmd)

        return ret    


    def mbed20(self, args):
        """
        Top level target for mbed 2.0 build/test operations. This command 
        is typically invoked by jenkins after cloning the git repository.
        this can be done manually with:
            git clone https://github.com/mbedmicro/mbed.git
        
        args.build      set true if a build step is required.
        args.test       set true if a test step is required.
        
        """
        dbg(sys._getframe().f_code.co_name + ":entered.")
        ret = MBED_FAILURE 

        # quick hack to support build_release.py
        if args.build_release is True:
            ret = self.mbed20_build_release(args)
            return ret 

        if args.clean is True:
            ret = self.mbed20_clean(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to clean local workspace.") 
                return ret;

        # clone is used on the command line; jenkins the clone is setup by project
        if args.clone is True:
            ret = self.clone20()
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to clone repository.") 
                return ret;

        
        # write test_spec.json and muts_all.json if performing NET_X testing
        if args.test_net is True:
            ret = self.mbed20_test_netx(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": mbed20_test_netx() failed.") 
                return ret;

        if args.build is True:
            self.make_private_settings20(args)
            ret = self.build20(args.toolchain, args.target)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to build clone.") 
                return ret;
        
        if args.target_pwr_restart is True:
            ret = self.target_pwr_restart(args) 
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": singletest failed.") 
                return ret;
        
        if args.test is True:
            ret = self.singletest(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": singletest failed.")
                
                # turn target off if it was started
                if args.target_pwr_restart is True:
                    self.target_pwr_off(args) 
                return ret;

            # check the junit test results
            filename = args.target + '_junit_report.xml'
            dbg(sys._getframe().f_code.co_name + ": filename=." + filename) 
            ts, tr = xunitparser.parse(open(filename))
    
            # check the test results.
            # if there are any errors, then the tr.errors list will be non-empty i.e.:
            # errors is a list containing 2-tuples of TestCase instances and strings 
            # holding formatted tracebacks. Each tuple represents a test which raised 
            # an unexpected exception. 
            
            if tr.errors:
                # tr.errors is true because its non-empty i.e. there have been errors
                print('error!')
                ret = MBED_FAILURE
            else:
                print('no errors')
                ret = MBED_SUCCESS

        if args.target_pwr_restart is True:
            self.target_pwr_off(args) 

        return ret

    def mbed20_build_release(self, args):
        """
        Top level target for running mbed 2.0 build_release.py. This command 
        is typically invoked by jenkins after cloning the git repository.
        this can be done manually with:
            git clone https://github.com/mbedmicro/mbed.git

        # mbed_jenkins.py --jenkins --mbed20  --project mbedmicro --clone --build-release

        
        args.build_release      set true if build_release is required
        args.build_release      set true if build_release is required
        args.jenkins            set true if running under jenkins (optional)
        args.mbed20             do build release for mbed2.0  
        arg.project             mbedmicro, name of cd to move into
        arg.clone               opt, set if clone of repo is requied. 
        
        #from os.path import join
        #
        #ARM_PATH = "C:/armcc5.03.117"
        ## ARM_PATH = "C:/Keil/ARM"
        #ARM_BIN = join(ARM_PATH,"bin")
        ## ARM_INC = join(ARM_PATH,"RV31","INC")
        ## ARM_LIB    = join(ARM_PATH,"ARMCC","lib")
        ## ARM_CPPLIB = join(ARM_PATH, "ARMCC","lib","cpplib")
        ## MY_ARM_CLIB = join(ARM_PATH, "lib", "microlib")
        # 
        ## GCC ARM
        ## GCC_ARM_PATH = "C:/arm-none-eabi-gcc-4_6/bin"
        #GCC_ARM_PATH = "C:/Program Files (x86)/GNU Tools ARM Embedded/4.8 2014q1/bin"
        # #
        ## GCC CodeSourcery
        #GCC_CS_PATH = "C:/Program Files (x86)/CodeSourcery/Sourcery_CodeBench_Lite_for_ARM_EABI/bin"
        # 
        ## GCC CodeRed
        #GCC_CR_PATH = "C:/LPCXpresso_7.1.1_125/lpcxpresso/tools/bin"
        # 
        ## IAR
        #IAR_PATH = "C:/Program Files (x86)/IAR Systems/Embedded Workbench 7.0/arm"
        """
    
        dbg(sys._getframe().f_code.co_name + ":entered.")
        ret = MBED_FAILURE

        if args.clean is True:
            ret = self.mbed20_clean(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to clean local workspace.") 
                return ret;

        if args.clone is True:
            ret = self.clone20()
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to clone repository.") 
                return ret;

        # clean if flag set by removing the build dir in workspace as clean.py doesnt work
        if args.clean is True:
            if os.path.exists("./build"):
                shutil.rmtree('./build')

        # write the private settings.py file that we need
        if args.jenkins is True:
            filepath = "./workspace_tools/private_settings.py"
        else:
            # bash command line
            filepath = args.project + "./workspace_tools/private_settings.py"
            
        #todo: del with open(args.project + "./workspace_tools/private_settings.py", "w+") as text_file:
        # todo: can 1 private_settings.py file be used for all files builds? no, uARM is not compatible.
        # the code to qrite private settings needs to be refactored into single function.
        with open(filepath, "w+") as text_file:
            text_file.write("from os.path import join\n")
            text_file.write("\n")
            text_file.write("ARM_PATH = \"" + ARM_PATH + "\"\n")
            text_file.write("ARM_BIN = join(ARM_PATH, \"bin\")\n")
            text_file.write("ARM_INC = join(ARM_PATH, \"include\")\n")
            text_file.write("ARM_LIB = join(ARM_PATH, \"lib\")\n")
            text_file.write("ARM_CPPLIB = join(ARM_LIB, \"cpplib\")\n")
            text_file.write("\n")
            text_file.write("GCC_ARM_PATH = \"" + GCC_ARM_PATH + "\"\n")
            text_file.write("\n")
            text_file.write("GCC_CS_PATH = \"" + GCC_CS_PATH + "\"\n")
            text_file.write("\n")
            text_file.write("GCC_CR_PATH = \"" + GCC_CR_PATH + "\"\n")
            text_file.write("\n")
            text_file.write("IAR_PATH = \"" + IAR_PATH + "\"\n")
            text_file.write("\n")
        
        if args.build_release is True:
            if args.jenkins is True: 
                # todo: remove trace
                dbg(sys._getframe().f_code.co_name + ":jenkins.")
                bashCommand = "python ./workspace_tools/" + "build_release.py"
            else:
                # cmdline
                # todo: remove trace
                dbg(sys._getframe().f_code.co_name + ":commandline.")
                bashCommand = "python " + args.project + "/workspace_tools/" + "build_release.py"

            ret = self.doBashCmd(bashCommand)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to run build_release.py.") 

        # check if just a sync operation is being performed
        if args.sync is True:
            ret = self.mbed20_sync(args)
            if ret != MBED_SUCCESS:
                dbg(sys._getframe().f_code.co_name + ": failed to sync repository.") 
       
        return ret

    def mbed20_muts_all_json_add(self, args, comport, disk):
        """
        write <src_root>/workspace_tools/muts_all.json with the following contents
            {
                "1" : {"mcu": "LPC1768",
                   "port":"COM6",
                   "disk":"D:\\",
                   "peripherals": []
                  },
            
            }        
            
        for NET_X testing, use something like this:    

            {
                "1" : {"mcu": "K64F",
                   "port":"COM6",
                   "disk":"D:\\",
                   "peripherals": ["ethernet"]
                  },
            
            }        
        """
        self.dbg(sys._getframe().f_code.co_name + ":entered.") 
        ret = MBED_FAILURE
        
        if args.target != "" and args.toolchain != "":

            if args.jenkins is True:
                filepath = "./workspace_tools/muts_all.json"
            else:
                # bash command line
                filepath = args.project + "./workspace_tools/muts_all.json"

            with open(filepath, "w+") as text_file:
                text_file.write("{\n")
                text_file.write("    \"1\" : {\"mcu\": \"" + args.target + "\",\n")
                text_file.write("           \"port\": \"" + comport + "\",\n")
                text_file.write("           \"disk\": \"" + disk + "\",\n")
                if args.test_net is True:
                    text_file.write("           \"peripherals\": [ \"ethernet\" ]\n")
                else:
                    text_file.write("           \"peripherals\": []\n")
                text_file.write("    }\n")
                text_file.write("}\n")

            ret = MBED_SUCCESS

        return ret;        
         

    def mbed20_muts_all_json_del(self, args):
        """
        delete the muts_all.json file if present.
        """
        self.dbg(sys._getframe().f_code.co_name + ":entered.")
        filepath = "" 
        
        if args.jenkins is True:
            #todo: delete filepath = "./workspace_tools/muts_all.json"
            filepath = "./" + MUTS_ALL_JSN_PATHNAME
            # 
        else:
            # bash command line
            # todo: delete filepath = args.project + "./workspace_tools/muts_all.json"
            filepath = args.project + "/" + MUTS_ALL_JSN_PATHNAME

        # delete file
        if os.path.exists(filepath):
            os.remove(filepath)

        return MBED_SUCCESS        

    def mbed20_sync(self, args):
        """
        work out if this is the second monday in the month and if it is then 
        invoke <src_root>/workspace_tools/sync.py to push release to mbed.org private fork 
        as part of the mbed2.0 release process 

        # mbed_jenkins.py --jenkins --mbed20 --build-release --sync
        
        # this re-uses the same workspace for the build-release was done

        """
        
        dbg(sys._getframe().f_code.co_name + ":entered.")
        days_of_week = {'mon' : 0, 'tue' : 1, 'wed' : 2, 'thu' : 3, 'fri' : 4, 'sat' : 5, 'sun' : 6}
        week_types = {'even' : 0, 'odd' : 1}
        ret = MBED_FAILURE

        # syncing of releases performed on even weeks at midnight on monday
        # configure {day, week} tuple to do release on
        release_day_of_week = 'mon'       # this is the correct day     
        #release_day_of_week = 'tue'         # day for testing today
        # release_week = 'even'             # this is the week we release on
        release_week = 'odd'                # week for testing today
        
        # today will be 0 if this is a monday
        today = datetime.date.today()
        
        if today.weekday() == days_of_week[release_day_of_week]:
            # today is release day; 
            # releases done every 2w currently on odd week
            
            # the iso calendar iso = (year, week, day) i.e. 1st element week = iso_cal[1]
            iso_cal = today.isocalendar()
            week = iso_cal[1]
            
            if week % 2 == week_types[release_week]:
                print "Make Release: today is " + release_day_of_week + " which is a release day, and the week is " + release_week +"(" + str(week) + ") so make release\n"
                
                # run the sync script
                if args.jenkins is True: 
                    # synch.py -m option for mbed, -n option for no push 
                    bashCommand = "python ./workspace_tools/" + "synch.py -m -n"
                else:
                    # cmdline
                    bashCommand = "python " + args.project + "/workspace_tools/" + "synch.py -m -n"
                ret = self.doBashCmd(bashCommand)
            else:
                print "Make No Release: today is " + release_day_of_week + " which is a release day, but the week is " + release_week + "(" + str(week) + ") so make no release\n"
                ret = MBED_SUCCESS   
            
        else:
            print "Make No Release: today is not the release day of the week, which is " +release_day_of_week + "\n"
            ret = MBED_SUCCESS   
            
        return ret

    def mbed20_test_netx(self, args):
        """
        """
        dbg(sys._getframe().f_code.co_name + ":entered.")
    
        ret = MBED_FAILURE
        ret = self.mbed20_generate_json_test_spec_files(args)
        return ret 

    def mbed20_test_spec_json_add(self, args):
        """
        write <src_root>/workspace_tools/test_spec.json with the following contents
            {
                "targets": {
                "LPC1768" : ["GCC_ARM"]
                }
            }
        """
        dbg(sys._getframe().f_code.co_name + ":entered.") 
        ret = MBED_FAILURE
        
        if args.target != "" and args.toolchain != "":

            if args.jenkins is True:
                # todo: delete filepath = "./workspace_tools/test_spec.json"
                filepath = "./" + TEST_SPC_JSN_PATHNAME
                
            else:
                # bash command line
                # todo: delete filepath = args.project + "./workspace_tools/test_spec.json"
                filepath = args.project + "./" + TEST_SPC_JSN_PATHNAME

            with open(filepath, "w+") as text_file:
                text_file.write("{\n")
                text_file.write("    \"targets\": {\n")
                text_file.write("    \"" + args.target + "\" : [\"" + args.toolchain + "\"]\n")
                text_file.write("    }\n")
                text_file.write("}\n")
            
            ret = MBED_SUCCESS

        return ret;        

    def mbed20_test_spec_json_del(self, args):
        """
        remove workspace_tools/test_spec.json file if present
        """
        dbg(sys._getframe().f_code.co_name + ":entered.") 
        filepath = "" 
        
        if args.jenkins is True:
            filepath = "./" + TEST_SPC_JSN_PATHNAME
        else:
            # bash command line
            filepath = args.project + "/" + TEST_SPC_JSN_PATHNAME

        # delete file
        if os.path.exists(filepath):
            os.remove(filepath)

        return MBED_SUCCESS        

    def mbed30_build(self, args):
        """
        Build a mbed 3.0 project
        ARGS:
            args.build      set true if a build step is required.
        """

        if args.target == "K64F":
            target = "frdm-k64f-gcc"
        else:
            print "no valid target"
            return MBED_FAILURE;

        if args.build is True and args.project != "":

            if args.jenkins is True: 
                bashCommand = "yotta target " + target
            else:
                bashCommand = "cd " + args.project + " && yotta target " + target
            
            print bashCommand 
            self.doBashCmd(bashCommand)
            print "\n" # tidy up yotta printing

            # todo: why do we need this auth token for yotta?
            if args.jenkins is True: 
                bashCommand = "set YOTTA_GITHUB_AUTHTOKEN=d828143194f27b01c955c0a337a898c2ac35336e && yotta -vvv build"
            else:
                bashCommand = "set YOTTA_GITHUB_AUTHTOKEN=d828143194f27b01c955c0a337a898c2ac35336e && cd " + args.project + " && yotta -vvv build"

            print bashCommand 
            self.doBashCmd(bashCommand)
            print "\n" # tidy up yotta printing

    def mbed30_clone(self, args):
        """
        Clone a mbed 3.0 project
        ARGS:
            args.clone      set true if a clone step is required.
        """
        
        if args.clone is True and args.project != "":
            # ARMmbed/mbed-example-asynch-spi.git
            bashCommand = """git clone git@github.com:ARMmbed/""" + args.project + ".git"
            self.doBashCmd(bashCommand)

    def mbed30_test(self, args):
        """
        Test a mbed 3.0 project
        ARGS:
            args.test       set true if a test step is required.
        
        """
        # this is currently not implemented
        #if args.test is True:
        #    bashCommand = "./" + path + "/yotta test"
        #    self.doBashCmd(bashCommand)
        print "todo: implement mbed_jenkins.mbed30_test()"


    def mbed30_clone_build_test(self, args):
        """
        Top level target for mbed 3.0 build/test operations. This command 
        is typically invoked by jenkins after cloning the git repository.
        This can be done manually with:
            https://github.com/ARMmbed/mbed-sdk.git
        
        args.clone      set true if a clone step is required.
        args.build      set true if a build step is required.
        args.projec     set to the project name e.g. mbed-sdk, mbed-example-asynch-spi
        args.test       set true if a test step is required.
        git_filename    e.g. ARMmbed/mbed-sdk.git for use in 
                        git clone git@github.com:ARMmbed/mbed-sdk.git
        
        this is what we are doing 
            git clone git@github.com:ARMmbed/mbed-sdk.git
            cd mbed-sdk
            yotta target frdm-k64f-gcc
            yotta build
            yotta test
            
        last step currently not implemented.
        """

        
        self.mbed30_clone(args)
        self.mbed30_build(args)
        self.mbed30_test(args)
        
    def mbed30_mbed_sdk(self, args):
        """
        Top level target for mbed 3.0 mbed-sdk build/test operations. This command 
        is typically invoked by jenkins after cloning the git repository.
        This can be done manually with:
            https://github.com/ARMmbed/mbed-sdk.git
        
        """


        mbed30_clone_build_test(args, "ARMmbed/mbed-sdk.git")

        #self.mbed30_clone(args, "ARMmbed/mbed-sdk.git")
        #self.mbed30_build(args)
        #self.mbed30_test(args)
        
        #if args.clone is True:
        #    bashCommand = """git clone git@github.com:ARMmbed/mbed-example-asynch-spi.git"""
        #   self.doBashCmd(bashCommand)
        #    
        #if args.build is True:
        #    bashCommand = "yotta build"
        #    self.doBashCmd(bashCommand)
        
        # this is currently not implemented
        #if args.test is True:
        #    bashCommand = "yotta test"
        #    self.doBashCmd(bashCommand)

        # need to check the junit test results
        
        # to run yotta regression tests do the following in the yotta source dir:
        #python setup.py test


    def mbed30(self, args):
        """
        Top level target for mbed 3.0 build/test operations. This command 
        is typically invoked by jenkins after cloning the git repository.
        This can be done manually with:
            https://github.com/ARMmbed/mbed.git
        
        args.build      set true if a build step is required.
        args.clone      set true if a build step is required.
        args.test       set true if a test step is required.
        
        
        this is what we need to do 
            git clone git@github.com:ARMmbed/mbed-example-asynch-spi.git
            or
            git clone git@github.com:ARMmbed/mbed-sdk.git
        for the latter:
            cd mbed-sdk
            yotta target frdm-k64f-gcc
            yotta build
            yotta test
            
        last step currently not implemented.
        """

        self.print_date()
        
        # special handling for yotta required
        
        self.mbed30_clone_build_test(args)
        self.print_date()
        
        #if args.clone is True:
        #    bashCommand = """git clone git@github.com:ARMmbed/mbed-example-asynch-spi.git"""
        #    self.doBashCmd(bashCommand)
        #    
        #if args.build is True:
        #    bashCommand = "yotta build"
        #    self.doBashCmd(bashCommand)
        
        # this is currently not implemented
        #if args.test is True:
        #    bashCommand = "yotta test"
        #    self.doBashCmd(bashCommand)

        # need to check the junit test results
        
        # to run yotta regression tests do the following in the yotta source dir:

    

    
    ##############################################################################
    # mbed_2_0_build_test_batch
    #  job for jenkins build test a target
    ##############################################################################
    def mbed_2_0_build_test_batch(self, args):
    	# do something
        print 'args.target=', args.target
        print 'args.toolchain=', args.toolchain
        #cd workspace_tools
        bashCommand = """cp c:/mbed_tools/scripts/private_settings.py ./workspace_tools/"""
        print "bashCommand=", bashCommand 
        self.doBashCmd(bashCommand)
        self.build20(args.toolchain, args.target)
        self.singletest(args)


    def print_date(self):
        # todo: output date: problem with this in jenkins
        #bashCommand = """date"""
        #print "bashCommand=", bashCommand 
        #self.doBashCmd(bashCommand)
        print ""


    def run(self, args):
        dbg(sys._getframe().f_code.co_name + ":entered")
        ret = MBED_FAILURE
        if args.mbed20 is True:
            ret = jenkins.mbed20(args)
            
        elif args.mbed30 is True:
            ret = jenkins.mbed30(args)
            
        dbg(sys._getframe().f_code.co_name + ":ret=" + str(ret))
        return ret
    
    def target_pwr_restart(self, args):
        """ use mbed_usb.py to turn off args.target[0] 
        """
        
        # - power off target just in case the job was interrupted and 
        #   it was left powered on.
        # - wait
        # - power on target
        # - wait for board to come up (MAXWSNENV takes 10s to come up)
        # this can be done with the following:
        #   mbed_usb.py --platform_name_unique <args.target>[0] -s off -f 3
        #   mbed_usb.py --platform_name_unique <args.target>[0] -s on -n 10
        
        ret = MBED_SUCCESS 
        ret = self.target_pwr_off(args)
        #bashCommand = "python + mbed_usb.py --platform_name_unique " + args.target + "[0] -s on -n 10"
        #bashCommand = """c:\\mbed_tools\\scripts\\mbed_usb.py --platform_name_unique """ + args.target + """\[0\] -s on -n 10"""
        #print "bashCommand=%s" % bashCommand
        #ret = self.doBashCmd(bashCommand)
        
        app = mbed_usb.MbedUsbTheApp()
        app.imported=True
        app.imported_arg_list = []
        app.imported_arg_list.append('dummy')
        app.imported_arg_list.append('--platform_name_unique')
        app.imported_arg_list.append('%s[0]' % args.target)
        app.imported_arg_list.append('-s')
        app.imported_arg_list.append('on')
        app.imported_arg_list.append('-n')
        app.imported_arg_list.append('10')
        app.mbed_usb_main()
        
        return ret    
        

    def target_pwr_off(self, args):
        """ use mbed_usb.py to turn off args.target[0] 
        """
        ret = MBED_SUCCESS 
        
        # - power off target  
        # - wait
        #   mbed_usb.py --platform_name_unique <args.target>[0] -s off -f 3

        #bashCommand = "python mbed_usb.py --platform_name_unique " + args.target + "[0] -s off -f 3"
        #bashCommand = r"""c:\\mbed_tools\\scripts\\mbed_usb.py --platform_name_unique """ + args.target + """\[0\] -s off -f 3"""
        bashCommand = """mbed_usb.py -h"""
        #bashCommand = """mbed_usb.py --platform_name_unique """ + args.target + """[0] -s off -f 3"""
        print "target_pwr_off:bashCommand=%s" % bashCommand
        #ret = self.doBashCmd(bashCommand)
        
        
        app = mbed_usb.MbedUsbTheApp()
        app.imported=True
        app.imported_arg_list = []
        app.imported_arg_list.append('dummy')
        app.imported_arg_list.append('--platform_name_unique')
        app.imported_arg_list.append('%s[0]' % args.target)
        app.imported_arg_list.append('-s')
        app.imported_arg_list.append('off')
        app.imported_arg_list.append('-f')
        app.imported_arg_list.append('3')
        
        print app.imported_arg_list
        #app.opts.platform_name_unique_list = True
        app.mbed_usb_main()
        
        return ret    
        

##############################################################################
# Unit test code
##############################################################################

class mbed_jenkins_unit_test(mbed_jenkins):

    NO_UNIT_TEST = 0

    def mbed20_test_01(self, args):
        """
        commandline test for testing the build and test of mbed 3.0 mbed-example-asynch-spi: 
            mbed_jenkins.py --mbed20 --project mbedmicro --clone --build --test --toolchain GCC_ARM --target K64F
        """
        args.mbed20 = True
        args.project = "mbedmicro"
        args.build = True
        args.clone = True
        args.test = True
        args.toolchain = "GCC_ARM"
        return self.run(args)
        

    def mbed20_test_02(self):
        """
        test to check the return code from subprocess.call()
        """
        dbg("we're in " + sys._getframe().f_code.co_name) 
        cmd = "exit 1"
        ret = self.doBashCmd(cmd)
        print "ret=", ret
        return ret

    def mbed20_test_03(self):
        """
        xunitparser example code
        """
        dbg("we're in " + sys._getframe().f_code.co_name)
        ts, tr = xunitparser.parse(open('K64F_junit_report.xml'))
        #ts, tr = xunitparser.parse(open('K64F_junit_report_no_error.xml'))
        for tc in ts:
            print('Class %s, method %s' % (tc.classname, tc.methodname))
            if tc.good:
                #print('went well...', 'but did not run.' if tc.skip else '')
                print('went well...')
            else:
                print('went wrong.')         

        # check the test results.
        # if there are any errors, then the tr.errors list will be non-empty i.e.:
        # errors is a list containing 2-tuples of TestCase instances and strings 
        # holding formatted tracebacks. Each tuple represents a test which raised 
        # an unexpected exception. 
        
        if tr.errors:
            # tr.errors is true because its non-empty
            print('error!')
        else:
            print('no errors')         

        return MBED_SUCCESS

    def mbed20_test_04(self):
        """
        xunitparser example code to cp file for junit testing
        """
        dbg("we're in " + sys._getframe().f_code.co_name)

        cmd = """cp C:/Jenkins/jobs/mbed_2.0_build_test_master_Freescale_FRDM_K64F_arm_cc/workspace/K64F_junit_report.xml  C:/Jenkins/jobs/wip_junit_test/workspace"""
        print cmd
        ret = self.doBashCmd(cmd)
        if ret != MBED_SUCCESS:
            dbg(sys._getframe().f_code.co_name + ": failed to cp file.") 
            return ret
        
        return MBED_SUCCESS

    def mbed30_test_01(self, args):
        """
        commandline test for testing the build and test of mbed 3.0 mbed-sdk: 
            mbed_jenkins.py --mbed20 --project mbedmicro --clone --build --test --toolchain GCC_ARM --target K64F
        """
        args.mbed30 = True
        args.project = "mbed-sdk"
        args.build = True
        args.clone = True
        args.test = True
        args.toolchain = "GCC_ARM"
        return self.run(args)

        return MBED_SUCCESS


    def mbed30_test_02(self, args):
        """
        commandline test for testing the build and test of mbed 3.0 mbed-example-asynch-spi: 
            mbed_jenkins.py --mbed30 --project mbed-example-asynch-spi --clone --build --test --toolchain GCC_ARM --target K64F
        """
        args.mbed30 = True
        args.project = "mbed-example-asynch-spi"
        args.build = True
        args.clone = True
        args.test = True
        args.toolchain = "GCC_ARM"
        return self.run(args)

    def runtest(self, args):
        ret = MBED_FAILURE
        dbg(sys._getframe().f_code.co_name + ":entered")
        dbg(sys._getframe().f_code.co_name + ":args.mbed20=" + str(args.mbed20))
        
        if args.mbed20 is True:
        
            if args.unit_test == "1":
                ret = self.mbed20_test_01(args)
                if ret != MBED_SUCCESS:
                    return ret
         
            elif args.unit_test == "2":
                 ret = self.mbed20_test_02()
                 if ret != MBED_SUCCESS:
                     return ret
         
            elif args.unit_test == "3":
                # xunitparser test
                ret = self.mbed20_test_03()
                if ret != MBED_SUCCESS:
                    return ret
                
            elif args.unit_test == "4":
                # xunitparser test in jenkins test
                ret = self.mbed20_test_04()
                if ret != MBED_SUCCESS:
                    return ret
                
        elif args.mbed30 is True:

            if args.unit_test == "1":
                ret = self.mbed30_test_01(args)
                if ret != MBED_SUCCESS:
                    return ret

            elif args.unit_test == "2":
                ret = self.mbed30_test_02(args)
                if ret != MBED_SUCCESS:
                    return ret
                    
        return ret
    

# example usage on the command line:
# to create the repository, then build then run the tests for GCC_ARM compiler for K64F target then:
# mbed_jenkins.py --mbed30 --project mbed-sdk --build --test --toolchain GCC_ARM --target K64F

# to create the repository, then build then run the tests for GCC_ARM compiler for NUCLEO_F072RB target then:
# mbed_jenkins.py --mbed20 --project mbedmicro --build --test --toolchain GCC_ARM --target NUCLEO_F072RB ; echo $?

# to create the repository, then build then rund the tests for ARM compiler for K64F target then:
# mbed_jenkins.py --mbed20 --project mbedmicro --build --clone --test --toolchain ARM --target K64F

# to create the repository, then build then run the tests for uARM compiler for NUCLEO_L152RE target then:
#mbed_jenkins.py --jenkins --mbed20 --project mbedmicro --build --test --toolchain uARM --target NUCLEO_L152RE

# example usage as jenkins windows batch command:
# mbed_jenkins.py --jenkins --mbed30 --project mbed-sdk --build --test --toolchain GCC_ARM --target K64F

# example usage to run a mbed 2.0 unit test 1 on the command line
# mbed_jenkins.py --mbed20 --unit--test 1

# example usage to run a mbed 2.0 build_release.py on command line 
# mbed_jenkins.py --mbed20  --project mbedmicro --clone --build-release

# example usage to run a mbed 2.0 build_release.py under jenkins 
# mbed_jenkins.py --jenkins --mbed20  --project mbedmicro --clone --build-release

# example usage to run a mbed 2.0 build and test but as device is detected as unknown by mbedls, generate test_spec.json and muts_all.json from id
# here STM NUCLEO_F091RC target_id is: 
#mbed_jenkins.py --jenkins --mbed20 --project mbedmicro --build --test --targetid 075002000750051938359374 --toolchain uARM --target NUCLEO_F091RC

# example usage to run mbed 2.0 build test for a board which is not correctly detect by mbedls e.g.: ST Nucleo F091RC, by specifying the 
# target id of the board.
# |unknown              |G:                 |COM18              |075002000750051938359374                |
# mbed_jenkins.py --mbed20 --project mbedmicro --build --test --toolchain GCC_ARM --target NUCLEO_F091RC --target-id 075002000750051938359374 

# example usage to run mbed 2.0 build test for networking  
# target id of the board.
# |K64F                 |U:                 |COM15              |024002011E661E5CE398E3E4                |
# mbed_jenkins.py --mbed20 --project mbedmicro --build --test --test-net --toolchain GCC_ARM --target K64F --target-id 024002011E661E5CE398E3E4 
 
# example usage to run mbed 2.0 build test for a board which is not correctly detect by mbedls e.g.: ST Nucleo F091RC, by specifying the 
# {comport, disk} of the board.
# |unknown              |G:                 |COM18              |075002000750051938359374                |
# mbed_jenkins.py --mbed20 --project mbedmicro --build --test --toolchain GCC_ARM --target K64F --comport COM15 --disk U: 


# example to invoke unit test:
# mbed_jenkins.py --mbed20 --unit-test 4

# this is the test job to invoke testing on delta board, which doesnt have mbedls support at the present time.
#  mbed_jenkins.py --mbed20 --project mbedmicro --clone --build --test --toolchain GCC_ARM --target DELTA_DFCM_NNN40 --comport COM46 --disk  K:

 
# example usage of singletest.py showing the use of the --auto keyword so the test_spec.json and muts_all.json files dont have to be used.
# python mbedmicro/workspace_tools/singletest.py -f NUCLEO_F091RC --tc=ARM -j 8 -v --report-junit NUCLEO_F091RC_junit_report.xml --report-html NUCLEO_F091RC_html_report.html -c cp --auto


if __name__ == "__main__":

    ret = MBED_FAILURE
    jenkins = mbed_jenkins()
    utest = mbed_jenkins_unit_test()

    # command line argment setup and parsing
    parser = argparse.ArgumentParser()
    #parser.add_argument('--mbed-build', action='store_true', help='git clone mbedmicro and build ')
    #parser.add_argument('--mbed-build-all', action='store_true', help='git clone mbedmicro and build ')
    #parser.add_argument('--mbed-clean-build', action='store_true', help='clean mbed build in current build dir') # clean switch: set true if switch is specified
    #parser.add_argument('--mbed-git', action='store_true', help='git clone mbedmicro')
    #parser.add_argument('--mbed-singletest', action='store_true', help='run the mbed singletest.py script')
    #parser.add_argument('--mbed-git-repo-src-root', default='src_root')

    # jenkins options
    parser.add_argument('--build', action='store_true', help='perform the build step')
    parser.add_argument('--build-release', action='store_true', help='perform the build step')
    parser.add_argument('--clean', action='store_true', help='perform clean before other steps e.g. the build step')
    parser.add_argument('--clone', action='store_true', help='get a copy of the relevant git repository')
    parser.add_argument('--comport', default='', help='generate test_spec.json and muts_all.json and use this comport value (e.g. --comport COM35). Must also specify --disk option.')
    parser.add_argument('--disk', default='', help='generate test_spec.json and muts_all.json and use this disk value (e.g. --disk M:). Must also specify --disk option.')
    parser.add_argument('--jenkins', action='store_true', help='switch to indicate running as part of jenkins')
    parser.add_argument('--mbed20', action='store_true', help='perform mbed 2.0 build steps')
    parser.add_argument('--mbed30', action='store_true', help='perform mbed 3.0 build steps')
    parser.add_argument('--test', action='store_true', help='perform the test step')
    parser.add_argument('--test-net', action='store_true', help='flag used in conjunction with --test perform the network testing (only K64F at present)')
    parser.add_argument('--target-id', default=mbed_jenkins.TARGET_ID_DEF, help='generate test_spec.json and muts_all.json from mbedls target_id')
    parser.add_argument('--project', default='', help="""specify the project to clone and build e.g.
                                    mbed-sdk, mbed-example-asynch-spi""")
    parser.add_argument('--sync', action='store_true', help='used with the build-release option to publish a previous build-release build to mbed.org private fork')
    parser.add_argument('--toolchain', default='GCC_ARM', help='specify toolchain (GCC_ARM, ARM_CC)')
    parser.add_argument('--target', default='K64F', help='mcu (K64F etc')
    parser.add_argument('--target-pwr-restart', default = True, action='store_true', help='at start of test turn target off then on; at end of test turn target off')
    parser.add_argument('--unit-test', default=mbed_jenkins_unit_test.NO_UNIT_TEST, help='perform unit tests')
    args = parser.parse_args()

    
    if args.unit_test > mbed_jenkins_unit_test.NO_UNIT_TEST:
    
        ret = utest.runtest(args)
    else:
        ret = jenkins.run(args)

    sys.exit(ret)
    





#
# the following command gives the supported toolchains. 
# 
# singletest.py --supported-toolchains >> singltest_supported_toolchains.txt
# 
# +-------------------------+-----------+-----------+-----------+-----------+-----------+-----------+------------+---------------+
# | Platform                |    ARM    |    uARM   |  GCC_ARM  |    IAR    |   GCC_CR  |   GCC_CS  | GCC_CW_EWL | GCC_CW_NEWLIB |
# +-------------------------+-----------+-----------+-----------+-----------+-----------+-----------+------------+---------------+
# | APPNEARME_MICRONFCBOARD | Supported |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARCH_BLE                |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | ARCH_GPRS               | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | ARCH_MAX                |  Default  | Supported | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARCH_PRO                |  Default  | Supported | Supported | Supported | Supported | Supported |     -      |       -       |
# | ARM_MPS2                |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARM_MPS2_M0             |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARM_MPS2_M0P            |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARM_MPS2_M1             |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARM_MPS2_M3             |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARM_MPS2_M4             |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | ARM_MPS2_M7             |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | DELTA_DFCM_NNN40        |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | DELTA_DFCM_NNN40_OTA    |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | DISCO_F051R8            |     -     |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | DISCO_F100RB            |     -     |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | DISCO_F303VC            |     -     |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | DISCO_F334C8            |     -     |     -     |  Default  |     -     |     -     |     -     |     -      |       -       |
# | DISCO_F401VC            |     -     |     -     |  Default  |     -     |     -     |     -     |     -      |       -       |
# | DISCO_F407VG            |  Default  | Supported | Supported |     -     |     -     |     -     |     -      |       -       |
# | DISCO_F429ZI            |     -     |     -     |  Default  | Supported |     -     |     -     |     -      |       -       |
# | DISCO_L053C8            | Supported |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | HRM1017                 |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | K20D50M                 |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | K22F                    |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | K64F                    |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | KL05Z                   | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | KL25Z                   |  Default  |     -     | Supported | Supported |     -     |     -     | Supported  |   Supported   |
# | KL43Z                   |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | KL46Z                   |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | LPC1114                 | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC11C24                |  Default  | Supported | Supported | Supported |     -     |     -     |     -      |       -       |
# | LPC11U24                | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | LPC11U24_301            |  Default  | Supported | Supported | Supported |     -     |     -     |     -      |       -       |
# | LPC11U34_421            | Supported |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | LPC11U35_401            | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC11U35_501            | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC11U35_Y5_MBUG        | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC11U37H_401           | Supported |  Default  | Supported |     -     | Supported |     -     |     -      |       -       |
# | LPC11U37_501            | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC11U68                | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC1347                 |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | LPC1549                 |     -     |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC1768                 |  Default  | Supported | Supported | Supported | Supported | Supported |     -      |       -       |
# | LPC2368                 |  Default  |     -     | Supported |     -     | Supported |     -     |     -      |       -       |
# | LPC4088                 |  Default  |     -     | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC4088_DM              |  Default  |     -     | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC4330_M0              |  Default  |     -     |     -     | Supported | Supported |     -     |     -      |       -       |
# | LPC4330_M4              |  Default  |     -     | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPC4337                 |  Default  |     -     |     -     |     -     |     -     |     -     |     -      |       -       |
# | LPC810                  |     -     |  Default  |     -     | Supported |     -     |     -     |     -      |       -       |
# | LPC812                  |     -     |  Default  |     -     | Supported |     -     |     -     |     -      |       -       |
# | LPC824                  |     -     |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | LPCCAPPUCCINO           | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# | MAXWSNENV               |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | MTS_DRAGONFLY_F411RE    |  Default  | Supported | Supported | Supported |     -     |     -     |     -      |       -       |
# | MTS_GAMBIT              |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | MTS_MDOT_F405RG         |  Default  | Supported | Supported | Supported |     -     |     -     |     -      |       -       |
# | MTS_MDOT_F411RE         | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NRF51822                |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | NRF51822_BOOT           |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | NRF51822_OTA            |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | NRF51822_Y5_MBUG        |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | NRF51_DK                |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | NRF51_DK_BOOT           |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | NRF51_DK_OTA            |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | NRF51_DONGLE            |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F030R8           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F070RB           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F072RB           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F091RC           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F103RB           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F302R8           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F303RE           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F334R8           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F401RE           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_F411RE           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_L053R8           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_L073RZ           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | NUCLEO_L152RE           | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | OC_MBUINO               | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | RBLAB_BLENANO           |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | RBLAB_NRF51822          |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | RZ_A1H                  |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | SEEED_TINY_BLE          |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | SEEED_TINY_BLE_BOOT     |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | SEEED_TINY_BLE_OTA      |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | SSCI824                 |     -     |  Default  |     -     |     -     |     -     |     -     |     -      |       -       |
# | STM32F3XX               | Supported |  Default  | Supported |     -     |     -     |     -     |     -      |       -       |
# | STM32F407               |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | TEENSY3_1               |  Default  |     -     | Supported |     -     |     -     |     -     |     -      |       -       |
# | UBLOX_C027              |  Default  | Supported | Supported | Supported | Supported | Supported |     -      |       -       |
# | UBLOX_C029              | Supported |  Default  | Supported | Supported |     -     |     -     |     -      |       -       |
# | WALLBOT_BLE             |  Default  |     -     | Supported | Supported |     -     |     -     |     -      |       -       |
# | XADOW_M0                | Supported |  Default  | Supported | Supported | Supported |     -     |     -      |       -       |
# +-------------------------+-----------+-----------+-----------+-----------+-----------+-----------+------------+---------------+
# *Default - default on-line compiler
# *Supported - supported off-line compiler
# 
# Total platforms: 95
# Total permutations: 313


# mbedmicro/workspace_tools/singletest.py -f NUCLEO_F091RC --tc=ARM -j 8 -v --report-junit NUCLEO_F091RC_junit_report.xml --report-html NUCLEO_F091RC_html_report.html -c cp -i test_spec.json -M muts_all.json
# mbedmicro/workspace_tools/singletest.py -i test_spec.json -M muts_all.json -f NUCLEO_F091RC --tc=ARM -j 8 -v --report-junit NUCLEO_F091RC_junit_report.xml --report-html NUCLEO_F091RC_html_report.html -c cp

# mbedmicro/workspace_tools/singletest.py -f NUCLEO_F091RC --tc=GCC_ARM -j 8 -v --report-junit NUCLEO_F091RC_junit_report.xml --report-html NUCLEO_F091RC_html_report.html -c cp -i mbedmicro/workspace_tools/test_spec.json -M muts_all.json
