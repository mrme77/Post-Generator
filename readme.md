# 📄 PDF to Social Media Post Generator

![GitHub](https://img.shields.io/badge/license-MIT-blue)

## 📝 Overview

This tool allows users to upload a PDF (i.e. research paper, article, or report) and automatically generates a Social Media post that summarizes the content. The app uses `mistralai/mistral-small-3.2-24b-instruct:free` via OpenRouter to produce compelling, professional summaries, while securely logging usage events to a Google Cloud bucket. It works seamlessly both locally and on Hugging Face Spaces. [PDF To Social Media Post Generator App](https://huggingface.co/spaces/mrme77/PDF-To-Social-Media-Post-Generator)


---

## ✨ Features

- 📄 PDF Text Extraction: Extracts text from uploaded PDFs using PyPDF2
- 🚨 PII Checker: Ensures no PII is sent to the LLM
- 🤖 AI-Powered Summarization: Uses LLM models for post generation
- 📄 Smart Document Handling: Automatically chunks or summarizes large PDFs to avoid token limits
- ✅ Relevance Assurance: Keeps key concepts from the original document
- 🎯 Format Optimization: Produces clean, ready-to-publish SocialMedia text
- 🌐 Cloud-Based Logging: Stores usage logs in a GCS bucket (Vertex AI compatible)
- 🧑‍💻 Works Locally and in Hugging Face Spaces

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
git clone https://github.com/mrme77/Post-Generator
cd post_generator

# 2. Create a virtual environment with uv package 
- Install UV if not already installed
  curl -LsSf https://astral.sh/uv/install.sh | sh

- Create a virtual environment with UV
  uv venv .venv

- Activate the virtual environment
  source .venv/bin/activate

- Install required dependencies
  uv pip install openai gradio python-dotenv PyPDF2 presidio-analyzer spacy
  
  python -m spacy download en_core_web_lg
```

---

### 🔐 API and Credential Setup

#### 📌 1. Create a `.env` file:

```ini
OPENROUTER_API_KEY= openrouter-key
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcp_key.json
```

> On Hugging Face Spaces, you don’t need the `.env` file — add secrets via **Settings > Secrets**.

#### 📌 2. Hugging Face Secret Configuration:

| Key                         | Value                         |
|----------------------------|-------------------------------|
| `OPENROUTER_API_KEY`       | OpenRouter API key       |
| `GOOGLE_APPLICATION_CREDENTIALS` | Paste raw JSON from GCP key |

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

- Upload PDF: User selects a file
- Text Extraction: PDF parsed using PyPDF2
- Content Processing:
For normal-sized PDFs: Uses full text
For large PDFs: Automatically chunks or summarizes content to fit model context window
- Post Generation: Processed text sent to LLM via OpenRouter
- Cloud Logging: Logs are pushed to your GCS bucket (if credentials exist)
- Display Result: The Social Media post appears, ready to copy

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
│   └── logs.josnl           # Application logs
│   └── explore.ipynb        # Jupyter Notebook for quick exploration
├── .env                     # (local only) API keys
├── requirements.txt         # Python dependencies
├── README.md  
├── LICENSE                  # It contains the terms of the MIT License
├── analytics_logs/          # Local logs (if GCS is not used)
```

---

## ⚙️ Configuration Options

### Change the LLM Model
Edit `llm_integration.py`:
```python
model = "mistralai/mistral-small-3.2-24b-instruct:free"
```
Explore more models at: [https://openrouter.ai/models](https://openrouter.ai/models)

### Customize Generation Style
Edit the `instruction` prompt in `llm_integration.py` to change tone, length, or format of the post.

---

## 🔒 Security Notes

- The app never stores the PDFs uploaded beyond session memory.
- OpenRouter keys and GCP credentials are stored in `.env` (local) or Hugging Face Secrets (hosted).
- GCS logs are append-only and used solely for usage analytics.

---

## 🛠️ Future Features

- 🔐 Authentication (e.g., for private use or teams)
- 🔄 Direct Social Media Posting (API integration)
- 📑 Support for DOCX, PPTX files
- 💾 Enhanced cloud storage of generated posts

---

## 📄 License

MIT License — see `LICENSE` file for details.

---

## 🤝 Contributing

All PRs, suggestions, and feedback are welcome!  
Open an issue or fork and submit a pull request.