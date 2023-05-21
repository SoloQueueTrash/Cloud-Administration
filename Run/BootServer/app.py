from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import storage
from flask import Flask, render_template, request, jsonify
import random
import os
import requests
import math
import json
import hashlib
import datetime

# Load regions information from JSON file
file = open('regions.json')
regions = json.load(file)
file.close()

# Round robin load balancer
next_server_index = 0

# ====================================================================

def get_location(ip):
    response = requests.get(f'https://ipinfo.io/{ip}/geo' ).json()
    geo_data = {
    "ip": ip,
    "city": response.get("city"),
    "country": response.get("country"),
    "lat" : float(response.get("loc").split(',')[0]),
    "lon" : float(response.get("loc").split(',')[1])
    }

    return geo_data

def geo_distance_lat_lon(client, serverLat, serverlon):
    R = 6371  # radius of the Earth in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [client[0], client[1], serverLat, serverlon])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return (distance)

def geoClosestFromRegions(client):
    min = 99999999
    serverInfo = ""

    data_client = get_location(client)
    coords1 = (data_client['lat'], data_client['lon'])

    for region in regions:
        distance = geo_distance_lat_lon(coords1, float( regions[region]["lat"] ), float( regions[region]["lon"] ))

        if(min > int(distance)):
            min = int(distance)
            serverInfo = region
        
    return serverInfo
    
# ====================================================================

# set credentials
credentials = service_account.Credentials.from_service_account_file('credentials.json')


def getIPlist(region):

    # set the project ID
    project = 'cloudsa2023'

    # create the compute engine service client
    compute = build('compute', 'v1', credentials=credentials)

    # use the instances().list() method to list all instances in the region
    result = compute.instances().list(project=project, zone=region).execute()

    alive = []
    for instance in result['items']:
    #    print(f'Instance name: {instance["name"]}')
    #    print(f'Instance status: {instance["status"]}')
        if instance.get("status") == "RUNNING":
            #print(f'External IP address: {instance[ "networkInterfaces"][0]["accessConfigs"][0]["natIP"]}')
            alive.append(instance[ "networkInterfaces"][0]["accessConfigs"][0]["natIP"])

    global next_server_index
    num_servers = len(alive)

    if(num_servers == 0):
        return []

    # Round robin
    server_ips = [alive[(next_server_index + i) % num_servers] for i in range(num_servers)]

    # Increment the next server index and wrap around to 0 if we reach the end of the list
    next_server_index = (next_server_index + 1) % num_servers
    
    return server_ips


'''
def getIPlist(region):

    # set the project ID
    project = 'cloudsa2023'

    # create the compute engine service client
    compute = build('compute', 'v1', credentials=credentials)

    # use the instances().list() method to list all instances in the region
    result = compute.instances().list(project=project, zone=region).execute()

    # shuffle the results
    random.shuffle(result['items'])

    res = []
    # print the list of instances
    for instance in result['items']:
    #    print(f'Instance name: {instance["name"]}')
    #    print(f'Instance status: {instance["status"]}')
        if instance.get("status") == "RUNNING":
            print(f'External IP address: {instance[ "networkInterfaces"][0]["accessConfigs"][0]["natIP"]}')
            res.append(instance[ "networkInterfaces"][0]["accessConfigs"][0]["natIP"])

    return res
'''
# ====================================================================

'''
def disseminate_file(source_bucket, source_blob, filename):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')

    with open('buckets.json', 'r') as file:
        json_data = json.load(file)

    for i in range(len(json_data)):  
        print(json_data[i]['region'])      
        destination_bucket = client.get_bucket(str(json_data[i]['region']))

        # Copy the source blob to the destination bucket
        source_bucket.copy_blob(
            source_blob,
            destination_bucket,
            new_name = filename
        )

def delete_disseminated(filename):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')

    with open('buckets.json', 'r') as file:
        json_data = json.load(file)

    for i in range(len(json_data)):        
        bucket = client.get_bucket(str(json_data[i]['region']))
        blob = bucket.blob(filename)
        blob.delete()
'''

# ====================================================================

def authenticate_request():
    api_key = request.headers.get('X-API-Key')

    server_api_key = calculate_sha256("cloudadmin2223")

    if api_key == server_api_key:
        return True

    return False

def calculate_sha256(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
    return sha256_hash

# ====================================================================

# pylint: disable=C0103
app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return 'Error: This route is not defined\n', 404

@app.route('/upload/<string:file>', methods=['GET'])
def upload_file(file):
    
    if not authenticate_request():
        return jsonify({'error': 'Unauthorized'}), 401

    client = storage.Client(credentials=credentials)

    bucket = client.bucket("asc_europe-southwest1")
    blob = bucket.blob(file)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=1),
        method="PUT",
    )

    return jsonify({'message': 'URL created with success', 'url' : url})

'''
@app.route('/upload', methods=['GET'])
def upload_file():

    if not authenticate_request():
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'

    upload_file = request.files.get('file')
    content_type = upload_file.content_type
        
    client = storage.Client('cloudsa2023')
    bucket = client.get_bucket('asc_europe-southwest1')
    
    blob = bucket.blob(upload_file.filename)
    blob.upload_from_string(upload_file.read(), content_type=content_type)
    
    return jsonify({'message': 'File uploaded successfully', 'filename' : upload_file.filename})
'''

@app.route('/delete/<string:file>', methods=['DELETE'])
def delete_file(file):

    if not authenticate_request():
        return jsonify({'error': 'Unauthorized'}), 401

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')

    bucket = client.get_bucket('asc_europe-southwest1')
    
    if not bucket.blob(file).exists():
        return jsonify({'error': 'File doesn\'t exist in the bucket'}), 404
    
    blob = bucket.blob(file)
    blob.delete()
    
    #delete_disseminated(file)

    return jsonify({'message': 'File deleted successfully', 'filename' : file})


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

@app.route('/servers')
def handle_ip():
    ip_address = request.headers['X-Forwarded-For']
    myIP = ip_address.split(',')

    closestServer = geoClosestFromRegions(myIP[0])
    ipList = getIPlist(closestServer)

    return jsonify({
        'region': closestServer,
        'ips': ipList
    })

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')

