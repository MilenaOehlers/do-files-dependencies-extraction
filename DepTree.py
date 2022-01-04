#################################################################################################
# This script is used to create a dependency tree of the SOEP-IS Dofiles every year;
# It consits of three main parts (functions):
#################################################################################################
# (_1___) It saves a copy of all STATA Do-files into the folder "DepTreeSTATA", which is
#           modified slightly: When executed in STATA, it will do exactly the same as the original
#           dofile, but every time it uses or saves a dataset, it will additionally print a line
#           into a target file that contains the name of the sub-dofile, the line number of the command,
#           if it uses, merges or saves, and the name of the dataset.
# (_2___) Then python commands STATA to execute the modified master- and sub-dofiles, creating
#           one target file for each master-dofile.
# (_3___) The target files will then be read back into python and analyzed row by row in order to
#           create the dependency tree on the level of master and subdofiles, create a graph of master
#           dependencies and derive independent (=starter) subdofiles as well as the sequence,
#           in which subdofiles should be executed (by assigning them levels- all level 0 subdofiles
#           can be edited simultaneously, once they are completed, all level 1 subdofiles can be edited
#           simultaneously and so on... in the first year of execution (2018), it turned out that there are loop
#           dependencies between the subdofiles (not good! if possible, change that in the stata files!)
#           in that case, the remaining subdofiles are listed under the "rest_with_loop_dependencies" keyword
#################################################################################################
import os
import shutil
import subprocess
import pandas as pd
import math
import re
import pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout, write_dot
from networkx.algorithms.cycles import find_cycle

class dependencyTree(object):
    def __init__(self,restore_attr=False):
        try:
            assert restore_attr
            self.load_attr()
        except:
            self.master_sourcedir = os.getcwd()  # current folder

            self.target_dir = "DepTreeSTATA"
            self.dofiles_dir = "modifiedDofiles"
            self.MASTER  = "MASTER"
            self.error_dir = "executionErrors"
            self.csv_dir = "dependencyCSVs"
            self.results_dir = "results"

            self.target_dofiles = self.uni_abs_join(self.target_dir,self.dofiles_dir)
            self.master_targetdir = self.uni_abs_join(self.target_dofiles,self.MASTER)
            self.target_csvs = self.uni_abs_join(self.target_dir,self.csv_dir)
            self.target_errors = self.uni_abs_join(self.target_dir,self.error_dir)
            self.target_results = self.uni_abs_join(self.target_dir,self.results_dir)

            self.masters = [file.replace(".do","") for file in os.listdir(self.master_sourcedir) if file[:7]=="master_" and file[-3:]==".do"]
            self.master_subdos = []

            self.file = {master: master + ".do" for master in self.masters}
            self.sourcepath = {master: self.uni_abs_join(self.master_sourcedir, master + ".do") for master in self.masters}
            self.targetpath = {master: self.uni_abs_join(self.master_targetdir, master + ".do") for master in self.masters}

            self.use = ["use", "useold","using"]
            self.merge_append = ["merge", "append"]
            self.save = ["save", "saveold","saveascii"]
            self.do_run = ["do", "run"]

            self.dataset_commands = self.use + self.merge_append + self.save
            self.dofile_commands = self.do_run

    # execution functions:
    def _1___prepareCSVcreation(self):
        self._1a__prepare()
        self._1b__checkErrorsBeforeMasterCreation()
        self._1c__createMastermaster()
        self._1d__createModifiedMasterFiles()
        self._1e__checkErrorsBeforeSubdofileCreation()
        self._1f__createModifiedSubdofiles()
        self._1g__moveAdditionalDofiles()
    def _1a__prepare(self):
        # Create folder for modified Dofile-copies: (after deleting possibly already existing folder)
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
        os.mkdir(self.target_dir)
        os.mkdir(self.target_dofiles)
        os.mkdir(self.target_errors)
        os.mkdir(self.target_csvs)
        os.mkdir(self.target_results)
        os.mkdir(self.master_targetdir)
    def _1b__checkErrorsBeforeMasterCreation(self):
        # Scan Master Folder for Sub Do-Files:
        error = False
        with open(self.target_errors + "/errors_DepTree_creation.csv", "w") as errorfile:
            errorfile.write("file,where,what,error message\n")
            for master in self.masters:
                masterpath = self.sourcepath[master]
                if not "master_" in masterpath:
                    error = True
                    errorfile.write(
                        "{0},filename,{0},All Dofiles in the MASTER folder must be master-dofiles; their names have to begin with \"master_\"".format(
                            masterpath))
                with open(masterpath, "r") as source_master:
                    source_master = self.realtext(source_master, "text")
                    for line, content, delimiter in source_master:  #
                        for command in self.dataset_commands:
                            if command != "useold" and self.command_where(command, content) != []:
                                error = True
                                errorfile.write(
                                    "{},line {},{},No Datasets can be used, merged, or saved in a masterfile. Datasets can only be touched by Subdofiles!".format(
                                        master, line + 1, content))
        assert not error, "An error occured during DependencyTree creation (on level 1 of 2). Please see errors_DepTree_creation.csv in the MASTER folder for information about which issues have to be addressed where, and how, before DependencyTree can be created."
        os.remove(self.target_errors + "/errors_DepTree_creation.csv")
    def _1c__createMastermaster(self):
        # Create master-master file that will execute all masterfiles in DepTreeSTATA:
        with open(self.uni_abs_join(self.master_targetdir, "mastermaster.do"), "w") as mastermaster:
            for master in self.masters:
                masterpath = self.targetpath[master]
                mastermaster.write("do \"{}\" \n".format(masterpath))
    def _1d__createModifiedMasterFiles(self):
        # Create modified copies of the masterfiles in DepTreeSTATA:
        for master in self.masters:
            subdo_targetdir = self.uni_abs_join(self.target_dofiles, master)
            os.mkdir(subdo_targetdir)
            with open(self.sourcepath[master], "r") as source_master:
                with open(self.targetpath[master], "w") as target_master:
                    target_master.write(
                        "file open dependencies_{0} using ../../{1}/dependencies_{0}.csv, write replace\n".format(
                            master, self.csv_dir))
                    source_master = self.realtext(source_master, "text")
                    for line, content, delimiter in source_master:  #
                        command, splitat, subdo_sourcepath, rest = self.get_command_splitat_path(
                            self.dofile_commands, content)
                        if subdo_sourcepath is None:  # if master does not execute sub-dofile in this line:
                            target_master.write(
                                content.replace("clear all", "clear") + "\n")  # copy its content to targetfile
                        else:  # if master does execute sub-dofile in this line:
                            subdo = subdo_sourcepath.split("/")[-1].replace(".do", "")
                            self.master_subdos += [(master, subdo)]
                            self.file[(master, subdo)] = subdo + ".do"
                            self.sourcepath[(master, subdo)] = subdo_sourcepath
                            self.targetpath[(master, subdo)] = self.uni_abs_join(subdo_targetdir, subdo + ".do")
                            if delimiter != "cr": target_master.write("#delimit cr")
                            target_master.write(content.split(splitat)[0] + splitat + " \"{}\"\n".format(
                                self.targetpath[(master, subdo)]))
                            if delimiter != "cr": target_master.write("#delimit {}".format(delimiter))
                    target_master.write("file close dependencies_" + master)
    def _1e__checkErrorsBeforeSubdofileCreation(self):
        error = False
        with open(self.target_errors + "/errors_DepTree_creation.csv", "w") as errorfile:
            errorfile.write("file,where,what,error message\n")
            for master, subdo in self.master_subdos:
                if any([el in self.sourcepath[(master, subdo)] for el in ["`", "'", "$"]]):
                    error = True
                    errorfile.write(
                        "{},line ?,{},,No Macros ($global / `local')  can be used in subdofilepaths in masterfile. Write the paths without them!".format(
                            master, self.sourcepath[(master, subdo)]))
                with open(self.sourcepath[(master, subdo)], "r") as source_subdofile:
                    source_subdofile = self.realtext(source_subdofile, "text")
                    for line, content, delimiter in source_subdofile:
                        if self.command_where(self.dofile_commands, content) != []:
                            error = True
                            errorfile.write(
                                "{},line {},{},,No Dofiles can be executed in Subdofiles. They must all be executed by the respective masterfile!".format(
                                    source_subdofile, line + 1, content))
        assert not error, "An error occured during DependencyTree creation (on level 2 of 2). Please see errors_DepTree_creation.csv in the MASTER folder for information about which issues have to be addressed where, and how, before DependencyTree can be created."
        os.remove(self.target_errors + "/errors_DepTree_creation.csv")
    def _1f__createModifiedSubdofiles(self):
        # Create modified copies of subdofiles in resp. folder in DepTreeSTATA:
        for master_subdo in self.master_subdos:
            with open(self.sourcepath[master_subdo], "r") as source_subdofile:
                source_subdofile = self.realtext(source_subdofile, "text")
                with open(self.targetpath[master_subdo], "w") as target_subdofile:
                    for line, content, delimiter in source_subdofile:
                        command, splitat, dataset_path, rest = self.get_command_splitat_path(self.dataset_commands,
                                                                                             content)
                        if dataset_path is not None:
                            if delimiter != "cr": target_subdofile.write("#delimit cr\n")
                            target_subdofile.write("cap {\n")
                            target_subdofile.write(content.split(command)[
                                                       0] + " file write dependencies_{} \"{},{},{},{}\" _n\n".format(
                                master_subdo[0], master_subdo[1], line + 1, command, dataset_path))
                            target_subdofile.write("}\n")
                            target_subdofile.write("cap {\n")
                            target_subdofile.write(content.replace("clear all", "clear") + "\n")
                            target_subdofile.write("}\n")
                            if delimiter != "cr": target_subdofile.write("#delimit {}\n".format(delimiter))

                        else:
                            target_subdofile.write(content.replace("clear all", "clear") + "\n")
    def _1g__moveAdditionalDofiles(self):
        additional_dofiles = [file for file in os.listdir("H:\git\isdatadoku") if file[-3:] == ".do"]
        for file in additional_dofiles:
            shutil.copyfile(os.path.join("H:\git\isdatadoku", file), os.path.join(self.target_dofiles, file))

    def _2___STATAcreateCSVs(self):
        try: subprocess.call(["stata","do","mastermaster.do"])
        except: assert False, "Error during MASTER/DepTreeSTATA/modifiedDofiles/mastermaster.do execution by STATA. Execute mastermaster.do directly from STATA in order to see where the defect is, and correct it in the original (!) masterfile in the MASTER-folder. Always make sure that all dofiles in MASTER run smoothly without errors before executing DepTree.py!"

    def _3___analyseCSVs(self):
        self._3a__readCSVsIntoDepDFs()
        self._3b__createDFsaved()
        self._3c__mapDFsavedToUsedMerged()
        self._3d__prepareAssignment()
        self._3e__reduceDepDFs()
        self._3f__deriveTables()
        self._3g__createDependencyTreeMap()
    def _3a__readCSVsIntoDepDFs(self):
        """ Each master-CSVs contains columns indicating the subdofile, line, command(=use/merge/save) and dataset
            Master and Subdofile-Indices are added for subsequent calculations and the whole content is saved in
            the Dataframes dep_dfs[master].
            For these DepDFs, if it turns out that the same dataset is saved multiple times in the same master file,
            only the row corresponding to the last saved version is kept.
            """
        dep_dfs = {}
        for csv in [os.path.join(self.target_csvs,csv) for csv in os.listdir(self.target_csvs)]:
            master = csv.split("dependencies_")[1].replace(".csv", "")
            df = pd.read_csv(csv, sep=",", names=["this_subdofile", "this_subdofile_line", "command", "dataset"])
            df["dataset"] = df["dataset"].apply(self.unify_paths).apply(self.unify2)
            df["this_master"] = master
            df["this_master_ind"] = list(range(len(df["this_master"])))
            for row in range(len(df["this_subdofile"])):
                df["this_subdofile_ind"] = df.iloc[:row, 0].tolist().count(df.iloc[row, 0])
            col_order = df.columns.tolist()
            newcol_order = col_order[-2:] + col_order[:-2]
            df = df[newcol_order]
            dep_dfs[master] = df
        self.dep_dfs_3a1 = dep_dfs
    def _3b__createDFsaved(self):
        """ For each master-file, the rows with "save" commands are extracted from DepDFs and appended to self.df_saved.
                    The same dataset cannot be saved by more than one masterfile. It is asserted that this
                    condition holds; if it doesnt, an error is raised. """
        self.dep_dfs_3a2 = {}
        for master, df in self.dep_dfs_3a1.items():
            df = df.reset_index(drop=True)
            saveddatasets,drop_rowinds = [],[]
            for i in df.index.tolist()[::-1]:
                if "save" in df.loc[i, "command"]:
                    if df.loc[i, "dataset"] in saveddatasets:
                        drop_rowinds += [i]
                    else:
                        saveddatasets += [df.loc[i, "dataset"]]
            if drop_rowinds!=[]:
                drop_rowinds = drop_rowinds if len(drop_rowinds)>1 else drop_rowinds[0]
            df = df.drop(drop_rowinds,axis=0)
            self.dep_dfs_3a2[master] = df

        df_saved = pd.DataFrame()
        for master, df in self.dep_dfs_3a2.items():
            df_save = df[["save" in df.loc[ind,"command"] and df.loc[ind,"dataset"][-4:]!=".tmp" for ind in df.index]]
            df_saved =  df_saved.append(df_save,ignore_index=True) #df_save if self.df_saved is None else
            df_saved = df_saved.drop(["command"],axis=1)

        dupl = df_saved[df_saved.duplicated(['dataset'], keep=False)].sort_values(by='dataset')
        self.df_saved = df_saved.set_index("dataset")

        assert dupl.shape[0]==0 , "Some Datasets are saved under same path by more than one Master:\n"+dupl
    def _3c__mapDFsavedToUsedMerged(self):
        """ For each row in DepDF, where a dataset is used or merged (<-column:command),
            the corresponding master- and subdofile-names and subdofile-line where it was saved
            are added in new columns"""
        self.dep_dfs_3a3 = {}
        thisyear = max([int(data.split("DATA2/SOEP-IS/SOEP-IS 20")[1][:2]) for data in self.df_saved.index.tolist() if "DATA2/SOEP-IS/SOEP-IS 20" in data])
        for master, df in self.dep_dfs_3a2.items():
            newcols = ["needed_master","needed_master_ind","needed_subdofile","needed_subdofile_ind","needed_line","needed_level"]
            savedcols = ["this_master","this_master_ind","this_subdofile","this_subdofile_ind","this_subdofile_line"]

            if not newcols[0] in df.columns.tolist():
                df = df.reindex(columns = df.columns.tolist()+newcols)
            for row in df.index:
                if "save" not in df.loc[row,"command"]:
                    if df.loc[row, "dataset"][-4:] == ".dta":
                        if df.loc[row, "dataset"] in self.df_saved.index.tolist():
                            df.loc[row,newcols] = self.df_saved.loc[df.loc[row,"dataset"],savedcols].tolist() + [-1]
                            if df.loc[row,"this_master"].strip() == df.loc[row,"needed_master"].strip():
                                df.loc[row,"needed_level"] = 0
                        elif "Rohdaten/" in df.loc[row, "dataset"] or "Datenlieferung/" in df.loc[row, "dataset"]:
                            df.loc[row, newcols] = ['rawdata']*len(newcols)
                        elif "/DATA/" in df.loc[row, "dataset"] or "soep-core" in df.loc[row, "dataset"]:
                            df.loc[row, newcols] = ['soepCOREdataset']*len(newcols)
                        elif "DATA2/SOEP-IS/SOEP-IS 20" in df.loc[row, "dataset"]:
                            datasetyear = df.loc[row, "dataset"].split("DATA2/SOEP-IS/SOEP-IS 20")[1][:2]
                            if int(datasetyear)!= int(thisyear):
                                df.loc[row, newcols] = ['old_generateddata']*len(newcols)
                            else:
                                datasetname = df.loc[row, "dataset"]
                                matchingmasters = [masterr.replace("_long", "_l").replace("master_","") for masterr in self.masters]
                                try: longestmatching = sorted([(len(masterr), masterr) for masterr in matchingmasters if masterr in datasetname])[-1][-1]
                                except:
                                    try:
                                        if any([brokenmaster.replace("BROKEN_master_","").replace(".do","") in datasetname
                                                for brokenmaster in os.listdir() if "BROKEN_" in brokenmaster]): longestmatching = None
                                        else:
                                            longestmatching = sorted([(len(masterr), masterr) for masterr in matchingmasters if masterr.replace("_l","") in datasetname])[-1][-1]
                                            if longestmatching.replace("_l","") in [master.replace("master_","") for master in self.masters]:
                                                longestmatching = longestmatching.replace("_l","")
                                    except:
                                        if "kid" in datasetname: longestmatching = "kind"
                                        else: longestmatching = None
                                if "/finaldata/" in df.loc[row, "dataset"]:
                                    if longestmatching is not None:
                                        currdf = self.dep_dfs_3a1["master_"+longestmatching]
                                        if master.replace("master_","")==longestmatching:
                                            df.loc[row, newcols] = ['same_master'] * (len(newcols) - 1) + [0]
                                        else:
                                            df.loc[row, newcols] = currdf.loc[currdf.index.tolist()[-1],savedcols].tolist() + [-1]
                                    else: df.loc[row, newcols] = ['finaldata_unknown_master']*len(newcols)
                                elif "/helpdata/" in df.loc[row, "dataset"]:
                                    if longestmatching is not None:
                                        if master.replace("master_","")==longestmatching:
                                            df.loc[row, newcols] = ['same_master'] * (len(newcols)-1) +[0]
                                        else: df.loc[row, newcols] = ['unknown']*len(newcols)
                                    else:
                                        df.loc[row, newcols] = ['helpdata_unknown_master'] * len(newcols)
                                else: df.loc[row, newcols] = ['unknown']*len(newcols)
                        else: df.loc[row, newcols] = ['unknown']*len(newcols)
                    elif df.loc[row, "dataset"][-4:] == ".tmp":
                        df.loc[row, newcols] = ['tmpfile'] * len(newcols)
                    else: "weird_datatype"
                else: df.loc[row, newcols] = [None]*len(newcols)
            #self.
            self.dep_dfs_3a3[master] = df
    def _3d__prepareAssignment(self):
        self.dep_dfs = {}
        for master, df in self.dep_dfs_3a3.items():
            df["level"] = math.nan
            changedinds = []
            for ind in df.index.tolist():
                if isinstance(df.loc[ind,"needed_master"],str) and isinstance(df.loc[ind,"this_master"],str):
                    if df.loc[ind,"needed_master"].strip() == df.loc[ind,"this_master"].strip() and df.loc[ind,"needed_level"] == -1:
                        changedinds += [ind]
                        df.loc[ind,"needed_level"] = 0
                    else: pass
            self.dep_dfs[master] = df
        self.ready = 0
        self.master_ind = {}  # master, ind
        self.level_saveddatasets = {}  # level, saved datasets
        self.master_to_level_ind = pd.DataFrame(index=self.masters, columns=[0, 1, 2])
        self.master_to_level_percentage = pd.DataFrame(index=self.masters, columns=[0, 1, 2])
        self.get_master_ind_for_completed_subdofiles()
    def _3e__reduceDepDFs(self):
        self.reduced_dep_dfs = {}
        self.no_dupl_dfs = {}
        for master in self.masters:
            inds = [ind for ind in list(self.dep_dfs[master].index) if self.dep_dfs[master].loc[ind, "needed_level"] == -1]
            inds = inds if len(inds) != 1 else inds[0]
            self.reduced_dep_dfs[master] = df = self.dep_dfs[master].loc[inds, :]
            indlst,datasets = [],[]
            if isinstance(df, pd.DataFrame):
                for ind in df.index.tolist():
                    newdat = str(df.loc[ind,"dataset"]).strip()
                    if newdat not in datasets:
                        datasets +=  [newdat]
                        indlst += [ind]
                self.no_dupl_dfs[master] = df.loc[indlst,:] if len(indlst)>1 else df.loc[indlst[0],:] if len(indlst)==1 else None
            elif isinstance(df, pd.Series):
                self.no_dupl_dfs[master] = df
            else:
                self.no_dupl_dfs[master] = None
    def _3f__deriveTables(self):
        self._3f1_IndepMasters_MasterNet_DetailedDeps()
        self._3f2_SubdoNet_SubdoLevels()
        self._3f3_saveResults()
    def _3f1_IndepMasters_MasterNet_DetailedDeps(self):
        this_master_subdos, needed_master_subdos = [], []
        for master in self.masters:
            df = self.no_dupl_dfs[master]
            if isinstance(df, pd.Series): df = df.to_frame
            if isinstance(df, pd.DataFrame):
                for ind in list(df.index):
                    thistup, neededtup = (df.loc[ind, "this_master"], df.loc[ind, "this_subdofile"]), (
                    df.loc[ind, "needed_master"], df.loc[ind, "needed_subdofile"])
                    if thistup not in this_master_subdos: this_master_subdos += [thistup]
                    if neededtup not in needed_master_subdos: needed_master_subdos += [neededtup]
        self.this_master_subdos = this_master_subdos
        self.needed_master_subdos = needed_master_subdos

        indx = pd.MultiIndex.from_tuples(this_master_subdos, names=("this master", "this subdo"))
        cols = pd.MultiIndex.from_tuples(needed_master_subdos, names=("needs master", "needs subdo"))

        indep_masters = []
        master_net = pd.DataFrame(0,index=self.masters,columns=self.masters)
        detailled_dependencies_csv = pd.DataFrame(index=indx, columns=cols)

        for master in self.masters:
            df = self.no_dupl_dfs[master]
            if isinstance(df, pd.Series): df = df.to_frame
            if isinstance(df, pd.DataFrame):
                for ind in list(df.index):
                    # detailled_dependencies_csv:
                    thistup = (df.loc[ind, "this_master"], df.loc[ind, "this_subdofile"])
                    neededtup = (df.loc[ind, "needed_master"], df.loc[ind, "needed_subdofile"])
                    this_perc_compl = df.loc[ind, "this_master_ind"] / self.dep_dfs[master]["this_master_ind"].tolist()[-1]
                    try:
                        needed_perc_compl = df.loc[ind, "needed_master_ind"] / self.dep_dfs[master]["needed_master_ind"].tolist()[-1]
                        needed_perc_compl = round(needed_perc_compl, 2)
                    except: needed_perc_compl = np.nan
                    perc_compl__thisneeded_line = np.array([
                        [   str(round(this_perc_compl, 2)),                 str(needed_perc_compl)              ],
                        [   str(int(df.loc[ind, "this_subdofile_line"])),   str(int(df.loc[ind, "needed_line"])) ]
                    ])
                    if isinstance(detailled_dependencies_csv.loc[thistup, neededtup], list):
                        detailled_dependencies_csv.loc[thistup, neededtup] = detailled_dependencies_csv.loc[thistup, neededtup] + [
                            perc_compl__thisneeded_line]
                    if isinstance(detailled_dependencies_csv.loc[thistup, neededtup], np.ndarray):
                        detailled_dependencies_csv.loc[thistup, neededtup] = [detailled_dependencies_csv.loc[thistup, neededtup]] + [
                            perc_compl__thisneeded_line]
                    else:
                        detailled_dependencies_csv.loc[thistup, neededtup] = perc_compl__thisneeded_line
                    # network masters:
                    master_net.loc[master,df.loc[ind, "needed_master"]] = 1
            if df is None: indep_masters += [master]

        self.indep_masters = indep_masters
        self.master_net = master_net
        self.detailled_dependencies_csv = detailled_dependencies_csv
    def _3f2_SubdoNet_SubdoLevels(self):
        previ = []
        thiss = sorted(list(set(self.this_master_subdos)))
        reverted = thiss[::-1][:-1]
        for ind2 in reverted:
            prevv = thiss[::-1][reverted.index(ind2) + 1]
            if prevv[0] == ind2[0]:
                previ += [prevv]
        inn = sorted(list(set(self.needed_master_subdos + previ)))
        symm = sorted(list(set(thiss+inn)))

        self.subdofile_net = pd.DataFrame(0, index=symm, columns=symm)  # sorted()

        for ind3 in symm:
            # deriving dependencies of subsequent subdofiles in same master:
            prevv = symm[::-1][symm[::-1].index(ind3) + 1] if symm.index(ind3) != 0 else (None, None)
            prev = prevv if prevv[0] == ind3[0] else None
            cols1 = [colll for colll in self.needed_master_subdos if ind3 in thiss and isinstance(self.detailled_dependencies_csv.loc[ind3, colll], np.ndarray)]
            colss = sorted(list(set(cols1 + [prev]))) if prev is not None else sorted(cols1)
            self.subdofile_net.loc[ind3, colss] = 1

        def rec_hierarch(df):
            levelmap = {}
            level = 0
            failed = False
            while df.shape!=(0,0) and failed==False:
                olddf = df.copy()
                inc = list(df.sum(axis=1))
                levelmap[level] = [list(df.index)[i] for i in range(len(list(df.index))) if inc[i]==0]
                df = df.drop(levelmap[level],axis=0).drop(levelmap[level],axis=1)
                if olddf.shape == df.shape: failed=True
                level += 1
            if failed==True: levelmap["rest_with_loop_dependencies"] = list(df.index)
            return levelmap

        self.levelmap_subdofiles = rec_hierarch(self.subdofile_net)
    def _3f3_saveResults(self):
        with open(os.path.join(self.target_results,"_Result_Files_Explanation.txt"),"w") as res:
            res.write("""General Info:
            
The results presented in this folder are based of the analysis of the following master-files,
whose name follow the DepTree conditions specified in the WIKI.

""")
            for master in self.masters:
                res.write(master+"\n")
            res.write("""
            
Hence, if any masterfiles are missing in the list above, their dependencies of the listed masters and
vice versa cannot be seen in the results. 


Execution Sequence: 

In "independent_masters.txt" the master files which do not depend on any other file are listed, thus you
can start each wave with those. In "subdofile_execution_sequence.txt" a subdofile execution sequence is recommended. n


Dependency Nets and Detailed Dependency Information:

On the level of masters and subdofiles, respectively, "master_net.csv" and "subdofile_net.csv" show which file (column header)
needs which other files (row names). More detailed information can be found in 'detailled_dependencies.csv', where the entries indicate
[  [ % of current masterfile completed when dataset is used,   % of needed masterfile completed when dataset is saved  ]
   [ line of subdofile where dataset is used,                  line of needed subdofile where dataset is saved    ]  ]
The dependencies on the level of masters are also depicted as a graph in 'Master_Dependencies__Visualization_Version_x'.png 
- there are 10 different versions as the visualization prodcued by python is kind of random and some graphs are too chaotic. 
They all have the same content though, you can choose any of them.
Nodes at the thinner edge ends are dependent on those on the thick ends.     

""")

        with open(os.path.join(self.target_results,"independent_masters.txt"),"w") as f:
            f.write("The following masters do not depend on other masters.\nThey are thus masters with which you would start each wave.\n\n")
            for item in self.indep_masters:
                f.write(str(item))
        self.master_net.T.to_csv(os.path.join(self.target_results,"master_net.csv"),sep=",")
        self.detailled_dependencies_csv.T.to_csv(os.path.join(self.target_results, 'detailled_dependencies.csv'),sep=",")

        self.subdofile_net.T.to_csv(os.path.join(self.target_results,"subdofile_net.csv"),sep=",")
        with open(os.path.join(self.target_results, "subdofile_execution_sequence.txt"), "w") as f:
            f.write(
                """Subdofile Execution Sequence:

In the following, the subdofiles that depend on each other across masters are assigned to levels
 - meaning, that all subdofiles in the same level can be edited and executed simultaneously,
 and after they are completed, all subdofiles in the next level can be edited simultaneously and so on.
 Please note that only subdofiles are listed here with cross-masterfile dependencies - hence, 
 if in level 0 there is only "ISbiopar_02mnr_vnr.do" listed, the previous bioparen-subdofiles 
 "ISbiopar_00Prolog_Stata_Missings.do" and "ISbiopar_01Biomatch.do" have to be executed before you can 
 begin with "ISbiopar_02mnr_vnr.do".
 """)
            for level, lst  in self.levelmap_subdofiles.items():
                f.write("\nlevel {}:\n".format(level))
                for item in sorted(lst):
                    f.write(str(item)+"\n")
    def _3g__createDependencyTreeMap(self):
        adjacency_matrix = self.master_net
        rows, cols = np.where(adjacency_matrix == 1)
        edges = list(zip([self.masters[r].replace("master_", "") for r in rows.tolist()],
                         [self.masters[c].replace("master_", "") for c in cols.tolist()]))
        for i in range(10):
            graphname = 'Master_Dependencies__Visualization_Version_{}'.format(i)

            gr = nx.DiGraph()
            for node in self.masters: gr.add_node(node.replace("master_", ""))
            for edge in edges: gr.add_edge(*edge)
            fig = plt.figure(figsize=(8,8))
            fig.suptitle(graphname)
            nx.draw(gr, with_labels=True, arrows=True)
            fig.savefig(os.path.join(self.target_results,graphname+".png"))

    # helpfunctions:
    def only_non_comments_goon_or_not(self,content,no_block_comments=0,delimiter="cr"):
        content = ' '.join(content.strip().split()) # strip outer whitespaces, join multiple spaces to one
        realcontent = ""
    
        simplequote, advquote = False,0
        iplus,restline_iscomment,noblockadd,goon,endblock = 1,False,False,False,False
        i = 0
        while i < len(content):
            endblock,iplus = False,1
            if content[i]=="\"": 
                if i>0 and content[i-1]=="`": advquote = advquote +1 
                elif i<len(content)-1 and content[i+1]=="'": advquote = advquote -1 if advquote!=0 else 0
                else: simplequote = not simplequote
            if advquote==0 and not simplequote: 
                if i==0 and content[i]=="*" and content[0:2]!="*/" and no_block_comments==0: 
                    restline_iscomment=True
                if i<len(content)-1 and content[i:i+2]=="//": 
                    iplus = 2
                    if no_block_comments==0 and not restline_iscomment: 
                        restline_iscomment,noblockadd=True,True
                        if i<len(content)-2 and content[i+2]=="/": 
                            goon,iplus=True,3
                if i<len(content)-1 and content[i:i+2]=="/*" and noblockadd==False: 
                    no_block_comments += 1
                    iplus = 2
                if i<len(content)-1 and content[i:i+2]=="*/" and noblockadd==False: 
                    no_block_comments = no_block_comments - 1 if  no_block_comments!=0 else 0
                    iplus,endblock = 2,True
                if i== len(content)-1 and delimiter!="cr" and content[i-1:i+1]!=delimiter: 
                    goon = True
            if no_block_comments==0 and restline_iscomment==False and endblock==False:
                if "#delimit"==content[i:i+8] or "# delimit"==content[i:i+9]: 
                    delimiter = content[i:].split("delimit")[1].strip().split(" ")[0]
                    realcontent += "#delimit "+delimiter
                    i = len(content)
                else:    
                    realcontent += content[i]
            i += iplus
        if no_block_comments>0: goon = True
        return realcontent, no_block_comments, goon, delimiter
    def realtext(self,filetext, is_file_or_text):
        no_block_comments, goon, delimiter = 0,False,"cr"
        together,alltog = "",[]
        if is_file_or_text=="file":
            with open(filetext,"r") as test:
                text = test
        if is_file_or_text=="text":
            text = filetext
        for line, content in enumerate(text):
            realcontent, no_block_comments, goon, delimiter = self.only_non_comments_goon_or_not(content,no_block_comments, delimiter)
            together += " " + realcontent
            if goon==False: 
                alltog += [(line, together,delimiter)]
                together = ""
        return alltog
    def string_ranges(self,content):
        pairs = [("`\"","\"'"),("\"","\"")]
        str_ranges = []
        for pair in pairs:
            started = False
            for i in list(range(len(content))):
                if not any([i in list(range(*rng)) for rng in str_ranges]):
                    if started==False and pair[0] == content[i:i+len(pair[0])]: started, start_ind = True, i
                    elif started==True and pair[1] == content[i:i+len(pair[1])]: started, str_ranges = False, str_ranges + [(start_ind,i+len(pair[1]))]
        return str_ranges
    def command_where(self,command_lst, realcontent):
        if isinstance(command_lst,str): command_lst = [command_lst]
        commands = [command + " " for command in command_lst]
        
        str_ranges = self.string_ranges(realcontent)
        command_indices = [m.start() for command in commands for m in re.finditer(command, realcontent) \
                  if m.start() == 0 or (  m.start() != -1 and realcontent[m.start() - 1] == " "  )]

        indxs = [ind for ind in command_indices  \
                 if not any([ind in list(range(*rng)) for rng in str_ranges])]

        return indxs
    def get_command_splitat_path(self,command_lst, content):
        ret = (None,None,None,None)
        if self.command_where(command_lst, content)!=[]:
            commands = [c+" " for c in command_lst if self.command_where(c,content)]
            if len([com for com in commands if com !="using "])==1:
                if "using " in commands: splitat,command = "using ", [cm for cm in commands if cm !="using "][0]
                else: splitat = command = commands[0]
                command_str = content.split(splitat)[1].split("\"")[1] if content.count("\"") >= 2 \
                            else content.split(splitat)[1].strip().split(",")[0]
                rest = content.split(command_str)[1]
                command_str = self.uni_abs_join(command_str)
                if "pathways.do" not in command_str: ret = (command, splitat, command_str,rest) 
        return ret
    def unify_paths(self,path):
        path = path.replace("\\", "/")
        while "//" in path: path = path.replace("//", "/")
        return path
    def unify2(self,path):
        path = "S:/DATA2/SOEP-IS/" + path.split("SOEP-IS/")[1] if "SOEP-IS/" in path else path
        path = "S:/DATA/" + path.split("/DATA/")[1] if "/DATA/" in path else path
        path = path.replace("H:/git/isdatadoku/MASTER","")
        path = path[1:] if path[0]=="/" else path
        return path
    def uni_abs_join(self,*args):
        return self.unify_paths(os.path.abspath(os.path.join(*args)))
    def get_master_ind_for_completed_subdofiles(self):
        self.master_subdofile_completionind = {}
        for master, df in self.dep_dfs.items():
            self.master_subdofile_completionind[master] = {}
            for masterr,subdofile in self.master_subdos:
                if master==masterr:
                    completionind = max(idx for idx, val in enumerate(df.loc[:,"this_subdofile"]) if val == subdofile)
                    self.master_subdofile_completionind[master][subdofile] = completionind

    # metafunctions for improved algorithm performance:
    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        if callable(method) and method.__name__[0]=="_":
            print("{}...".format(method.__name__))
        return method
    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        self.save_attr()
    def save_attr(self):
        if not os.path.exists('./DepTreeSTATA/pickledAttributes'):
            os.makedirs('./DepTreeSTATA/pickledAttributes')
        with open('./DepTreeSTATA/pickledAttributes/attr','wb') as pic:
            pickle.dump(self.__dict__,pic)
    def load_attr(self):
        with open('./DepTreeSTATA/pickledAttributes/attr', 'rb') as pic:
            self.__dict__ = pickle.load(pic)