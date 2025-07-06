import os
import json
from dotenv import load_dotenv
import openai
from presidio_analyzer import AnalyzerEngine
import tiktoken

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
"""

analyzer = AnalyzerEngine()

PII_ENTITIES_TO_CHECK = ["PHONE_NUMBER", "CREDIT_CARD", "US_SSN"]
MIN_CONFIDENCE = 0.8

def num_tokens_from_string(string: str, model_name: str = "mistral-small") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(string))
    except:
        return len(string) // 4

def chunk_text(text, max_chunk_size=80000):
    words, chunks, current_chunk, current_size = text.split(), [], [], 0
    for word in words:
        word_size = len(word) + 1
        if current_size + word_size > max_chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk, current_size = [word], word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def contains_pii(text: str) -> bool:
    results = analyzer.analyze(text=text, entities=PII_ENTITIES_TO_CHECK, language='en')
    return any(r.score >= MIN_CONFIDENCE for r in results)

def summarize_content(text):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            extra_headers={
                "HTTP-Referer": "https://huggingface.co/spaces/mrme77/PDF-To-Social-Media-Post-Generator",
                "X-Title": "PDF to Social Media Post Generator",
            },
            messages=[
                {"role": "system", "content": "Summarize the following content, extracting the key points, main arguments, and important details. Focus on information that would be valuable for creating a social media post about this document."},
                {"role": "user", "content": text[:80000]}
            ],
            temperature=0.5,
            max_tokens=4000,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception:
        return text[:1000]

def generate_linkedin_post(pdf_content: str, tone: str = "Professional", retry_num: int = 0) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    if contains_pii(pdf_content):
        return (
            "⚠️ The uploaded PDF appears to contain personal or sensitive information. "
            "Please remove such details before generating a post."
        )

    if len(pdf_content.strip()) < 300 or num_tokens_from_string(pdf_content) < 100:
        return (
            "⚠️ The uploaded content is too short to generate a compelling social media post. "
            "Please provide a longer document."
        )

    instruction = INSTRUCTION_TEMPLATE.format(tone=tone)
    temperature = 0.7 + 0.1 * retry_num

    instruction_tokens = num_tokens_from_string(instruction)
    max_total_tokens = 32000
    available_tokens = max_total_tokens - instruction_tokens - 3000

    content_tokens = num_tokens_from_string(pdf_content)

    if content_tokens > available_tokens:
        if content_tokens < available_tokens * 2:
            chunks = chunk_text(pdf_content, available_tokens)
            content_to_process = chunks[0]
        else:
            content_to_process = summarize_content(pdf_content)
    else:
        content_to_process = pdf_content

    if not content_to_process.strip():
        return "⚠️ Unable to extract usable content from the document. Please try again with a different file."

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            extra_headers={
                "HTTP-Referer": "https://huggingface.co/spaces/mrme77/PDF-To-Social-Media-Post-Generator",
                "X-Title": "PDF to Social Media Post Generator",
            },
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": f"PDF Content:\n{content_to_process}"}
            ],
            temperature=temperature,
            max_tokens=3000,
            top_p=0.85,
        )

        if response and "choices" in response and response["choices"]:
            result = response["choices"][0]["message"]["content"]
            return result.strip() if result and result.strip() else "⚠️ No usable output returned by the language model."
        else:
            return "⚠️ No content returned by the language model."

    except Exception as e:
        return f"Error generating Social Media post: {str(e)}"
