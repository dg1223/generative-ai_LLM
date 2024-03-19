#!/usr/bin/env python3
import sys
import re
import os
import shutil
from pypdf import PdfReader
from collections import Counter

def get_arguments():
    """
    The get_arguments function takes the arguments passed to it
    from the command line and returns them as a tuple.
    It also checks that there are 4 arguments, and if not, prints
    an error message.
    
    :return: A tuple of the 4 arguments
    """
    if len(sys.argv) != 5:
        print(f"You must specify all 4 parameters as arguments.\
parameters are: current directory, page number, word, pdf file name")
        sys.exit(1)
    
    current_dir = sys.argv[1]
    page_num = sys.argv[2]
    word = sys.argv[3]
    pdf_file = sys.argv[4]

    return tuple(sys.argv[1:5])

def preprocess_text(text):
    """
    The preprocess_text function takes a string of text as input
    and returns a string with the following modifications:
        1. All square brackets are replaced by spaces
        2. All non-alphanumeric characters (except for underscores)
           are replaced by spaces
    
    :param text: Pass in the text to be cleaned
    :return: A string of lowercase words separated by spaces
    """
    square_brackets = r'\[|\]'
    
    # replace other non-alphanumeric character
    non_alpha_numeric = r'[^\w\s]|_'

    # replace brackets first, then the rest
    clean_text = re.sub(square_brackets, ' ', text.lower())    
    clean_text = re.sub(non_alpha_numeric, ' ', clean_text)

    return clean_text


def count_word(file, page_num, word):
    """
    The count_word function takes in a PDF file, page number and word
    as input. It then opens the PDF file, extracts the text from that
    page and preprocesses it. Finally it returns the count of that
    word on that particular page.
    
    :param file: Specify the file to be read
    :param page_num: Specify which page to look at
    :param word: Search for the word in the text and count how many times it appears
    :return: The number of times a word appears on a page
    """
    with open(file, 'rb') as pdf:
        reader = PdfReader(pdf)
        text = reader.pages[int(page_num)].extract_text()
        clean_text = preprocess_text(text)

        return Counter(clean_text.split())[word]

def execute_script():
    """
    The execute_script function is the main function of this script.
    It extracts three arguments: a pdf file, a page number and a word.
    The function then counts how many times the word appears on that
    page of the pdf file.
    
    :return: The number of times the word appears in the page
    """
    current_dir, page_num, word, pdf_file = get_arguments()
    input_pdf = os.path.join(current_dir, pdf_file)
    print((count_word(input_pdf, page_num, word)))


# Prevent autorun if script is being imported by test_InitialTask.py
if os.getenv("FROM_TEST_SCRIPT") == "true":
    RUN_INITIAL_TASK = False
else:
    RUN_INITIAL_TASK = True

if RUN_INITIAL_TASK or os.getenv("TEST_SCRIPT_OVERRIDE") == "true":
    execute_script()
