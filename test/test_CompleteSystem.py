import os
import unittest
import shutil
import subprocess
from ganga.GangaTest.Framework.utils import sleep_until_completed

os.environ["FROM_TEST_SCRIPT"] = "true"

wrapper_script = 'run_initial_task.sh'
word_counting_script = 'count_it.py'
split_pdf_script = 'split_pdf.py'

class TestInitialTask(unittest.TestCase):
    def testCreateCallScript(self):
        """
        The testCreateCallScript function tests the create_call_script
        function in the initial_task module.
        It checks if a wrapper bash script exists in the current directory
        and is executable.
        
        :return: True if the wrapper bash script exists in current directory
                 and is executable
        """
        from genai.initial_task import create_call_script

        script, _ = create_call_script(word_counting_script)

        # check if wrapper bash script exists in current directory
        current_dir = os.getcwd()
        filepath = os.path.join(current_dir, word_counting_script)

        self.assertTrue(os.path.exists(wrapper_script), "Wrapper bash script doesn't exist.")
        self.assertTrue(os.access(wrapper_script, os.X_OK), "Wrapper bash script is not executable.")

    # simple test to see if ganga is working
    def testCreateAndRemoveGangaJob(self):
        """
        The testCreateAndRemoveGangaJob function creates a Ganga job,
        submits it and waits for it to complete. It then removes the job.
        """
        from ganga.ganga import ganga
        from ganga import Job
        
        j = Job()
        j.submit()

        self.assertTrue(sleep_until_completed(j, 60), 'Timeout on completing job')
        self.assertEqual(j.status, 'completed', 'Job did not complete successfully.')
        
        j.remove()

    def tryFileCopy(self, root, cur_dir, par_dir, script):
        """
        The tryFileCopy helper function copies a file from the current directory
        to the root directory. This is necessary because when running CI,
        the tests are run in a different directory than where they are stored. The 
        tryFileCopy function first tries to copy the file from its location in the 
        current working directory (root). If this fails, it then tries copying it from 
        its location relative to where it was called (cur_dir). This allows for both
        local and CI runs.
        
        :param root: the root directory of the project
        :param cur_dir: the current directory of the script
        :param par_dir: the directory of the file to be copied
        :param script: the name of the file to be copied
        """
        try:
            # for local runs
            filepath = os.path.join(root, par_dir, script)
            shutil.copy(filepath, script)
        except:
            # for CI runs
            filepath = os.path.join(cur_dir, par_dir, script)
            shutil.copy(filepath, script)

    def testSubmitGangaJob_WordCounting(self):
        """
        The testSubmitGangaJob_WordCounting function tests the submit_ganga_job
        function in initial_task.
        It checks that a job is created, and that it has been submitted to
        Ganga's Local backend. It also checks that an application, splitter
        and postprocessor have been defined for the job. The number of subjobs
        should be 29, as there are 29 pages in LHC.pdf (the PDF file used for
        testing). Finally, it waits until all subjobs have completed and then
        removes them from Ganga.
        """
        from ganga.ganga import ganga
        from ganga import Local
        from genai.initial_task import create_call_script
        from genai.initial_task import submit_ganga_job

        # get script into test directory for testing
        current_dir = os.getcwd()
        root_dir = os.path.dirname(current_dir)
        parent_dir = 'genai'

        self.tryFileCopy(root_dir, current_dir, parent_dir, word_counting_script)

        script, _ = create_call_script(word_counting_script)
        j, job_name = submit_ganga_job(script, current_dir)

        self.assertEqual(j.name, job_name, 'Job names do not match.')
        self.assertEqual(j.backend.__class__, Local, 'Job backend is not local.')
        self.assertIsNotNone(j.application, 'Application is not defined.')
        self.assertIsNotNone(j.splitter, 'Splitter is not defined.')
        self.assertEqual(len(j.postprocessors), 1), 'Postprocessors not defined correctly.'

        # there should be a subjob for each page of LHC.pdf
        self.assertEqual(len(j.subjobs), 29, 'Number of subjobs is not 29 as in the 29-page PDF.')

        # wait for job completion
        sleep_until_completed(j)
        self.assertEqual(j.status, 'completed', 'Job did not complete successfully.')
        
        j.remove()

        # remove main scripts after testing
        os.remove('run_initial_task.sh')
        os.remove(word_counting_script)

    def testSubmitGangaJob_SplitPDF(self):
        """
        The testSubmitGangaJob_SplitPDF function tests the submit_ganga_job
        function in the initial task.
        It checks that a job is created, and that it has been submitted to
        the local backend. It also checks that an application has been defined
        for this job, and then waits until it completes before checking that its
        status is 'completed'. Finally, it removes both itself and any scripts
        used during testing.
        """
        from ganga.ganga import ganga
        from ganga import Local
        from genai.initial_task import create_call_script
        from genai.initial_task import submit_ganga_job

        # get script into test directory for testing
        current_dir = os.getcwd()
        root_dir = os.path.dirname(current_dir)
        parent_dir = 'genai'

        self.tryFileCopy(root_dir, current_dir, parent_dir, split_pdf_script)

        script, _ = create_call_script(split_pdf_script)
        j, job_name = submit_ganga_job(script, current_dir)

        self.assertEqual(j.name, job_name, 'Job names do not match.')
        self.assertEqual(j.backend.__class__, Local, 'Job backend is not local.')
        self.assertIsNotNone(j.application, 'Application is not defined.')

        # wait for job completion
        sleep_until_completed(j)
        self.assertEqual(j.status, 'completed', 'Job did not complete successfully.')
        
        j.remove()

        # remove main scripts after testing
        os.remove('run_initial_task.sh')
        os.remove(split_pdf_script)

    def testCountFrequency(self):
        """
        The testCountFrequency function tests the count_frequency
        function in the initial_task.py file.
        It creates a test output file with three lines of numbers,
        and then checks that the count_frequency function returns 6.
        """
        from genai.initial_task import count_frequency

        output_file = "test_output.txt"
        with open(output_file, "w") as f:
            f.write("1\n2\n3\n")

        self.assertEqual(count_frequency(output_file), 6, 'Frequency count is incorrect.')

        os.remove('test_output.txt')

    def testStoreWordCount(self):
        """
        The testStoreWordCount function tests the store_word_count function by checking
        if a text file exists with the correct word count.
        """
        from ganga.ganga import ganga
        from ganga import Job, Local
        from genai.initial_task import store_word_count

        current_dir = os.getcwd()
        job_name = "test_store_word_count"
        j = Job(name=job_name, backend=Local())
        j.submit()
        sleep_until_completed(j)

        output_file = os.path.join(j.outputdir, 'stdout')

        # mimic merged output; overwrite default stdout
        with open(output_file, "w") as f:
            f.write("#sometext\n1\n2\n3\n#sometest\n")
        
        store_word_count(j, job_name, current_dir)

        result_file = job_name + '.txt'
        self.assertTrue(os.path.exists(result_file), 'Result file does not exist.')

        with open(result_file, 'r') as f:
            count = f.read().strip(' \n')
        self.assertEqual(count, '6', 'Stored word count is incorrect.')

        j.remove()
        os.remove(result_file)

'''
These are complete system calls to count_it.py and split_pdf.py
through the calling script initial_task.py
'''
class TestSystem(unittest.TestCase):
    # set up file paths to make system calls
    def setupPath(self, main_script, output):
        """
        The setupPath function is used to set up the path for the
        wrapper script, the main script and the output file.
        
        :param main_script: the name of the main script to be run
        :param output: the output file name
        :return: the wrapper_path, main_path and result
        """
        current_dir = os.getcwd()
        root_dir = os.path.dirname(current_dir)
        parent_dir = 'genai'
        wrapper_script = "initial_task.py"

        # for local runs
        wrapper_path = os.path.join(root_dir, parent_dir, wrapper_script)
        main_path = os.path.join(root_dir, parent_dir, main_script)
        result = os.path.join(root_dir, parent_dir, output)

        # for CI runs
        if not os.path.exists(wrapper_path) and \
            not os.path.exists(main_path):
            wrapper_path = os.path.join(current_dir, parent_dir, wrapper_script)
            main_path = os.path.join(current_dir, parent_dir, main_script)
            result = os.path.join(current_dir, parent_dir, output)

        return wrapper_path, main_path, result

    # Mimic a complete system test of count_it.py
    def testCountIt(self):
        wrapper, main, result = self.setupPath(word_counting_script, 'count_it.txt')
        
        os.environ["TEST_SCRIPT_OVERRIDE"] = "true"
        command = ["python3", wrapper, main]
        subprocess.run(command)

        self.assertTrue(os.path.exists(result), 'Result file does not exist.')

        with open(result, 'r') as f:
            count = f.read().strip(' \n')
        self.assertEqual(count, '31')

        os.remove(result)
        os.environ["TEST_SCRIPT_OVERRIDE"] = "true"

    # Mimic a complete system test of split_pdf.py
    def testSplitPDF(self):
        wrapper, main, result = self.setupPath(split_pdf_script, 'extracted_pages')
        
        os.environ["TEST_SCRIPT_OVERRIDE"] = "true"
        command = ["python3", wrapper, main]
        subprocess.run(command)

        self.assertTrue(os.path.exists(result), 'Result directory does not exist.')

        # check if directory has 29 files
        files = os.listdir(result)
        number_of_files = len(files)
        self.assertEqual(number_of_files, 29, 'Number of files in the result directory is not 29.')

        # check if some filenames match with expected names
        self.assertTrue(os.path.exists(os.path.join(result, 'LHC_page_1.pdf')))
        self.assertTrue(os.path.exists(os.path.join(result, 'LHC_page_17.pdf')))
        self.assertTrue(os.path.exists(os.path.join(result, 'LHC_page_29.pdf')))

        shutil.rmtree(result)
        os.environ["TEST_SCRIPT_OVERRIDE"] = "false"
