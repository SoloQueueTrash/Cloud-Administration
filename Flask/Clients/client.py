import requests
import argparse
import json
import os

url = "https://boot-server-ml5itwavqq-no.a.run.app"
baseUrl = "http://"

# get the current directory of the Python script
script_dir = os.path.dirname(os.path.abspath(__file__))

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

def getFile(filename):

    response = serverRequest()
    availableIPS = json.loads(response.text)
    print(availableIPS['ips'])

    for ip in availableIPS['ips']:
        response = requests.get(baseUrl + ip + "/files/" + filename)

        if response.status_code == 200:
            
            save_to_path = os.path.join(script_dir, filename)
            
            with open(save_to_path, "wb") as f:
                f.write(response.content)

            print('Request was successful!')
            return
        else:
            print('Request failed. Lets try another IP')

    print("We try all the ips and none of them is working!")



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-GET', metavar='filename', type=str, help='Get file from bucket')
    args = parser.parse_args()

    if args.GET:
        print(f'Performing GET operation with file: {args.GET}')
        getFile(args.GET)
        
    else:
        print('Please provide a valid operation')


