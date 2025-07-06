import os
import json
import re
from dotenv import load_dotenv
import openai
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
import tiktoken

# Load environment variables
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


try:
    nlp_engine_provider = NlpEngineProvider(nlp_configuration={"en": {"model_name": "en_core_web_lg"}})
    nlp_engine = nlp_engine_provider.create_engine()
    registry = RecognizerRegistry()
    analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
    anonymizer = AnonymizerEngine()
    enhanced_pii_available = True
except Exception:
    # Fall back to basic analyzer if enhanced setup fails
    analyzer = AnalyzerEngine()
    enhanced_pii_available = False

# Comprehensive list of PII entities
PII_ENTITIES = [
    'PERSON', 'PHONE_NUMBER', 'EMAIL_ADDRESS', 'CREDIT_CARD', 'US_SSN', 'US_PASSPORT',
    'US_DRIVER_LICENSE', 'US_BANK_NUMBER', 'US_ITIN', 'DATE_TIME', #'LOCATION',
    'NRP', 'UK_NHS', 'UK_NINO', 'IP_ADDRESS', 'IBAN_CODE', 'MEDICAL_LICENSE',
    'AU_MEDICARE', 'AU_TFN', 'AU_ACN', 'AU_ABN', 'CRYPTO', 'SG_NRIC_FIN',
    'IN_PAN', 'IN_AADHAAR', 'IN_VOTER', 'IN_PASSPORT', 'IN_VEHICLE_REGISTRATION'
]

# Custom regex patterns for additional PII types
CUSTOM_PATTERNS = {
    #'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    #'URL': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[\w=&\%\-]*',
    #'USERNAME': r'@[\w\d_]+',
    'CUSTOM_ID': r'ID[\d]{6}'
}

# Confidence thresholds
ENHANCED_CONFIDENCE = 0.65
MIN_CONFIDENCE = 0.8  # For backward compatibility

def num_tokens_from_string(string: str, model_name: str = "mistral-small") -> int:
    """Calculate the number of tokens in a string."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(string))
    except:
        # Fall back to simple approximation if tiktoken fails
        return len(string) // 4

def chunk_text(text, max_chunk_size=80000):
    """Break text into chunks of specified maximum size."""
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

def detect_pii_with_presidio(text, threshold=ENHANCED_CONFIDENCE):
    """Detect PII using Presidio with detailed results."""
    results = analyzer.analyze(text=text, entities=PII_ENTITIES, language='en')
    
    detected_items = []
    for result in results:
        if result.score >= threshold:
            detected_items.append({
                'entity_type': result.entity_type,
                'text': text[result.start:result.end],
                'position': (result.start, result.end),
                'confidence': result.score
            })
    
    return detected_items

def detect_pii_with_regex(text):
    """Detect PII using custom regex patterns."""
    detected_items = []
    
    for pattern_name, pattern in CUSTOM_PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            detected_items.append({
                'entity_type': pattern_name,
                'text': match.group(),
                'position': (match.start(), match.end()),
                'confidence': 1.0  # Regex matches are certain
            })
    
    return detected_items

def verify_pii_with_llm(text, potential_pii):
    """Use LLM to verify if detected items are actually PII."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not potential_pii:
        return potential_pii
        
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    
    # Create context for the LLM
    pii_context = "\n".join([
        f"Type: {item['entity_type']}, Text: '{item['text']}', Confidence: {item['confidence']}"
        for item in potential_pii
    ])
    
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            extra_headers={
                "HTTP-Referer": "https://huggingface.co/spaces/mrme77/PDF-To-Social-Media-Post-Generator",
                "X-Title": "PDF to Social Media Post Generator",
            },
            messages=[
                {"role": "system", "content": "You are a PII verification assistant. Review the potential PII detected and determine if each item is genuinely personally identifiable information."},
                {"role": "user", "content": f"Verify if these items are actually PII. For each item, respond with 'CONFIRM' or 'FALSE_POSITIVE':\n{pii_context}"}
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        
        verification = response["choices"][0]["message"]["content"].strip()
        
        # Parse verification results
        verified_pii = []
        verification_lines = verification.split('\n')
        
        for i, item in enumerate(potential_pii):
            if i < len(verification_lines) and "CONFIRM" in verification_lines[i]:
                verified_pii.append(item)
            # If we run out of verification lines, default to including the item
            elif i >= len(verification_lines):
                verified_pii.append(item)
                
        return verified_pii
        
    except Exception as e:
        print(f"LLM verification failed: {str(e)}")
        return potential_pii  # Fall back to unverified results

def redact_pii(text, pii_items):
    """Redact detected PII from text."""
    if not pii_items:
        return text
        
    # Sort PII items by position in reverse order to avoid offset issues
    pii_items.sort(key=lambda x: x['position'][0], reverse=True)
    
    # Create a mutable copy of the text
    redacted_text = text
    
    for item in pii_items:
        start, end = item['position']
        entity_type = item['entity_type']
        replacement = f"[{entity_type}]"
        redacted_text = redacted_text[:start] + replacement + redacted_text[end:]
    
    return redacted_text

def contains_pii_comprehensive(text):
    """Comprehensive PII detection combining multiple methods."""
    # Step 1: Detect with Presidio
    presidio_results = detect_pii_with_presidio(text)
    
    # Step 2: Detect with custom regex
    regex_results = detect_pii_with_regex(text)
    
    # Combine results
    all_potential_pii = presidio_results + regex_results
    
    # Step 3: Verify with LLM (if available)
    verified_pii = verify_pii_with_llm(text, all_potential_pii)
    
    # Return detailed results
    return {
        'contains_pii': len(verified_pii) > 0,
        'pii_count': len(verified_pii),
        'pii_items': verified_pii,
        'redacted_text': redact_pii(text, verified_pii) if verified_pii else text
    }

# Replace old contains_pii with comprehensive version
def contains_pii(text: str) -> bool:
    """Enhanced PII detection that returns a boolean result for compatibility."""
    result = contains_pii_comprehensive(text)
    return result['contains_pii']

def summarize_content(text):
    """Summarize content using LLM."""
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
    """Generate a LinkedIn post based on the PDF content."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    # Enhanced PII detection
    pii_result = contains_pii_comprehensive(pdf_content)
    if pii_result['contains_pii']:
        # Provide more detailed information about detected PII
        pii_types = set(item['entity_type'] for item in pii_result['pii_items'])
        return (
            f"⚠️ The uploaded PDF appears to contain {pii_result['pii_count']} instances of personal or sensitive information. "
            f"Types detected: {', '.join(pii_types)}. "
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

    # Handle long content
    if content_tokens > available_tokens:
        if content_tokens < available_tokens * 2:
            chunks = chunk_text(pdf_content, available_tokens)
            content_to_process = chunks[0]
        else:
            # For very long content, summarize first
            content_to_process = summarize_content(pdf_content)
    else:
        content_to_process = pdf_content

    if not content_to_process.strip():
        return "⚠️ Unable to extract usable content from the document. Please try again with a different file."

    # Generate post with LLM
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
