from litellm import completion
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Instruction template for the LLM
instruction = """
Generate a compelling LinkedIn post based on the PDF content provided, following these guidelines:

1. STYLE & TONE:
   - Write in first-person perspective as someone who has personally read and been impacted by the document
   - Use a conversational, thoughtful tone that reflects genuine interest in the topic
   - Include 1-2 personal reflections or opinions that demonstrate engagement with the material
   - Vary sentence structure and length to create natural rhythm and flow

2. STRUCTURE (1300-2000 characters):
   - Start with an attention-grabbing opening that poses a question or shares a surprising insight
   - Break content into 2-3 short paragraphs with strategic spacing for readability
   - Include 1-2 specific facts or statistics from the document to establish credibility
   - End with a thought-provoking question or call-to-action that encourages comments

3. CONTENT ELEMENTS:
   - Mention authors and publication date naturally within the flow of text
   - Reference that you've been reading/reviewing this document (without explicitly saying "PDF")
   - Focus on 1-3 key takeaways rather than attempting to summarize everything
   - Include your perspective on why these insights matter to your professional network

4. ATTRIBUTION & FORMATTING:
   - Use 1-3 emojis maximum, placed strategically (not in succession)
   - At the end of the post, include a clear attribution line with authors and publication date
   - Follow the attribution with these hashtag related to the content; always include #llm
   - Format example: "Based on work by [Authors] ([Publication Date]) #llm #sports #innovation"
   - DO NOT include character counts, introductory phrases, or any meta-commentary
   - DO NOT present as a formal summary or book report - write as a professional sharing valuable insights

The final post should read as if a thoughtful professional read something interesting and wanted to share their genuine takeaways with their network, while properly crediting the original authors.

"""

def generate_linkedin_post(pdf_content):
    """
    Generates a LinkedIn post based on the extracted PDF content using LiteLLM with OpenRouter.
    
    Args:
        pdf_content (str): The extracted text content from the PDF.
    
    Returns:
        str: The generated LinkedIn post.
    """
    # Check if API key is set
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    
    # Prepare messages for the LLM
    # messages = [
    #     {"role": "system", "content": instruction},
    #     {"role": "user", "content": f"PDF Content:\n{pdf_content}"}
    # ]
    
    # Call the OpenRouter API via LiteLLM
    # You can choose different models from OpenRouter by changing the model parameter
    # See https://openrouter.ai/models for available models
    try:
        # response = completion(
        #     #model="openrouter/anthropic/claude-3-sonnet-20240229",  # You can change this to any model available on OpenRouter
        #     model ="meta-llama/llama-3.3-8b-instruct:free",
        #     messages=messages,
        #     temperature=0.7,
        #     max_tokens=1000
        # )
       

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="<OPENROUTER_API_KEY>",
        )

        completion = client.chat.completions.create(
        extra_headers={"Authorization": f"Bearer {openrouter_api_key}"},
        extra_body={},
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": f"PDF Content:\n{pdf_content}"}
    ],
        temperature=0.7,
        max_tokens=1000,
        stop=None,
        top_p=0.85,
        stream=False
)

        
        # Extract the generated LinkedIn post from the response
        linkedin_post = completion.choices[0].message.content.strip()
        #linkedin_post = response.choices[0].message.content
        return linkedin_post
    
    except Exception as e:
        return f"Error generating LinkedIn post: {str(e)}"
