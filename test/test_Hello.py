import os
import unittest
from ganga.GangaTest.Framework.utils import sleep_until_completed

os.environ["FROM_TEST_SCRIPT"] = "true"

wrapper_script = 'run_initial_task.sh'
hello_script = 'hello.py'


class TestHello(unittest.TestCase):    
    def testExecuteScript(self):
        '''
        Mimics a complete system call to hello.py
        '''
        from genai.hello import execute_script

        job = execute_script()
        stdout = os.path.join(job.outputdir, 'stdout')

        sleep_until_completed(job)

        with open(stdout, 'r') as f:
            job_output = f.read().strip(' \n')

        self.assertEqual(job_output, 'Hello World',\
            "Output doesn't match expected 'Hello World'.")

        job.remove()
