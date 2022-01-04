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
do "..\hbrutto\0_is_altbrutto_sample.do"
if $aufwuchs==1 do "..\hbrutto\1_is_aufwuchsbrutto_sample.do"
do "..\hbrutto\2_BIP_hbrutto_sample.do"
do "..\hbrutto\3_choosename.do"
do "..\hbrutto\4_is_regtype.do"
do "..\hbrutto\5_save_data.do"

* 6. Delete unnecessary datasets
****************************************************************************************************
*cap erase "..."
