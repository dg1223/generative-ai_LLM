#!/usr/bin/env python3
import os
import shutil
import sys
import time
from pypdf import PdfReader
from tqdm import tqdm

# globals
call_script = 'run_initial_task.sh'
word_counting_script = 'count_it.py'
split_pdf_script = 'split_pdf.py'
pdf_file = 'LHC.pdf'
current_dir = os.getcwd()

def set_current_dir(cur_dir):
    """
    The set_current_dir function is used to set the current directory
    of the script.
    This is done because when running locally, we are in a test folder
    and when running on CI, we are in a GangaGSoC2024 folder.
    The function takes as input the current directory and returns it
    after setting it to be either:
        - The parent_dir (genai) if local run or 
        - The grandparent_dir/parent_dir (GangaGSoC2024/genai) if
          CI run
    
    :param cur_dir: Set the current directory
    :return: The current directory path
    """
    root_dir = os.path.dirname(cur_dir)
    parent_dir = 'genai'

    # for local runs
    leaf_dir = os.path.basename(cur_dir)
    if leaf_dir == 'test':
        cur_dir = os.path.join(root_dir, parent_dir)

    # for CI runs
    if leaf_dir == 'GangaGSoC2024':
        cur_dir = os.path.join(cur_dir, parent_dir)

    return cur_dir


def create_call_script(script=None):
    """
    The create_call_script function creates a bash script that will run
    the specified Python script.
    
    :param script: Pass the name of the script to be run
    :return: The name of the python script to be run
    """
    if not script and len(sys.argv) < 2:
        print(f"You must specify the Python file as an argument")
        print(f"If making a complete system call, \
            pass the run flag too.")
        sys.exit(1)

    python_script = script if script else sys.argv[1]
    python_script = os.path.basename(python_script)
    cur_dir = set_current_dir(current_dir)

    # Create a bash script that will run the specified Python script
    with open(call_script, 'w') as script:
        if python_script == word_counting_script:
            script.write(f"""#!/bin/bash
            python3 "{cur_dir}/{python_script}" "$1" "$2" "$3" {pdf_file}
            """)
        else:
            script.write(f"""#!/bin/bash
            python3 "{cur_dir}/{python_script}" "{cur_dir}" {pdf_file}
            """)

    # make it executable
    os.system(f"chmod +x {call_script}")

    return python_script, cur_dir

def check_file_existence(filepath):
    """
    The check_file_existence function checks if a file exists.
    If the file does not exist, it prints an error message and
    exits the program.    
    
    :param filepath: Specify the filepath of the file to be checked
    """
    if not os.path.exists(filepath):
        print(f"\nThe file '{filepath}' does not exist.")
        print("Please store the file in the current directory and rerun the job.\n")
        sys.exit(1)

def submit_ganga_job(python_script, cur_dir):
    """
    The submit_ganga_job function is used to submit a Ganga job.
    
    :param python_script: Specify the python script to be executed
    :param cur_dir: Specify the directory where the input file is located
    :return: A job object and a job name
    """
    script_filename = os.path.basename(python_script)
    job_name = os.path.splitext(script_filename)[0]

    j = Job(name=job_name, backend=Local())
    j.application = Executable()
    j.application.exe = File(call_script)

    # Create splitter for the word count job
    if script_filename == word_counting_script:
        input_pdf = os.path.join(cur_dir, pdf_file)
        check_file_existence(input_pdf)
        reader = PdfReader(input_pdf)
        number_of_pages = len(reader.pages)
        word = 'it'

        # split using ArgSplitter
        splitter_args = [ [cur_dir, page_num, word] for page_num in range(number_of_pages)]
        j.splitter = ArgSplitter(args=splitter_args)

        # merge using TextMerger
        j.postprocessors.append(TextMerger(files=['stdout']))

    j.submit()

    return j, job_name

def count_frequency(output_file):
    """
    The count_frequency function takes a file as input and
    adds up only the integers.
    
    :param output_file: Specify the file that is being read
    :return: The sum of all integers in the file
    """
    with open(output_file, 'r') as f:
        lines = f.readlines()

    word_count = 0
    for line in lines:
        # Check if the line does not start with '#'
        if not line.startswith('#'):
            try:
                word_count += int(line.strip())
            except ValueError:
                continue

    return word_count

def store_word_count(job, job_name, cur_dir):
    '''
    1. Wait (1 min) until job finishes with 'completed' status.
    2. Extract the word counts from the merged file, calculate
    the total word count and store it to a file
    '''
    start_time = time.time()
    timeout = 60 # 1 minute

    print("\nWaiting for job to finish. Maximum wait time: 1 minute\n")

    with tqdm(total = timeout, \
        leave=False, \
        bar_format='{elapsed}') as progress_bar:

        '''
        Running this script externally does not provide direct access
        to the jobs registry. So, we need to explicitly fetch it.
        However running it from ganga doesn't have this issue as we 
        have direct access to the registry there.
        '''
        if os.getenv("TEST_SCRIPT_OVERRIDE") == "true":
            jobs = getRegistryProxy('jobs')
            current_status = jobs(job.id).status

            if not monitoring_component.enabled:
                monitoring_component.enable()
        else:
            current_status = None

        while current_status != 'completed' and job.status != 'completed':
            if os.getenv("TEST_SCRIPT_OVERRIDE") == "true":
                current_status = jobs(job.id).status

            # update progress bar
            elapsed_time = time.time() - start_time
            progress_bar.update(elapsed_time - progress_bar.n)
            
            # timeout if job is still running, can be a monitoring or job issue
            if elapsed_time > timeout:
                if job.status == 'completed':
                    break
                else:
                    print("Timeout reached. Job didn't finish. Exiting job...")
                    return

            time.sleep(1)

    merged_output = job.outputdir + 'stdout'
    word_count = count_frequency(merged_output)
    result_file = cur_dir + '/' + job_name + '.txt'

    with open(result_file, 'w') as f:
        f.write(str(word_count))

    print(f"\n>>> Frequency of the word 'it' = {word_count} <<<\n")
    print(f"The word count has been stored in the same directory as this script: {result_file}")    
    print(f"\nRun this command to see the stored result: cat {result_file}")
    print(f"\nRun this command to check the output from TextMerger: jobs({job.id}).peek('stdout')\n")

def execute_initial_task():
    """
    The execute_initial_task function is the main function of this module.
    It creates a script to be executed by Ganga, submits it as a job and
    stores the output in an appropriate manner.
    The script can either be word_counting_script or split_pdf_script
    depending on what task has been chosen by the user.
    """
    script, cur_dir = create_call_script()
    job, job_name = submit_ganga_job(script, cur_dir)

    if script == word_counting_script:
        store_word_count(job, job_name, cur_dir)
    elif script == split_pdf_script:
        print(f"\nExtracted pages from {pdf_file} have been saved in the folder {cur_dir}/extracted_pages")
        print(f"\nFor a detailed stdout, run the command: jobs({job.id}).peek('stdout') in ganga prompt.\n")
    
    try:
        os.remove('run_initial_task.sh')
    except FileNotFoundError:
        print(f"run_initial_task.sh not found in {cur_dir}")


# Prevent autorun if script is being imported by test_InitialTask.py
if os.getenv("FROM_TEST_SCRIPT") == "true":
    RUN_INITIAL_TASK = False
else:
    RUN_INITIAL_TASK = True

# TEST_SCRIPT_OVERRIDE helps mimic an entire system call from test scripts
if RUN_INITIAL_TASK:
    execute_initial_task()
elif os.getenv("TEST_SCRIPT_OVERRIDE") == "true":
    from ganga.ganga import ganga
    from ganga import Job, Local, Executable, File, ArgSplitter, TextMerger
    '''
    Importing sleep_until_completed() here throws a ConfigError,
    so I have used some of its logic to implements a sleep timer myself
    '''
    from GangaCore.Core.GangaRepository import getRegistryProxy
    from GangaCore.Core import monitoring_component
    execute_initial_task()
else:
    from ganga.ganga import ganga
    from ganga import Job, Local, Executable, File, ArgSplitter, TextMerger
    from GangaCore.Core.GangaRepository import getRegistryProxy
    from GangaCore.Core import monitoring_component
