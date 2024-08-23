# Cloud Systems Administration Project

## Introduction

The project aims to create a decentralized service using Google Cloud tools to deliver content globally with low latency through a Content Delivery Network (CDN).

## Architecture

The architecture is divided into two main stages:

1. **Requesting Server IPs**: The client requests a list of IPs for servers closest to their location and makes content requests until a response is received. We divided the world into 10 regions, each with at least one Region Server.

2. **Content Delivery**: After obtaining the server IPs, the client interacts with these servers to request the content.

### Boot Server

The Boot Server is implemented using Google Cloud Run with a Docker image running a Flask server in Python. Its functions include:

1. **Returning Closest Server IPs**: Queries Google Cloud for active VMs and returns a list of IPs, with load balancing using Round Robin.

   ```python
   result = compute.instances().list(project=project, zone=region).execute()
   alive = [instance["networkInterfaces"][0]["accessConfigs"][0]["natIP"] for instance in result['items'] if instance.get("status") == "RUNNING"]
2. Managing Content: Generates a signed URL for uploading content to the main bucket, valid for 1 minute. For deleting content, the server directly removes files from the bucket. HTTPS is used for secure communication.

```python
bucket = client.bucket("asc_europe-southwest1")
blob = bucket.blob(file)
url = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=1), method="PUT")
```

## Region Server
Each of the 10 regions has at least one Region Server. These are e2-micro VMs running a Flask application to serve files. Production readiness is ensured with Gunicorn and NGINX. A caching mechanism is used to store content for 1 hour. Auto-scaling is based on CPU usage, triggered when average usage exceeds 80%. HTTPS with self-signed certificates is used for secure connections.

```bash

openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -signkey server.key -out server.crt
```

## NGINX configuration:

```bash

server {
    listen 443 ssl;
    server_name 34.175.243.40;
    ssl_certificate /etc/nginx/server.crt;
    ssl_certificate_key /etc/nginx/server.key;
    ...
}
```

## Buckets
Buckets store files and are accessed by Region Servers. Permissions are set, and a JSON key is used for access. Changes in the main bucket are propagated to other buckets using Google Cloud Functions.

## Costs

### Google Storage

#### Price per Invocation

| Invocations/Month | US$/Million |
|-------------------|-------------|
| First 2 Million   | Free        |
| After 2 Million   | $0.40       |

#### Bucket Costs

| City/State    | Region             | US$ (GB/Month) |
|---------------|---------------------|----------------|
| Iowa          | us-central1         | $0.020         |
| São Paulo     | southamerica-east1  | $0.035         |
| Frankfurt     | europe-west3        | $0.023         |
| Madrid        | europe-southwest1   | $0.023         |
| Sydney        | australia-southeast1| $0.023         |
| South Carolina| us-east1            | $0.020         |
| Oregon        | us-west1            | $0.020         |
| London        | europe-west2        | $0.023         |
| Mumbai        | asia-south1         | $0.023         |

### Virtual Machines

We used 10 VMs, each in different locations, with scaling up to 10 VMs per region. Each VM has the following specs:

| Name      | Virtual CPUs | Memory | Price/Month | Location |
|-----------|--------------|--------|-------------|----------|
| e2-micro  | 2            | 1GB    | $7.88       | Madrid   |

### Google Cloud Run

Cloud Run was chosen for its scalability and cost efficiency, charging only for actual usage. It handles VM scaling, load balancing, and request routing.

### Cost Estimate

Assuming high load, with an average of 9 VMs per region:

- **VM Costs**: 9 VMs x 9 regions x $7.88 = $638.28
- **Storage Costs**: 10 TB/month x $0.023 = $230

**Total estimated cost**: $638.28 (VMs) + $230 (Storage) = $868.28
