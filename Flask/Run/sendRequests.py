import requests
import argparse

url = "http://localhost:8080/"


def getMyIp():
    response = requests.get('https://ipinfo.io/json')
    data = response.json()
    return data['ip']


def serverRequest():
    path = "/servers"

    myIP = getMyIp()

    headers = {'X-Forwarded-For': myIP}

    response = requests.get(url + path, headers=headers)
    
    return response


def uploadRequest(filename):
    
    path = '/upload'

    headers = {
        'X-API-key': 'f977c8ba19c5baf83b457b31a676f9020c9991ee15f357e4a3f46e6140b1931a'
        }
    
    myfiles = {'file': open(filename ,'rb')}
    
    response = requests.post(url + path, headers=headers, files=myfiles)

    return response


def deleteRequest(filename):
    path = '/delete/'

    headers = {
        'X-API-key': 'f977c8ba19c5baf83b457b31a676f9020c9991ee15f357e4a3f46e6140b1931a'
        }
    
    response = requests.delete(url + path + filename, headers=headers)

    return response


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-POST', metavar='filename', type=str, help='Operation to insert file')
    parser.add_argument('-DELETE', metavar='filename', type=str, help='Operation to remove file')
    parser.add_argument('-SERVERS', action='store_true', help='Discover the nearest VMs IPs')
    args = parser.parse_args()

    # Check which operation was requested and handle accordingly
    if args.POST:
        print(f'Performing POST operation with file: {args.POST}')
        response = uploadRequest(args.POST)
        print(response.text)

    elif args.DELETE:
        print(f'Performing DELETE operation with file: {args.DELETE}')
        response = deleteRequest(args.DELETE)
        print(response.text)

    elif args.SERVERS:
        print(f'Performing SERVERS operation')
        response = serverRequest()
        print(response.text)

    else:
        print('Please provide a valid operation')



