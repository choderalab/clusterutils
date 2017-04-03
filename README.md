clusterutils
=============

Tools for use in cluster environments.

Scripts
-------

* `build_mpirun_configfile`
  * builds a `hostfile` and `configfile` for use with MPICH3 mpirun
  * used as a workaround to set the hosts and CUDA\_VISIBLE\_DEVICES environment variable properly on the cbio-cluster 
    (both hal and lila), and on the the Merck GPU cluster (SLURM based)
* `monq.py`
  * Provides an interface to the XML returned by the command "qstat -f"
  * Allows custom XPath queries
  * **Currently outdated**
  
Usage
-----

`build_mpirun_configfile` is installed as a command line command and has a very simple usage syntax:
```shell
build_mpirun_configfile [--configfilepath {CONFIGFILE}] [--hostfilepath {HOSTFILE}] [--nocheckmpich] COMMANDS
```
* `--configfilepath` sets the name of the Multi-Process Multi-Data (MPMD) settings (i.e. the config of each MPI task). 
  Default: `configfile`
* `--hostfilepath` sets the name of the host file which houses the list of hosts, 1 line per process, repeating as 
  required and determined automatically from the scheduler.
  Default: `hostfile`
* `--nocheckmpich` is a flag that, if set, ignores determining the MPICH version on disk. Right now `clusterutils` can 
  only build against MPICH3 versions. The configuration and host files will still be built if this check fails, but a 
  warning is raised.
* `COMMANDS` is the complete command that will be executed by each MPI task. For instance, if you are using a Pythons 
  script, your command may look like `python myscript.py`.
  
The output from `build_mpirun_configfile` will be a host file, and a configuration file. The way to execute your MPI 
job from these files is the following:
```shell
mpiexec.hydra -f hostfile -configfile configfile
```
This assumes default options and the `hydra` MPI variant. Replace parts of this command with what is appropriate to your
environment.
