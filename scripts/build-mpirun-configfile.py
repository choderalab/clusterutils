#!/usr/bin/env python
"""
 
Construct a configfile for MPICH2 mpirun from Torque/Moab $PBS_GPUFILE contents.
 
Usage:
 
python build-mpirun-configfile.py executable [args...]
mpirun -configfile configfile
 
"""
 
import os
import re
import sys
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('-mpi', type='str', options=['conda'])
args = argparser.parse_args()
 
# Assemble executable name and arguments.
executable = ' '.join(sys.argv[1:])
 
# Open $PBS_GPUFILE for reading
filename = os.environ['PBS_GPUFILE']
infile = open(filename, 'r')
lines = infile.readlines()
infile.close()
 
# Extract (hostname,gpuid) pairs.
hostlist = list()
for (index, line) in enumerate(lines):
    # Extract hostname and gpuid
    # $PBS_GPUFILE format is like 'gpu-1-13-gpu0', where '%(hostname)s-gpu%(gpuid)s'
    line = line.strip()
    result = re.match('^(\S+)-gpu(\d)$', line)
    hostname = result.group(1)
    gpuid = result.group(2)
    hostlist.append((index, hostname, gpuid))
 
# Open configfile for writing.
outfile = open('configfile', 'w')
 
# Construct hostlist argument for hydra.
outline = '-hosts '
for (index, hostname, gpuid) in hostlist:
    outline += '%(hostname)s:1' % vars()
    if (index+1) != len(lines):
        outline += ','
outline += ' '
print outline,
outfile.write(outline)
 
# Construct configfile lines.
for (index, hostname, gpuid) in hostlist:
    # Construct MPICH2 configfile line
    #outline = "-host %(hostname)s -env HOSTNAME %(hostname)s -env CUDA_VISIBLE_DEVICES %(gpuid)s %(executable)s" % vars() # This works for non-hydra
    outline = "-np 1 -env CUDA_VISIBLE_DEVICES %(gpuid)s %(executable)s" % vars() # This works for hydra
    # Different processes must be separated by colon ':'
    if (index+1) != len(lines):
        outline += ' :'
    # Each line in configfile should end with newline.
    outline += ' '
    
    # Write out to terminal.
    print outline,
 
    # Write out to file.
    outfile.write(outline)
 
# Close output file.
outfile.close()
