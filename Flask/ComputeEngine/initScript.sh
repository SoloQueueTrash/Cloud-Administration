#!/bin/bash

# Install NGINX
apt-get update
apt-get install nginx -y

cat > requirements.txt << EOF
Flask==2.2.2
Flask-Caching==2.0.2 
requests==2.28.1
gunicorn==20.1.0
ptvsd==4.3.2 # Required for debugging.
google-auth>=1.16.0,<2dev
google-api-python-client==2.1.0
google-cloud-storage==2.9.0
EOF

# Install Python dependencies
apt-get install python3-pip -y
pip3 install -r requirements.txt

# Install Flask app
mkdir /home/server
cd /home/server

cat > regions.json << EOF
{
  "us-central1-a": {"lat": "41.2619", "lon": "-95.8608", "bucket_name": "asc_us-central1"},
  "us-west1-a": {"lat": "45.5946", "lon": "-121.1787", "bucket_name": "asc_us-west1"},
  "us-east1-b": {"lat": "32.9336", "lon": "-80.1026", "bucket_name": "asc_us-east1"},
  "southamerica-east1-a": {"lat": "-23.5475", "lon": "-46.6361", "bucket_name": "asc_southamerica-east1"},
  "europe-southwest1-a": {"lat": "40.4165", "lon": "-3.7026", "bucket_name": "asc_europe-southwest1"},
  "europe-west2-a": {"lat": "51.5085", "lon": "-0.1257", "bucket_name": "asc_europe-west2"},
  "europe-west3-a": {"lat": "50.1155", "lon": "8.6842", "bucket_name": "asc_europe-west3"},
  "australia-southeast1-a": {"lat": "-33.8678", "lon": "151.2073", "bucket_name": "asc_australia-southeast1"},
  "asia-northeast1-a": {"lat": "35.6940", "lon": "139.7536", "bucket_name": "asc_asia-northeast1"},
  "asia-south1-a": {"lat": "19.0728", "lon": "72.8826, ", "bucket_name": "asc_asia-south1"}
}
EOF

cat > server.py << EOF
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
EOF

rm /etc/nginx/nginx.conf
touch /etc/nginx/nginx.conf

cat > /etc/nginx/nginx.conf << EOF
user www-data;

worker_processes auto;

pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
        # Number of simultaneously connections per process
        worker_connections 1024;
}

http {
        server {
                listen 80;
                server_name example.com;

                #proxy_set_header X-Real-IP \$remote_addr;
                #proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;

                location / {
                        proxy_pass http://127.0.0.1:8000/;
                        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto \$scheme;
                        proxy_set_header X-Forwarded-Host \$host;
                        proxy_set_header X-Forwarded-Prefix /;
                }

#                location /api {
#                        add_header Content-Type "application/json";
#                        return 200 '{"message": "Hello, world!"}';
#                }

#                location /test {
#                        default_type text/html;
#                        return 200 "<!DOCTYPE html><h2>gangnam style!</h2>\n";
#                }

        }
        ##
        # Basic Settings
        ##

        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # Logging Settings
        ##

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

}
EOF

nginx -t
systemctl restart nginx

# Start Gunicorn
gunicorn server:app

# Start Flask app 
#python3 server.py