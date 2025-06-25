import os
import json
from dotenv import load_dotenv
import openai
from presidio_analyzer import AnalyzerEngine

load_dotenv()

INSTRUCTION_TEMPLATE = """
Generate a compelling social media posts in a {tone} tone based on the PDF content provided, following these guidelines:

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

# Initialize the Presidio PII Analyzer
analyzer = AnalyzerEngine()

# Define which PII entities to check for
PII_ENTITIES_TO_CHECK = [
    #"EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "US_SSN"
]

MIN_CONFIDENCE = 0.8  # Minimum confidence threshold for detected entities

def contains_pii(text: str) -> bool:
    """
    Analyze the text for presence of specified PII entities above a confidence threshold.
    Returns True if any PII entities are found, False otherwise.
    """
    results = analyzer.analyze(text=text, entities=PII_ENTITIES_TO_CHECK, language='en')
    high_confidence_results = [r for r in results if r.score >= MIN_CONFIDENCE]
    if high_confidence_results:
        print("Detected PII:", [(r.entity_type, text[r.start:r.end], r.score) for r in high_confidence_results])
        return True
    return False

def generate_linkedin_post(pdf_content: str, tone: str = "Professional", retry_num: int = 0) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    # Set up OpenAI client (module-level config)
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    
    if contains_pii(pdf_content):
        return (
            "⚠️ The uploaded PDF appears to contain personal or sensitive information. "
            "Please remove such details before generating a post."
        )

    instruction = INSTRUCTION_TEMPLATE.format(tone=tone)
    temperature = 0.7 + 0.1 * retry_num  # Add variability on retries

    try:
        response = openai.ChatCompletion.create(
        model="mistralai/mistral-small-3.2-24b-instruct:free",
        messages=[
        {"role": "system", "content": instruction},
        {"role": "user", "content": f"PDF Content:\n{pdf_content}"}
        ],
        temperature=temperature,
        max_tokens=2000,
        top_p=0.85,
)


    

        if response and "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"].strip()
        else:
            raise RuntimeError("No content returned by the language model.")

    except Exception as e:
        return f"Error generating Social Media post: {str(e)}"
