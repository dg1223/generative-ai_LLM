import re
import sys
import time
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM

class InterfaceGanga:
    def __init__(self, llm_model="deepseek-ai/deepseek-coder-1.3b-instruct",\
                       llm_input="Find approximation of Pi using Monte Carlo",\
                       return_tensor_format='pt',\
                       token_length=1024):

        self.llm_model = llm_model
        self.llm_input = llm_input
        self.return_tensor_format = return_tensor_format
        self.token_length = token_length

    def run_llm_inference(self):
        """
        The run_llm_inference method takes in a string of text and 
        returns the generated output from the LLM.
        
        :param from constructor:
            llm_model: the LLM model to use
            llm_input: prompt
            return_tensor_format: format of the return tensor
            token_length: maximum token length of the output
        :return: The generated text
        """
        tokenizer = AutoTokenizer.from_pretrained(self.llm_model,\
            trust_remote_code=True)

        model = AutoModelForCausalLM.from_pretrained(self.llm_model,\
            trust_remote_code=True, torch_dtype=torch.bfloat16)

        # Run on GPU if available
        if torch.cuda.is_available():
            print("\nFound CUDA compatible GPU. Utilizing GPU...\n\
Esimated runtime: less than 1 minute\n")
            model = model.cuda()
        else:
            print("\nNo CUDA compatible GPU found. Running on CPU only...\n\
Esimated runtime: 10 to 25 minutes\n")

        if not tokenizer.pad_token:
            tokenizer.pad_token = tokenizer.eos_token

        input_text = self.llm_input
        inputs = tokenizer(input_text,\
                return_tensors=self.return_tensor_format).to(model.device)

        start_time = time.time()

        # testing: Assert max_length >= input length
        outputs = model.generate(**inputs, max_length=self.token_length)

        end_time = time.time()

        print("\nTime taken:", round((end_time - start_time) / 60.0, 2), "minutes\n")

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    ### THIS FUNCTION BLOCK IS AUXILLARY TO THE PROBLEM STATEMENT ###

    def store_llm_output(self, output):
        output_file = 'llm_output.txt'
        with open(output_file, 'w') as f:
            f.write(output)

        return output_file

    def read_llm_output(self, output_file): 
        with open(output_file, 'r') as f:
            llm_output = f.read()

        return llm_output

    def print_llm_output(self, llm_output):
        print(llm_output)

    ### THIS FUNCTION BLOCK IS AUXILLARY TO THE PROBLEM STATEMENT ###


    def extract_code_snippet(self, pattern_type, pattern_1, pattern_2, llm_output):
        """
        The extract_code_snippet function is used to extract code snippets
        from the LLM's output.
        The function takes in a pattern_type, which is a string that describes
        what type of code snippet is being extracted (e.g., 'Pi approximation',
        'Ganga job', etc.). The function also takes in two patterns, which are
        regular expressions that describe how the code snippet should be parsed
        from the LLM's output. The first pattern will be tried first; if it fails
        to parse any text, then the second pattern will be tried instead.
        
        :param pattern_type: detect code for pi estimation or ganga job or bash
        :param pattern_1: the first pattern of text that llm wraps the code with
        :param pattern_2: the second pattern of text that llm wraps the code with
        :param llm_output: raw output from the LLM given the prompt
        :return: A snippet of code that requires futher processing
        """
        total_tries_left = 2
        while total_tries_left > 0:
            if total_tries_left == 2:
                snippets = re.findall(pattern_1, llm_output, re.DOTALL)
            else:
                snippets = re.findall(pattern_2, llm_output, re.DOTALL)
                    
            snippet = self.helper_extract_code_snippet(snippets)

            if not snippet:
                total_tries_left -= 1
                if total_tries_left == 1:
                    print(f"\nWARNING: No code snippet for '{pattern_type}' was parsed \
using coding marker #1.\nLLM probably generated a different pattern of text.")
                    print("Trying a different coding marker to match pattern...")            
                    continue
                # No point running a Ganga job when there's no code to run
                elif pattern_type == 'Pi approximation' or pattern_type == 'Ganga job':
                    print("\nERROR: Unable to parse code from LLM's output. Exiting...\n")
                    return None
                else:
                    print("LLM generated incomplete code. Continuing...")
            else:
                print(f"\n'SUCCESS!! {pattern_type}' code found in LLM's output.")

            return snippet

    def helper_extract_code_snippet(self, snippets):
        """
        The helper_extract_code_snippet function takes in a list of code snippets
        and returns the first snippet. The LLM usually generates many blank lines
        after generating code which get extracted separately and need to be ignored
        
        :param snippets: LLM's output after first phase of processing
        :return: The first element of the snippets list
        """
        snippet_size = np.shape(snippets)
        dimensions = len(snippet_size)
        # no dimension
        if not snippet_size or snippet_size[0] == 0:
            return None
        # one-dimensional
        elif dimensions == 1 and snippet_size[0] > 0:
            try:
                snippet = snippets[0]
            except:
                return None
        # two-dimensional
        else:
            try:
                snippet = snippets[0][0]
            except:
                return None

        return snippet

    def write_code_snippet_to_file(self, llm_output):
        '''
        These hardcoded patterns were developer after doing multiple simulation runs
        with the same prompt on the deepseeker model. However, the LLM's consistency
        cannot be guaranteed.
        
        :param llm_output: processed output from LLM
        '''
        pi_pattern_1 = r'python code snippet #1:(.*?)((?=\npython code snippet #2)|$)'
        ganga_pattern_1 = r'python code snippet #2:(.*?)((?=\nbash code snippet)|$)'
        bash_pattern_1 = r'bash code snippet:(.*?)((?=\npython code snippet)|$)'
        pi_pattern_2 = r"```python(.*?)```"
        ganga_pattern_2 = r"```python(\n[^`]*?from.*?)```"
        bash_pattern_2 = r"```bash(.*?)```"

        python_snippet = self.extract_code_snippet(\
            'Pi approximation', pi_pattern_1, pi_pattern_2, llm_output)
        # print(python_snippet)
        
        ganga_snippet = self.extract_code_snippet(\
            'Ganga job', ganga_pattern_1, ganga_pattern_2, llm_output)
        # print(ganga_snippet)

        if not ganga_snippet:
            print("ERROR: LLM failed to generate any code to run Ganga job.")
            return False
        
        bash_snippet = self.extract_code_snippet(\
            'Bash', bash_pattern_1, bash_pattern_2, llm_output)
        # print(bash_snippet)

        # all code snippets should be ready by this point. #
        
        # Generate file names
        pi_function_name = re.findall(r'def\s+(\w+)\(', python_snippet, re.DOTALL)
        if pi_function_name:
            if len(pi_function_name) > 1:
                pi_filename = f"{pi_function_name[0]}.py"        
            else:
                pi_filename = f"{pi_function_name}.py"
        else:
            pi_filename = "pi_estimation.py"

        ganga_filename = "run_ganga_job.py"
        bash_filename = "run_ganga.sh"

        # Write available code snippets to respective files
        if python_snippet:
            self.helper_write_to_file(pi_filename, python_snippet)
        if ganga_snippet:
            self.helper_write_to_file(ganga_filename, ganga_snippet)
        if bash_snippet:
            self.helper_write_to_file(bash_filename, bash_snippet)

        return True

    def helper_write_to_file(self, filename, snippet):
        with open(filename, 'w') as file:
            file.write(snippet.lstrip())
