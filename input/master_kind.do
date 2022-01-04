*******************************
***  MASTER DO-FILE			***   
***  Dataset: Kind	     	***
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
global alt_gr "20${thisyear}-17"                             
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
*a)1. Erstellung eines Datensatzes mit Haushalts- und Personeninformationen benutzt *hbrutto und *pbrutto
  *2.Identifikation von Kindern bis 16 Jahren im HH Generierung der *kzahl variablen
****************************************************************************************************
do "H:/git/isdatadoku/kind/0_kind_load_data.do"
****************************************************************************************************
*b) Generierung der Vars `wave'khv `wave'khvp `wave'kmutti `wave'kmup
****************************************************************************************************
do "H:/git/isdatadoku/kind/1_kindanzeiger.do"
****************************************************************************************************
*c) 1. Vergleich mit Elternzeigern aus Vorjahr 
 *  2. Umbenennen und Labeln der Variablen und Values im Kinderdatensatz
****************************************************************************************************
do "H:/git/isdatadoku/kind/2_kind_Vergleich_und_Label.do"
****************************************************************************************************
*d) Kind_long erstellen
****************************************************************************************************
do "H:/git/isdatadoku/kind/3_kind_long_de_en.do" //saves final as long 

