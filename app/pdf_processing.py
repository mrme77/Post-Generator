import PyPDF2
import os

def extract_pdf_content(pdf_file):
    """
    Extracts text content from a PDF file.
    
    Args:
        pdf_file: The uploaded PDF file.
    
    Returns:
        str: Extracted text content from the PDF.
    """
    if pdf_file is None:
        return "No PDF file was uploaded. Please upload a PDF file."
    
    try:
        # Gradio file component returns the file path
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if not text.strip():
            return "No text content could be extracted from the PDF. The file might be scanned or contain only images."
        
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"
