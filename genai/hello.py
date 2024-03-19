#!/usr/bin/env python3
import os

def execute_script():
    """
    The execute_script function is a simple example of
    how to submit a ganga job.
    It creates a Local() backend job, submits it, and
    prints the command needed to check its stdout.
    
    :return: A job object
    """
    j = Job(name='hello', backend=Local())
    j.submit()
    print(f"\nTo check the job's stdout, run the command: jobs({j.id}).peek('stdout')")

    return j

# Prevent autorun if script is being imported by test_InitialTask.py
if os.getenv("FROM_TEST_SCRIPT") == "true":
    RUN_INITIAL_TASK = False
else:
    RUN_INITIAL_TASK = True

if RUN_INITIAL_TASK:
    execute_script()
else:
    from ganga.ganga import ganga
    from ganga import Job, Local
