# BUSCOMP: BUSCO Compiler and Comparison tool

```
BUSCOMP v0.7.0
```

[TOC]

## Introduction

BUSCOMP is designed to overcome some of the non-deterministic limitations of BUSCO to:

1. compile a non-redundant maximal set of non-redundant complete BUSCOs from a set of assemblies, and
2. use this set to provide a "true" comparison of completeness between different assemblies of the same genome
with predictable behaviour.

For each BUSCO gene, BUSCOMP will extract the best "Single Complete" sequence from those available, using the
`full_table_*.tsv` results table and `single_copy_busco_sequences/` directory of hit sequences. BUSCOMP ranks all
the hits across all assemblies by Score and keeps the top-ranking hits. Ties are then resolved by Length, keeping
the longest sequence. Ties for Score and Length will keep an arbitrary entry as the winner. Single complete hits
are given preference over Duplicate hits, even if they have a lower score, because only Single hit have their
sequences saved by BUSCO in the `single_copy_busco_sequences/` directory. This set of predicted gene sequences
forms the "BUSCOMPSeq" gene set.

BUSCOMP uses minimap2 to map BUSCOSeq predicted CDS sequences onto genome/transcriptome assemblies, including
those not included in the original BUSCO compilation. This way, the compiled set of species-specific BUSCO
sequences can also be used to generate a quick-and-dirty assessment of completeness for a new genome assembly.
Hits are converted into percentage coverage stats, which are then used to reclassify the BUSCO gene on the basis
of coverage and identity. BUSCOMP ratings are designed to mimic the original BUSCO ratings but have different
definitions. In addition, two extra classes of low quality hit have been added: "Partial" and "Ghost".

* **Complete**: 95%+ Coverage in a single contig/scaffold. (Note: accuracy/identity is not considered.)
* **Duplicated**: 95%+ Coverage in 2+ contigs/scaffolds.
* **Fragmented**: 95%+ combined coverage but not in any single contig/scaffold.
* **Partial**: 40-95% combined coverage.
* **Ghost**: Hits meeting local cutoff but <40% combined coverage.
* **Missing**: No hits meeting local cutoff.

In addition to individual assembly stats, BUSCO and BUSCOMP ratings are compiled across user-defined groups of
assemblies with various outputs to give insight into how different assemblies complement each other. Ratings are
also combined with traditional genome assembly statistics (NG50 and LG50) based on a given `genomesize=X` to help
identify the "best" assemblies. Details of settings, key results, tables and plots are output to an HTML report
using Rmarkdown.

**NOTE:** For HTML output, R must be installed and a pandoc environment variable must be set, e.g.

    export RSTUDIO_PANDOC=/Applications/RStudio.app/Contents/MacOS/pandoc

**NOTE:** BUSCOMPSeq sequences can be provided with `buscofas=FILE` in place of compilation. This option has not been
tested and might give some unexpected behaviours, as some of the quoted figures will still be based on the
calculated BUSCOMPSeq data. Please report any unexpected behaviour.

---

# Running BUSCOMP

BUSCOMP is written in Python 2.x and can be run directly from the commandline:

    python $CODEPATH/buscomp.py [OPTIONS]

If running as part of [SLiMSuite](http://slimsuite.blogspot.com/), `$CODEPATH` will be the SLiMSuite `tools/`
directory. If running from the standalone [BUSCOMP git repo](https://github.com/slimsuite/buscomp), `$CODEPATH`
will be the path the to `code/` directory. Please see details in the [BUSCOMP git repo](https://github.com/slimsuite/buscomp)
for running on example data.

For BUSCOMPSeq analysis, [minimap2](https://github.com/lh3/minimap2) must be installed and either added to the
environment `$PATH` or given to BUSCOMP with the `minimap2=PROG` setting.

## Commandline options

A list of commandline options can be generated at run-time using the `-h` or `help` flags. Please see the general
[SLiMSuite documentation](http://slimsuite.blogspot.com/2013/08/command-line-options.html) for details of how to
use commandline options, including setting default values with **INI files**.

```
### ~ Input/Output options ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
runs=DIRLIST    : List of BUSCO run directories (wildcards allowed) [run_*]
fastadir=DIRLIST: List of directories containing genome fasta files (wildcards allowed) [./]
fastaext=LIST   : List of accepted fasta file extensions that will be checked for in fastadir [fasta,fas,fsa,fna,fa]
genomes=FILE    : File of Prefix and Genome fields for generate user-friendly output [*.genomes.tdt if found]
restrict=T/F    : Restrict analysis to genomes with a loaded alias [False]
runsort=X       : Output sorting order for genomes and groups (or "Genome","Prefix","Complete","Group") [Group]
stripnum=T/F    : Whether to strip numbers ("XX_*") at start of Genome alias in output [True]
groups=FILE     : File of Genome and Group fields to define Groups for compilation [*.groups.tdt]
buscofas=FASFILE: Fasta file of BUSCO DNA sequences. Will combine and make (NR) if not given [None]
buscomp=T/F     : Whether to run BUSCO compilation across full results tables [True]
dupbest=T/F     : Whether to rate "Duplicated" above "Complete" when compiling "best" BUSCOs across Groups [False]
buscompseq=T/F  : Whether to run full BUSCO comparison using buscofas and minimap2 [True]
ratefas=FILELIST: Additional fasta files of assemblies to rate with BUSCOMPSeq (No BUSCO run) (wildcards allowed) []
rmdreport=T/F   : Generate Rmarkdown report and knit into HTML [True]
fullreport=T/F  : Generate full Rmarkdown report including detailed tables of all ratings [True]
missing=T/F     : Generate summary tables for sets of Missing genes for each assembly/group [True]
dochtml=T/F     : Generate HTML BUSCOMP documentation (*.info.html) instead of main run [False]
summarise=T/F   : Include summaries of genomes in main `*.genomes.tdt` output [True]
### ~ Mapping/Classification options ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
minimap2=PROG   : Full path to run minimap2 [minimap2]
endextend=X     : Extend minimap2 hits to end of sequence if query region with X bp of end [10]
minlocid=INT    : Minimum percentage identity for aligned chunk to be kept (local %identity) [0]
minloclen=INT   : Minimum length for aligned chunk to be kept (local hit length in bp) [1]
uniquehit=T/F   : Option to use *.hitunique.tdt table of unique coverage for GABLAM coverage stats [True]
mmsecnum=INT    : Max. number of secondary alignments to keep (minimap2 -N) [3]
mmpcut=NUM      : Minimap2 Minimal secondary-to-primary score ratio to output secondary mappings (minimap2 -p) [0]
mapopt=CDICT    : Dictionary of additional minimap2 options to apply (caution: over-rides conflicting settings) []
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
```

---

## Input Data: BUSCO runs and Assembly fasta files

STEP 1 is to set up the input data. BUSCOMP will first identify and check the run directories (given with the
`runs=DIRLIST` command). This command can either be a list of directories, or an expandable list with wildcard.
A list of individual directories can be provided as a file if desired.

**NOTE:** `runs=DIRLIST` wants the actual BUSCO run directories (`run_$PREFIX[.busco]/`), not the parent
directory. These directories can optionally have a `.busco` suffix, which will be trimmed off. By default,
BUSCOMP will look for `./run*`.

From these, the run list will be extracted, consisting of a number of genome `$PREFIX` values. It is expected
that the `$PREFIX` for each run will match the input genome file, found in a directory set by `fastadir=DIRLIST`.
This file can also match the `Genome` alias for that genome (see below). If you have not used consistent naming
across files, please check data has been loaded and mapped correctly during the Review phase (below).

The presence of a `full_$PREFIX[.busco].tsv` table and `single_copy_busco_sequences/` directory within each run
directory will also be checked. If `buscocompseq=F` then all of the `full_*.tsv` tables in the `runs`
directories will be loaded for compilation, but no sequence searching will be performed. The presence of
sequences available for compilation will be stored in the `Sequences` field of `*.genomes.tdt`.

### BUSCOMPSeq Analysis Only

Additional assemblies can rated using the BUSCOMPSeq analysis (see below) without having BUSCO data analysed.
These are given with the `ratefas=LIST` command (wildcards allowed), and will be added to the main Genomes table
after BUSCO compilation has been performed. The default prefix for these files will be their basename (filename,
minus path and extension). This can be linked to an alias and/or have a prefix number stripped, as with the
run directories. When combined with `buscofas=FASFILE`, this enables the BUSCOMPSeq analysis to be performed in
the absence of _any_ BUSCO results.

### Genome Prefixes

Each genome analysed has a "Prefix" that can be used to help sorting (if `runsort=prefix`) and identify relevant
BUSCO files where the genome (Fasta) name and BUSCO run name do not match. This Prefix is set once as the data
is loaded and is never changed. (Sorting and visualisations can be made more informative altered using the Genome
(a.k.a. Alias) and Description fields.)

The assembly Prefix will be set as:

1. If a `full_table_*.tsv` file is found, the core (indicated with `*`) will be used as the prefix.
2. If no BUSCO results are available, the path- and extension-stripped fasta file name will be used for the prefix

### Genome Aliases

Genome Aliases will be parsed initially from the loaded data:

1. If a BUSCO run directory is given and it contains a single BUSCO run, the run directory name will be used for
the `Genome` alias, minus the leading "`run_`".
2. If the run directory contains multiple BUSCO runs, the `full_table_*.tsv` core used for the `Prefix` will also
be used for the `Genome` alias.
3. If no BUSCO results are available, the path- and extension-stripped fasta file name will be used for the
`Genome` alias.

If `Genome` contains a trailing `.busco`, this will be stripped. If `Genome` starts with preceding numbers
(`XX_`), these will be kept for sorting but stripped for outputs and fasta matching (unless `stripnum=F`).

**NOTE:** If the assembly fasta file does not match the name used for the BUSCO run file, then the `Genome` alias
*must* be set to the `basefile` of the fasta file by appropriate naming of the `run_` directory, _i.e._ the
`run_*` directory should contain a single BUSCO run and the directory name should match a `*.fasta` file (or
other accepted `fastaext=LIST` extension) in one of the directories given by `fastadir=DIRLIST`.

An optional alias table can be provided (`genomes=FILE`) that contains `Prefix` and `Genome` fields (others
allowed) and can give alternative names for each genome to be used in other outputs. If running interactively,
there will also be an option to check/update these aliases manually. Genome aliases are output as part of the
main `*.genomes.tdt` output, which can also be used as subsequent `genomes=FILE` input (the default, if found).
This table can also have a `Description` field, which will be used to update descriptions for output if found.
(Empty descriptions will not be mapped.)

**NOTE:** The optional Alias table *can* be used to change a `Genome` name to something other than its Fasta file
- this mapping is performed _after_ fasta files have been identified.

**NOTE:** `Prefix` and `Genome` fields must be unique. A common `Prefix` and `Genome` value is permitted but
these will be assumed to refer to the _same_ assembly. (In other words, do not run BUSCO on two assemblies
and give each BUSCO run the name of the other assembly!)

**NOTE:** Some `Genome` names may cause conflicts with running minimap2 and/or the Rmarkdown output.
**Whitespace is not permitted** in `Genome` names (though can be in R labels) and will be stripped. It is
recommended to keep `Genome` names simple and only containing standard characters (letters, numbers, dots and
underscores).

---

## Grouping and BUSCO compilation

BUSCOMP compilation will take a set of genomes and identify the best rating for each BUSCO across the set. By
default, this is done for all input genomes and assigned to a "BUSCOMP" rating. Ratings are compiled according
to the `ratings=LIST` hierarchy, which by default is: `Complete`, `Duplicated`, `Fragmented`, `Missing`. The
"best" rating (first in the hierarchy) will be used for that group, even if it is found in only a single
assembly in the group. If `dupbest=T`, the hierarchy is `Duplicated`, `Complete`, `Fragmented`, `Missing`.

### Loading Groups

Additional subsets of genomes can also be grouped together for compilation, using the `groups=FILE` input. This
must have `Genome` and `Group` fields. Once generated, a Group becomes a "Genome". Groups can therefore include
other Groups in them, provided there is no circular membership. Genome mapping should also recognise Prefix
values. The "BUSCOMP" group with *all* genomes will be added unless a conflicting "BUSCOMP" group is provided,
or `buscomp=F`.

**NOTE:** Genome groups are generated mapping onto the `Genome` (or `Prefix`) values _after_ any alias mapping
but _before_ any manual editing of `Genome` aliases.

### Manual group review/editing

When running interactively (`i>=0`), Group review and editing can be accessed from the main Genome menu. This
will show the genomes currently in each group, and provides the following menu options:

* `<A>dd` = Create a new Group. First, a group name will need to be chosen, then the `<E>dit` menu will be
triggered.
* `<D>elete` = Remove the Group. Note that this will not remove Group members from any "parent" groups that
contained the deleted group when they were loaded.
* `<R>ename` = Change the Group name.
* `<E>dit` = Edit group membership. This will give options to add/remove each assembly in the analysis.
* `E<x>it menu` = Return to main Genome Menu.
* `<Q>uit` = Quit BUSCOMP.

### Saving and sorting

Once group edits are complete, group data will be saved to the `*.groups.tdt` file. If `runsort=group` then
genome sorting will also be performed following group edits.


## BUSCOMP Genome/Group menu

Following initial setup of genomes and groups, a Genome/Group edit menu enables updating loaded information.
(This menu will not be available if running in non-interactive mode, e.g. `i=-1`.) The primary use for this is
to convert unwieldy genome and/or BUSCO run names into something more user-friendly for display. It can also be
used for adding descriptions to assemblies, adding or modifying group membership, and sorting genomes using
different criteria. Assemblies can also be dropped from analysis from this menu.

The main menu offers five options:

- `R` = Review genomes
- `G` = Review/edit genome groups
- `S` = Sort genomes
- `Q` = Quit BUSCOMP
- `X` = Exit Menu and Proceed [default]

### Genome review menu

If running in interactive mode, users will have the option to review and manually update loaded data. Each
loaded genome will be displayed in turn, in its current sorted order. (Sorting can be altered or updated via
the `Sort genomes` option of the main genome/group menu.) Options will be presented to modify data, or quit
the menu (or BUSCOMP program). Modifications permitted are:

- `<A>lias` = Sets the `Genome` field for the entry. This can have a "silent" numeric prefix for sorting if
`runsort=Genome` or `runsort=Group`. Most importantly, this will be the default label in tables and plots, and
used for fields in compiled data.
- `<D>escription` = This gives the option to set a manual description of the assembly, which is used in the
final output.
- `<R>emove` = Drop this assembly from the analysis. BUSCOMP will ask for confirmation. This cannot be undone.

If genomes are edited and `runsort=Genome` or `runsort=Group`, they will be re-sorted upon exiting the menu.


### Output order

An optional `runsort=LIST` parameter will determine the output order. Future releases of BUSCOMP will proceess
a mixed list of Prefix, Genome and Group names. Any data missing from the list will be appended at the end in
Genome order. (NOTE: Group names are a special kind of Genome in this context.) This sorting is preformed after
all manual reviews and updates are complete. Currently, providing a list of genomes (or `runsort=Manual`) will
trigger manual ordering via the sort menu.

There are also four special sort modes that can be implemented:

- Genome = sort alphabetically based on Genome alias and Group name. (NOTE: "silent" numerical prefixes will
affect this sorting (see below).
- Group = sort alphabetically using `Genome` sorting within each group with the Group summary immediately
following the last Group member. [Default]
- Prefix = sort alphabetically based on Prefix. (NOTE: "silent" numerical prefixes will
affect this sorting (see below).
- Complete = sort in order of most complete to least complete.
- Missing = sort in order of fewest missing to most missing BUSCOs

The `runsort=prefix` option is best combined with the addition of a number to the run directory name:

* `run_01_OneGenome/` containing `full_OneGenome.tsv` and generated from `OneGenome.fasta`
* `run_02_AnotherGenome.busco/` containing `full_AnotherGenome.busco.tsv` and generated from `AnotherGenome.fasta`

This example would sort OneGenome before AnotherGenome if runsort=prefix, but AnotherGenome before OneGenome if
`runsort=Genome`.

---

## Genome Summary Statistics

The final setup step is to load any genomes for which Fasta files have been provided. Unless `summarise=F`,
summary statistics will be calculated for each genome, enabling assessements of genome completeness and quality
in combination with the BUSCO and BUSCOMP results. Summary statistics are calculated by `rje_seqlist`. The
following statistics are calculated for each genome:

* **SeqNum**: The total number of scaffolds/contigs in the assembly.
* **TotLength**: The total combined length of scaffolds/contigs in the assembly.
* **MinLength**: The length of the shortest scaffold/contig in the assembly.
* **MaxLength**: The length of the longest scaffold/contig in the assembly.
* **MeanLength**: The mean length of scaffolds/contigs in the assembly.
* **MedLength**: The median length of scaffolds/contigs in the assembly.
* **N50Length**: At least half of the assembly is contained on scaffolds/contigs of this length or greater.
* **L50Count**: The smallest number scaffolds/contigs needed to cover half the the assembly.
* **NG50Length**: At least half of the genome is contained on scaffolds/contigs of this length or greater.
This is based on `genomesize=X`. If no genome size is given, it will be relative to the biggest assembly.
* **LG50Count**: The smallest number scaffolds/contigs needed to cover half the the genome.
This is based on `genomesize=X`. If no genome size is given, it will be relative to the biggest assembly.
* **GapLength**: The total number of undefined "gap" (`N`) nucleotides in the assembly.
* **GC**: The %GC content of the assembly.

**NOTE:** `NG50Length` and `LG50Count` statistics use `genomesize=X` or the biggest assembly loaded.
If BUSCOMP has been run more than once on the same data (_e.g._ to update descriptions or sorting),
previously calculates statistics will be read from the `genomes=FILE` table, if loaded. This may cause some
inconsistencies between reported NG50 and LG50 values and the given/calculated `genomesize=X`. If partial
results are reloaded following a change in `genomesize=X`, this will give rise to inconsistencies between
assemblies. When re-running, please make sure that a consistent genome size is used.
If in doubt, run with `force=T` and force regeneration of statistics.

---

## BUSCO Compilation

Once all the genomes are loaded, BUSCOMP compiles the BUSCO results. This is done for three purposes:

1. Report comparative BUSCO statistics across assemblies and plot with other assembly statistics.
2. Combine BUSCO results across groups of assemblies to summarise total BUSCO coverage.
3. Identify and compile the best `Complete` BUSCO hits for BUSCOMPSeq analysis (below).

Loaded assemblies with an identified full results `Table` will be processed and added to the `*.full.tdt` table.
The best rating per BUSCO gene will then be used for summary BUSCO counts for each genome. Finally, each Group
will have its combined BUSCO rating calculated. This is performed by choosing the "best" rating for each BUSCO
across the Group's members, where "best" is determined by the `dupbest=T/F` setting:

- By default (`dupbest=F`), the rating hierarchy is: 'Complete', 'Duplicated', 'Fragmented', 'Missing'.
- If `dupbest=T`, the rating hierarchy is: 'Duplicated', 'Complete', 'Fragmented', 'Missing'.

Where ratings are defined (quoting from the [BUSCO v3 User Guide](http://gitlab.com/ezlab/busco/raw/master/BUSCO_v3_userguide.pdf) as:

* `Complete`: Single-copy hits where "BUSCO matches have scored within the expected range of scores and within the expected range of length alignments to the
BUSCO profile."
* `Duplicated`: As `Complete` but 2+ copies.
* `Fragmented`: "BUSCO matches ... within the range of scores but not within the range of length alignments to the BUSCO profile."
* `Missing`: "Either no significant matches at all, or the BUSCO matches scored below the range of scores for the BUSCO profile."

Total BUSCO counts (`N`) and summed Ratings are added to the main `*.genomes.tdt` table for each assembly and
group. A `*.busco.tdt` file is also generated that has the rating for each BUSCO gene (rows) in each
assembly/group (columns).

If output is being sorted using `runsort=Complete` or `runsort=Missing`, data will be sorted at this point.
Raw BUSCO results and compiled numbers will then be output to the log file.

The following tables will then be saved (see **Output files**, below, for details):

* `*.genomes.tdt` = summary of loaded data, genome statistics and BUSCO ratings.
* `*.full.tdt` = full BUSCO results across all assemblies.
* `*.busco.tdt` = compiled BUSCO results showing the rating per genome/group for each BUSCO gene.

### BUSCOMPSeq sequence compilation

The final step of the BUSCOMP BUSCO compilation is to extract the best Complete BUSCO sequences from those
available. For all assemblies with BUSCO results and a `single_copy_busco_sequences/`, BUSCOMP ranks all the hits
across all assemblies by `Score` and keeps the top-ranking hits. Ties are then resolved by `Length`, keeping the
longest sequence. Ties for `Score` and `Length` will keep an arbitrary entry as the winner. `Single` complete
hits are given preference over `Duplicate` hits, even if they have a lower score, because only `Single` hit
have their sequences saved by BUSCO in the `single_copy_busco_sequences/` directory.

If `buscofas=FASFILE` has been given, this will be used for BUSCOMPSeq searches. Otherwise, the best BUSCO
seqences identified for each BUSCO gene will be saved as `*.buscomp.fasta` for BUSCOMPSeq analysis. The
exception is if `buscofas=FASFILE` is pointing to the `*.buscomp.fasta` and `force=T`, or if the
`buscofas=FILE` fasta file cannot be found.

**NOTE:** The `buscofas=FASFILE` option has not been tested and might give some unexpected behaviours, as some
of the quoted figures will still be based on the calculated BUSCOMPSeq data.

## BUSCOMPSeq Minimap2 searches

Once the gene sequences for BUSCOMPSeq have been established, the next step is to search for them in the assembly
fasta files using a more deterministic (and faster) approach. For this, minimap2 has been chosen. BUSCOMP will
perform a minimap2 search on each assembly fasta file. (Use `minimap2=FILE` to tell BUSCOMP where to find
minimap2 if the path is not an environment variable.)

Minimap2 will run with `-x splice -uf -C5` and hits will be filtered by length, keeping those that meet the
`minloclen=X` cutoff (default 20 bp). A percentage identity cutoff can also be applied with `minlocid=X`
(default 0%). Hits are also reduced to unique coverage by starting with the local alignment with the largest
number of identical positions,
and then trimming any other local alignments that overlap with the same part(s) of the query (BUSCO) sequence.
This is repeated until all local alignments are non-overlapping (and still meet the identity and length
criteria). Local hits are then compiled into global alignment (GABLAM) statistics of coverage and identity.

By default, Minimap2 searches will keep the **Top 3** secondary alignments for each sequence (the minimap2 `-N`
commandline parameter). In limited tests, this appears to give a good trade-off between search speed and the
identification of `Duplicated` BUSCO genes. This default can be adjusted with `mmsecnum=INT` to make runs faster
or more sensitive, as required. This can be further modulated using `mmpcut=NUM`, which sets the Minimap2 minimal
secondary-to-primary score ratio to output secondary mappings (the minimap2 `-p` commandline parameter).

Minimap2 search results are saved in a `*.minimap/` directory, with the prefix `$BASEFILE.$CUTOFFS`, where
`$BASEFILE` is the fasta file basename for assembly, and `$CUTOFFS` takes the form `NXLXXIDXX`, where `NX` is the
max number of secondary hits (`mmpcut=NUM`), `LXX` is the
length cutoff (`minloclen=X`) and `IDXX` is the identity cutoff (`minlocid=X`) - `L20ID0` by default. Unless
`uniquehit=F` (see below), `$CUTOFFS` will have a `U` suffix, e.g. `L20ID0U`. The Minimap2 `*.paf` file will only
have the `.NX` suffix. A `*.NX.paf.cmd` file with the actual Minimap2 command used will also be saved, so the
`mmpcut=NUM` setting and any other Minimap2 options set using `mapopt=CDICT` can be checked if required.

Existing files will be loaded and reused unless `force=T`.

Minimap2 hits are first converted into BLAST-style "local" hits, which are then converted into
[GABLAM](http://rest.slimsuite.unsw.edu.au/gablam)-style summary statistics. For the `*.hitsum.tdt` table,
local hits are reduced to unique coverage of each Query, such that each part of the Query is covered by a single
hit. Local hits are selected in order of the number of identical positions between Query and Hit, followed by
Length in the case of a tie. Overlapping regions from other local hits are trimmed, and the process repeated with
the next-best local hit, ranked on trimmed stats where necessary. For the `*.gablam.tdt` output, each Query-Hit
pair is considered independently and local hits are reduced to (a) unique coverage of the Query for `Qry_*`
output, and (b) unique coverage of the Hit for `Hit_*` output. (Note that for each Query-Hit pair, only the local
hits between that pair are considered for "unique" local hit reduction - there may be overlapping alignments to
different queries/hits.) Unless `uniquehit=F`, hits will first be reduced to be non-overlapping across _all_
queries before being coverted to Query-Hit pair GABLAM coverage stats.

**NOTE:** Re-using results does NOT robustly check whether the BUSCOMPSeq data has changed, so this directory
should be deleted if re-running with different sequences. BUSCOMP will save the name of the BUSCO file along
with the md5sum of its contents to `*.NX.input.md5`, which will be checked if present and re-using data. Some basic
checks should also be performed during the following results compilation stage, but please note that BUSCO IDs
are used for sequence identifiers and so changes in BUSCO hit sequences will not be identified if files have
been inappropriatley copied/moved between runs etc. - please look out for unexpected behaviour outside a "clean"
run.

**NOTE:** Minimap2 only works with high sequence identity. BUSCOMP is designed to be used on multiple assemblies
_from the same species_. If using cross-species BUSCO analysis, odd results might be obtained, biased by the
evolutionary distance from the species with the most BUSCOMP sequences. Under these circumstances, it might be
better to swap out minimap2 for BLAST+. This can be achieved by independently running GABLAM using the
BUSCOMPSeq fasta file as queries and each assembly as the search database, then replacing the `*.gablam.tdt` and
`*.hitsum.tdt` files before re-running BUSCOMP. Please contact the author if you want help with this.

### BUSCOMPSeq Minimap2 search compilation.

Minimap2 searches of the compiled BUSCOMP sequences are then compiled in similar vein to the original BUSCO
results. The primary difference is that the search results need to first be converted into BUSCO-style ratings.
This rating is explicitly more "quick and dirty" than the original BUSCO ratings, and should be considered
complementary rather than superior. It aims to provide a quick, consistent assessment, but does have fewer checks
and balances as a result.

BUSCOMP uses results from both the `*.hitsum.tdt` table (overall coverage in assembly) and the `*.gablam.tdt`
table (coverage in a single contig/scaffold) to rate sequences as:

* **Complete**: 95%+ Coverage in a single contig/scaffold. (Note: unlike BUSCO, accuracy/identity is not considered.
This will make it more prone to misidentification of closely related paralogues.)
* **Duplicated**: 95%+ Coverage in 2+ contigs/scaffolds.
* **Fragmented**: 95%+ combined coverage but not in any single contig/scaffold. (Note: as with BUSCOMP `Complete`
ratings, these might include part of closely related paralogues.)
* **Partial**: 40-95% combined coverage. (Note: these might be marked as "Fragmented" by BUSCO, which does not
discriminate between "split" full-length hits, and single partial hits.)
* **Ghost**: Hits meeting local cutoff but <40% combined coverage.
* **Missing**: No hits meeting local cutoff.

When compiling the results for all BUSCO genes, Single/Duplicated Complete hits will also be rated as
**Identical** if they have 100% coverage and 100% identity in at least one contig/scaffold.

Once all the individual assemblies have been rated for the full set of assemblies, results are compiled across
Groups as described for the original BUSCO results (above). Because no genes receive an individual "Identical"
rating, Groups will _not_ have a summary count for Identical hits.

Individual gene ratings for each genome and group are output to `*.LnnIDxx.buscomp.tdt`, where `LnnIDxx` records
the `minloclen=nn` and `minlocid=xx` settings. Compiled ratings are output to `*.LnnIDxx.ratings.tdt`.

### BUSCOMP Summary

The final step of the BUSCOMP compilation is to summarise the findings in the log afile, akin to the BUSCO
summary file. This will first generate a one line summary of the percentages, along with the original number of
complete BUSCOs and the number of BUSCOMP sequences contributed by that assembly (i.e. the number with the best
score of all the BUSCO searches.) This is followed by a more detailed breakdown of each category. For example:

```
#BUSCO	00:00:41	Results: C:89.2%[S:87.8%,D:1.4%,I:23.3%],F:5.8%,P:3.8%,G:1.6%,M:0.9%,n:3736 - canetoad_v2.2 (3194 Complete BUSCOs; 102 BUSCOMP Seqs)
#INFO	00:00:41	870 Identical BUSCOs (I)  [100% complete and identical]
#INFO	00:00:41	3333 Complete BUSCOs (C)  [95%+ coverage in a single contig/scaffold]
#INFO	00:00:41	3281 Complete and single-copy BUSCOs (S)  [1 Complete hit]
#INFO	00:00:41	52 Complete and duplicated BUSCOs (D)  [2+ Complete hits]
#INFO	00:00:41	217 Fragmented BUSCOs (F)  [95%+ coverage spread over 2+ contigs/scaffolds]
#INFO	00:00:41	143 Partial BUSCOs (P)  [40-95% coverage]
#INFO	00:00:41	61 Ghost BUSCOs (G)  [<40% coverage]
#INFO	00:00:41	34 Missing BUSCOs (M)  [No hits]
#INFO	00:00:41	3736 Total BUSCO gene hits searched
```

## BUSCO versus BUSCOMP comparisons

There is a risk that performing a low stringency search will identify homologues or pseudogenes of the desired BUSCO gene in error.
If there is a second copy of a gene in the genome that is detectable by the search then we would expect the same
genes that go from `Missing` to `Complete` in some genomes to go from `Single` to `Duplicated` in others.

To test this, data is reduced for each pair of genomes to BUSCO-BUSCOMP rating pairs of:

* `Single`-`Single`
* `Single`-`Duplicated`
* `Missing`-`Missing`
* `Missing`-`Single`

This is then converted in to `G`ain ratings (`Single`-`Duplicated` & `Missing`-`Single`) or `N`o Gain ratings
(`Single`-`Single` & `Missing`-`Missing`). The `Single`-`Duplicated` shift in one genome is then used to set the expected `Missing`-`Single`
shift in the other, and assess the probability of observing the `Missing`-`Single` shift using a cumulative binomial
distribution, where:

* `k` is the number of observed `GG` pairs (`Single`-`Duplicated` _and_ `Missing`-`Single`)
* `n` is the number of `Missing`-`Single` `G`ains in the focal genome (`NG`+`GG`)
* `p` is the proportion of `Single`-`Duplicated` `G`ains in the background genome (`GN`+`GG` / (`GN`+`GG`+`NN`+`NG`))
* `pB` is the probability of observing `k+` `Missing`-`Single` gains, given `p` and `n`

This is output to `*.gain.tdt`, where each row is a Genome and each field gives the probability of the row
genome's `Missing`-`Single` gains, given the column genome's `Single`-`Duplicated` gains.

---

# Output files

Contents of the main output files are given below. In addition to the tab-delimited text output, a summary HTML
(and source RMarkdown) file will be generated, assuming R is installed. If `buscompseq=T` then a fasta file of
the "best" (top-scoring) Single Complete BUSCO genes will also be generate (`*.buscomp.fasta`), unless it is
provided using `buscofas=FASFILE`.

## BUSCOMPSeq Fasta files

Unless `buscompseq=F` or `buscofas=FASFILE` is provided, nucleotide and protein sequences for the "best" BUSCO
gene hits will be output to `*.buscomp.fasta` (nucleotide) and `*.buscomp.faa` (protein). The `*.buscomp.faa`
protein file is not used by BUSCOMP but is provided as a useful set of (near-)complete protein sequences. Each
fasta file is made from concatenating individual fasta files from the `single_copy_busco_sequences/` directories.
As such, they will be named as with the standard BUSCO output:

```
>$BUSCOID $FASTAFILE:$CONTIG:$START-$END
```

**NOTE:** The `$FASTAFILE` path given in this file will be the one from the original BUSCO run, not the path to
the genome file used by BUSCOMP if it has subsequently been moved/renamed.


## Data Tables

### genomes.tdt

The `*.genomes.tdt` table is the main summary table for the input genomes, their BUSCO rating summaries and genome statistics.

- `#` = Sorting order for output
- `Directory` = Directory for this BUSCO run
- `Prefix` = Prefix identified from BUSCO directory (or full table), corresponding to BUSCO output files
- `Genome` = Optional alternative name (or "alias") to be used in outputs
- `Fasta` = path to genome file, if found
- Genome statistics = genome summary statistics if genome found and `summarise=T`. (See above.)
- `Sequences` (True/False) = Whether `single_copy_busco_sequences/` directory found
- `Table` = Path to `full_*.tsv` table
- BUSCO Ratings summary will be added (assuming `Table` is `True`) (See above.)

### groups.tdt

The `*.groups.tdt` table has the mappings between `Genome` and `Group` identifiers to make the groups for combined ratings (see
above).

- `#` = Arbitrary unique key for table
- `Genome` = Genome alias or Prefix
- `Group` = Name for grouped rating

### full.tdt

The `*.full.tdt` table is a compiled version of the all the individual BUSCO full results tables.

- `Genome` = Genome alias
- `#` = Arbitrary unique key element for table (adjusting for duplicates)
\       - `BuscoID` = BUSCO gene identifier
- `Status` = BUSCO rating
- `Contig` = Contig containing BUSCO hit
- `Start` = Start position
- `End` = End position
- `Score` = BUSCO score
- `Length` = Length of BUSCO hit

### busco.tdt

The `*.busco.tdt` table has the compiled ratings for individual BUSCO genes in each genome/group

- `BuscoID` = BUSCO EOG gene identifier
- Genomes and Groups fields have the rating of that gene in that Genome or Group

### buscoseq.tdt

The `*.buscoseq.tdt` table has the set of best BUSCO genes used for the compiled BUSCOMPSeq sequence set. In
addition to the BUSCO stats for all the BUSCOMP sequences, BUSCOMP ratings for each Genome are output in this
file.

- `Genome` = Genome alias
- `BuscoID` = BUSCO gene identifier
- `Status` = BUSCO rating
- `Contig` = Contig containing BUSCO hit
- `Start` = Start position
- `End` = End position
- `Score` = BUSCO score
- `Length` = Length of BUSCO hit
- Genomes fields have the BUSCOMP rating of that gene in that Genome

### buscomp.tdt

The `*.LnnIDxx.buscomp.tdt` table is the same as the `*.busco.tdt` but with revised ratings based on BUSCOMP analysis.

- `BuscoID` = BUSCO EOG gene identifier
- Genomes and Groups fields have the rating of that gene in that Genome or Group

### ratings.tdt

The `*.LnnIDxx.ratings.tdt` table has the compiled BUCOMP summary ratings per genome/group.

- `Genome` = Genome alias or group name
- `N` = Number of BUSCOMP genes
- `Identical` = 100% coverage and 100% identity in at least one contig/scaffold. These will also be rated as
`Complete` or `Duplicated`. Groups do not have `Identical` ratings.
- `Complete` = 95%+ Coverage in a single contig/scaffold. (Note: accuracy/identity is not considered.)
- `Duplicated` = 95%+ Coverage in 2+ contigs/scaffolds.
- `Fragmented` = 95%+ combined coverage but not in any single contig/scaffold.
- `Partial` = 40-95% combined coverage.
- `Ghost` = Hits meeting local cutoff but <40% combined coverage.
- `Missing` = No hits meeting local cutoff.

### changes.tdt

The `*.LnnIDxx.changes.tdt` table has counts of change ratings (BUSCO to BUSCOMP) for each genome, in addition
to a Total count across all genomes.

- `BUSCO` = BUSCO rating.
- `BUSCOMP` = BUSCOMP rating.
- Genome fields have the count of the number of genes with this combination of ratings.
- `Total` = Summed count over all genomes.

### changes.full.tdt

The `*.LnnIDxx.changes.full.tdt` table is the complete set of ratings changes (BUSCO to BUSCOMP) for each gene
and genome.

- `BuscoID` = BUSCO EOG gene identifier
- Genome fields have the ratings change for that gene, using the first letters of the ratings.

<small>**C**omplete, **D**uplicated, **F**ragmented, **P**artial, **G**host, **M**issing</small>

### unique.tdt

The `*.LnnIDxx.unique.tdt` table has `Genome` and `Group` identifiers for each `BuscoID` where that gene is only
`Complete` (or `Duplicated`) in that genome/group.

- `BuscoID` = BUSCO EOG gene identifier
- `BUSCO` = Genome/Group that uniquely has a BUSCO `Complete` rating.
- `BUSCOMP` = Genome/Group that uniquely has a BUSCOMP `Complete` rating.

### rdata.tdt

The `*.LnnIDxx.rdata.tdt` table has the BUSCOMP summary ratings (converted into percentage values) and sequence
statistics for each `Genome`/`Group`, in addition to:

- `BUSCO` = BUSCO `Complete` (`Single` and `Duplicated`) percentage
- `NoBUSCO` = BUSCO `Missing` percentage
- `UniqBUSCO` = Number of unique BUSCO `Complete` genes
- `UniqBUSCOMP` = Number of unique BUSCOMP `Complete` genes
- `col` = colour field for R plotting.
- `pch` = point type for R plotting.
- `label` = Genome/Group label for R plotting.
- `plot` = TRUE/FALSE, whether to plot the Genome/Group statistics.
- `best` = any categories for which this Genome is rated "best".


## Minimap2 output

Minimap2 will be run for each genome with a `Fasta` file, generating:

- `*.paf`
- `*.paf.cmd`
- `*.input.md5`
- `*.L20ID80.local.tdt`
- `*.L20ID80.hitunique.tdt`
- `*.L20ID80.qryunique.tdt`
- `*.L20ID80.hitsum.tdt`
- `*.L20ID80.gablam.tdt`

_Output details will be added here._

---

# BUSCOMP Report (RMarkdown HTML output)

The final step in BUSCOMP analysis is to generate a summary report. This is produced as an RMarkdown document
(`*.Rmd`) and (assuming the path to pandoc is set) is then "knitted" to make an HTML file (`*.html`). The
RMarkdown file is retained to make it easy for the user to modify the content and convert the output into a
report of their own. HTML output can be switched off with `rmdreport=F`. Unless `fullreport=F`, a larger report
with full BUSCO results tables and comparative plots of Missing BUSCO genes will be generated (`*.full.html').

## Compilation of ratings and genomes tables for summary plots and tables.

Prior to generation of the document, results are first compiled into an overview stats file with additional plot
attributes, before the "best" assemblies are identified under various criteria. Finally, there is an option to
modify some of the plotting attributes before the report is generated.

The main BUSCOMP `*.ratings.tdt` output is combined with key genome statistics and BUSCO ratings from the
`*.genomes.tdt` table. BUSCOMP ratings are converted into percentage values. BUSCO ratings are converted into
percentage values and reduced to `BUSCO` (Single and Duplicated Complete BUSCOs) and `NoBUSCO` (Missing BUSCOs).
(Full BUSCO results are plotted directly from the `*.genomes.tdt`.)

After results are compiled, additional plotting fields are generated:

* `col` = Plotting colour. (Default, "red". Genomes with 1+ "best" ratings, "blue")
* `pch` = Point type. (Default, 21 [circle]. Genomes with "best" rating will be 22 [square] for best BUSCO(MP)
ratings, 24 [triangle] for best contiguity ratings, or 23 [diamond] for best in both categories.
* `label` = Additional text field to be used for labels. In interactive mode, the option will be given to leave
this blank for unlabelled plots.
* `plot` = Whether or not to include a genome in the plot. (Default, TRUE)

In interactive mode, the option will be provided to edit plotting attributes for each assembly, following the
calculation of "best" assemblies (below). Compiled data are then saved to `*.LnnIDxx.rdata.tdt` for summary plots
and tables in the RMarkdown output.

## Identifying the "best" assemblies

There are many ways of assessing genome assembly quality, but they can be broadly broken down into four aspects:

1. **Coverage.** How much of the genome is included in the assembly.

2. **Contiguity.** How many fragments is the genome in, and how big are they.

3. **Accuracy.** How accurate is the assembly in terms of sequence errors.

4. **Redundancy.** How much of the genome has been included multiple times.

Standard reference-free genome statistics (e.g. number, length and gappiness of scaffolds), can only give limited
insights. Whilst assemblies smaller than the genome size are clearly missing bits, assembly size could be
artificially inflated by redundant regions, making it impossible to assess Coverage. Scaffold sizes can give an
indicator of Contiguity, but are also prone to biases introduced by filtering of small scaffolds, for example.
If an estimated Genome Size can be provided, the most useful measures in this respect are `NG50` and `LG50`.
These statistics sort scaffolds by length (big to small) and identify the contig/scaffold size at which half the
*genome* (not the *assembly*) is covered by contigs/scaffolds of that size or bigger. This is the `NG50` value
(called `NG50Length` in BUSCOMP), with `LG50` (`LG50Count`) being the number of contigs/scaffolds needed to
cover half the genome. (`N50` and `L50` are the same statistics only for the assembly.) These statistics can
still be mislead by redundancy in the assembly. None of theses statistics speak to sequence accuracy.

The power of BUSCO is that it speaks to all four aspects of quality. `Complete` and `Fragmented` genes give
an indication of Coverage, Continuity and Accuracy; `Duplicated` genes give an indication of Redundancy;
`Missing` genes give an indication of Coverage and Accuracy. However, the weakness is that these different
aspects cannot easily be disentangled. This makes side-by-side comparisons of different assemblies challenging,
as it is not always clear what a difference is indicating.

BUSCOMP is designed on the principle that **Coverage** and **Contiguity** are the two most important aspects of
assembly quality. *Accuracy* can, in principle, be improved by additional error-correction steps (including
manual curation). Suspected *Redundancy* can likewise be identified a flagged. *Coverage* and *Contiguity*, in
contrast, can only be improved by further assembly - either trying again from scratch, or employing a
scaffolding or gap-filling alogrithm.

BUSCOMP has therefore identified seven statistics that can be used to rank assemblies on inferred Completeness
or Contiguity:

* **Completeness**:
    1. `Complete` = Maximum number of Complete BUSCOMP ratings.
    2. `BUSCO` = Maximum number of Complete BUSCO ratings.
    3. `Missing` = Smallest number of Missing BUSCOMP ratings.
    4. `NoBUSCO` = Smallest number of Missing BUSCO ratings.
* **Contiguity**:
    1. `MaxLength` = Maximum length of contigs/scaffolds.
    2. `NG50Length` = Half the genome lies on contigs/scaffolds at least this size. (See above.)
    3. `LG50Count` = Half the genome can be covered by this many contigs/scaffolds. (See above.)

Individual assemblies are rated as "best" under all seven criteria, with ties allowed. Each assembly can
be best under multiple criteria and each criterion can have several best assemblies. BUSCOMP will report all
such combinations.

---

## BUSCOMP Report sections

The BUSCOMP HTML reports (full and summary) consist of the following sections:

### 1. Run summary

Details of the BUSCOMP run, including the version, directory and commands.

- 1.1 BUSCOMP summary: A brief overview of the "best" assembly ratings.

### 2. Genome summary

This section contains summary details of the genome assemblies analysed, including the loaded data, the summary
statistics for the assemblies, and coverage/contiguity assessment plots:

- 2.1 Genome statistics
- 2.2 Genome coverage assessment plots
- 2.3 Genome contiguity assessment plots

### 3. BUSCO Ratings

The compilation of BUSCO ratings, including details of the BUSCOMP Groups is given in this section. In addition
to the summary ratings for each genome/group, the full report will have a table of all the individual gene
ratings:

- 3.1 Genome Groups
- 3.2 BUSCO Summary
- 3.3 BUSCO Gene Details

### 4. BUSCOMP Ratings

Next, BUSCOMP ratings using the compiled BUSCOSeq dataset are reported. In addition
to the summary ratings for each genome/group, the full report will have a table of all the individual gene
ratings:

- 4.1 BUSCOMP re-rating of genomes
- 4.2 BUSCOMP re-rating full results

### 5. BUSCO and BUSCOMP Comparisons

The final report section features direct comparisons of the BUSCO and BUSCOMP ratings, reporting
changes in ratings between BUSCO and BUSCOMP. _Unique_ Complete genes are also identified: those rated as
`Complete` in only a single genome, or multiple genomes in a single Group.
The full report also has a series of summary ratings plots for subsets of BUSCO genes that are rated as
`Missing` in a genome or group.

- 5.1 BUSCO to BUSCOMP ratings changes
- 5.2 Unique BUSCO and BUSCOMP Complete genes
- 5.3 Ratings for Missing BUSCO genes

### 6. Appendix: BUSCOMP run details

Details of the BUSCOMP run in terms of when, where and how (e.g. commandline options) are found in the Appendix.
Any errors or warnings generated during the BUSCO run are reported here. Check the `*.log` file generated for
details.

- 6.1 BUSCOMP errors
- 6.2 BUSCOMP warnings



<br>
<small>&copy; 2019 Richard Edwards | richard.edwards@unsw.edu.au</small>
