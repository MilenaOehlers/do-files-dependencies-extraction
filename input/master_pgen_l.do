*******************************
***  MASTER DO-FILE			***   
***  Dataset: Pgen_long		***
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

* #### Arbeitsschritte #### ***************
*1: Use current wave dataset and merge with impuation information if already available
do "../pgen_l/00_preparation.do"
do "../pgen_l/01_Imputationvars.do"
*2: Append the current wave to pgen_long 
*3: Do small recodings & corrections
*4: Recode variables to -5 if not genereted in SOEP core
*5: Add prestige scores
do "..\pgen_l\02_intermediate.do"
do "..\pgen_l\03_pgen_scores_labels.do"
*6: German labels
do "..\pgen_l\04_09_pber_labels.do"
do "..\pgen_l\05_more_labels.do"
do "..\pgen_l\06_pgen_labels_de.do"
do "..\pgen_l\07_pgen_labels.do" 
*3: Labelling auf Englisch
do "..\pgen_l\08_pgen_scores_labels_en.do"
do "..\pgen_l\04_09_pber_labels.do"
do "..\pgen_l\10_labels_addition.do"
do "..\pgen_l\11_pgen_var_labels.do"
do "..\pgen_l\12_more_labels_en.do"
*4: Check count
do "..\pgen_l\13_count_check.do"
*******************************************

* 6. Delete unnecessary datasets
****************************************************************************************************
*cap erase "..."
