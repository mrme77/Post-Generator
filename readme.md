# 📄 PDF to Social Media Post Generator

![GitHub](https://img.shields.io/badge/license-MIT-blue)

A Gradio application that transforms PDF documents into professionally crafted social media posts using GenAI, with secure analytics logging to Google Cloud Storage — works seamlessly both locally and on Hugging Face Spaces.

---

## 📝 Overview

This tool allows users to upload a PDF (research paper, article, or report) and automatically generates a LinkedIn-ready post that summarizes the content. The app uses `meta-llama/llama-3.3-8b-instruct:free` via OpenRouter to produce compelling, professional summaries, while securely logging usage events to a Google Cloud bucket.

---

## ✨ Features

- 📄 **PDF Text Extraction**: Extracts text from uploaded PDFs using `PyPDF2`
- 🤖 **AI-Powered Summarization**: Uses GenAI models for post generation
- ✅ **Relevance Assurance**: Keeps key concepts from the original document
- 🎯 **Format Optimization**: Produces clean, ready-to-publish LinkedIn text
- 🏷️ **Hashtag Management**: Automatically adds relevant hashtags
- 🌐 **Cloud-Based Logging**: Stores usage logs in a GCS bucket (Vertex AI compatible)
- 🧑‍💻 **Works Locally and in Hugging Face Spaces**

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.8 or higher
- OpenRouter API key → [https://openrouter.ai](https://openrouter.ai)
- (Optional for local use) GCP Service Account JSON key for logging

---

### 🔧 Installation

```bash
# 1. Clone the repository
git clone https://huggingface.co/spaces/your-username/post_generator
cd post_generator

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

### 🔐 API and Credential Setup

#### 📌 1. Create a `.env` file:

```ini
OPENROUTER_API_KEY=your-openrouter-key
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/your/gcp_key.json
```

> On Hugging Face Spaces, you don’t need the `.env` file — add secrets via **Settings > Secrets**.

#### 📌 2. Hugging Face Secret Configuration:

| Key                         | Value                         |
|----------------------------|-------------------------------|
| `OPENROUTER_API_KEY`       | Your OpenRouter API key       |
| `GOOGLE_APPLICATION_CREDENTIALS` | Paste raw JSON from your GCP key |

---

### ▶️ Running the App

#### Locally:
```bash
python app/main.py
```
Your app will be available at: [http://127.0.0.1:7860](http://127.0.0.1:7860)

#### Hugging Face Spaces:
Just push the code — it auto-deploys!

---

## 💡 How It Works

1. **Upload PDF**: User selects a file
2. **Text Extraction**: PDF parsed using `PyPDF2`
3. **Post Generation**: Text sent to LLM via OpenRouter
4. **Cloud Logging**: Logs are pushed to your GCS bucket (if credentials exist)
5. **Display Result**: The LinkedIn post appears, ready to copy

---

## 📁 Project Structure

```
pdf-to-socialmedia-app/
├── app/
│   ├── main.py              # Gradio UI + routing
│   ├── llm_integration.py   # LLM logic via OpenRouter
│   ├── pdf_processing.py    # PDF extraction
│   ├── export_handler.py    # Text export logic
│   └── analytics.py         # Cloud/local logging abstraction
├── .env                     # (local only) API keys
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── analytics_logs/          # Local logs (if GCS is not used)
```

---

## ⚙️ Configuration Options

### Change the LLM Model
Edit `llm_integration.py`:
```python
model = "meta-llama/llama-3.3-8b-instruct:free"
```
Explore more models at: [https://openrouter.ai/models](https://openrouter.ai/models)

### Customize Generation Style
Edit the `instruction` prompt in `llm_integration.py` to change tone, length, or format of the post.

---

## 🔒 Security Notes

- The app never stores your PDFs or generated text beyond session memory.
- OpenRouter keys and GCP credentials are stored in `.env` (local) or Hugging Face Secrets (hosted).
- GCS logs are append-only and used solely for usage analytics.

---

## 🛠️ Future Features

- 🔐 Authentication (e.g., for private use or teams)
- 🔄 Direct Social Media Posting (LinkedIn API integration)
- 📑 Support for DOCX, PPTX files
- 💾 Enhanced cloud storage of generated posts

---

## 📄 License

MIT License — see `LICENSE` file for details.

---

## 🤝 Contributing

We welcome PRs, suggestions, and feedback!  
Open an issue or fork and submit a pull request.