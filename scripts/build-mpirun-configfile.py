#!/usr/bin/env python
import os
import re
import sys
import argparse


def main():
    args = parse_args()
    pbs_gpufile_lines = read_pbs_gpufile()
    hostlist = extract_hostlist(pbs_gpufile_lines)
    hydra_hostlist_arg = construct_hydra_hostlist_arg(hostlist)
    hydra_exec_lines = construct_hydra_exec_lines(hostlist, args.exec_args)
    hydra_command_str = construct_hydra_command(hydra_hostlist_arg, hydra_exec_lines, args_mpi=args.mpi)
    write_configfile(hydra_command_str)


def parse_args():
    help_text = """Construct a configfile for MPICH2 mpirun from Torque/Moab $PBS_GPUFILE contents.

    Usage:

    python build-mpirun-configfile.py executable [args...]
    mpirun -configfile configfile"""

    argparser = argparse.ArgumentParser(description=help_text)
    argparser.add_argument('exec_args', nargs='+', help='e.g. "python yourscript.py -arg1 x"')
    argparser.add_argument(
        '-mpi', type='str', options=['conda'],
        help='some versions of MPI, such as the conda-installable version,'
             'can have the configfile text split over multiple lines'
    )
    args = argparser.parse_args()
    return args


def read_pbs_gpufile(filename=os.environ['PBS_GPUFILE']):
    infile = open(filename, 'r')
    lines = infile.readlines()
    infile.close()
    return lines


def extract_hostlist(pbs_gpufile_lines):
    hostlist = []
    for (index, line) in enumerate(pbs_gpufile_lines):
        # Extract hostname and gpuid
        # $PBS_GPUFILE format is like 'gpu-1-13-gpu0', where '%(hostname)s-gpu%(gpuid)s'
        line = line.strip()
        result = re.match('^(\S+)-gpu(\d)$', line)
        hostname = result.group(1)
        gpuid = result.group(2)
        hostlist.append((index, hostname, gpuid))
    return hostlist


def construct_hydra_hostlist_arg(hostlist):
    text = '-hosts '
    for (index, hostname, gpuid) in hostlist:
        text += '%s:1' % hostname
        if (index + 1) != len(hostlist):
            text += ','
    return text


def construct_hydra_exec_lines(hostlist, exec_args):
    exec_arg_str = ' '.join(exec_args)
    exec_lines = []
    for (index, hostname, gpuid) in hostlist:
        # outline = "-host %(hostname)s -env HOSTNAME %(hostname)s -env CUDA_VISIBLE_DEVICES %(gpuid)s %(exec_arg_str)s" % vars() # This works for non-hydra
        exec_line = "-np 1 -env CUDA_VISIBLE_DEVICES %s %s" % (gpuid, exec_arg_str)  # This works for hydra
        # Different processes must be separated by colon ':'
        if (index + 1) != len(hostlist):
            exec_line += ' :'
        exec_lines.append(exec_line)
    return exec_lines


def construct_hydra_command(hostlist_arg, exec_lines, args_mpi):
    if args_mpi == 'conda':
        delimiter = '\n'
    else:
        delimiter = ' '
    text = delimiter.join([hostlist_arg] + exec_lines)
    return text


def write_configfile(command_str, filepath='configfile'):
    with open(filepath, 'w') as ofile:
        ofile.write(command_str)


if __name__ == '__main__':
    main()