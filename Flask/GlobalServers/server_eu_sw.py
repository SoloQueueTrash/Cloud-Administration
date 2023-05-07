from flask import Flask, request, send_file
import os
from google.cloud import storage
from io import BytesIO
import mimetypes

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return 'Error: This route is not defined\n', 404

@app.route('/files/<string:file>')
def getFile(file):
    print("FILE:" + file)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')
    # Create a bucket object for our bucket
    bucket = client.get_bucket('asc_us-central1')
    # Check if file exists in the bucket

    if not bucket.blob(file).exists():
        return "File doesn't exist in the bucket\n", 404
    
    blob = bucket.blob(file)
    file_bytes = blob.download_as_bytes()
    file_stream = BytesIO(file_bytes)

    mimetype = mimetypes.guess_type(file)[0]
    print("MIME" + mimetype)
    if mimetype is None:
        mimetype = 'application/octet-stream'

    return send_file(file_stream, mimetype=mimetype, as_attachment=True, download_name=file)

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=8000)
