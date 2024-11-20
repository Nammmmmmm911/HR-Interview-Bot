from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
import pandas as pd
from models.rag_model import process_resume  # Replace process_rag with process_resume
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash  # Import for password hashing
from flask import Flask, request, jsonify
from chromadb import Client 
import chromadb
import os
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Namratha@9113*",
    database="hr_bot_db"
)

# Configure ChromaDB
chroma_client = chromadb.Client()
collection_name = "job_listings"
if collection_name not in chroma_client.list_collections():
    chroma_client.create_collection(collection_name)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_company_data_to_chromadb(file_path):
    """Load company details from an Excel file into ChromaDB if not already loaded."""
    df = pd.read_excel(file_path, usecols=["jobTitle", "jobUrl", "jobDescription"])
    
    # Check if data already exists in ChromaDB
    existing_jobs = chroma_client.get_collection(collection_name).get_all()
    existing_titles = {doc.metadata["jobTitle"] for doc in existing_jobs}

    # Insert data into ChromaDB only if it doesn't already exist
    for _, row in df.iterrows():
        if row["jobTitle"] not in existing_titles:
            chroma_client.get_collection(collection_name).add(
                documents=[row["jobDescription"]],
                metadatas=[{"jobTitle": row["jobTitle"], "jobUrl": row["jobUrl"]}],
                ids=[row["jobTitle"]]  # You can use a unique identifier
            )
    print("Company data loaded into ChromaDB.")

# Route for Home
@app.route('/')
def home():
    return render_template('home.html')

# Route for Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                       (username, email, password))
        db.commit()
        return redirect(url_for('signin'))
    return render_template('signup.html')

# Route for Signin
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = user[1]
            return redirect(url_for('upload_resume'))
        else:
            return "Invalid Credentials"
    return render_template('signin.html')

# Configure the upload folder
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for Resume Upload
@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume' in request.files:
            resume = request.files['resume']
            
            if resume.filename != '':
                resume_filename = secure_filename(resume.filename)
                resume.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
                
                # Process RAG model
                results = process_resume(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
                
                return render_template('result.html', result=results)
    return render_template('upload_resume.html')


if __name__ == "__main__":
    app.run(debug=True)


