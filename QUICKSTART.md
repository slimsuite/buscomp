# Installation

## Step 1. Clone the git repository, or download and unpack the buscomp tarball.

git clone https://github.com/slimsuite/buscomp.git 

## Step 2. Unpack the BUSCO run data.

cd buscomp/example 
tar -xzf example_busco3.tgz

**NOTE:** Instead of unpacking pre-generated results, you could run BUSCO v3 on the genomes in `example/fasta/`.

# Run BUSCOMP on example data

## Step 3. Create a run directory.

The example data has already been run in the `run/` directory to compare against. To test run the program, create a second directory (e.g. `test/`) to run the program in:

mkdir test/ 
cd test/

## Step 4. Run BUSCOMP.

The required commands have been provided in an `ini` file in the `run/` directory, `example.ini`:

``` 
genomesize=13.1e6 # This sets the genome size for NG50 and LG50 calculations (not required) 
genomes=../example.genomes.csv # This pre-populates genome aliases and descriptions (not required) 
groups=../example.groups.csv # This pre-populates analysis groups of genomes (not required) 
runs="../busco3/run_*" # This identifies the set of run directories to process (wildcards allowed). 
fastadir=../fasta/ # This identifies the location for any fasta files for BUSCOMP analysis. 
basefile=yeast # This sets the prefix for all output files. 
```

**Note:** File and directory paths in the `example.ini` file are all relative and assume BUSCOMP is being run from a subdirectory of `example/`. To run the example data from a different directory, these paths will have to be altered.

BUSCOMP can then be run with a simply python command, providing the program with the INI file and setting the interactivity to -1 for a non-interactive run (`i=-1`):

python ../../code/buscomp.py -ini ../run/example.ini i=-1

**Note:** You will also need to set `minimap2=PROG` unless directly callable, and may need to set the Rstudio pandoc environment variable prior to running:

export RSTUDIO_PANDOC=/Applications/RStudio.app/Contents/MacOS/pandoc 
python ../../code/buscomp.py -ini ../run/example.ini i=-1 -minimap2 ~/Bioware/minimap2/minimap2

**Note:** This is the same as putting all the `example.ini` commands in the program call:

python ../../code/buscomp.py genomesize=13.1e6 genomes=../example.genomes.csv groups=../example.groups.csv runs="../busco3/run_*" fastadir=../fasta/ basefile=yeast i=-1 -minimap2 ~/Bioware/minimap2/minimap2

BUSCOMP will take a few minutes to run on the example data. You can speed it up a bit by allocating multiple threads with with `forks=X` command, e.g.:

python ../../code/buscomp.py -ini ../run/example.ini i=-1 -minimap2 ~/Bioware/minimap2/minimap2 -forks 4

**Note:** BUSCOMP recognises two parameter formats: `-forks 4` and `forks=4` are directly equivalent.

## Step 5. Look at Report files

Provided R is installed and `$RSTUDIO_PANDOC` is set, two report files should have been produced: `yeast.N3L20ID0U.html` and `yeast.N3L20ID0U.full.html`. Open the `yeast.N3L20ID0U.html` file and read the report. If everything ran correclty, it should match the results in `example/run/yeast.N3L20ID0U.html`. The `*.full.html` contains some additional tables and plots. These reports are designed to be largely self-explanatory. See the [main documentation](../BUSCOMP.md) for details.
