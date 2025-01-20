import os
import io
import logging
import openai
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
print("success" if load_dotenv() else 'failed to load env')

# Retrieve API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
print(api_key)
openai.api_key = api_key

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_text(pdf_bytes, max_pages=5):
    """Extracts text from the uploaded PDF file."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages[:max_pages]:
        text += page.extract_text() or ""
    return text

def extract_information_from_text(text):
    """Uses a chat LLM to extract required information from the text."""
    if not text.strip():
        logger.error("No text provided to process.")
        return "Error: No text provided to process."
    
    prompt = f"""
    You are an AI assistant designed to extract the following specific information from a research paper:

    1. **Title of the Paper**: Only the full title of the paper.
    2. **Abstract**: The full abstract section, if available.
    3. **Authors**: The full names of the authors. Remove any extraneous symbols or characters like "†" or similar unwanted marks from the author names.
    4. **Author Emails**: If available, provide the email addresses of the authors, without any unwanted characters or symbols (such as "†").
    5. **Summary of the Conclusion**: Provide a concise summary of the conclusion section.

    Please **do not include extra text or words** that are not part of the above sections. If any section is not available, respond with "Not available" for that section.

    The extracted information should be in this exact format (no extra text):
    Title: [Title]
    Abstract: [Abstract]
    Authors: [Author Names]
    Author Emails: [Author Emails]
    Summary of the Conclusion: [Conclusion]

    Text:
    {text}
    """
    logger.info(f"Prompt prepared for extraction: {prompt[:500]}...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Extract key information from the text as instructed."},
                      {"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        result = response['choices'][0]['message']['content'].strip()
        logger.info(f"Extracted information: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {str(e)}")
        return f"Error: {str(e)}"

@app.post("/upload/")  
async def upload_file(file: UploadFile = File(...)):
    """Endpoint to upload a PDF and extract information."""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    if file.content_type != "application/pdf":
        return HTMLResponse(content="<p>Only PDF files are allowed.</p>", status_code=400)

    if file.size > MAX_FILE_SIZE:
        return HTMLResponse(content="<p>File size exceeds the 5MB limit.</p>", status_code=400)

    try:
        file_content = await file.read()
        pdf_text = extract_pdf_text(file_content)
        extracted_info = extract_information_from_text(pdf_text)

        extracted_data = {}
        for line in extracted_info.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                extracted_data[key.strip()] = value.strip()

        html_table = """
        <style>
            body {font-family: Arial, sans-serif; background-color: #ffffff; color: #333333;}
            table {
                width: 80%; margin: 50px auto; border-collapse: collapse; box-shadow: 0 0 20px rgba(0,0,0,0.15);
                border: 1px solid #ccc; /* Add border to the table */
            }
            th, td {
                padding: 10px; background-color: #f2f2f2; color: #333;
                border: 1px solid #ccc; /* Add borders to each cell */
            }
            th {
                background-color: #005f73; color: #ffffff; text-align: center;
            }
            tr:nth-child(even) {
                background-color: #e9e9e9;
            }
            .header {
                background-color: #005f73; padding: 20px; text-align: center; border-radius: 6px; color: white;
                font-size: 24px; /* Larger font size */
            }
        </style>
        <div class='header'>
            <h1>Extracted Information</h1>
        </div>
        <table>
            <tr><th>Section</th><th>Details</th></tr>
        """
        for key, value in extracted_data.items():
            html_table += f"<tr><td>{key}</td><td>{value}</td></tr>"
        html_table += "</table>"
        return HTMLResponse(content=html_table)

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return HTMLResponse(content=f"<p>Error processing file: {str(e)}</p>", status_code=500)

@app.get("/")
def read_root():
    """Homepage with a Bootstrap-styled HTML form."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Research Paper Extractor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {font-family: Arial, sans-serif; background-color: #ffffff; color: #333333; text-align: center;}
            .header {
                padding: 20px; background-color: #005f73; color: white; text-align: center; font-size: 24px;
            }
            .container {width: 50%; margin: auto; padding-top: 40px; padding-bottom: 40px;}
            .card {box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); transition: 0.3s; border-radius: 5px; background: #fff;}
            .card:hover {box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);}

            .card-body {padding: 2px 16px;}
            .btn-primary {
                background-color: #005f73; border: none; padding: 10px 20px; border-radius: 5px; color: white; font-size: 16px; transition: background-color 0.3s;
                width: 100%; /* Full width */
            }
            .btn-primary:hover {
                background-color: #004a5c;
            }
            input[type="file"] {
                width: 100%; margin-bottom: 20px; /* Full width */
            }
        </style>
    </head>
    <body>
        <div class="header">Research Paper Extractor</div>
        <div class="container">
            <div class="card">
                <div class="card-body">
                    <p>Upload a research paper (PDF) to extract its title, abstract, authors, emails, and a summary of the conclusion.</p>
                    <form action="/upload/" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" id="file" required>
                        <button type="submit" class="btn-primary">Extract Information</button>
                    </form>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
