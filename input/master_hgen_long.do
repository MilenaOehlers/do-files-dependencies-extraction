*******************************
***  MASTER DO-FILE			***   
***  Dataset: hegn_long		***
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
* 1.) SOEP hgen long vorbereiten (Filter: Wellen 2009-2011, Sample "E" & "I")
* 2.) IS11 hgen (Welle 2011) hinzufügen
* 3.) IS12 hgen (Welle 2012) hinzufügen
* 4.) SOEP hgen long alte Wellen hinzufügen (Filter: Wellen 1998-2008, Sample "E")
* 5.) Löschen der Personen, die aus dem Sample E nicht zu IS gehören
do  "H:\git\isdatadoku\hgen_long\0_preparation.do"
do  "H:\git\isdatadoku\hgen_long\1_is_hpfad_help.do" // Syntax von Michael: hgen\is_hpfad_help.do ; Syntax ursprünglich von Paul ("S:\DATA2\SOEP-IS\SOEP-IS 2012 Generierung HiWi\Syntax\h_l\is_hpad_help.do")
* 6.) IS13 hgen (Welle 2013) hinzufügen
* 7.) IS14 hgen (Welle 2014) hinzufügen
* 8.) IS15 hgen (Welle 2015) hinzufügen
* 9.) IS16 hgen (Welle 2016) hinzufügen
do "H:\git\isdatadoku\hgen_long\2_append_and_correct.do"
do "H:\git\isdatadoku\hgen_long\3_h_gen_anzahlkind.do"
do "H:\git\isdatadoku\hgen_long\4_intermediate.do"
* 10.)IS17 hgen (Welle 2017) hinzufügen
* 11.)Korrekturen am Datensatz
* 12.)Labelling auf Englisch
do "H:\git\isdatadoku\hgen_long\5_hgen_labels.do"
do "H:\git\isdatadoku\hgen_long\6_hgen_labels_addition.do"
do "H:\git\isdatadoku\hgen_long\7_hgen_var_labels.do"
do "H:\git\isdatadoku\hgen_long\8_save_data.do"

* 6. Delete unnecessary datasets
****************************************************************************************************
*cap erase "..."






