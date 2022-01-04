*******************************
***  MASTER DO-FILE			***   
***  Dataset: ppfad	     	***
*******************************
set more off
clear
capture log close

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
*a) Erstellung notwendiger Datensätze und Generierung von Variablen 
do "H:/git/isdatadoku/ppfad/0_ppfad_basis.do"
****************************************************************************************************
*b)3k migback & co
do "H:/git/isdatadoku/ppfad/1_ppfad_germborn_migback.do"
qui do "H:/git/isdatadoku/ppfad/1c_ppfad_mig_dtlabel.do"
****************************************************************************************************
*c) * 3l gebmonat/gebmoval
****************************************************************************************************
do "H:/git/isdatadoku/ppfad/2_ppfad_gebmo.do"
****************************************************************************************************
*d) Prüfungen & Finalisieren
do "H:/git/isdatadoku/ppfad/3_ppfad_Pruefungen_finalisieren.do"
****************************************************************************************************
*e) englischer Datensatz
do "H:/git/isdatadoku/ppfad/4_ppfad_labels_eng.do" //MK17: attention!! this file also needs to be adapted each year (only the one loop, though)
