*******************************
***  MASTER DO-FILE			***   
***  Dataset:	p.dta	***
*******************************
set more off
clear

global  thisyearlist 	"2009 2010 2011 2012 2013 2014 2015 2016 2017 2018" // list with all years until current release year

* 1. Globals for work in do-Files
****************************************************************************************************
global  lastyearlist:	di substr("$thisyearlist", 1, length("$thisyearlist")-5) 						// list with all years until last year
global  thiswave: 		word count $thisyearlist 														// number of all soep waves
global  lastwave	"`=$thiswave -1'" 																// number of all soep waves last year
global 	thisyear:		di substr("$thisyearlist", length("$thisyearlist")-1, length("$thisyearlist")) 	// number with abbreviated current year
global 	lastyear		"`=$thisyear -1'" 																// number with abbreviated last year
global  thisyearfull: di substr("$thisyearlist", length("$thisyearlist")-4, length("$thisyearlist")) // number of current year in full for char _dta[version] command
****************************************************************************************************


* 2. Create needed Folders
****************************************************************************************************
*capture confirm file "missingfolder/"
*if _rc mkdir "missingfolder/"
****************************************************************************************************


* 3. Create needed Paths as globals
****************************************************************************************************
qui do "H:/git/isdatadoku/pathways.do" 	// runs pathways.do if dofilepath is one level under path of pathways.do
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
foreach package in useold saveascii soeptools {
	if !regexm("`r(names)'", " `package' ") {
		display as result "Paket " as error  "`package'" as result " wird versucht über SSC-Server zu installieren"
		ssc install `package'
	} 
} 	
*** 4.2 Own functions
do "H:/git/isdatadoku/WIKI/FUN_Generierung_WIKI.do"
****************************************************************************************************


* 5. do-Files for generation
****************************************************************************************************
do "H:/git/isdatadoku/p/0_p_generation_start.do"
do "H:/git/isdatadoku/p/1_p_recoding_of_pnat.do"
do "H:/git/isdatadoku/p/2_p_generation_continued_with_excel.do"
do "H:/git/isdatadoku/p/3_p_final_corrections.do"
do "H:/git/isdatadoku/p/4_p_labeling.do"


* 6. Delete unnecessary datasets
****************************************************************************************************
*cap erase "..."


