*******************************
***  MASTER DO-FILE			***   
***  Dataset:				***
*******************************
set more off
clear all
set matsize 800 
set maxvar 32767, perm

global  thisyearlist 	"1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018" // list with all years until current year
global	aufwuchs	0		// set this global to 1 if this year, there is an Aufwuchssample, else to 0
global  bip 		1       // set to 1 if bip sample exists this year, else to 0
global	deen 		"_de"	// set this global to _de or _en to create the german or english dataset, respctively
** this dofile has to be executed various times for different setups of the following variables:
global	suppl		0		// set to 0 to impute old samples (every year!)
							//	   to 1 to impute supplementary samples (only in some waves there are supplementary samples!) 	
global 	noknn		5		// set to 5 and 10 and compare distributions and correlations of observed and imputed values for hghinc; choose the better model
							// -> 2017: knn=5 and knn=10 worked both well, take knn=10 as no of observations high ~3300
							// -> 2018: knn=5 performedslightly better than knn=10 for burnin=50, wait for stone-server results for final decision
global	stone		0		// David: set to 1 if code is to be executed on Stone-Server, 
							//     		  to 0 if code is to be executed on local machine
* h-imputation global definitions:
global 	rohname 	"EIBIP14S1-4" 	// set to shorthand for all newly introduced samples in past (Rohdatensätze (E,I), BIP (BIP14) And past Aufwuchssample (S1-4)
global 	aufname		"S5"			// if this year a Aufwuchssample is introduced, set the samplename accordingly (probably S5 is the right name)	
* p-imputation global definitions:
global	dataset 	"together"	// set to "together"/ "pglabgro" or "pglabnet" to generate respective datasets below (p-imputation)				
global keyword_preselection 1


* 1. Globals for work in do-Files
****************************************************************************************************
global 	thisyear:		di substr("$thisyearlist", length("$thisyearlist")-1, length("$thisyearlist")) 	// number with abbreviated current year
global 	lastyear		"`=$thisyear -1'" 																// number with abbreviated last year
if "${deen}" =="_de" global DEEN "\DE"
if "${deen}" =="_en" global DEEN "\EN"
global 	lastyear	"`=$thisyear -1'"
global  thiswave    "`=$thisyear -8'"
global 	lastwave	"`=$thiswave -1'"
global lastyearlist "09 10 11"
global lastwavelist "z ba bb"
	foreach yr of num 11/$lastyear {
	global lastyearlist $lastyearlist `yr'
	global lastwavelist $lastwavelist is`yr'
	}
global yearlist $lastyearlist $thisyear
global wavelist $lastwavelist is$thisyear
if $suppl==0 global roh_auf  $rohname 				
if $suppl==1 global roh_auf  $aufname			
if $stone==0 {	
	qui do "H:\git\isdatadoku\pathways.do"  				// this line must stay BEHIND def of the global variables above										// only used for knn=5 and knn=10 model comparison: 
	global path 	"$imputation"						// - calculation on local machine
	global noburnin	10									// - low burnin saves computation time (set to 50!!)
	}
if $stone==1 {															// only used when model is chosen (knn=5 OR knn=10)
	global path 	"/soep/drichter/imputation"	// - calculation on cluster (more computing power)
	global noburnin 2000												// - high burnin for more accurate computation
	}


****************************************************************************************************

* 2. Create needed Folders
****************************************************************************************************
cap mkdir "$path" 			// creates folder if doesnt exist
cap mkdir "&path/helpdata"
cap mkdir "&path/finaldata"

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
do "../imputation/1_dataset_h.do"
do "../imputation/2_equation_h.do"
do "../imputation/3_imputation_h.do"
do "../imputation/4_dataset_p.do"
do "../imputation/5_equation_p.do"
do "../imputation/6_imputation_p.do"

* 6. Delete unnecessary datasets
****************************************************************************************************
*cap erase "..."
