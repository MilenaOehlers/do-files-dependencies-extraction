General Info:
            
The results presented in this folder are based of the analysis of the following master-files,
whose name follow the DepTree conditions specified in the WIKI.

master_bio
master_bioage
master_biobirth
master_bioparen
master_hbrutto_l
master_hgen
master_hgen_long
master_h_l
master_ibip_parent
master_ibip_pupil
master_ilanguage
master_imputation
master_inno
master_inno_h
master_kind
master_partner
master_pbrutto_l
master_pgen
master_pgen_l
master_ppfad
master_p_l

            
Hence, if any masterfiles are missing in the list above, their dependencies of the listed masters and
vice versa cannot be seen in the results. 


Execution Sequence: 

In "independent_masters.txt" the master files which do not depend on any other file are listed, thus you
can start each wave with those. In "subdofile_execution_sequence.txt" a subdofile execution sequence is recommended. n


Dependency Nets and Detailed Dependency Information:

On the level of masters and subdofiles, respectively, "master_net.csv" and "subdofile_net.csv" show which file (column header)
needs which other files (row names). More detailed information can be found in 'detailled_dependencies.csv', where the entries indicate
[  [ % of current masterfile completed when dataset is used,   % of needed masterfile completed when dataset is saved  ]
   [ line of subdofile where dataset is used,                  line of needed subdofile where dataset is saved    ]  ]
The dependencies on the level of masters are also depicted as a graph in 'Master_Dependencies__Visualization_Version_x'.png 
- there are 10 different versions as the visualization prodcued by python is kind of random and some graphs are too chaotic. 
They all have the same content though, you can choose any of them.
Nodes at the thinner edge ends are dependent on those on the thick ends.     

