#!/usr/bin/env python

"""
This script helps automate a number of mbl-manifest related tasks:
  - Do a mbl-manifest build of master, or other branches.
  - Do a mbl-manifest build using a specfied mytest.xml on the local machine.
  - Perform a test campaign of builds from a set of test-manifest*.xml files.
  - Generate a test campaign set of test.xml files from a template.xml and a set of 
    commits for one or 2 or the projects of the projects. 
  - Perform the above operations as part of a jenkins job.

Procedure for using this script:
- create manifest*.xml to specifiy the build to be performed.
  These should be of the form 20171005_1111_mbl_test.xml so the 
  workspace dirs (created from the xml file name) are ordered by
  job number 
- check that the test-manifest.xml is correct using the repo init -m 
  test-manifest.xml command. 

DEPENDENCIES  
- Depends on repo tool being installed and on the path.
- Github ssh keys installed for user so repo can use git ssh transport
  and authentication.

EXAMPLE USAGE

Do a build of mbl-manifest master branch

    mbl_too.py

Do a build of mbl-manifest pyro branch

    mbl_too.py --mbl-manifest-branch=pyro


Do a build of mbl-manifest sdh_iotmbl7_simplify branch for testing a PR:

    mbl_too.py --mbl-manifest-branch=sdh_iotmbl7_simplify


Do a build of mbl-manifest but use a local test.xml file rather than the repo default.xml

    mbl_too.py --manifest=test.xml

Run a test campaign of all the test.xml files in a jobs directory:

   mbl_tool.py --jobdir=jobs

Redo a bitbake mbl-console-image build for a previously created workspace:

   mbl_tool.py --do-mbl-console-image --manifest=jobs/20171006_1030_test_23.xml

Generate a test campaign (set of test.xml files):

   mbl_tool.py --manifest=20171006_1030.xml --revfile=commits.txt \
       --project-name=openembedded\/meta-openembedded

The command: 
- takes a manifest.xml file as a template for the test campaign tests
- a project-name that identifies the line in the template manifest.xml
  where the revision="xx" will be set for a set of commit ids
- commits.txt is a list of N commit ids that are used as the revisions
  in the N manifest_test_nn.xml test case files forming the test campaign. 
where: 
- 20171006_1030.xml is the template from which test.xml manifests will be
  generated by setting the revision attribute of the project line.
- commits.txt is text file with 1 commit id per line for a potential
  test.xml. this file is generated by the following git command in the 
  repo of interest:
    git log --pretty=format:%H b063789560bfb9c60a7a15277b5b3a9839b5ba74^..remotes/github/master > commits.txt
  This git command lists the commit ids with the commit
  b063789560bfb9c60a7a15277b5b3a9839b5ba74 listed last in the file
  (which is typically the first that you want testing to make sure 
  it works). Note remotes/github/master is the commit id of a build
  thats expected to fail (e.g.fail to boot) and so you're trying to 
  produce a series of builds between commit_A and commit_B.
- openembedded\/meta-openembedded identifies the project name line
  in the manifest.xml that you want to set the revision for.  
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
import logging
import xml.etree.ElementTree as ET
import fnmatch
import tempfile


# error codes are positive numbers because sys.exit() returns a +ve number to the env
MBL_SUCCESS = 0
MBL_FAILURE = 1
MBL_ERROR_MAX = 2

"""
do_build.sh bash script
  A script used to automate the bitbake build 
"""
do_build_sh = '''\
#!/bin/bash

MACHINE=raspberrypi3 DISTRO=mbl . setup-environment
bitbake mbl-console-image > log.txt 2>&1
'''


bb_layers_conf = '''\
# LAYER_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
LCONF_VERSION = "7"
OEROOT := "${@os.path.abspath(os.path.dirname(d.getVar('FILE', True)))}/../.."

BBPATH = "${TOPDIR}"

BBFILES = ""

# These layers hold recipe metadata not found in OE-core, but lack any machine or distro content
BASELAYERS ?= " \
  ${OEROOT}/layers/meta-openembedded/meta-networking \
  ${OEROOT}/layers/meta-openembedded/meta-filesystems \
  ${OEROOT}/layers/meta-openembedded/meta-python \
  ${OEROOT}/layers/meta-virtualization \
"

# These layers hold machine specific content, aka Board Support Packages
BSPLAYERS ?= " \
  ${OEROOT}/layers/meta-freescale \
  ${OEROOT}/layers/meta-freescale-3rdparty \
  ${OEROOT}/layers/meta-raspberrypi \
"

# Add your overlay location to EXTRALAYERS
# Make sure to have a conf/layers.conf in there
EXTRALAYERS ?= " \
  ${OEROOT}/layers/meta-linaro/meta-linaro \
  ${OEROOT}/layers/meta-linaro/meta-linaro-toolchain \
  ${OEROOT}/layers/meta-linaro/meta-optee \
"

BBLAYERS = " \
  ${OEROOT}/layers/meta-mbl \
  ${BASELAYERS} \
  ${BSPLAYERS} \
  ${EXTRALAYERS} \
  ${OEROOT}/layers/openembedded-core/meta \
"
'''

class mbl_tool:
    """
    Class for automating mbed linux distro builds to help locate commits 
    that break builds/working images. 
    """
    def __init__(self):
        """
        Dected 
        """

        # attribute indicating whether the script is running on jenkins or not 
        self.jenkins = False 
        self.ws_path = ""  

        # check if running on jenkins
        if os.environ.get('JENKINS_URL') != None and os.environ.get('JENKINS_HOME') != None:
            self.ws_path = os.environ['WORKSPACE'] + "/"  
            self.jenkins = True
        else:
            # set a default for use all the time
            self.ws_path = os.environ['PWD'] + "/"

    def do_bash(self, cmd):
        ret = subprocess.call(cmd, shell=True)
        return ret
    
    def get_job_list(self, jobs_dir):
        # get list of jobs from the jobs dir filtering out 
        # temp files generated by emacs i.e *~ files
        files = [f for f in os.listdir(jobs_dir) if os.path.isfile(os.path.join(jobs_dir, f)) and not fnmatch.fnmatch(f, '*~')]
        return files
        

    ############################################################################# 
    # FUNCTION: do_build
    #   Perform a build by:
    #   - initialising the workspace with repo init using default.xml and master 
    #     branch
    #   - optionally replace the default.xml with a local manifest_test.xml
    #   - repo sync-ing the workspace to pull down the project repos/
    #   - building the project.
    #  
    # ARGUMENTS:  
    #   test_filename_xml    
    #     manifest.xml filename that specifies build. If empty
    #     then use default.xml from mbl-manifest.
    #   mbl_manifest_branch
    #     branch in the mbl-manifest repo to take default xml from e.g. for 
    #     testing PRs.
    ############################################################################# 
    def do_build(self, test_filename_xml, jobs_dir, mbl_manifest_branch):

        ret = MBL_FAILURE
        default_build = False
        
        if test_filename_xml == "":
            # test_filename_xml = "default_" + '{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
            test_filename_xml = "default_20171017_145602"
            default_build = True
            
        # ws_dir is the top level directly of the workspace set to the test job manifest
        # xml name withtout extension
        ws_dir = os.path.splitext(test_filename_xml)[0]
        print ws_dir 
        
        if self.jenkins:
            # in the case we're running on jenkins, prepend the path to the workspace
            ws_dir = self.ws_path + ws_dir
         
        # create new dir for workspace with sdh_dev_mx as root
        ret = self.do_bash("mkdir " + ws_dir)
        
        # cd into ws and  repo init using ssh
        cmd = "cd " + ws_dir + " && repo init -u ssh://git@github.com/armmbed/mbl-manifest.git -b " + args.mbl_manifest_branch + " -m default.xml"
        ret = self.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to preform repo init from mbl-manifest.git.")
            return ret
        
        if not default_build:
            # cp new manifest.xml with revisions for testing
            cmd = "cp " + self.ws_path + "/" + jobs_dir + "/" + test_filename_xml + " " + ws_dir + "/.repo/manifests"
            ret = self.do_bash(cmd)
            if ret != 0:
                logging.debug("Error: failed to copy test manifest xml to repo manifest directory.")
                return ret
        
            # repo init with new manifest
            cmd = "cd " + ws_dir + " && repo init -m " + test_filename_xml
            ret = self.do_bash(cmd)
            if ret != 0:
                logging.debug("Error: failed to repo init with local manifest.")
                return ret
    
        # repo sync
        cmd = "cd " + ws_dir + " && repo sync"
        print "cmd=%s" % cmd
        ret = self.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to repo sync.")
            return ret
    
        # generate and store the pinned-manfiest
        cmd = "cd " + ws_dir + " && repo manifest -r -o " + ws_dir + "-pinned-manifest.xml"
        ret = self.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to repo sync.")
            return ret

        # link to shared downloads
        if not self.jenkins:
            cmd = "cd " + ws_dir + " && ln -s /data/2284/shared_downloads downloads"
            ret = self.do_bash(cmd)
            if ret != 0:
                logging.debug("Error: failed to link to shared_downloads.")
                return ret
        
        # cp the do_build.sh to the top level dir
        file = tempfile.NamedTemporaryFile()
        scriptfile.write(do_build_sh)
        scriptfile.flush()
        cmd = "cp " + scriptfile.name + " " + ws_dir + "/"
        ret = self.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to copy build script.")
            return ret
    
        # run build. this will fail the first time because bblayers.conf has the wrong layers in it
        cmd = "cd " + ws_dir  + " && /bin/bash " + os.path.basename(scriptfile.name)
        print cmd
        print "cmd=%s" % cmd
        ret = self.do_bash(cmd)
        
        # Remove the bad bblayers.conf received from the mbl-manifest repo.
        cmd = "rm " + ws_dir + "/build-mbl/conf/bblayers.conf"
        ret = app.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to remove bad bblayers.conf")
            return ret

        # Copy the correct bblayers.conf to conf dir.
        bblayers_conf_file = tempfile.NamedTemporaryFile()
        bblayers_conf_file.write(bb_layers_conf)
        bblayers_conf_file.flush()
        cmd = "cp " + bblayers_conf_file.name + " " + ws_dir + "/build-mbl/conf/bblayers.conf"
        ret = app.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to copy new bblayers.conf into place.")
            return ret
    
        # run build 2nd time, which should succeed with correct bblayers.conf
        cmd = "cd " + ws_dir  + " && /bin/bash " + os.path.basename(scriptfile.name)
        ret = app.do_bash(cmd)
        if ret != 0:
            logging.debug("Error: failed to perform build.")
            return ret

        return ret


    # ARGUMENTS:  
    # test_filename_xml    manifest.xml filename that specifies build
    def do_mbl_console_image(self, test_filename_xml):

        ret = MBL_FAILURE
        
        # ws_dir is the top level directly of the workspace set to the test job manifest
        # xml name without extension
        ws_dir = os.path.basename(test_filename_xml)
        ws_dir = os.path.splitext(ws_dir)[0]
         
        # cp the do_build.sh to the top level dir
        cmd = "cp " + "do_build_wip.sh" + " " + ws_dir + "/"
        ret = self.do_bash(cmd)
        if ret != 0:
            logging.error("Error: failed to copy build script.")
            return ret

        # run build 2nd time, which should succeed with correct bblayers.conf
        cmd = "cd " + ws_dir  + " && ./do_build_wip.sh"
        print cmd
        ret = app.do_bash(cmd)
        if ret != 0:
            logging.error("Error: failed to perform build.")
            return ret

        return ret


# class to help build test campaigns
class mbl_test_campaign:
    
    # generates a set of test.xml test files forming a test campaign
    def create(self, manifest, revfile, project_name):

        ret = MBL_FAILURE
        if revfile != "" and manifest != "":
    
            # read manifest file
            tree_mbl = ET.parse(manifest)
            root_mbl = tree_mbl.getroot()
            
            # read in the commits into an ordered array
            commitId = open(revfile).read().split("\n")
            
            # reverse the array so that commit id at the end of the list are tested first
            commitId.reverse()
           
            # extract the project line of interest from the xml tree
            #project_meta_oe = root_mbl.findall(".//*[@name='openembedded/meta-openembedded']")
            search_exp = ".//*[@name='" + project_name + "']"
            project_meta_oe = root_mbl.findall(search_exp)
            
            # can do approx 15 builds per night. step through hashes so there is about 
            # 15 tests
            #step_size = int(len(commitId)/15)
            step_size = 1
            test_id = 1
            
            # loop through array selecting commits to test
            for i in range(1, len(commitId), step_size):
                
                project_meta_oe[0].set('revision', commitId[i])
    
                # save to new file with the basename of the manifest filename and "_test_nn.xml" appended
                output_fname = os.path.basename(args.manifest)
                output_fname = os.path.splitext(output_fname)[0]
                output_fname += ('_test_%02d.xml' % test_id)
                print "Writing test manifest file: %s : commit_is: %s" % (output_fname, commitId[i])
                tree_mbl.write(output_fname, encoding="UTF-8", xml_declaration=None, default_namespace=None, method="xml")
                test_id += 1
            
            ret = MBL_SUCCESS
    

    # generates a set of test.xml test files forming a test campaign
    def create2(self, manifest, revfile, project_name):

        ret = MBL_FAILURE
        test_id = 1
        tree_mbl = ET.parse(manifest)
        root_mbl = tree_mbl.getroot()

        if manifest != "":
            with open("commits_data.txt", "rt") as f:
                for line in f:
                    meta_virt_commit_id = line.split(',')[0]
                    oe_core_commit_id = line.split(',')[2]
    
                    # extract the project line of interest from the xml tree
                    project_meta_virt = root_mbl.findall(".//*[@name='git/meta-virtualization']")
                    project_oe_core = root_mbl.findall(".//*[@name='openembedded/openembedded-core']")
        
                    # set the new revisions
                    project_meta_virt[0].set('revision', meta_virt_commit_id)
                    project_oe_core[0].set('revision', oe_core_commit_id)
    
                    # save to new file with the basename of the manifest filename and "_test_nn.xml" appended
                    output_fname = os.path.basename(args.manifest)
                    output_fname = os.path.splitext(output_fname)[0]
                    output_fname += ('_test_%02d.xml' % test_id)
                    print "Writing test manifest file: %s : meta-virt: %s, oe-core: %s" % (output_fname, meta_virt_commit_id, oe_core_commit_id)
                    tree_mbl.write(output_fname, encoding="UTF-8", xml_declaration=None, default_namespace=None, method="xml")
                    test_id += 1
            
            ret = MBL_SUCCESS
    



if __name__ == "__main__":

    ret = MBL_FAILURE
    do_print_usage = False
    app = mbl_tool()
    
    # setup logging
    logging.basicConfig(filename= 'mbl_tool_script.log',level=logging.DEBUG)

    # command line argment setup and parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--do-mbl-console-image', action='store_true', help='perform the mbl-console-image build (--manifest required)')
    parser.add_argument('--do-test', action='store_true', help='perform test code')
    parser.add_argument('--manifest', default='', help='specify manifest.xml file for test or template for test campaign generation')
    parser.add_argument('--jobsdir', default='', help='specify dir containing manifest.xml files for test campaign.')
    parser.add_argument('--tcg-revfile', default='', help='test campaign generator: text file containing list of commits to populate in revision field.')
    parser.add_argument('--tcg-project-name', default='', help='test campaign generator: project name for which to set revision field.')
    parser.add_argument('--mbl-manifest-branch', default='master', help='mbl-manifest branch from which to take project.')


    args = parser.parse_args()

    if args.do_mbl_console_image:
        # Rebuild a previously created workspace, that may have only partially built, for example
        if args.manifest == "":
            logging.error("Error: name of manifest.xml not set. Required to identify workspace dir.")
            do_print_usage = True
        
        else: 
            # just perform build step
            ret = app.do_mbl_console_image(args.manifest)

    elif args.jobsdir != "":
        # run a test campaign of all the test.xml files in the specified dir
        # get the list of files and loop over them performing the tests. 
        job_list = app.get_job_list(args.jobsdir)
        job_list.sort(cmp=None, key=None, reverse=False)
        for job in job_list:
            # continue even if job is unsuccessful 
            ret = app.do_build(job, args.jobsdir, args.mbl_manifest_branch)

    elif args.tcg_revfile != "" or args.tcg_project_name != "":

        if args.tcg_project_name == "":
            logging.error("Error: project name not set. Required to specify project for setting revision.")
            do_print_usage = True

        elif args.tcg_revfile == "":
            logging.error("Error: revisions file not set. Required to specify commit for generating test campaign.")
            do_print_usage = True
        else:
            tc = mbl_test_campaign()
            ret = tc.create(args.manifest, args.tcg_revfile, args.tcg_project_name) 
            
    elif args.do_test:
            tc = mbl_test_campaign()
            ret = tc.create2(args.manifest, args.tcg_revfile, args.tcg_project_name) 
            
            
    else:
        ret = app.do_build(args.manifest, args.jobsdir, args.mbl_manifest_branch)

    if do_print_usage:
        parser.print_usage()


    sys.exit(ret)
    
