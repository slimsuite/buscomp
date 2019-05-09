# Setup path to BUSCOMP to run
BUSCOMP="/Users/redwards/Dropbox/code/slimsuite/tools/buscomp.py -ini test.ini -minimap2 ~/Bioware/minimap2/minimap2"

#1# Standard run
python $BUSCOMP basefile=test1

#2# No summarise
python $BUSCOMP basefile=test2 summarise=F

#3# No BUSCOMP compilation
python $BUSCOMP basefile=test3 buscompseq=F

#4# Simple run plus pre-defined BUSCOMP
python $BUSCOMP runs=../example/fulltables/ buscofas=test1.buscomp.fasta basefile=test4

#5# Pure BUSCOMP
python $BUSCOMP runs= ratefas="../example/fasta/*.fsa" buscofas=test1.buscomp.fasta basefile=test5
