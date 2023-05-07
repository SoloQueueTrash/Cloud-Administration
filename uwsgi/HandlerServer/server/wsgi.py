import requests
import math
import os
from google.cloud import storage

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

def geo_distance(client, ip_server):
    data_server = get_location(ip_server)

    R = 6371  # radius of the Earth in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [client[0], client[1], data_server['lat'], data_server['lon']])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return (distance, ip_server)

def geoClosest(ip_list, client):
    min = 99999999
    response_ip = ""

    data_client = get_location(client)
    coords1 = (data_client['lat'], data_client['lon'])

    for i in range(len(ip_list)):
        data = geo_distance(coords1, ip_list[i])

        if(min > int(data[0])):
            min = int(data[0])
            response_ip = data[1]

    return response_ip

def get_country(ip):
    response = requests.get(f'https://ipinfo.io/{ip}/geo' ).json()

    geo_country = response.get("country")
    return geo_country   

def application(env, start_response):
    
    # Get the client IP address from the X-Forwarded-For header
    x_forwarded_for = env.get('HTTP_X-Forwarded-For')
    x_real_ip = env.get('HTTP_X_REAL_IP')

    ip_list = ["34.175.82.31", "124.108.114.218", "156.129.83.106", "62.25.188.217"]
    closest_ip = geoClosest(ip_list, x_real_ip)
    country = get_country(x_real_ip)

    status = '200 OK'
    headers = [('Content-type', 'text/plain')]   
    response_body = "The client ip is " + x_real_ip + "\nThe closest server's IP address is " + closest_ip +" in " + country +"\n"

    start_response(status, headers)
    return [response_body]
