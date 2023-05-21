from flask import Flask, request, send_file
from flask_caching import Cache
from google.cloud import storage
from io import BytesIO
import os
import mimetypes
import requests
import json

# Load regions information from JSON file
file = open('regions.json')
regions = json.load(file)
file.close()

def getMyRegion():
    
    # Set the metadata server URL and metadata headers.
    metadata_server = 'http://metadata.google.internal'
    metadata_flavor = {'Metadata-Flavor': 'Google'}

    # Set the metadata request URL.
    metadata_request_url = f'{metadata_server}/computeMetadata/v1/instance/zone'

    # Get the metadata.
    metadata_response = requests.get(metadata_request_url, headers=metadata_flavor)

    # Extract the zone from the metadata.
    zone = metadata_response.text.split('/')[-1]

    # Print the zone.
    print(f'The VM is in zone {zone}.')

    return zone


myRegion = getMyRegion()
bucketName = regions[myRegion]['bucket_name']

# ==============================================

app = Flask(__name__)

app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600 # Cache timeout set to 1 hour

cache = Cache(app)

@app.errorhandler(404)
def not_found(error):
    return 'Error: This route is not defined\n', 404

@app.route('/ola')
def hello():
    return 'Hello from server', 200

@app.route('/files/<string:file>')
@cache.cached()  # Cache the result of this route
def getFile(file):

    client = storage.Client()

    # Create a bucket object for our bucket
    bucket = client.get_bucket(bucketName)
    
    # Check if file exists in the bucket

    if not bucket.blob(file).exists():
        return "File doesn't exist in the bucket\n", 404
    
    blob = bucket.blob(file)
    file_bytes = blob.download_as_bytes()
    file_stream = BytesIO(file_bytes)

    mimetype = mimetypes.guess_type(file)[0]

    if mimetype is None:
        mimetype = 'application/octet-stream'

    return send_file(file_stream, mimetype=mimetype, as_attachment=True, download_name=file)


if __name__ == '__main__':  
    #app.run(host='0.0.0.0', port=8080)
    app.run()