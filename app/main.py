import gradio as gr
import os
from dotenv import load_dotenv
from pdf_processing import extract_pdf_content
from llm_integration import generate_linkedin_post

# Load environment variables
load_dotenv()

def process_pdf(file):
    """
    Process the uploaded PDF and generate a LinkedIn post.
    
    Args:
        file: The uploaded PDF file.
        
    Returns:
        str: The generated LinkedIn post.
    """
    if file is None:
        return "Please upload a PDF file to generate a LinkedIn post."
    
    # Extract text from the uploaded PDF
    pdf_content = extract_pdf_content(file)
    
    # Check if extraction failed
    if pdf_content.startswith("Error") or pdf_content.startswith("No PDF"):
        return pdf_content
    
    # Generate LinkedIn post using the LLM
    linkedin_post = generate_linkedin_post(pdf_content)
    
    return linkedin_post

# Define the Gradio interface
with gr.Blocks(title="PDF to LinkedIn Post Generator") as app:
    gr.Markdown("# 📄 PDF to LinkedIn Post Generator")
    gr.Markdown("Upload a PDF document and get a professionally crafted LinkedIn post based on its content.")
    
    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(
                label="Upload PDF", 
                file_types=[".pdf"]
            )
            generate_button = gr.Button("Generate LinkedIn Post", variant="primary")
        
        with gr.Column(scale=2):
            with gr.Row():
                output_box = gr.Textbox(
                    label="Generated LinkedIn Post", 
                    placeholder="Your LinkedIn post will appear here...",
                    lines=15,
                    show_copy_button=True  # Add built-in copy button to textbox
                )
            
            # Add character count display
            with gr.Row():
                char_count = gr.HTML(value="<p style='text-align:right; color:#666;'>Character count: 0</p>")
    
    # Update character count when the output changes
    def update_char_count(text):
        if not text or text.startswith("Please upload") or text.startswith("Error") or text.startswith("No PDF"):
            return "<p style='text-align:right; color:#666;'>Character count: 0</p>"
        return f"<p style='text-align:right; color:#666;'>Character count: {len(text)}</p>"
    
    output_box.change(fn=update_char_count, inputs=output_box, outputs=char_count)
    
    # Generate button functionality
    generate_button.click(
        fn=process_pdf, 
        inputs=pdf_input, 
        outputs=output_box
    )
    
    gr.Markdown("### How it works")
    gr.Markdown("""
    1. Upload a PDF document (research paper, article, report, etc.)
    2. Click 'Generate LinkedIn Post'
    3. The app extracts the text from the PDF
    4. An LLM will then summarize the content into a professional LinkedIn post
    5. The generated post includes relevant hashtags and citations
    6. Click the copy button to easily copy the post to your clipboard
    """)

# Launch the app
if __name__ == "__main__":
    app.launch(share=True)
