from genai.InterfaceGanga import InterfaceGanga

def run_ganga_llm():
    """
    The run_ganga_llm function runs inference on the LLM using a prmopt.
    It returns a boolean indicating whether or not the output generated
    by the LLM contain any meaningful code.
    
    :return: True if it receives a meaningful code snippet from llm
    """
    prompt = "I want to use Ganga to calculate an approximation to the number \
    pi using an accept-reject simulation method with one million simulations. I \
    would like to perform this calculation through a Ganga job. The job should be \
    split into a number of subjobs that each do thousand simulations.The code \
    should be written in Python. \
    Here are some instructions that you can follow. \
    1. Write code to calculate the approximation of pi using the above-mentioned \
    method. \
    2. Write a bash script that will execute the code above. \
    3. Run a ganga job using local backend: j = Job(name=job_name, backend=Local()) \
    4. Run the Bash script as an Executable application: \
    j.application = Executable() \
    j.application.exe = File(the_script_to_run) \
    5. Use ArgSplitter to split the job: j.splitter = ArgSplitter(args=splitter_args) \
    It should split the job into a number of subjobs that each do thousand simulations. \
    6. Merge output from the splitter using TextMerger: \
    j.postprocessors.append(TextMerger(files=['stdout'])) \
    7. Run the ganga job: j.submit() \
    Do not give me code as IPython or Jupyter prompts. Give me the python script."

    llm = InterfaceGanga(llm_input=prompt)
    output = llm.run_llm_inference()
    print(output)

    # Write code snippets to file and return a bool indicatory
    received_code_from_llm = llm.write_code_snippet_to_file(output)

    return received_code_from_llm
