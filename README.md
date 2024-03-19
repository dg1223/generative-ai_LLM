# Description
(Jump directly to [How to Test](#how-to-test))

My codes and input files are kept in the `genai` directory. All unit tests are kept in the `test` directory.

## <ins>Preparation</ins>

I contributed to [Ganga](https://github.com/ganga-devs/ganga). While working on it, I was able to familiarize myself with ganga’s [documentation](https://ganga.readthedocs.io/en/latest/index.html) and source code. I was able to contribute to 2 issues, opened 3 new issues and made 4 pull requests.

After that, I set up the GangaGSoC2024 project on my local machine.

## <ins>Initial Task</ins>

The initial task has three subtasks: hello world, split PDF and count word frequency in PDF. The first one is pretty straightforward. The script `initial_task.py` helps execute the second and third one.

### Hello World

The script `hello.py` runs a default ‘Hello World’ job in Ganga on `Local` backend.

[Note: A [visual tree of the working directories](#appendix-a-directory-trees) may help you easily follow the different code dependencies mentioned below.]

### Split PDF
(Go back to [Testing](#testing))

`initial_task.py` → task execution script (submits ganga job)

`run_initial_task.sh` → wrapper script that invokes the actual task script

`split_pdf.py` → splits PDF file

- The script `initial_task.py` creates a bash script called `run_initial_task.sh` and submits a ganga job that executes this script as an `Executable` application.
- This wrapper script, when invoked by the ganga job ‘split_pdf’, calls the python script `split_pdf.py` that splits the PDF file `LHC.pdf` into 29 separate PDFs to account for the 29 pages.
- These extracted files are stored in the folder `extracted_pages` inside the `genai` directory.

### Count Word Frequency
(Go back to [Testing](#testing))

`initial_task.py` → task execution script (submits ganga job)

`run_initial_task.sh` → wrapper script that invokes the actual task script

`count_it.py` → counts the number of occurences of the word ‘it’ in `LHC.pdf`

- The same script `initial_task.py` submits a ganga job named ‘count_it’ that invokes the bash script `run_initial_task.sh`.
- However, this time the job passes individual **page numbers** and the **target word ‘it’** as arguments to the bash script using `ArgSplitter`. As a result, `run_initial_task.sh` gets called 29 times to account for every page in `LHC.pdf`.
- Each time `run_initial_task.sh` gets called, it invokes the Python script `count_it.py` with a different page number as one of the arguments.
- The Python script then counts the word frequency of ‘it’ in that page and prints it out. Ganga’s `ArgSplitter` saves the output to a file called `stdout` in the user's local ganga workspace directory.
- Then the job calls `TextMerger` to merge the 29 stdout files.
- Finally, `count_it.py` parses the merged output by singling out the word counts, adds them up and stores the final count to a text file called `count_it.txt` in the `genai` directory.

### Testing

- There are 4 test files that contain 17 unit tests.
- The files `test_Hello.py`, `test_SplitPDF.py` and `test_CountIt.py` contain tests that demonstrate if each unit that contribute to executing the tasks is working.
- The file `test_CompleteSystem.py` contains 2 unit tests. These tests make complete system calls to demonstrate if the subtasks [split PDF](#split-pdf) and [Count word frequency](#count-word-frequency) are getting executed properly.
- I used the `sleep_until_completed` function from ganga’s core testing framework to wait for job completion before making post-job assertions.

## <ins>Interfacing Ganga</ins>

For this task, I chose the LLM [deepseek-coder-1.3b-instruct](https://github.com/deepseek-ai/DeepSeek-Coder). This model is trained for code generation and completion.

### Preparation

At first, I [studied the basics of Large Language Models](#additional-references) (LLM). I read about how they are trained, fine-tuned, sometimes optimized for performance ([quantized](https://towardsdatascience.com/which-quantization-method-is-right-for-you-gptq-vs-gguf-vs-awq-c4cd9d77d5be)) and what LLM hallucination means. I also crafted a **prompt** (see [Appendix B: Prompt](#appendix-b-prompt)) to feed the LLM.

### Shortlist LLMs

I used the [Extractum LLM search directory](https://llm.extractum.io/list/?benchmark=bc_lang_humaneval_python), which has details on about 30,000 LLMs, to make a list of models that I would be able to test locally as well as on online notebook platforms Google Collab and Kaggle for free. These online platforms provide free GPU time that helped expedite testing time.

After shortlisting, I retrieved the models from [Huggingface](https://huggingface.co/models) and created a test script to test their performance on the prompt.

### Choose the Best Model

I tested 33 LLMs (see [Appendix C: List of LLMs tested](#appendix-c-list-of-llms-tested)).

Based on quality of output, the best model was **deepseek-coder-1.3b-instruct**. It was consistently able to generate a perfect Python code snippet to approximate Pi using accept-reject simulation, generate another snippet to submit the Ganga job and also a wrapper bash script.

While testing the models, I was also able to fine tune my prompt (Appendix B shows this version).

I faced some drawbacks and challenges while testing the model.

- The LLM could not generate proper import statements for ganga.
- It would not use the bash script that it wrote as an argument to the ganga job. Instead, it kept passing the Python script as the argument to `File` or started hallucinating.
- It used different types of markers to delineate the different code snippets. This issue made parsing its output to extract only the codes somewhat challenging.

### <ins>Complete the Task</ins>

With the LLM selected and a working prompt crafted, I created two Python scripts, `InterfaceGanga.py` and `run_InterfaceGanga.py`, to programmatically generate output from the LLM. I also created a test file `test_GangaLLM.py` that executes a unit test to examine if the proposed code by the LLM tries to execute the job in Ganga.

- `InterfaceGanga.py`
    
    Contains the class `InterfaceGanga` that contains methods to:
    
    - Initialize model parameters
    - Run inference on the LLM to generate output
    - Store the output
    - Extract necessary code snippets from the output
    - Write the snippets to appropriate scripts
- `run_InterfaceGanga.py`
    
    Creates an `InterfaceGanga` object to generate code for the task using the LLM and store them as scripts in the `genai` directory.
    
- `test_GangaLLM.py`
    
    Executes `run_InterfaceGanga.py` and checks if the code generated by the LLM attempts to execute the proposed code in Ganga. This test file is kept in the `test` directory.
    

## Configuration

The `setup.py` file includes all the required packages to run and test my code.

---

# How to Test

## Setup Project

[1.setup.webm](https://github.com/dg1223/GangaGSoC2024/assets/4992116/9a4958b2-9843-4b2e-b481-1b3ab959aabc)

- In the Linux terminal in your favourite directory, clone this repository by replacing `[PAT]` in the command below with your GitHub PAT ([Personal Access Token](https://docs.github.com/en/enterprise-server@3.9/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)) and enter the `GangaGSoC2024` project directory.
    
    ```bash
    git clone https://[PAT]@github.com/dg1223/GangaGSoC2024.git
    cd GangaGSoC2024
    ```
    
- Set up a virtual environment
    
    ```bash
    python3 -m venv GSoC
    cd GSoC/
    . bin/activate
    ```
    
- Install dependencies (note the double dots in the second command - we need to be in the project's root directory to install additional packages)
    
    ```bash
    python -m pip install --upgrade pip wheel setuptools
    python -m pip install ..
    ```
    
- Activate ganga

  [activate-ganga.webm](https://github.com/dg1223/GangaGSoC2024/assets/4992116/fd848073-ce95-4893-9e10-ffd667eee7b9)
    
    ```bash
    ./bin/ganga
    ```
    

## ‘**Ganga Initial Task**’

You can run all three subtasks in the ganga prompt.

### Subtask 1

> Demonstrate that you can run a simple Hello World Ganga job that executes on a Local backend.
> 

This task is executed by the script `hello.py`.

[2.hello-world.webm](https://github.com/dg1223/GangaGSoC2024/assets/4992116/754eef53-1b99-4ead-a7ed-3da28d24f2ca)

In the ganga prompt, first go to the `genai` directory which should be at the same level as the GSoC directory.

```python

cd ../genai
```

Then run:

```python
ganga hello.py
```

It will run the Hello World Ganga job. If the job runs successfully, you should see the following output:

```
To check the job's stdout, run the command: jobs(job_id).peek('stdout')
```

Let’s say the `job_id` is `100`. Running the command shown in the output should show you the `stdout` of the job:

```python
jobs(100).peek('stdout')
```

You should see:

```
Hello World
/path_to_your_ganga_workspace/user/LocalXML/100/output/stdout (END)
```

Press `q` to get back to ganga prompt.

### Subtask 2

> Create a job in Ganga that demonstrates splitting a job into multiple pieces and then collates the results at the end.
> 

This task is executed by the script `initial_task.py` which takes the script `split_pdf.py` as an argument. `split_pdf.py` contains the logic for this subtask.

[3.split-pdf.webm](https://github.com/dg1223/GangaGSoC2024/assets/4992116/82b8a0d6-6f7a-4f8f-b97b-149bc9159d19)

In the ganga prompt, run:

```python
ganga initial_task.py split_pdf.py
```

If the job runs successfully, you should see the following output:

```
Extracted pages from LHC.pdf have been saved in the folder /path_to_this_git_repo/GangaGSoC2024/genai/extracted_pages

For a detailed stdout, run the command: jobs(job_id).peek('stdout') in ganga prompt.
```

Let’s say the `job_id` is `101`. Running the command shown in the output should show you the `stdout` of the job:

```python
jobs(101).peek('stdout')
```

You should see 29 lines in the output. Each one of them should look like the following:

```
Extracted page 1 from /path_to_this_git_repo/GangaGSoC2024/genai/LHC.pdf and saved as /path_to_this_git_repo/GangaGSoC2024/genai/extracted_pages/LHC_page_1.pdf
```

Press `q` to get back to ganga prompt.

**Check output**

In the `genai` directory, you should see a new folder called `extracted_pages`. In this folder, there should be 29 PDF files. Page 1 of `LHC.pdf` has been extracted as `LHC_page_1.pdf`, page 2 as  `LHC_page_2.pdf` and so on up to `LHC_page_29.pdf`.

### Subtask 3

> Create a a second job in Ganga that will count the number of occurences of the word "it" in the text of the PDF file.
> 

This task is executed by the script `initial_task.py` which takes the script `count_it.py` as an argument. `count_it.py` contains the logic for this subtask.

[4.count_it.webm](https://github.com/dg1223/GangaGSoC2024/assets/4992116/2278eb26-ec75-4535-bf58-a36b01fd005e)

In the ganga prompt, run:

```python
ganga initial_task.py count_it.py
```

As the job executes, you should see the following output that includes a timer. This job times out after 1 minute. It should not take more than a few seconds for this job to finish.

```
Waiting for job to finish. Maximum wait time: 1 minute

00:01
```

If the job runs successfully, you should see the following output:

```
>>> Frequency of the word 'it' = 31 <<<

The word count has been stored in the same directory as this script: /path_to_this_git_repo/GangaGSoC2024/genai/count_it.txt

Run this command to see the stored result: cat /path_to_this_git_repo/GangaGSoC2024/genai/count_it.txt

Run this command to check the output from TextMerger: jobs(746).peek('stdout')
```

**Check output**

As the second line in the output suggests, the job should have created a text file called `count_it.txt` in the `genai` directory. Open this file to check the word count. It should read `31`.

Alternatively, you can check the content of this file by running the command shown by the third line of the job’s stdout:

```
cat /path_to_this_git_repo/GangaGSoC2024/genai/count_it.txt
```

You should see `31` in the ganga prompt.

Let’s say the `job_id` is `102`. Running the command shown in the last line of the output should display the `stdout` from the job:

```python
jobs(101).peek('stdout')
```

You should see the merged output from Ganga TextMergeTool.

```
# Ganga TextMergeTool - [date_and_timestamp] #
# Start of file /path_to_your_ganga_workspace/user/LocalXML/746/0/output/stdout #
5
...
# Ganga Merge Ended Successfully #
(END)
```

Press `q` to get back to ganga prompt.

This is all there is to checking if the ‘initial task’ was successfully executed. How to execute the unit tests is shown in [the last section](#running-unit-tests) below.

Quit ganga and get back to the `GSoC` directory:

```python
quit
```

**Edge Cases to Consider in Counting Word Frequency**

There were 2 edge cases that I needed to address to get the correct word count. I used the most popular PDF processing library `pypdf` to extract text from `LHC.pdf`. Upon examining the extracted text, I found the following edge cases:

- The word ‘It’ appears after a line break and a bullet point in page 3.
    - It is already known that…’
- Citation markers (square brackets `[]`)
    - page 8: safety systems to contain it.[85]
    - page 16: TV series based on it.[177]

## ‘**Interfacing Ganga**’

> The purpose is to demonstrate that you can communicate with a Large Language Model in a programmatic way.
> 

The most straightforward way to test this task is to run the corresponding unit test. If it passes, then the task is complete.

However, this test takes time to complete if it is run on a CPU. In this case, I suggest running all the tests together (see [Running unit tests](#running-unit-tests)) to save time. The test first executes the run script `run_InterfaceGanga.py` that automatically detects if the system has a CUDA compatible GPU or not.

If you want to run this unit test spefically from `test_GangaLLM.py`, go to the `test` directory (assuming you are in `GSoC`):

```bash
cd ../test
```

Now run:

```bash
python -m pytest test_GangaLLM.py
```

If it passes, it means the test tried to execute the code in ganga that was proposed by the LLM.

### Test Success or Failure Criteria

The test actually calls the function `run_ganga_llm()` from `run_InterfaceGanga.py`.

**Success**

If the LLM remains consistent with the type of answers it produced when I tested it locally, you should see 3 scripts in the `test` directory:

- `estimate_pi.py` or `pi_estimation.py`, or a Python script with the same name as the function name that the LLM generated for the Pi approximation code.
- `run_ganga.sh`: This script is supposed to be the `Executable` application for the ganga job that invokes the Python script to estimate Pi’s value.
- `run_ganga_job.py`: This is the main script that submits the ganga job.

**Failure**

The **test** **will fail** if the script `run_ganga_job.py` is not found. It means the LLM either provided the code snippets in a different style than what it did during my testing or it hallucinated.

The **test** **will also fail** if it fails in its attempt to run the ganga job.

### **System Requirements**

Depending on the system configuration. the test takes 8-25 minutes to finish on a CPU (at least Intel Core i5 3rd generation) or less than a minute on a CUDA compatible GPU such as the NVIDIA Tesla P100. Minimum memory requirements are 16GB RAM and 8GB vRAM (if run on GPU).

## Running Unit Tests

(Go back to [Subtask 3](#subtask-3) or [‘Interfacing Ganga’](#interfacing-ganga-1))

[5.test.webm](https://github.com/dg1223/GangaGSoC2024/assets/4992116/89432c7f-b96b-4757-9dce-c875218f8d06)

Assuming you are in the `test` directory of the project, all of the 18 unit tests can be run by executing:

```bash
python -m pytest
```

Test scripts:

```
test_ArgSplitter.py
test_CompleteSystem.py
test_CountIt.py
test_GangaLLM.py
test_Hello.py
test_SplitPDF.py
test_trivial.py
```

# Additional References
(Go back to [Preparation](#preparation-1))

https://github.com/jncraton/languagemodels

[](https://llm.extractum.io/list/?benchmark=bc_lang_humaneval_python)

[languagemodels API documentation](https://jncraton.github.io/languagemodels/languagemodels.html)

[](https://hackernoon.com/run-llama-without-a-gpu-quantized-llm-with-llmware-and-quantized-dragon)

[👋 Welcome to MLC LLM — mlc-llm 0.1.0 documentation](https://llm.mlc.ai/docs/index.html#getting-started)

[New localllm lets you develop gen AI apps locally, without GPUs | Google Cloud Blog](https://cloud.google.com/blog/products/application-development/new-localllm-lets-you-develop-gen-ai-apps-locally-without-gpus)

[Large Language Models for Code Generation](https://blog.fabrichq.ai/large-language-models-for-code-generation-f95f93fe7de4)

[Which Quantization Method is Right for You? (GPTQ vs. GGUF vs. AWQ)](https://towardsdatascience.com/which-quantization-method-is-right-for-you-gptq-vs-gguf-vs-awq-c4cd9d77d5be)

[OpenAI GPT2](https://huggingface.co/docs/transformers/en/model_doc/gpt2)

[GitHub - GoogleCloudPlatform/localllm](https://github.com/googlecloudplatform/localllm?tab=readme-ov-file#running-locally)

# Appendix A: Directory trees

(Go back to [Initial task](#initial-task))

**genai**

```
./genai
├── count_it.py
├── hello.py
├── initial_task.py
├── __init__.py
├── InterfaceGanga.py
├── LHC.pdf
├── run_InterfaceGanga.py
└── split_pdf.py
```

**test**

```
./test
├── __init__.py
├── LHC.pdf
├── test_ArgSplitter.py
├── test_CompleteSystem.py
├── test_CountIt.py
├── test_GangaLLM.py
├── test_Hello.py
├── test_SplitPDF.py
└── test_trivial.py
```

# Appendix B: Final Prompt

(Go back to [Preparation](#preparation-1))

I want to use Ganga to calculate an approximation to the number pi using an accept-reject simulation method with one million simulations. I would like to perform this calculation through a Ganga job. The job should be split into a number of subjobs that each do thousand simulations.The code should be written in Python. 

Here are some instructions that you can follow.

1. Write code to calculate the approximation of pi using the above-mentioned method.
2. Write a bash script that will execute the code above.
3. Run a ganga job using local backend: j = Job(name=job_name, backend=Local())
4. Run the Bash script as an Executable application:
j.application = Executable()
j.application.exe = File(the_script_to_run)
5. Use ArgSplitter to split the job: j.splitter = ArgSplitter(args=splitter_args)
It should split the job into a number of subjobs that each do thousand simulations.
6. Merge output from the splitter using TextMerger:
j.postprocessors.append(TextMerger(files=['stdout']))
7. Run the ganga job: j.submit()

Do not give me code as IPython or Jupyter prompts. Give me the python script.

# Appendix C: List of LLMs tested

(Go back to [Choose the best model](#choose-the-best-model))

List of LLMs that were tested:

```
# 33 models
deepseek-coder-1.3b-base
deepseek-coder-1.3b-instruct
deepseek-coder-6.7b-base
deepseek-coder-6.7b-instruct
Deci/DeciCoder-1b
ramgpt/deepseek-coder-6.7B-GPTQ
mlx-community/stable-code-3b-mlx
mlx-community/CodeLlama-7b-Python-4bit-MLX
mlx-community/CodeLlama-7b-Instruct-hf-4bit-MLX
stabilityai/stable-code-3b
stabilityai/stablecode-instruct-alpha-3b
stabilityai/stablecode-completion-alpha-3b
TheBloke/CodeLlama-7B-GGUF
TheBloke/CodeLlama-7B-GGML
TheBloke/Llama-2-Coder-7B-GGUF
TheBloke/deepseek-coder-1.3b-base-AWQ
TheBloke/deepseek-coder-6.7B-base-GGUF
TheBloke/deepseek-coder-6.7B-instruct-GGUF
TheBloke/stablecode-instruct-alpha-3b-GGML
Salesforce/codegen2-1B
microsoft/phi-1
LoneStriker/deepseek-coder-6.7b-instruct-4.0bpw-h6-exl2-2
casperhansen/mpt-7b-8k-chat-gptq
smangrul/codellama-hugcoder-merged
unsloth/gemma-2b-bnb-4bit
unsloth/codellama-13b-bnb-4bit
davzoku/cria-llama2-7b-v1.3-q4-mlx
Deci/DeciCoder-1b
WizardLM/WizardCoder-1B-V1.0
WizardLM/WizardCoder-3B-V1.0
codellama/CodeLlama-7b-hf
codellama/CodeLlama-7b-Python-hf
smallcloudai/Refact-1_6B-fim
```
