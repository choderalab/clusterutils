clusterutils
=============

Tools for use in cluster environments.

Manifest
--------

scripts/

Scripts
-------

* build-mpirun-configfile.py
  * builds a configfile for use with MPICH2 mpirun
  * used as a workaround to set the hosts and CUDA\_VISIBLE\_DEVICES environment variable properly on the cbio-cluster
* monq.py
  * Provides an interface to the XML returned by the command "qstat -f"
  * Allows custom XPath queries
