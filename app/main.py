# main.py
import gradio as gr
import os
from dotenv import load_dotenv
from pdf_processing import extract_pdf_content
from llm_integration import generate_linkedin_post
from export_handler import export_to_txt
from analytics import log_analytics

load_dotenv()

def process_pdf(file, tone, version):
    if file is None:
        return "Please upload a PDF file.", "Character count: 0"

    content = extract_pdf_content(file)
    if content.startswith("Error"):
        return content, "Character count: 0"

    post = generate_linkedin_post(content, tone)
    log_analytics("generation", {"tone": tone, "version": version, "length": len(post)})
    return post, f"Character count: {len(post)}"

def export_post(text):
    filename = export_to_txt(text)
    return gr.File.update(value=filename)

with gr.Blocks(title="PDF to Social Media Post Generator", css=".blue-button {background-color: #0A66C2; color: white;}") as app:
    gr.Markdown("# 📄 PDF to Social Media Post Generator")
    gr.Markdown("Upload a PDF document, choose tone and version, and generate a Social Media post.")

    with gr.Row():
        with gr.Column():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            tone_dropdown = gr.Dropdown(label="Select Tone", choices=["Professional", "Mario Bros Style", "Insightful", "Promotional"], value="Professional")
            
            version_dropdown = gr.Dropdown(label="Select Version", choices=["v1-Standard structure and tone", "v2-Experimental with richer sentence variety and longer posts"], value="v1-Standard structure and tone")
            
            generate_button = gr.Button("Generate Social Media Post", elem_classes="blue-button")
            export_button = gr.Button("Export as TXT")

        with gr.Column():
            output_box = gr.Textbox(label="Generated Social Media Post", lines=15, show_copy_button=True)
            char_count = gr.Markdown("Character count: 0")
            txt_download = gr.File(label="Download.txt", visible=False)

    generate_button.click(fn=process_pdf, inputs=[pdf_input, tone_dropdown, version_dropdown], outputs=[output_box, char_count])
    export_button.click(fn=export_post, inputs=[output_box], outputs=[txt_download])

if __name__ == "__main__":
    app.launch(share=True)
