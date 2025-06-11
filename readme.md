# PDF to Social Media Post Generator

![GitHub](https://img.shields.io/badge/license-MIT-blue)

A Gradio application that transforms PDF documents into professionally crafted LinkedIn posts using Gen AI.

## 📝 Overview

This tool allows users to upload a PDF document (such as a research paper, article, or report) and automatically generates a LinkedIn-ready post summarizing the content. The application leverages `meta-llama/llama-3.3-8b-instruct:free` through OpenRouter to create engaging, professional posts that maintain fidelity to the original content.

## ✨ Features

- **PDF Text Extraction**: Automatically extracts text content from uploaded PDF files
- **AI-Powered Summarization**: Uses LLM models to generate professional LinkedIn posts
- **Relevance Verification**: Ensures the generated post maintains key elements from the source material
- **Format Optimization**: Produces clean post formatting ready for LinkedIn
- **Hashtag Management**: Automatically includes relevant hashtags for better visibility
- **Simple User Interface**: Clean, intuitive Gradio interface for easy interaction

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- An OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Installation

1. **Clone the repository**


2. **Create a virtual environment** (recommended)


3. **Install dependencies**
```bash pip install -r requirements.txt```


4. **Set up your API key**
   
   Create a `.env` file in the root directory and add:

### Running the Application


The application will start on a local server, typically at http://127.0.0.1:7860.

## 💻 How It Works

1. **Upload a PDF**: User uploads a PDF document through the Gradio interface
2. **Text Extraction**: The app extracts text content from the PDF using PyPDF2
3. **Content Generation**: The extracted text is sent to Claude 3 Sonnet through OpenRouter
4. **Post-Processing**: The generated post is cleaned and verified for relevance
5. **Result**: A LinkedIn-ready post is displayed in the interface, ready to be copied

## 📚 Project Structure


## ⚙️ Configuration

You can modify the following aspects of the application:

### Changing the AI Model

In `llm_integration.py`, you can change the model by modifying:


Other options include:
- `openrouter/openai/gpt-4-turbo`
- `openrouter/anthropic/claude-3-opus`
- `openrouter/meta-llama/llama-3-70b-instruct`

### Adjusting Post Generation Guidelines

Modify the `instruction` variable in `llm_integration.py` to change the post generation guidelines.

## 🔒 Security Notes

- The application processes PDF files locally and only sends the extracted text to OpenRouter
- Your OpenRouter API key is stored in the `.env` file and is not committed to version control
- No PDF content or generated posts are stored by the application

## 🛠 Future implementation

1. **Adding authentication** to control access to the application
2. **Integrating with LinkedIn API** to post directly to LinkedIn
3. **Adding support for more document types** (like Word, PowerPoint)
4. **Implementing a save/history feature** to store generated posts

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

