from flask import Flask, render_template, request, redirect, url_for
import boto3
import json
import db

app = Flask(__name__)

# --- IMPORTANT: Replace with your new 'terraform output' values ---
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/590184002207/ResumeProcessingQueue"
BUCKET_NAME = "resume-ranker-bucket-tanya-2025-final"
# -------------------------------------------------------------

s3 = boto3.client('s3', region_name='us-east-1')
sqs = boto3.client('sqs', region_name='us-east-1')


@app.route('/')
def dashboard():
    jobs_data = db.get_all_jobs_with_candidates()
    return render_template('dashboard.html', jobs=jobs_data)


@app.route('/upload_resume/<job_id>', methods=['POST'])
def upload_resume(job_id):
    if 'resume_file' not in request.files:
        return "No file part", 400
    file = request.files['resume_file']
    if file.filename == '':
        return "No selected file", 400
    s3_key = file.filename
    try:
        db.create_resume_record(job_id, s3_key, file.filename)
        s3.upload_fileobj(file, BUCKET_NAME, s3_key)
        print(f"Successfully uploaded {s3_key} to S3.")
        message_body = json.dumps({'job_id': job_id, 's3_key': s3_key})
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=message_body)
        print(f"Sent message to SQS for {s3_key}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred during upload.", 500
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
