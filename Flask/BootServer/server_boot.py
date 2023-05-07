import requests
import math
from flask import Flask, request, jsonify
import hashlib
from google.cloud import storage
import os

app = Flask(__name__)

ip_list = ["34.175.82.31", "124.108.114.218", "156.129.83.106", "62.25.188.217"]

@app.errorhandler(404)
def not_found(error):
    return 'Error: This route is not defined\n', 404

@app.route('/upload', methods=['POST'])
def upload_file():

    if not authenticate_request():
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')
    bucket = client.get_bucket('eu_asc_project')
    
    filename = file.filename

    blob = bucket.blob(filename)

    blob.upload_from_filename(filename)
    
    return jsonify({'message': 'File uploaded successfully', 'filename' : filename})

@app.route('/delete/<string:file>', methods=['DELETE'])
def delete_file(file):

    if not authenticate_request():
        return jsonify({'error': 'Unauthorized'}), 401

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')
    bucket = client.get_bucket('eu_asc_project')
    
    if not bucket.blob(file).exists():
        return jsonify({'error': 'File doesn\'t exist in the bucket'}), 404
    
    blob = bucket.blob(file)
    blob.delete()
    
    return jsonify({'message': 'File deleted successfully', 'filename' : file})

@app.route('/servers')
def handle_ip():
    client_ip = request.remote_addr
    closest_ip, country = closest_server(ip_list, client_ip)
    return jsonify({'client_ip': client_ip, 'server' : closest_ip , 'country' : country})

def get_location(ip):
    response = requests.get('https://ipinfo.io/'+ip+'/geo' ).json()
    print(response)
    geo_data = {
        "ip": ip,
        "city": response.get("city"),
        "country": response.get("country"),
        "lat" : float(response.get("loc").split(',')[0]),
        "lon" : float(response.get("loc").split(',')[1])
    }
    return geo_data

def geo_distance(client, ip_server):
    data_server = get_location(ip_server)

    R = 6371  # radius of the Earth in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [client[0], client[1], data_server['lat'], data_server['lon']])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return (distance, ip_server, data_server['country'])

def closest_server(ip_list, client):
    min = 999999
    response_ip = ""

    data_client = get_location(client)
    coords1 = (data_client['lat'], data_client['lon'])
    location = ""
    for i in range(len(ip_list)):
        data = geo_distance(coords1, ip_list[i])

        if(min > int(data[0])):
            min = int(data[0])
            response_ip = data[1]
            location = data[2]

    return (response_ip, location)

def authenticate_request():
    api_key = request.headers.get('X-API-Key')

    server_api_key = calculate_sha256("cloudadmin2223")

    if api_key == server_api_key:
        return True

    return False

def calculate_sha256(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
    return sha256_hash

if __name__ == '__main__':
    # Generate a self-signed certificate
    # import ssl
    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context.load_cert_chain('certificate.pem', 'private_key.pem')

    # app.run(host='0.0.0.0', port=8000, ssl_context=context)
    app.run(host='0.0.0.0', port=8000)