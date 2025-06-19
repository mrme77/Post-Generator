# main.py
import os
import gradio as gr
from dotenv import load_dotenv
from pdf_processing import extract_pdf_content
from llm_integration import generate_linkedin_post
from analytics import log_analytics, is_too_similar

load_dotenv()

def process_pdf(file, tone, version):
    if file is None:
        return "Please upload a PDF file.", "Character count: 0", gr.update(visible=False), gr.update(visible=False)

    content = extract_pdf_content(file)
    if content.startswith("Error"):
        return content, "Character count: 0", gr.update(visible=False), gr.update(visible=False)

    max_attempts = 3
    for attempt in range(max_attempts):
        post = generate_linkedin_post(content, tone, retry_num=attempt)
        if not is_too_similar(post):
            log_analytics("generation", {"tone": tone, "version": version, "length": len(post)}, content=post)
            return post, f"Character count: {len(post)}", gr.update(visible=True), gr.update(visible=False)

    return "⚠️ Could not generate a unique post after 3 tries. Try changing the tone or the document.", "Character count: 0", gr.update(visible=False), gr.update(visible=False)

def submit_feedback(post, sentiment, has_feedback):
    if has_feedback:
        return gr.update(visible=True, value="You've already provided feedback. Thank you!"), gr.update(visible=False), True
        
    if not post or post.startswith("Please upload") or post.startswith("Error"):
        return gr.update(visible=True, value="⚠️ No valid post to rate. Generate a post first!"), gr.update(visible=True), False
    
    # Log the feedback
    log_analytics("feedback", {"sentiment": sentiment}, content=post)
    
    feedback_message = "Thank you for your feedback! 😊" if sentiment == "positive" else "Thank you for your feedback! We'll work to improve. 🙏"
    # Hide the feedback buttons and show the thank you message
    return gr.update(visible=True, value=feedback_message), gr.update(visible=False), True

with gr.Blocks(title="PDF to Social Media Post Generator", css=".blue-button {background-color: #0A66C2; color: white;}") as app:
    # Create a state variable to track if feedback has been given
    has_given_feedback = gr.State(False)
    
    gr.Markdown("# 📄 PDF to Social Media Post Generator")
    gr.Markdown("Upload a PDF document, choose tone and version, and generate a Social Media post.")

    with gr.Row():
        with gr.Column():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            tone_dropdown = gr.Dropdown(
                label="Select Tone",
                choices=["Professional", "Mario Bros Style", "Insightful", "Promotional"],
                value="Professional"
            )

            version_dropdown = gr.Dropdown(
                label="Select Version",
                choices=["v1-Standard structure and tone", "v2-Experimental with richer sentence variety and longer posts"],
                value="v1-Standard structure and tone"
            )

            generate_button = gr.Button("Generate Social Media Post", elem_classes="blue-button")

        with gr.Column():
            output_box = gr.Textbox(label="Generated Social Media Post", lines=15, show_copy_button=True)
            char_count = gr.Markdown("Character count: 0")
            
            # Add feedback components
            with gr.Row(visible=False) as feedback_row:
                gr.Markdown("### Was this post helpful?")
                positive_btn = gr.Button("👍 Yes", variant="primary", size="sm")
                negative_btn = gr.Button("👎 No", variant="secondary", size="sm")
            feedback_status = gr.Markdown(visible=False)

    generate_button.click(
        fn=process_pdf, 
        inputs=[pdf_input, tone_dropdown, version_dropdown], 
        outputs=[output_box, char_count, feedback_row, feedback_status]
    )
    
    # Reset feedback status when generating a new post
    def reset_feedback():
        return False
    
    generate_button.click(fn=reset_feedback, outputs=has_given_feedback)
    
    # Add click handlers for feedback buttons
    positive_btn.click(
        fn=submit_feedback, 
        inputs=[output_box, gr.Textbox(value="positive", visible=False), has_given_feedback], 
        outputs=[feedback_status, feedback_row, has_given_feedback]
    )
    
    negative_btn.click(
        fn=submit_feedback, 
        inputs=[output_box, gr.Textbox(value="negative", visible=False), has_given_feedback], 
        outputs=[feedback_status, feedback_row, has_given_feedback]
    )

if __name__ == "__main__":
    app.launch(share=True)
