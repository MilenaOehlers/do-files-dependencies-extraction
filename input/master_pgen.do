*******************************
***  MASTER DO-FILE			***   
***  Dataset:				***
*******************************
set more off
clear

global  thisyearlist 	"1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018" // list with all years until current year
global	aufwuchs	0		// set this global to 1 if this year, there is an Aufwuchssample, else to 0
global	deen 		"_de"	// set this global to _de or _en to create the german or english dataset, respctively

* 1. Globals for work in do-Files
****************************************************************************************************
global 	thisyear:		di substr("$thisyearlist", length("$thisyearlist")-1, length("$thisyearlist")) 	// number with abbreviated current year
global 	lastyear		"`=$thisyear -1'" 																// number with abbreviated last year
if "${deen}" =="_de" global DEEN "\DE"
if "${deen}" =="_en" global DEEN "\EN"
global  thiswave    "`=$thisyear -8'"
global 	lastyear	"`=$thisyear -1'"
global 	lastwave	"`=$thiswave -1'"

global lastyearlist "09 10 11"
global lastwavelist "z ba bb"
	foreach yr of num 11/$lastyear {
	global lastyearlist $lastyearlist `yr'
	global lastwavelist $lastwavelist is`yr'
	}
global yearlist $lastyearlist $thisyear
global wavelist $lastwavelist is$thisyear
****************************************************************************************************

* 2. Create needed Folders
****************************************************************************************************
*cap mkdir "$..."
*cap mkdir "$..."
****************************************************************************************************

* 3. Create needed Paths as globals
****************************************************************************************************
qui do H:\git\isdatadoku\pathways.do
global  dofilepath		"H:/git/isdatadoku/" //Path of dofiles
****************************************************************************************************

***4. Load Ados:
****************************************************************************************************
*** 4.1 Other Ados
capture which adolist
if _rc==111{ 
	ssc install adolist
}
quietly adolist list
local allAdos `r(names)'
foreach package in fre labutil2 {
	if !regexm("`r(names)'", " `package' ") {
		display as result "Paket " as error  "`package'" as result " wird versucht über SSC-Server zu installieren"
		ssc install `package'
	} 
} 	
*** 4.2 Own functions
*do "FUN_Generierung_WIKI.do"
****************************************************************************************************

* 5. do-Files for generation
****************************************************************************************************

***********************************************************************************
*  												Generation of pgen - introduction
***********************************************************************************
*
*  PGEN is a dataset of all persons that answered the p-questionnaire. The variables are mostly generated, ie. the raw data 
*  are combined to produce new variables (unlike p.dta). The final dataset is a long file. 
*  
*  There are 2 master do-files: 1st do file (master_pgen.do) produces just the current wave in a wide format. 
*								2nd do file (master_pgen_l.do) appends the current wave to the old long dataset.
*
***********************************************************************************
* 										         This do-file (master_pgen.do)
***********************************************************************************
*  
*  First half of the syntax 
*		aims to collect all the necessary data from various sources, mostly old pgen but also bio or ppfad.
*  		Each year, current raw data is added by the same logic as the previous ones ->
*  		append current p-datasets (old-, new- and BIP-samples) as well as berufe-und-bildung datasets (old-, new- and BIP-sample): see below.

*  		All the information is then collected in "$helpdatapgen\IS[current_wave]_pgen_WORKFILE2.dta".
*
*  In the second half of the syntax, 
*		the generation takes places. For each variable, a separate sub-do-file exists in the Gitlab/pgen-folder.
*  		Each sub-do-file contains a variable-specific-program written by SOEP-IS but based on the syntax used by FiD (Familie in Deutschland) 
*  		All the pgen syntax was based by that of FiD in 2012. Hence, if noone in SOEP-IS knows where some part of code came from, it is worth checking it -> ask David Richter. 
*  		On the other hand, any particularities in the final dataset (like value labels) should be compared to the SOEP-core pgen, not FiD.  
*  
*  		The generation follows after running the sub-do-file and launching the program together with its arguments in the master-do-file. Some of these sub-do-files need to be 
*  		checked and adjusted every year. The usual procedure is to open all of them and check the syntax thoroughly.

do "..\pgen\00_programs.do"
do "..\pgen\01_part1.do"
do "..\pgen\02_p_gen_erwtyp.do"  
do "..\pgen\03_p_gen_betr.do"
do "..\pgen\04_p_gen_oeffd.do"
do "..\pgen\05_part2_begin.do"
do "..\pgen\06_p_gen_nation.do" 
do "..\pgen\07_p_gen_psbil_psbilo_psbila.do"
do "..\pgen\08_p_gen_pbbil_pbbilo.do"
do "..\pgen\09_p_gen_famstd_partnr_partz.do"   // These 3 variables are generated separately by the partner-procedure. The author of the current wave partner should provide the necessary dataset
do "..\pgen\10_p_gen_bilzeit.do"
do "..\pgen\11_p_gen_erwzeit.do"
do "..\pgen\12_p_gen_tatzeit.do"
do "..\pgen\13_p_gen_vebzeit.do"
do "..\pgen\14_p_gen_uebstd.do"
do "..\pgen\15_p_gen_lfs.do" // TODO schon jahresunabhängig?
do "..\pgen\16_p_gen_nace.do"
do "..\pgen\17_p_gen_autono.do"
do "..\pgen\18_p_gen_isced.do" 
do "..\pgen\19_p_gen_casmin.do" 
do "..\pgen\20_p_gen_stib.do"
do "..\pgen\21_p_gen_mode.do" // MO18 jahresunabh?
do "..\pgen\22_p_gen_month.do" // MO18 jahresunabh?
do "..\pgen\23_p_gen_labgro.do"
do "..\pgen\24_p_gen_labnet.do"
do "..\pgen\25_p_gen_allbet.do"			//MK17: Why so many [-1] this year?
do "..\pgen\26_p_gen_emplst.do"
do "..\pgen\27_p_gen_jobch.do"
do "..\pgen\28_p_gen_sndjob.do" // sndjob 2011 generiert in dem pgen master long
do "..\pgen\29_save_data.do"

* 6. Delete unnecessary datasets
****************************************************************************************************
*cap erase "..."

