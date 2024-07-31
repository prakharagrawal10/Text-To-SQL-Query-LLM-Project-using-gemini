from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from dotenv import load_dotenv
import os
import sqlite3
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

# Function to load Google Gemini model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to retrieve query from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Define your prompt
prompt = [
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name STUDENT and has the following columns - NAME, CLASS, SECTION.
    For example,
    Example 1 - How many entries of records are present?,
    the SQL command will be something like this SELECT COUNT(*) FROM STUDENT ;
    Example 2 - Tell me all the students studying in Data Science class?,
    the SQL command will be something like this SELECT * FROM STUDENT 
    where CLASS="Data Science";
    The SQL code should not have ``` in the beginning or end and the SQL word in output
    """
]

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    question = data['question']
    sql_query = get_gemini_response(question, prompt)
    response = read_sql_query(sql_query, "student.db")
    return jsonify({
        'sql_query': sql_query,
        'response': response
    })

if __name__ == '__main__':
    app.run(debug=True)
