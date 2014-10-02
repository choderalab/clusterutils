"""
Executes qstat -f [-u username], and provides an interface to the xml-format output.
Allows custom XPath queries to be made.
"""

import subprocess
from lxml import etree

class QStatF:
    def __init__(self, username=None):

        if username != None:
            xmltext = subprocess.check_output(['qstat', '-fx', '-u', username])
        else:
            xmltext = subprocess.check_output(['qstat', '-fx'])

        self.xml = etree.fromstring(xmltext)

    def get_running_job_ids(self):
        print ' '.join([x.text for x in self.xml.xpath('/Data/Job[job_state[text()="R"]]/Job_Id')])

        # for exec_gpus_node in xml.xpath('/Data/Job/exec_gpus'):
        #     job = exec_gpus_node.getparent()
        #     jobid = job.find('Job_Id').text
        #     jobname = job.find('Job_Name').text
        #     job_state = job.find('job_state').text
        #     print jobid, jobname, job_state, exec_gpus_node.text

    def get_jobs_by_host(self, hostname):
        """
        e.g. "gpu-1-13"
        """
        [self.print_job_info(job) for job in self.xml.xpath('/Data/Job/exec_host[contains(text(), "%s")]/..' % hostname)]

    def get_gpu_jobs_by_host(self, hostname):
        """
        e.g. "gpu-1-13"
        """
        [self.print_job_info(job) for job in self.xml.xpath('/Data/Job/exec_gpus[contains(text(), "%s")]/..' % hostname)]

    def print_job_info(self, job_node):
        job_owner = job_node.find('Job_Owner').text.split('@')[0]
        job_id = job_node.find('Job_Id').text
        job_name = job_node.find('Job_Name').text
        print job_owner, job_id, job_name

# Data
#   Job
#     Job_Id
#     Job_Name
#     Job_Owner
#     resources_used
#     job_state
#     queue
#     server
#     Checkpoint
#     ctime
#     Error_
#     exec_host
#     exec_port
#     exec_gpus
#     Hold_Types
#     Join_
#     Keep_Files
#     Mail_Points
#     Mail_Users
#     mtime
#     Output_
#     Priority
#     qtime
#     Rerunable
#     Resource_List
#     session_id
#     Variable_List
#     etime
#     submit_args
#     start_time
#     Walltime
#     start_count
#     fault_tolerant
#     job_radix
#     submit_host
#     gpu_flags

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-u', '--user', required=False)
    args = argparser.parse_args()
    qstatf = QStatF(args.user)
