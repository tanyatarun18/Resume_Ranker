import psycopg2
from psycopg2.extras import RealDictCursor
import os

# --- IMPORTANT: Replace with your 'terraform output' value ---
# It's good practice to get this from an environment variable, but for this project,
# pasting it directly is fine.
DB_HOST = "terraform-20250801172656445000000002.cyfioy2g0n7y.us-east-1.rds.amazonaws.com"
DB_NAME = "resumeranker"
DB_USER = "rankeradmin"
DB_PASSWORD = "yoursecurepassword123"
# -------------------------------------------------------------

def get_db_connection():
    """Establishes a new connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=5432,
            connect_timeout=5 # Add a timeout
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: Could not connect to the database. {e}")
        # In a real web app, you'd want to handle this more gracefully.
        raise e


def get_all_jobs_with_candidates():
    """Fetches all jobs and their ranked candidates from the database."""
    conn = get_db_connection()
    # RealDictCursor allows us to access columns by name (like a dictionary), which is easier in Flask templates.
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch all jobs, most recent first
    cur.execute("SELECT * FROM jobs ORDER BY job_id DESC")
    jobs = cur.fetchall()

    # For each job, fetch its associated resumes, highest score first
    # NULLS LAST ensures that resumes still processing appear at the bottom.
    for job in jobs:
        cur.execute(
            "SELECT * FROM resumes WHERE job_id = %s ORDER BY match_score DESC NULLS LAST",
            (job['job_id'],)
        )
        job['candidates'] = cur.fetchall()

    cur.close()
    conn.close()
    return jobs


def create_resume_record(job_id, s3_key, filename):
    """Creates an initial record for an uploaded resume before it's processed."""
    conn = get_db_connection()
    cur = conn.cursor()
    # We insert a record with a null score, which will be updated by the backend worker.
    cur.execute(
        "INSERT INTO resumes (job_id, s3_key, candidate_name) VALUES (%s, %s, %s)",
        (job_id, s3_key, filename)
    )
    conn.commit()
    cur.close()
    conn.close()

