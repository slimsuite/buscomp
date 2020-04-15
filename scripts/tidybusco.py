#!/usr/bin/env python3

### BUSCO DIRECTORY TIDYING ###
import string, os, sys, glob, shutil

### Setup script
version = '0.0.1'

helptext = '''tidybusco.py v{}
Author: Richard J. Edwards

Usage: tidybusco.py RUNPATH [PREFIX] [--targz] [--pigz] [--delete] [--collate] [DESCRIPTION]

This script tidies up a BUSCO run directory ready for processing with BUSCOMP. If $PREFIX is given, the files within $RUNPATH will be renamed. Other options are:

--targz = tarball the whole directory prior to cleanup
--pigz = use pigz for zipping the tarball
--delete = delete all the *output directories
--collate = rename the description.txt file and single_copy_busco_sequences directory (for collating BUSCO results in one directory)

If PREFIX is given, any remaining non-option words will be used for the description and saved as description.txt or description_$PREFIX.txt. 

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
arglist = ['targz','pigz','delete','collate','debug']
cmd = {}
for argstr in arglist:
    cmd[argstr] = False
    if '--{}'.format(argstr) in argcmd:
        argcmd.remove('--{}'.format(argstr)); cmd[argstr] = True
if not argcmd:
    print('BUSCO run path must be given as first argument')
    sys.exit(2)
runpath = argcmd.pop(0)
prefix = description = ''
if argcmd: prefix = argcmd.pop(0)
if argcmd: description = ' '.join(argcmd)
if not prefix:
    prefix = os.path.basename(runpath)
    if prefix.startswith('run_'): prefix = prefix[4:]
    if prefix.endswith('.busco'): prefix = prefix[:-6]
## Print options
print('\nInput options:')
print('|-- Run path: {}'.format(runpath))
print('|-- Prefix: {}'.format(prefix))
if description: print('|-- Description: {}'.format(description))
for argstr in arglist: print('|-- {}: {}'.format(argstr,cmd[argstr]))
print('')

### Process directory
if runpath.endswith('/'): runpath = runpath[:-1]
if not os.path.exists(runpath):
    print('Runpath not found: {}'.format(runpath)); sys.exit(1)
#i# Optional tarball
if cmd['targz']:
    if cmd['pigz']:
        syscmd = 'tar -c {} | pigz > {}.tar.gz'.format(runpath,runpath)
    else:
        syscmd = 'tar -czf {}.tar.gz {}'.format(runpath,runpath)
    print(syscmd); os.system(syscmd)
#i# Optional delete
if cmd['delete']:
    for deldir in glob.glob('{}/*output'.format(runpath)):
        print('Deleting {}'.format(deldir))
        shutil.rmtree(deldir)
#i# Optional description
if description:
    descfile = '{}/description.txt'.format(runpath)
    if os.path.exists(descfile): print('Replacing old description: {}'.format(open(descfile,'r').readlines()[0]))
    open(descfile,'w').write('{}\n'.format(description))
#i# Rename files
rename = ['full_table*.tsv','missing_busco_list*.tsv','short_summary*.txt']
if cmd['collate']:
    rename.append('single_copy_busco_sequences*')
    rename.append('description*.txt')
for rfile in rename:
    rlist = glob.glob('{}/{}'.format(runpath,rfile))
    if not rlist: print('No {} files found to rename'.format(rfile)); continue
    newfile = rfile.replace('*','_{}'.format(prefix))
    print('{} -> {}/{}'.format(rlist[0],runpath,newfile))
    os.rename(rlist.pop(0),'{}/{}'.format(runpath,newfile))
    if rlist: print('WARNING: Multiple {}'.format(rfile))

print('\nEnd')
### END OF SCRIPT ###
