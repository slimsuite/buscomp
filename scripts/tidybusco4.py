#!/usr/bin/env python3

### BUSCO DIRECTORY TIDYING ###
import string, os, sys, glob, shutil

### Setup script
version = '0.0.1'

helptext = '''tidybusco4.py v{}
Author: Richard J. Edwards

Usage: tidybusco.py RUNPATH PREFIX [--targz] [--pigz] [--delete] [DESCRIPTION]

This script tidies up a BUSCO v4 run directory ready for processing with BUSCOMP. The files within $RUNPATH will be renamed with $PREFIX. Other options are:

--targz = tarball the whole directory prior to cleanup
--pigz = use pigz for zipping the tarball
--delete = delete all the *output directories

Any remaining non-option words will be used for the description and saved as description_$PREFIX.txt. 

Example usage:
./tidybusco.py run_SGDR64.2.1 SGDREF --targz --pigz --delete SGD Yeast Reference Genome v64.2.1

'''.format(version)

#i# Help text
for htext in ['help','-h','-help','--help']:
    if htext in sys.argv: print(helptext); sys.exit(0)
#i# Print version number
for vtext in ['version','-v','-version','--version']:
    if vtext in sys.argv: print(version); sys.exit(0)

## Process commandline args
argcmd = sys.argv[1:]
arglist = ['targz','pigz','delete','debug']
cmd = {}
for argstr in arglist:
    cmd[argstr] = False
    if '--{}'.format(argstr) in argcmd:
        argcmd.remove('--{}'.format(argstr)); cmd[argstr] = True
if not argcmd:
    print('BUSCO run path must be given as first argument')
    sys.exit(2)
    
## Identify runpath
runpath = argcmd.pop(0)
description = ''
if not argcmd:
    print('BUSCOMP prefix must be given as second argument')
    sys.exit(2)
prefix = argcmd.pop(0)
if argcmd: description = ' '.join(argcmd)

## Print options
print('\nInput options:')
print('|-- Run path: {}'.format(runpath))
print('|-- Prefix: {}'.format(prefix))
if description: print('|-- Description: {}'.format(description))
for argstr in arglist: print('|-- {}: {}'.format(argstr,cmd[argstr]))
print('')

### Check directory
if runpath.endswith('/'): runpath = runpath[:-1]
if not os.path.exists(runpath):
    print('Runpath not found: {}'.format(runpath)); sys.exit(1)
newpath = 'run_' + prefix    
if os.path.exists(newpath):
    print('Newpath already exists: {}'.format(newpath))
    print('|-- Delete or re-run with different $PREFIX')
    sys.exit(2)

#i# Optional tarball
if cmd['targz']:
    if cmd['pigz']:
        syscmd = 'tar -c {} | pigz > {}.tar.gz'.format(runpath,runpath)
    else:
        syscmd = 'tar -czf {}.tar.gz {}'.format(runpath,runpath)
    print(syscmd); os.system(syscmd)

### Switch to run_directory if needed
runrun = glob.glob(runpath+'/run_*')
if runrun and not os.path.exists(runpath+'/full_table.tsv'):
    runpath = runrun[0]
    print('|-- Updated run path: {}'.format(runpath))

### Check BUSCO v4
if not os.path.exists(runpath+'/full_table.tsv'):
    print('No full_table.tsv found: not BUSCO v4 output?')
    sys.exit(2)

#i# Rename output files
os.mkdir(newpath)
for (output,newout) in [('full_table.tsv','full_table_{}.tsv'.format(prefix)),('short_summary.txt','short_summary_{}.tsv'.format(prefix))]:
    if os.path.exists(runpath+'/'+output):
        print('|-- {} -> {}/{}'.format(output,newpath,newout))
        shutil.copy(runpath+'/'+output,newpath+'/'+newout)
    else:
        print('|-- WARNING: No {} found: partial BUSCO v4 output?'.format(output))
for (output,newout) in [('busco_sequences/single_copy_busco_sequences','single_copy_busco_sequences_{}'.format(prefix))]:
    if os.path.exists(runpath+'/'+output):
        print('|-- {} -> {}/{}'.format(output,newpath,newout))
        shutil.copytree(runpath+'/'+output,newpath+'/'+newout)
    else:
        print('|-- WARNING: No {} found: partial BUSCO v4 output?'.format(output))

#i# Optional delete
if cmd['delete']:
    for deldir in glob.glob('{}/*output'.format(runpath)):
        print('Deleting {}'.format(deldir))
        shutil.rmtree(deldir)

#i# Optional description
if description:
    descfile = '{}/description_{}.txt'.format(newpath,prefix)
    if os.path.exists(descfile): print('Replacing old description: {}'.format(open(descfile,'r').readlines()[0]))
    open(descfile,'w').write('{}\n'.format(description))

print('\nEnd')
### END OF SCRIPT ###
