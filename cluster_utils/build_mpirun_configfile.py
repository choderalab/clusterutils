#!/usr/bin/env python
import os
import re
import argparse
import textwrap


def main():
    args, exec_args = parse_args()
    pbs_gpufile_lines = read_pbs_gpufile()
    hostlist = extract_hostlist(pbs_gpufile_lines)
    hydra_hostlist_arg = construct_hydra_hostlist_arg(hostlist)
    hydra_exec_lines = construct_hydra_exec_lines(hostlist, exec_args)
    hydra_command_str = construct_hydra_command(hydra_hostlist_arg, hydra_exec_lines, args_mpitype=args.mpitype)
    write_configfile(hydra_command_str)


def parse_args():
    help_text = textwrap.dedent(r"""
        Construct a configfile for MPICH2 mpirun from Torque/Moab $PBS_GPUFILE contents.

        Put the command to be executed after the command for this script, e.g.
        "build_mpirun_configfile python yourscript.py -yourarg x".
        Run in a batch job script or interactive session as follows:
            python build_mpirun_configfile.py python yourscript.py -yourarg x
            mpirun -configfile configfile"""
    )
    argparser = argparse.ArgumentParser(description=help_text, formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument(
        '--mpitype', type=str, choices=['conda'],
        help='some versions of MPI, such as the conda-installable version, ' \
             'allow the configfile text to be split over multiple lines'
    )
    args, unknown_args = argparser.parse_known_args()
    exec_args = unknown_args
    return args, exec_args


def read_pbs_gpufile(filename=os.environ.get('PBS_GPUFILE')):
    if filename == None:
        raise Exception('PBS_GPUFILE environment variable not found.')
    infile = open(filename, 'r')
    lines = infile.readlines()
    infile.close()
    return lines


def extract_hostlist(pbs_gpufile_lines):
    hostlist = []
    for (index, line) in enumerate(pbs_gpufile_lines):
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


def construct_hydra_exec_lines(hostlist, exec_args, mpitype='hydra'):
    exec_arg_str = ' '.join(exec_args)
    exec_lines = []
    for (index, hostname, gpuid) in hostlist:
        if mpitype == 'hydra':
            exec_line = "-np 1 -env CUDA_VISIBLE_DEVICES %s %s" % (gpuid, exec_arg_str)
        else:
            exect_line = "-host %(hostname)s -env HOSTNAME %(hostname)s " \
                         "-env CUDA_VISIBLE_DEVICES %(gpuid)s %(exec_arg_str)s" \
                         % vars()
        # Different processes must be separated by colon ':'
        if (index + 1) != len(hostlist):
            exec_line += ' :'
        exec_lines.append(exec_line)
    return exec_lines


def construct_hydra_command(hostlist_arg, exec_lines, args_mpitype):
    if args_mpitype == 'conda':
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
