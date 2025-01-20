# Research Paper Information Extractor

This FastAPI application provides a web interface for uploading PDF files of research papers and extracts key information such as the title, abstract, authors, author emails, and a summary of the conclusions using OpenAI's GPT models.

## Features

- **PDF Upload and Text Extraction**: Upload PDF files and extract text from the first few pages.
- **Information Extraction**: Utilizes OpenAI's GPT to interpret and structure the extracted text into meaningful data.
- **Web Interface**: A simple and user-friendly web interface for file upload and data display.

## Installation

Make sure you have Python installed on your system. You'll also need to install several packages including FastAPI and its dependencies, PyPDF2 for PDF handling, and `python-dotenv` for environment management.

```bash
pip install fastapi uvicorn python-multipart PyPDF2 dotenv

To run the server:
uvicorn app:app --reload

Environmental Variables:
You must provide your OpenAI API key in a .env file:
OPENAI_API_KEY='your_openai_api_key_here'


