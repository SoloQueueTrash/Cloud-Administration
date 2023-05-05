import os
from google.cloud import storage

def getFile(bucket_file):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'credentials.json'
    client = storage.Client('cloudsa2023')
    # Create a bucket object for our bucket
    bucket = client.get_bucket('eu_asc_project')
    # Check if file exists in the bucket
    if not bucket.blob(bucket_file).exists():
        #raise ValueError(f"File {bucket_file} does not exist in the bucket")
        raise ValueError("File " + bucket_file + " does not exist in the bucket\n")
    
# Create a blob object from the filepath
    blob = bucket.blob(bucket_file)
    file_bytes = blob.download_as_bytes()
    return file_bytes

def application(env, start_response):
    path = env.get('PATH_INFO', '')
    file = os.path.basename(path)
    if not file:
        status = '400 Bad Request'
        headers = [('Content-type', 'text/plain')]
        response_body = "No file specified\n"
    else:
        try:
            response_body = getFile(file)
            status = '200 OK'
            #headers = [('Content-type', 'application/octet-stream'), ('Content-Disposition', f'attachment; filename={file}'), ('Content-Length', str(len(response_body)))]
            headers = [('Content-type', 'application/octet-stream'), ('Content-Disposition', 'attachment; filename={}'.format(file)), ('Content-Length', str(len(response_body)))]

        except ValueError as e:
            status = '404 Not Found'
            response_body = str(e)
            headers = [('Content-type', 'text/plain')]
    
    start_response(status, headers)
    return [response_body]