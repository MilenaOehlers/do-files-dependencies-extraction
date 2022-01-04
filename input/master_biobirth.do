*******************************
***  MASTER DO-FILE			***   
***  Dataset: biobirth	    ***
*******************************
set more off
clear
capture log close
set type double, perm

global  thisyearlist 	"2009 2010 2011 2012 2013 2014 2015 2016 2017 2018" // list with all years until current year

* 1. Globals for work in do-Files
****************************************************************************************************
global aufwuchs 0		                                                                               //kein Aufwuchssample für 2018 verfügbar
global  lastyearlist:	di substr("$thisyearlist", 1, length("$thisyearlist")-5) 					   // list with all years until last year
global 	thisyear:		di substr("$thisyearlist", length("$thisyearlist")-1, length("$thisyearlist")) // number with abbreviated current year
global 	lastyear		"`=$thisyear -1'" 															   // number with abbreviated last year
global  thiswave: 		word count $thisyearlist 			                                           // number of all soep-is waves
global  lastwave    "`=$allwaves -1'"                                                                  // number of all soep-is waves last year										
global wave "IS${thisyear}"                                                                                             
****************************************************************************************************
* 2. Create needed Folders
****************************************************************************************************
/*                            
cap mkdir "$..."
cap mkdir "$..."
*/
****************************************************************************************************
* 3. Create needed Paths as globals
****************************************************************************************************
qui do "H:/git/isdatadoku/pathways.do"	// runs pathways.do
global  dofilepath		"H:/git/isdatadoku/" //Path of dofiles
****************************************************************************************************

****************************************************************************************************
***4. Load Ados:
****************************************************************************************************
*** 4.1 Other Ados
*net install soeptools, from(http://ddionrails.org/soeptools/) // following code should also work and also take care of useold and saveascii
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
qui do "H:/git/isdatadoku/WIKI/FUN_Generierung_WIKI.do"

****************************************************************************************************
*5. do-Files for generation of kind
****************************************************************************************************
*5.1
do "H:/git/isdatadoku/biobirth/0_biobirth_basis.do"
*5.2 
do "H:/git/isdatadoku/biobirth/1a_biobirth.do"
do "H:/git/isdatadoku/biobirth/1b_biobirth.do"
*5.3
do "H:/git/isdatadoku/biobirth/2a_biobrthm.do"
do "H:/git/isdatadoku/biobirth/2b_biobrthm.do"
*5.4
do "H:/git/isdatadoku/biobirth/3a_biobirth_Korrekturen_Mutter.do"
do "H:/git/isdatadoku/biobirth/3b_biobirth_Korrekturen_Vater.do"
do "H:/git/isdatadoku/biobirth/3c_biobirth_Corrections_Mothers.do"
do "H:/git/isdatadoku/biobirth/3d_biobirth_Corrections_Fathers.do"

