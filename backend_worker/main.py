import boto3
import fitz  # PyMuPDF
from docx import Document
from sentence_transformers import SentenceTransformer, util
import psycopg2
from psycopg2 import errors
import json
import os
import time
import tempfile  # <-- IMPORT THE TEMPFILE LIBRARY

# --- IMPORTANT: Make sure these values are correct from your terraform output ---
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/590184002207/ResumeProcessingQueue"
BUCKET_NAME = "resume-ranker-bucket-tanya-2025-final"
DB_HOST = "terraform-20250801172656445000000002.cyfioy2g0n7y.us-east-1.rds.amazonaws.com"
DB_NAME = "resumeranker"
DB_USER = "rankeradmin"
DB_PASSWORD = "yoursecurepassword123"


# -----------------------------------------------------------------------------

def setup_database():
    """Connects to the database and creates tables if they don't exist."""
    print("Attempting to set up database tables...")
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Create jobs table
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS jobs
                    (
                        job_id
                        SERIAL
                        PRIMARY
                        KEY,
                        job_title
                        VARCHAR
                    (
                        255
                    ) NOT NULL,
                        job_description TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                                 );
                    """)
        print("Table 'jobs' is ready.")
        # Create resumes table
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS resumes
                    (
                        resume_id
                        SERIAL
                        PRIMARY
                        KEY,
                        job_id
                        INTEGER
                        REFERENCES
                        jobs
                    (
                        job_id
                    ),
                        s3_key VARCHAR
                    (
                        255
                    ) NOT NULL,
                        candidate_name VARCHAR
                    (
                        255
                    ),
                        match_score REAL,
                        processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                                   );
                    """)
        print("Table 'resumes' is ready.")
        # Insert a sample job only if the table is empty
        cur.execute("SELECT COUNT(*) FROM jobs")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                        INSERT INTO jobs (job_title, job_description)
                        VALUES ('Senior Python Developer',
                                'Seeking a senior python developer with experience in AWS, microservices, and SQL.');
                        """)
            print("Inserted sample job posting.")
        conn.commit()
        cur.close()
    except psycopg2.OperationalError as e:
        print(f"DATABASE CONNECTION FAILED: {e}")
        print("Please check your DB_HOST and firewall settings.")
        exit()
    except Exception as e:
        print(f"An error occurred during database setup: {e}")
    finally:
        if conn:
            conn.close()


print("Loading NLP model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.")


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=5432)
    return conn


def parse_resume(file_path):
    text = ""
    try:
        if file_path.lower().endswith('.pdf'):
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        elif file_path.lower().endswith('.docx'):
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + '\n'
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
    return text


def score_resume(resume_text, job_description_text):
    embedding1 = model.encode(resume_text, convert_to_tensor=True)
    embedding2 = model.encode(job_description_text, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embedding1, embedding2)
    return cosine_scores.item()


def process_message(message):
    print("Received new message, processing...")
    body = json.loads(message['Body'])
    job_id = body.get('job_id')
    s3_key = body.get('s3_key')

    if not job_id or not s3_key:
        print("Message is missing 'job_id' or 's3_key'. Skipping.")
        return

    s3_client = boto3.client('s3')

    # --- FIX: Use tempfile to handle temporary files correctly on any OS ---
    temp_dir = tempfile.gettempdir()
    local_filename = os.path.join(temp_dir, os.path.basename(s3_key))
    # ----------------------------------------------------------------------

    conn = None
    try:
        s3_client.download_file(BUCKET_NAME, s3_key, local_filename)
        print(f"Downloaded {s3_key} to temporary location: {local_filename}")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT job_description FROM jobs WHERE job_id = %s", (job_id,))
        result = cur.fetchone()
        if not result:
            print(f"Job with ID {job_id} not found.")
            return
        job_description_text = result[0]
        resume_text = parse_resume(local_filename)
        if not resume_text:
            print("Could not extract text from resume.")
            return
        score = score_resume(resume_text, job_description_text)
        print(f"Calculated score for {s3_key}: {score:.4f}")
        cur.execute(
            "UPDATE resumes SET match_score = %s WHERE job_id = %s AND s3_key = %s",
            (score, job_id, s3_key)
        )
        conn.commit()
        print("Successfully updated score in the database.")
        cur.close()
    except Exception as e:
        print(f"An error occurred during message processing: {e}")
    finally:
        if conn:
            conn.close()
        if os.path.exists(local_filename):
            os.remove(local_filename)
            print(f"Cleaned up temporary file: {local_filename}")


def main():
    sqs = boto3.client('sqs', region_name='us-east-1')
    print("Worker started. Polling for messages from SQS...")
    while True:
        try:
            response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=20)
            if 'Messages' in response:
                message = response['Messages'][0]
                process_message(message)
                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])
            else:
                print("No new messages. Waiting...")
        except Exception as e:
            print(f"A top-level error occurred in the main loop: {e}")
            time.sleep(10)


if __name__ == '__main__':
    setup_database()
    main()
