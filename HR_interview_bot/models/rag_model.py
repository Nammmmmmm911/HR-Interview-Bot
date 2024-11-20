import fitz  # PyMuPDF
import re
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoModelForCausalLM, AutoTokenizer
 # Ensure the function name matches exactly

# Initialize the OpenAI model
def initialize_openai_model():
    return OpenAI(model="gpt-neo-1.3B", temperature=0, openai_api_key="your-api-key-here")

def extract_text_from_pdf(pdf_file):
    """Extracts the full text from a PDF file uploaded by the user."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_below_skills(resume_text, llm):
    """
    Uses AI to extract all the text below the 'Skills' section in a resume.
    
    Args:
    - resume_text (str): The full text of the resume.
    - llm (OpenAI): Initialized OpenAI model to analyze the resume.
    
    Returns:
    - str: The extracted text below the 'Skills' section.
    """
    # Prompt the AI model to find and extract text below "Skills"
    prompt = f"""
    You are a resume parser. Extract all the text below the 'Skills' section from the following resume text. If there is no clear 'Skills' section, return an empty string. 

    Resume Text:
    {resume_text}
    """

    response = llm.predict(prompt)
    return response.strip()

def format_resume_text(resume_text):
    """
    Formats the resume text by highlighting main headings and ensuring readability.

    Args:
    - resume_text (str): The full text of the resume.

    Returns:
    - str: Formatted resume text with bold headings.
    """
    # Define the main headings we want to highlight
    main_headings = [
        "Name", "Contact number", "Phone number", "Email", "Skills", "Experience",
        "Education", "Hobbies", "Achievements", "Languages known"
    ]

    # Replace headings with bolded HTML versions
    for heading in main_headings:
        resume_text = re.sub(rf"(?<=\n){heading}:", f"<b>{heading}:</b>", resume_text, flags=re.IGNORECASE)

    # Make sure each section title is followed by a line break for readability
    resume_text = resume_text.replace("\n", "<br>")
    
    return resume_text

# Example function to use the above methods
def process_resume(pdf_file):
    """Processes the uploaded resume file and extracts text below 'Skills'."""
    # Step 1: Initialize the OpenAI model
    llm = initialize_openai_model()

    # Step 2: Extract raw text from the PDF
    resume_text = extract_text_from_pdf(pdf_file)

    # Step 3: Format the resume text by highlighting main headings
    formatted_resume_text = format_resume_text(resume_text)

    # Step 4: Extract text below the 'Skills' section using AI
    text_below_skills = extract_text_below_skills(formatted_resume_text, llm)

    # Step 5: Format the extracted text for HTML
    formatted_text = text_below_skills.replace("\n", "<br>")
    
    return formatted_text
