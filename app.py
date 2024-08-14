import os
from flask import Flask, request, render_template, redirect, url_for, flash
from google.cloud import storage

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration
BUCKET_NAME = 'beam-summit-2024-uploads'
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_gcs(file, bucket_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.seek(0)
            upload_to_gcs(file, BUCKET_NAME, filename)
            flash('File successfully uploaded', 'success')
            return redirect(request.url)
    
    # Fetch the files in the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs]
    file_count = len(files)
    required_files = max(0, 5 - file_count)

    return render_template('index.html', files=files, file_count=file_count, required_files=required_files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
