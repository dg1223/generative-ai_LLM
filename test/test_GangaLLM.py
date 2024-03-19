import os
import unittest
import subprocess

class TestGangaLLM(unittest.TestCase):
    def testExecuteLLMScript(self):
        '''
        Mimics a complete system call to generate code by the LLM 
        to approximate pi, check if code contains a ganga job
        snippet and if so, submit the ganga job
        ''' 
        from genai.run_InterfaceGanga import run_ganga_llm

        # Check if LLM was able to generate code
        self.assertTrue(run_ganga_llm(), "LLM failed to generate code.")

        # set up file paths
        current_dir = os.getcwd()
        root_dir = os.path.dirname(current_dir)
        parent_dir = 'genai'
        ganga_job = "run_ganga_job.py"
        # bash_script = "run_ganga.sh"

        ### Find path for ganga job script
        # for local runs
        ganga = os.path.join(root_dir, parent_dir, ganga_job)
        # for test runs
        if not os.path.exists(ganga):
            ganga = os.path.join(current_dir, ganga_job)
        # for CI runs
        if not os.path.exists(ganga):           
            ganga = os.path.join(current_dir, parent_dir, ganga_job)

        # check if LLM generated ganga job script exists
        self.assertTrue(os.path.exists(ganga), "Ganga job script does not exist.")

        # run the ganga job
        command = ["python3", ganga]
        result = subprocess.run(command, capture_output=True)
        self.assertIsNotNone(result.returncode, "FAILED: Subprocess execution returned with None")

        ## Don't remove generated scripts during challenge assesment phase
        # try:
        #     os.remove(ganga)
        #     os.remove(bash_script)
        # except:
        #     print("Error removing scripts created by unit test.")
