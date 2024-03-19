import os
import sys
import unittest
import shutil
from fpdf import FPDF

os.environ["FROM_TEST_SCRIPT"] = "true"

wrapper_script = 'run_initial_task.sh'
split_pdf_script = 'split_pdf.py'


class TestSplitPDF(unittest.TestCase):
    def testGetCurrentDirectory(self):
        """
        The testGetCurrentDirectory function tests the get_current_directory
        function in split_pdf.py.
        It does this by simulating a call to split_pdf.py through 
        run_initial_task.sh from initial task, and then checking if the
        arguments are retrieved correctly.
        """
        from genai.split_pdf import get_current_directory

        # simulate call to split_pdf.py through run_intial_task.sh from initial_task.py
        sys.argv = ["split_pdf.py", "current_dir", "pdf_file"]
        self.assertEqual(get_current_directory(), ("current_dir", "pdf_file"), "Arguments not retrieved correctly.")

    def create_pdf_with_numbers(self):
        """
        The create_pdf_with_numbers function creates a PDF file with 3 pages.
        Each page has its number written on it in the top left corner.
        """
        pdf_file = 'test_pdf.pdf'
        pdf_writer = FPDF()

        # Add blank pages and write their page numbers inside
        for i in range(3):
            pdf_writer.add_page()
            pdf_writer.set_xy(0, 0)
            pdf_writer.set_font('Times')
            pdf_writer.cell(ln=0, align='L', w=0, txt=str(i+1), border=0)
        
        pdf_writer.output(pdf_file, 'F')

        return pdf_file

    def testSplitPdf(self):
        """
        The testSplitPdf function tests the split_pdf function in
        the split_pdf module. It creates a dummy PDF file with three
        pages, each containing a number from 1 to 3. The test then calls
        the split_pdf function on this dummy PDF file and checks that
        the extracted pages are present in the extracted_pages directory.
        """
        from genai.split_pdf import split_pdf

        # create a dummy PDF file to test
        pdf_file = self.create_pdf_with_numbers()

        # test pdf splitting
        split_pdf(pdf_file, os.getcwd())
        self.assertTrue(os.path.exists("extracted_pages/LHC_page_1.pdf"),\
            "Page 1 of PDF not extracted.")
        self.assertTrue(os.path.exists("extracted_pages/LHC_page_2.pdf"),\
            "Page 2 of PDF not extracted.")
        self.assertTrue(os.path.exists("extracted_pages/LHC_page_3.pdf"),\
            "Page 3 of PDF not extracted.")

        # remove dummy files
        os.remove(pdf_file)
        shutil.rmtree('extracted_pages')
