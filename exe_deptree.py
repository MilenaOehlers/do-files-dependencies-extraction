# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 21:35:05 2020

@author: moehlers
"""
############################################################################
# Execute the following lines to get DepTree (by clicking 'run'):
############################################################################

import DepTree as deptree
d = deptree.dependencyTree(restore_attr=True)
d._1___prepareCSVcreation()
d._2___STATAcreateCSVs()
d._3___analyseCSVs()

############################################################################
# In case an error occurs in the _1___ or _3___ functions, their subfunctions
# can be executed at the bottom of this script
# (after removing the leading "#") one by one after fixing the error in DepTree.py
# Comment out lines that shall not be executed with "#"
# If you do this, make sure restore_attr is set to True above in deptree.dependencyTree()
############################################################################
# # If an error occurs during _2___, execute
#  H:\git\isdatadoku\MASTER\DepTreeSTATA\modifiedDofiles\MASTER\mastermaster.do
# manually - if errors occur during execution,
# try to row-by-row-execute as many lines in mastermaster.do as possible
# in order to get CSVs for each master-file.
#
# (hence, if error is in
# mastermaster.do > master_bioparen.do > ISbiopar_02mnr_vnr.do > line 13,
# open
#   H:\git\isdatadoku\MASTER\DepTreeSTATA\modifiedDofiles\master_bioparen\ISbiopar_02mnr_vnr.do
# in the same STATA where error occured, and try to make code run from there.
# If that doesnt work, go on to next <use <Dataset>> command in
#   H:\git\isdatadoku\MASTER\DepTreeSTATA\modifiedDofiles\master_bioparen\ISbiopar_02mnr_vnr.do
# and try to run it from there.
# Then execute the remaining code of bioparen and the other masterfiles as called
# by mastermaster.do)
############################################################################

#d._1___prepareCSVcreation(self):
#d._1a__prepare()
#d._1b__checkErrorsBeforeMasterCreation()
#d._1c__createMastermaster()
#d._1d__createModifiedMasterFiles()
#d._1e__checkErrorsBeforeSubdofileCreation()
#d._1f__createModifiedSubdofiles()
#d._1g__moveAdditionalDofiles()
#d._1a__prepare()
#d._1b__checkErrorsBeforeMasterCreation()
#d._1c__createMastermaster()
#d._1d__createModifiedMasterFiles()
#d._1e__checkErrorsBeforeSubdofileCreation()
#d._1f__createModifiedSubdofiles()
#d._1g__moveAdditionalDofiles()

#d._2___STATAcreateCSVs()

#d._3___analyseCSVs()
#d._3a_readCSVsIntoDepDFs()
#d._3b_createDFsaved()
#d._3c__mapDFsavedToUsedMerged()
#d._3d__prepareAssignment()
#d._3e__reduceDepDFs()
#d._3f__deriveTables()
#d._3f1_IndepMasters_MasterNet_DetailedDeps()
#d._3f2_SubdoNet_SubdoLevels()
#d._3f3_saveResults()
#d._3g__createDependencyTreeMap()