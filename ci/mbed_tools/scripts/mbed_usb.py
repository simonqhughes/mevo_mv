#!/usr/bin/env python

#############################################################################
# mbed_usb.py
#  Script to:
#   - manage Cambrionix USB Hub
#   - allow user to perform operations e.g. set hub ports on/off using the
#     platform_name_unique identifier e.g. K64F[0] e.g. to turn on K64F[0] do
#     the following:
#       python mbed_usb.py --set on --platform_name_unique K64F[0]
#     The application figures out which {hub_id, hub_port_id} tuple addresses
#     the required target.
#
#############################################################################
# version 0.0.1     20150703 simon d hughes
# version 0.0.3     20150703 simon d hughes back on devmachine
# version 0.0.4     20150703 simon d hughes on e102501 (jenkins slave win7)
# version 0.0.5     20150703 simon d hughes on e102501 (jenkins slave win7)
#                            working version for fast on/offing of multiple 
#                            ports
# version 0.0.6     20150708 simon d hughes on e102501 (jenkins slave win7)
#                            working to integrated into jenkins
# version 0.0.7     20150709 simon d hughes on e102501 (jenkins slave win7)
#                            working to integrate with mbed_jenkins.py
# version 0.0.8     20150709 simon d hughes moving to buildnode01 for more work


"""
mbed USB
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


#todo: need 10s after turning port power on to allow board to power up
# some boards are faster than others
# some pcs are faster than others

import os
import sys
import optparse
import serial
import time
import mbed_lstools
import json
from pprint import pprint
import re
import os.path


# map for E102501
#
# simhug01@E102501 /c/develop/2212/work/20150707
#$ mbedls
#+-----------------------+----------------------------+-------------------+-------------------+------------------------------------------------------------------------+
#|platform_name          |platform_name_unique        |mount_point        |serial_port        |target_id                                                               |
#+-----------------------+----------------------------+-------------------+-------------------+------------------------------------------------------------------------+
#|EFM32GG_STK3700        |EFM32GG_STK3700[0]          |M:                 |COM8               |2015000900004A3FD65079F0                                                |
#|EFM32HG_STK3400        |EFM32HG_STK3400[0]          |L:                 |COM6               |2005010300008A48D75AB997                                                |
#|EFM32LG_STK3600        |EFM32LG_STK3600[0]          |G:                 |COM9               |20200009000056BFD6506545                                                |
#|EFM32WG_STK3800        |EFM32WG_STK3800[0]          |K:                 |COM7               |2010000900005541D650668B                                                |
#|EFM32ZG_STK3200        |EFM32ZG_STK3200[0]          |J:                 |COM12              |203000090000591FD6506AF5                                                |
#|K22F                   |K22F[0]                     |N:                 |COM20              |0231020337317E7FCACD83B6                                                |
#|K64F                   |K64F[0]                     |I:                 |COM16              |024002011E661E5CE398E3E4                                                |
#|KL25Z                  |KL25Z[0]                    |F:                 |COM18              |02000203240881BBD9F47C43                                                |
#|KL46Z                  |KL46Z[0]                    |H:                 |COM19              |02200203E6761E7B1B8AE3A3                                                |
#|LPC11U24               |LPC11U24[0]                 |S:                 |COM23              |104000000000000000000002F7F0E66Ad4ee01d42444f6213cf712529d8ea0ea        |
#|LPC11U68               |LPC11U68[0]                 |P:                 |COM21              |116802021D4C8D9A222B0DCF                                                |
#|LPC1768                |LPC1768[0]                  |R:                 |COM22              |101000000000000000000002F7F1FFE202dc4967b42527c22b716e19fe633fa9        |
#|MAXWSNENV              |MAXWSNENV[0]                |O:                 |COM3               |0400020312345678EFC8AD80                                                |
#|NRF51822               |NRF51822[0]                 |Q:                 |COM10              |1070021854313020313239343130333234313031A9D6DFA8                        |
#|UBLOX_C027             |UBLOX_C027[0]               |E:                 |COM17              |12340200E38AD607992A0941                                                |
#+-----------------------+----------------------------+-------------------+-------------------+------------------------------------------------------------------------+
#
#
#{"maps":[{"id":"blabla","iscategorical":"0"},{"id":"blabla","iscategorical":"0"}],
#"masks":{"id":"valore"},
#"om_points":"value",
#"parameters":{"id":"valore"}
#}
#Then you can use your code:
#import json
#from pprint import pprint
#
#with open('data.json') as data_file:    
#    data = json.load(data_file)

#pprint(data)
#With data, you can now also find values in like so:
#data["maps"][0]["id"]
#data["masks"]["id"]
#data["om_points"]


   
class MbedUsbHub:
    """ Base class for usb hub with capability to turn power on/off to each port"""

    MAX_PORTS = 9999

    PORT_STATE_OFF = 0
    PORT_STATE_ON = 1
    PORT_STATE_MAX = 2
    
    ERROR_SUCCESS = 0
    ERROR_FAIL = 1
    
    # identification string for hub
    description = ""

    def __init__(self):
        """ Constuctor"""
        #extra flags
        self.DEBUG_FLAG = False     # Used to enable debug code / prints
        self.ERRORLEVEL_FLAG = 0    # Used to return success code to environment

        # dictionary of port entries of the form {port_num, attrib1, attrib2, ...}
        # where the attributes are things like state, and other things.
        # init should initialise the state
        # port_data is list of ports 
        # port = { 'num' : <num_int>, 'state' : <PORT_STATE_OFF|PORT_STATE_ON> }
        self.port_data = {}

        # child should set up some communication channel with the hub, which 
        # will be reference with handle
        self.handle = None

    # Logging functions
    def err(self, text):
        """! Prints error messages

        @param text Text to be included in error message

        @details Function prints directly on console
        """
        print 'error: %s'% text

    def debug(self, name, text):
        """! Prints error messages

        @param name Called function name
        @param text Text to be included in debug message

        @details Function prints directly on console
        """
        if self.DEBUG_FLAG is True:
            print 'debug @%s.%s: %s'% (self.__class__.__name__, name, text)

    def __str__(self):
        """! Object to string casting

        @return Stringified class object should be prettytable formated string
        """
        return self.dump()


    def close(self):
        """! close a connection established with the hub

        @return None
        """
        return None

    def dump(self):
        """! Dump function which displays internal state of the class

        @return None
        """

        result = ""

        # iterate over the port data to dump informaion
        for item in self.port_data:
            result += "port number = %d  port state = %d\n" % (item['num'], item['state']) 

        return result

    def enumerate(self):
        """! enumerate the different devices on each of the ports

        @return None
        """

        result = ""

        # iterate over the port data to dump informaion
        for item in self.port_data:
            result += "port number = %d  port state = %d\n" % (item['num'], item['state']) 

        return result

    def port_state_get(self, port_num):
        """! get the state of a port

        @return ON, OFF   
        @details 
        """
        
        return None

    def open(self):
        """! open a connection established with the hub

        @return None
        """
        return None

    def recv(self):
        """! Receive a reply from a previously sent command to the hub

        @return  None 
        @details Virtual to be implemented by child class.
        """
    
        return None

    def send(self):
        """! Send a command to the hub
        
        @return  None 
        @details Virtual to be implemented by child class.
        """
        
        return None

    def set_port_state(self, port_num, port_state = PORT_STATE_OFF):
        """! set the state of a port number port_num to port_state

        @return ON, OFF   
        @details 
        """
        
        return None


class MbedCambrionix(MbedUsbHub):
    """class for managing the Cambrionix USB Hub"""
    
    MAX_HUBS = 2
    MAX_PORTS = 12
    
    
    # identification string of hub
    description = "cambrionix U12S 12 Port USB Charge+Sync"
    
    def __init__(self):
        """ Constuctor"""
        
        MbedUsbHub.__init__(self)
        self.port = ''
        # config read from json file describing port mapping
        self.config = {}
        return    

    # implementation of parent interface
    def close(self):
        """ Close a previously opened connection to the hub"""

        if self.handle != None:
            self.handle.close()
            self.handle = None

    # implementation of parent interface
    def do_cmd(self, cmd):
        """ todo: """

        self.send(cmd)
        return self.recv(cmd)
		

    def open(self, port = ""):
        """ open a connection to the hub with the cambrionix default values for serial communication"""
    
        self.port = port
        self.handle = serial.Serial(
            port=port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
            )   

        # todo: check that we have a valid handle 
        self.handle.timeout = 0.1
        self.handle.write('\x03\r')
        
        # check we have a valid system
        sys_data =  self.cmd_system()
        if sys_data['description'] != self.description:
        
            self.close()
        
        return None

    def send(self, command):
        '''
        Writes a command to a port
        allows for 2 parameters with a command, such as en_profile 5 1
        w.i.p
        '''
    
        self.handle.write( str(command) + '\r')

    def recv(self, last_command=''):
        '''
        reads upto 500 bytes from the serial port
        
        last_command 	last command to remove from recv string.	
        '''
    
        # for the "state 12" command for example, read command returns string of the form  
        #===================================
        #  state 12
		#  12, 0000, R D O, 0, 0, x, 0.00
		#
		#  >>	
        #===================================
        # - to remove the command echo use [len(last_command):]
        # - to remove the \r\n\r\n>> at the end >> use [:-4]
        read_val = self.handle.read(size=500).decode('utf-8')[len(last_command):-4]
        
        return read_val

    # class methods

    def cmd_state(self, port_num=MAX_PORTS):
        """! Execute the state command to get the port status information
        
        @param port_num     number of port to get state data for (enumerating from 0). 
        specify MAX_PORTS to get the data for all the ports
                            
        """
        
        self.debug(__name__, "cmd_state:port_num=%s" % port_num)
        
        
        result = []
        columns = ['port_num', 'current_ma', 'flags', 'profile_id', 'time_charging', 'time_charged', 'energy']
        
        if port_num == self.MAX_PORTS:
            # get all the port data
        
            self.send('state')
            recv_data = self.recv()
    
            for line in recv_data.splitlines():
                line.strip()
                if not line:
                    continue
                
                num = 0
                port_data = {}
                for item in line.split(","):
                    print item
                    port_data[columns[num]] = item;
                    num = num + 1;
    
                result.append(port_data)                    
                
        else:
            # get the data for the specific port
            cmd = "state " + str(port_num+1)
            line = self.do_cmd(cmd)

            num = 0
            port_data = {}
            line.strip()
            if not line:
                return result
                
            for item in line.split(","):
                port_data[columns[num]] = item.strip();
                num = num + 1;

            result.append(port_data)                    
        
        return result

    def cmd_system(self):
        """! Execute the system command on the hub
        
        @return     dictionary containing system reported itemss
        
           { 'description' : <string describing system>} }
           
        """
        
        result = {}
        
        self.send('system')
        recv_data = self.recv()
        
        # todo: check returned data is ok
        
        for line in recv_data.splitlines():
            line.strip()
            if not line:
                continue
            if line.find('system') != -1:
                # found echo of command system; skipping over"
                continue

            if line.find(self.description) != -1:
                result['description'] = line
                continue

            # use the string before the ':' as the dict key, and the string 
            # after the ':' as the value
            if line.find(':') == -1:
                continue;
            result[line.split(":")[0]] = line.split(":")[1]
            
        return result


    def port_data_get(self, port_num=0):
        """! Get the port data for port numbers 
        
        @details   ports are enumerated starting at 0.
        @param     port_num     number of port for which to get the data
        @return    returns port_data dict for port port_num, if found, otherwise None
         """
        
        self.debug(__name__, "port_data_get:port_num=%s" % port_num)
        ret = {}
         
        # note port 0 on the Cambrionix is labelled port '1' in the data returned
        # from the state command
        result = self.cmd_state(port_num)
        
        if len(result) == 1:
            if int(result[0]['port_num']) -1 == port_num:
                # have found the port
                ret = result[0]
                
        return ret

    def port_state_get(self, port_num=0):
        """! Get the port state 
        
        @details   ports are enumerated starting at 0.
        @param     port_num     number of port for which to get the data
        """
        
        self.debug(__name__, "port_state_get:port_num=%s" % port_num)
        
        ret = self.PORT_STATE_MAX
        result = self.port_data_get(port_num)
        
        if result != {}:
            if result['flags'].find('S') != -1:
                # found SYNC flag which indicated port is on
                ret = self.PORT_STATE_ON
                
            elif result['flags'].find('O') != -1:
                # found SYNC flag which indicated port is on
                ret = self.PORT_STATE_OFF
        
        return ret

    def port_state_set(self, num, state=MbedUsbHub.PORT_STATE_ON):
        """! set the port state 
        
        @details   ports are enumerated starting at 0.
        @param     num      number of port for which to set the state
        @param     state    state to set the port to i.e. on/off
        """

        ret = ""
        mode_char = ['o', 's']
        if num < self.MAX_PORTS and state < self.PORT_STATE_MAX:
            cmd = "mode " + mode_char[state] + ' ' + str(num+1)
            ret = self.do_cmd(cmd)
        elif num == self.MAX_PORTS and state < self.PORT_STATE_MAX:
            for i in range(0, 12):
                print i
                cmd = "mode " + mode_char[state] + ' ' + str(i+1)
                print cmd
                ret = self.do_cmd(cmd)

        return ret        

    def is_port_num_in_range(self, port_num):
        if port_num >= 0 and port_num < MbedCambrionix.MAX_PORTS:
            return True

        return False

    @staticmethod
    def get_config(config_file_name):
        """read in the json file describing the hub config
        """
        
        config = {}
        if config_file_name != "":
            with open(config_file_name) as data_file:    
                config = json.load(data_file)

        return config
        
    def get_hub_port_data_by_platform_name_unique(self, platform_name_unique):

        hub_port_data = {}
        if not self.config:
            raise AssertionError
    
        # search it to find platform unique name
        for key in self.config:
            if self.config[key]['platform_name_unique'] == platform_name_unique:
                hub_port_data = self.config[key]
        
        return hub_port_data
                
        

class MbedSubrack():
    """ class for managing multiple cards """
    
    def __init__(self):
        """ Constuctor"""
        #extra flags
        self.DEBUG_FLAG = False     # Used to enable debug code / prints
        self.ERRORLEVEL_FLAG = 0    # Used to return success code to environment

        self.subrack_hubs_config = {}

class MbedUsbTheApp():
    """ app class for this application"""
    
    # todo: fix fact that have to specify absolute path
    #SUBRACK_CONFIG_FILENAME='mbed_usb_hubs.json' 
    DIR_PATH= r"c:\\mbed_tools\\scripts\\" 
    SUBRACK_CONFIG_FILENAME= r"mbed_usb_hubs.json" 
    
    def __init__(self):
        """ Constuctor"""

        self.DEBUG_FLAG = False     # Used to enable debug code / prints
        self.ERRORLEVEL_FLAG = 0    # Used to return success code to environment

        self.hub = None
        self.opts = None
        self.args = None
        
        # dictionary for subrack config (.json file) 
        self.subrack_hubs_config = {}

        # dictionary for reading subrack card config (.json file)
        self.subrack_card_config = {}
        self.subrack_card_config = {}
        self.imported = False
       
        return
    
    def debug(self, name, text):
        """! Prints error messages

        @param name Called function name
        @param text Text to be included in debug message

        @details Function prints directly on console
        """
        if self.DEBUG_FLAG is True:
            print 'debug @%s.%s: %s'% (self.__class__.__name__, name, text)


    def mbed_usb_test(self, test_num):
        """! implement test
    
        todo: further info
        """
        
        if test_num == 1:
            mbeds = mbed_lstools.create()
            #d1 = mbeds.list_mbeds_ext()
            #print d1 
            d2 = mbeds.list_mbeds_by_targetid()
            #print d2
            #dict1 = mbeds.list_mbeds()
            #print dict1
            
            for key in d2:
                print key 
            
    
    
    def mbed_usb_cmd_parser_setup(self):
        """! Configure CLI (Command Line OPtions) options
    
        @return Returns OptionParser's tuple of (options, arguments)
    
        @details Add new command line options here to control 'mbed_usb' command line iterface
        """
        parser = optparse.OptionParser()
    
        parser.add_option('-g', '--get',
                          dest='get',
                          default=False,
                          action="store_true",
                          help='Get the state of the port')
    
        parser.add_option('-s', '--set',
                          type='string',
                          dest='set',
                          default="",
                          action="store",
                          help='Set the port to the specified state [on|off]')
    
        parser.add_option('-d', '--debug',
                          dest='debug',
                          default=False,
                          action="store_true",
                          help='Outputs extra debug information')
    
        parser.add_option('-m', '--mbedls',
                          dest='mbedls',
                          default=False,
                          action="store_true",
                          help='performs mbedls after command to list detect devices')
    
        parser.add_option('-p', '--port',
                          type ='int',
                          dest='port_num',
                          default=MbedCambrionix.MAX_PORTS,
                          help='Specify the port number on hub to work with. (%d => get all | turn all ports [off|on])' % MbedCambrionix.MAX_PORTS)
    
        parser.add_option('-n', '--sleep_on',
                          type ='int',
                          dest='sleep_on',
                          default=0,
                          help='time to sleep after setting port on (s)(allows time for OS to instantiate port)')
    
        parser.add_option('-f', '--sleep_off',
                          type ='int',
                          dest='sleep_off',
                          default=0,
                          help='time to sleep after setting port off (s)(allows time for OS to de-instantiate port')
    
        parser.add_option('-x', '--sys_up',
                          dest='sys_up',
                          default=False,
                          action="store_true",
                          help='power on all ports sequentially sleeping between each port on operation')
    
        parser.add_option('-u', '--usb_hub_com_port',
                          type ='string',
                          dest='usb_hub_com_port',
                          default="",
                          help='Specify the com port number for serial connection to usb hub')
    
        parser.add_option('-t', '--test',
                          type ='int',
                          dest='test_num',
                          default=0,
                          help='Specify test number to run')

        parser.add_option('--platform_name_unique_list',
                          dest ='platform_name_unique_list',
                          default=False,
                          action="store_true",
                          help='list platform unique names documented in json file')

        parser.add_option('--platform_name_unique',
                          type ='string',
                          dest ='platform_name_unique',
                          default="",
                          help='platform unique name')

        # todo: fix ugly hack:
        if not self.imported:
            (opts, args) = parser.parse_args()
        else:
            (opts, args) = parser.parse_args(args = self.imported_arg_list)
        return (opts, args)
    
    def mbed_usb_main(self):
        """! Function used to drive CLI (command line interface) application
    
        @return Function exits with successcode
    
        @details Function exits back to command line with ERRORLEVEL
        """
        
        (self.opts, self.args) = self.mbed_usb_cmd_parser_setup()


        # read the cached config files (.json) if present
        self.mbed_usb_read_config()

        #todo: we want to fix the code so we dont crate a hub until we know which 
        # one it is, or to create all hub instances if/when we need them
        # and not be predicated on locating a hub by the serial port specified on the command line
        # for now, fix everything up by reading some config
    
        self.hub = MbedCambrionix()
        if self.hub is None:
            sys.stderr.write('Failed to create an instance of the usb hub\n')
            sys.exit(-1)

        self.hub.DEBUG_FLAG = self.opts.debug
        self.DEBUG_FLAG = self.opts.debug

        # check have a hub port specified
        # hub_serial_port = self.mbed_usb_get_hub_serial_port_from_args()
        (hub_id, hub_serial_port, hub_config_file_name) = self.mbed_usb_get_hub_serial_port_from_args()
        
        self.hub.debug(__name__, "hub_id=%s, hub_serial_port=%s, debug=%d, get=%d, port_num=%d" % (hub_id, hub_serial_port, self.opts.debug,self.opts.get,self.opts.port_num))
        if hub_id == str(MbedCambrionix.MAX_HUBS):
            sys.stderr.write('Error: Failed to find a valid hub id for this target\n')
            sys.exit(self.hub.ERRORLEVEL_FLAG)
        
        if hub_serial_port == "":
            sys.stderr.write('Error: Failed to specify hub com port\n')
            sys.exit(self.hub.ERRORLEVEL_FLAG)
        
        self.hub.open(hub_serial_port)
        
        ## populate self.hub.config
        self.hub.config = self.hub.get_config(hub_config_file_name)                      
        
        ## todo: check range of port number
        
        if self.opts.platform_name_unique_list:
            MbedUsbTheApp.mbed_usb_platform_name_unique_list() 
            sys.exit(self.hub.ERRORLEVEL_FLAG)
        
        if self.opts.get:
            self.mbed_usb_get()
            
        elif self.opts.set:
            self.mbed_usb_set()

        elif self.opts.test_num > 0:
            self.mbed_usb_test(self.opts.test_num)
            
    	# do mbedls if instructed to do so
        if self.opts.mbedls:
            mbeds = mbed_lstools.create()
            print mbeds
    		
        if self.hub.DEBUG_FLAG:
            self.hub.debug(__name__, "Return code: %d" % self.hub.ERRORLEVEL_FLAG)
    
        self.hub.close()
        # todo: fix exit codes when imported.
        #sys.exit(self.hub.ERRORLEVEL_FLAG)
        return self.hub.ERRORLEVEL_FLAG

    @staticmethod
    def mbed_usb_natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(re.compile('([0-9]+)'), s)]   

                
    @staticmethod
    def mbed_usb_platform_name_unique_list():
        """list the platform unique names from the config file
        
        @param platform_unique_name     unique name of platform to use.
        """
        # load in the json config

        hub_config = {}
        subrack_hubs_config = MbedUsbTheApp.mbed_usb_hubs_get_config()
        
        target_list= []
        for key in subrack_hubs_config:
            # get port_config
            MbedUsbTheApp.DIR_PATH
            config_file_pathname = MbedUsbTheApp.DIR_PATH + subrack_hubs_config[key]['config_file'] 
            hub_config = MbedCambrionix.get_config(config_file_pathname)
            for hkey in hub_config:
                target_list.append(hub_config[hkey]['platform_name_unique'])
        
        if len(target_list) > 0:
            target_list.sort(key=MbedUsbTheApp.mbed_usb_natural_sort_key)
            for target in target_list:
                print "\t%s" % target            

        return                
        
    def mbed_usb_get_hub_port_id_from_args(self):
        """
        
        @param 
        
        returns hub_port_if valid, otherwise MbedCambrionix.MAX_PORTS
        """
        
        hub_port_id = MbedCambrionix.MAX_PORTS
        
        if self.hub.is_port_num_in_range(self.opts.port_num) == True :
            hub_port_id = self.opts.port_num
            
        else:
            # map platform_unique_name to hub_port_id
            
            if not self.hub.config:
                raise AssertionError
        
            # search it to find platform unique name
            for key in self.hub.config:
                if self.hub.config[key]['platform_name_unique'] == self.opts.platform_name_unique:
                    # have found entry
                    hub_port_id = int(self.hub.config[key]['hub_port_id'])
             
        return hub_port_id                
        
    def mbed_usb_read_config(self):
        """If present, read the json files enumerating the config
        member to read:
            - subrack config e.g. mbed_usb_hubs.json
            - each of the card config files enumerated in subrack config file 
        """
        
        self.subrack_hubs_config = MbedUsbTheApp.mbed_usb_hubs_get_config()
        if self.subrack_hubs_config:
            for key in self.subrack_hubs_config:
                # get port_config
                config_file_pathname = MbedUsbTheApp.DIR_PATH + self.subrack_hubs_config[key]['config_file']
                self.subrack_card_config[key] = MbedCambrionix.get_config(config_file_pathname)

        return
    
    def mbed_usb_get_hub_serial_port_from_args(self):
        """find the hub serial com port given the parsed command line args
        
        @param 
        
        @returns the tuple (hub_id, hub_serial_port, hub_config_file)
        
        hub_id      
        the identifier string of the hub, MbedCambrionix.MAX_HUBS is the 
        value returned if the data is invalid.
        
        hub_serial_port
        if hub_id is valid then the serial commport is the comport for 
        serial access to the device.
       
        hub_config_file
        if hub_id is valid then this is the cached config file containing
        the hub port data.
        """

        self.debug(__name__, "mbed_usb_get_hub_serial_port_from_args")
        
        hub_serial_port = ""
        hub_id = MbedCambrionix.MAX_HUBS
        hub_config_file_name = ""

        if self.opts.usb_hub_com_port != "":
            hub_serial_port = self.opts.usb_hub_com_port

        elif self.opts.platform_name_unique != "":
            # find hub_id from platform_name_unique
            
            hubs_config = self.mbed_usb_hubs_get_config()
            # fix up: have to read the config

            hubs_config = MbedUsbTheApp.mbed_usb_hubs_get_config()
            
            for key in hubs_config:
                # get port_config
                config_file_pathname = MbedUsbTheApp.DIR_PATH + hubs_config[key]['config_file']
                hub_config = MbedCambrionix.get_config(config_file_pathname)
                for hkey in hub_config:
                    if hub_config[hkey]['platform_name_unique'] == self.opts.platform_name_unique:
                        hub_serial_port = self.mbed_usb_get_hub_com_port_from_id(key)
                        hub_id = key
                        hub_config_file_name = MbedUsbTheApp.DIR_PATH + hubs_config[key]['config_file']
            
        elif self.opts.platform_name_unique_list:
            # means we have to discover the hub com ports and generate a composite list
            # for the purposes of this method, its sufficient to return at least 1 serial port
            for i in range(0, MbedCambrionix.MAX_HUBS-1):
                hub_serial_port = self.mbed_usb_get_hub_com_port_from_id(str(i))
                if hub_serial_port != '':
                    break
        
        return (hub_id, hub_serial_port, hub_config_file_name)                


    def mbed_usb_get(self):
        """
        
        @param 
        """
        
        hub_port_id = self.mbed_usb_get_hub_port_id_from_args()
        if hub_port_id == MbedCambrionix.MAX_PORTS:
            print "Error: port number (%d) out of range(%d..%d), or platform unique name(%s) not recognised"  % (self.opts.port_num, 0, MbedCambrionix.MAX_PORTS-1, self.opts.platform_unique_name)
            sys.exit(self.hub.ERRORLEVEL_FLAG)
    
        ret = self.hub.port_state_get(hub_port_id)
        if ret == self.hub.PORT_STATE_ON:
            print "on\n"
        elif ret == self.hub.PORT_STATE_OFF:
            print "off\n"
        else:
            print "unknown\n"
        
        return                
        
    def mbed_usb_set(self):
        """
        
        @param 
        """
        hub_port_id = self.mbed_usb_get_hub_port_id_from_args() 
        if hub_port_id == MbedCambrionix.MAX_PORTS:
            print "Error: port number (%d) out of range(%d..%d), or platform unique name(%s) not recognised"  % (self.opts.port_num, 0, MbedCambrionix.MAX_PORTS-1, self.opts.platform_unique_name)
            sys.exit(self.hub.ERRORLEVEL_FLAG)

        on_off_map = { 'off' : MbedUsbHub.PORT_STATE_OFF , 'on' : MbedUsbHub.PORT_STATE_ON  }
        on_off_sleep_map = { 'off' : self.opts.sleep_off , 'on' : self.opts.sleep_on }

        if self.opts.set not in on_off_map.keys():
            sys.stderr.write('Error: invalid set arg. alid args are %s\n' % on_off_map.keys())
            sys.exit(self.hub.ERRORLEVEL_FLAG)
        
        new_port_state = ''
        if self.opts.set == 'on' or self.opts.set == 'off':
            new_port_state = on_off_map[self.opts.set]
        else:
           print "error"
           sys.exit(self.hub.ERRORLEVEL_FLAG)
        
        ret = self.hub.port_state_set(hub_port_id, new_port_state)
        if ret != None:
            print "OK\n"
            
        # perform sleep
        time.sleep(on_off_sleep_map[self.opts.set])
        
        return                
        
    # make this a statis member function and then have a factory 
    # to create hub instances, one per enumerated in the hubs.json file.
    #todo: move to MbedUsbHub?, and make static?
    @staticmethod
    def mbed_usb_hubs_get_config():
        """Get the config for the usb hubs from the json file
        """
        config = {}
        config_file_pathname = MbedUsbTheApp.DIR_PATH + MbedUsbTheApp.SUBRACK_CONFIG_FILENAME
        if os.path.isfile(config_file_pathname): 
            with open(config_file_pathname) as data_file:    
                config = json.load(data_file)

        return config

    #todo: move to MbedUsbHub?
    
    @staticmethod
    def mbed_usb_get_hub_com_port_from_id(hub_id='0'):
        """ get the serial port of the hub
        """
        serial_port = ""
        config = MbedUsbTheApp.mbed_usb_hubs_get_config()
        if hub_id in config:
            serial_port = config[hub_id]['serial_port']
        
        return serial_port
        
# usage examples
#
# Commands Used for Commissioning a Hub/Creating json configuration files.
# ======================================================================
# Turn port 0 off on hub accessible over serial port com30
#  python mbed_usb.py --usb_hub_com_port com30 -s off -p 0 

# turn on all the port and wait 10s after turning on last port, and then do mbedls
#  python mbed_usb.py -u com15 -s on -p 12 -n 10 -m
#
#
# Commands Used by Scripts to turn on/off targets
# ===============================================
# To turn on a particular target board:
#
#  python mbed_usb.py --platform_name_unique K64F[0] --set on
#
# To get the on/off start of a particular target 
#
#  python mbed_usb.py --platform_name_unique K64F[0] -g
#
# To get a list of the particular targets from the json files: 
#
#  python mbed_usb.py --platform_name_unique_list
#
if __name__=='__main__':

    app = MbedUsbTheApp()
    app.mbed_usb_main()
            