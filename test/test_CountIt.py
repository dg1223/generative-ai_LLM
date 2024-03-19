import os
import sys
import unittest
from fpdf import FPDF
from ganga.GangaTest.Framework.utils import sleep_until_completed

os.environ["FROM_TEST_SCRIPT"] = "true"

wrapper_script = 'run_initial_task.sh'
word_counting_script = 'count_it.py'

class TestCountIt(unittest.TestCase):
    def testGetArguments(self):
        """
        The testGetArguments function tests the get_arguments
        function in count_it.py by passing it a list of arguments
        and comparing the output to what is expected.
        """
        from genai.count_it import get_arguments

        sys.argv = ["count_it.py", "current_dir", "page_num", "word", "pdf_file"]
        self.assertEqual(get_arguments(),\
            ("current_dir", "page_num", "word", "pdf_file"),\
                "Arguments retrieved incorrectly.")

    def testPreprocessText(self):
        """
        The testPreprocessText function tests the preprocess_text
        function in count_it.py by comparing the output of preprocess_text
        to a string that is expected to be returned.
        """
        from genai.count_it import preprocess_text

        text = "The Large Hadron Collider! [citation] {CERN} more TEXT."
        self.assertEqual(preprocess_text(text),\
            "the large hadron collider   citation   cern  more text ", "Text preprocessing incorrect.")

    def testCountWord(self):
        """
        The testCountWord function tests the count_word function in
        the count_it module. It creates a PDF file with a single page
        containing some text, and then calls the count_word function
        to check if it can correctly find how many times a word appears
        on that page. The test passes if the number of occurrences is correct.
        """
        from genai.count_it import count_word

        pdf_file = 'test_pdf.pdf'
        pdf_writer = FPDF()
        pdf_writer.add_page()
        pdf_writer.set_xy(0, 0)
        pdf_writer.set_font('Times')
        text = "The Large Hadron Collider at CERN aka LHC aka large-hadron-collider."
        pdf_writer.cell(ln=0, align='L', w=0, txt=text, border=0)        
        pdf_writer.output(pdf_file, 'F')

        self.assertEqual(count_word(pdf_file, "0", "hadron"), 2, "Word count incorrect.")
        os.remove(pdf_file)
