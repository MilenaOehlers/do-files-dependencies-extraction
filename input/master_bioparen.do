********************************************************************************************************************* 
* Projekt: 	  	BIOPAREN-IS 2018
*
* Master Do-File
*	
* Author:		Lucia Grajcarova	
*
* This Version: 16.03.2020 Charvan Chaikhmous									
*********************************************************************************************************************  

***MO: 	set the following variables in order to obtain the desired dataset
global 	thisyear 	"18"	// set this variable to the actual year, e.g. "19"
global 	lastyear	"17"	// set this variable to the previous year, e.g. "18"
global 	thiswave 	"10"	// set this variable to the number of the actual Welle, e.g. "11"
global  thisintv	"35"	// set this variable to the number of the actual interview round number, e.g. "36"

clear all
set more off, permanently
global  dofilepath		"H:/git/isdatadoku/" //Path of dofiles
qui do "../pathways.do"

do "../bioparen/ISbiopar_00Prolog_Stata_Missings.do"
do "../bioparen/ISbiopar_01Biomatch.do"
do "../bioparen/ISbiopar_02mnr_vnr.do"
do "../bioparen/ISbiopar_03bildun_aus_pgen.do"
do "../bioparen/ISbiopar_04stib_aus_pgen.do"
do "../bioparen/ISbiopar_05biogener.do"
do "../bioparen/ISbiopar_06biocheck.do"
do "../bioparen/ISbiopar_07erster_aufbau_bioparen.do"
do "../bioparen/ISbiopar_08prestige.do"
do "../bioparen/ISbiopar_09alter_zeitpunkt_erhebung.do"
do "../bioparen/ISbiopar_10gebland_eltern_gen.do"
do "../bioparen/ISbiopar_11Todjahre_Eltern.do"
do "../bioparen/ISbiopar_12geschw_ansp.do"
do "../bioparen/ISbiopar_13outfile.do"
