#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import glob
import datetime

import pcraster as pcr

import configuration
import virtualOS as vos

import logging
logger = logging.getLogger(__name__)

# get the configuration/ini file given in the system argument
iniFileName = os.path.abspath(sys.argv[1])

# option for debugging
debug_option = str(sys.argv[2])

# object to handle configuration/ini file
generalConfiguration = configuration.Configuration(iniFileName = iniFileName, debug_mode = False, no_modification = False)

# clean any files exists on the ouput directory
clean_previous_output = True
if clean_previous_output and os.path.exists(generalConfiguration.globalOptions['outputDir']): shutil.rmtree(generalConfiguration.globalOptions['outputDir'])

# make log folder and initialize logging
generalOutputFolder = generalConfiguration.globalOptions['outputDir']
logFileFolder = generalOutputFolder+"/global/log/"
if os.path.exists(logFileFolder): shutil.rmtree(logFileFolder)
os.makedirs(logFileFolder)
generalConfiguration.initialize_logging(logFileFolder)

# copy ini file to the log folder:
timestamp = datetime.datetime.now()
shutil.copy(iniFileName, logFileFolder + \
                         os.path.basename(iniFileName) + '_' +  str(timestamp.isoformat()).replace(":",".") + '.ini')

# make global output maps directory (it will contain a "maps" directory that will contain merged pcraster maps)
global_maps_folder = generalConfiguration.globalOptions['outputDir']+"/global/maps/"
if os.path.exists(global_maps_folder): shutil.rmtree(global_maps_folder)
os.makedirs(global_maps_folder)

# make the backup of these python scripts to a specific backup folder and go to the backup folder
scriptDir = generalConfiguration.globalOptions['outputDir']+"/global/scripts/"
if os.path.exists(scriptDir): shutil.rmtree(scriptDir)
os.makedirs(scriptDir)
path_of_this_module = os.path.abspath(os.path.dirname(__file__))
# working/starting directory where all script files are used
for filename in glob.glob(os.path.join(path_of_this_module, '*.py')):
    shutil.copy(filename, scriptDir)
os.chdir(scriptDir)    

# pcr-globwb clone areas (for pcr-globwb multiple runs)
clone_codes = list(set(generalConfiguration.globalOptions['cloneAreas'].split(",")))
if clone_codes[0] == "Global": clone_codes = ['M%02d'%i for i in range(1,54,1)]

# TODO: run a steady state modflow to estimate the initial values for relativeGroundwaterHead, storGroundwater and baseflow

# command lines for PCR-GLOBWB 
i_clone = 0
cmd = ''
for clone_code in clone_codes:

   cmd += "python deterministic_runner_glue_october_2015.py " + iniFileName +" "+\
                                                                debug_option +" "+\
                                                                clone_code +" "+\
                                                                "1.00 -0.25 0.00 1.00"+" "
   cmd = cmd+" & "
   i_clone += 1

# don't foget to add the following line
cmd = cmd + "wait"       

print cmd

# execute PCR-GLOBWB and MODFLOW
vos.cmd_line(cmd, using_subprocess = False)      
