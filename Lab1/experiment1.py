import json
from bs4 import BeautifulSoup
import socket
import ssl


def cleanItem(script):
    anomaly = script.find("description")
    print(anomaly)
    anomaly = script.find('\n', anomaly)
    script = script[:anomaly] + script[anomaly+1:]
    anomaly = script.find('\n', anomaly)
    script = script[:anomaly] + script[anomaly+1:]

    return script

def cleanSoup(script):
    script = script.replace("4000", "")
    script = script.replace("8000", "")
    anomaly = script.find('ku": "10866"')
    normal = script.find('"sku": "10866"')
    print(anomaly)
    if anomaly != -1 and normal == -1:
        script = script[:anomaly-4] + script[anomaly:]
    return script

# Fetch HTTPS resource using the custom function
def fetch_https_resource(hostname, path):
    # Create a TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket with SSL for secure connection
    context = ssl.create_default_context()
    secure_socket = context.wrap_socket(tcp_socket, server_hostname=hostname)

    # Connect to the server on port 443 (HTTPS)
    secure_socket.connect((hostname, 443))

    # Formulate the HTTP GET request
    http_request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"

    # Send the HTTP request
    secure_socket.sendall(http_request.encode())

    # Receive the HTTP response
    response = b""
    while True:
        data = secure_socket.recv(4096)  # Receive data in chunks
        if not data:
            break
        response += data

    # Close the secure socket
    secure_socket.close()

    # Extract the body of the HTTP response
    response_text = response.decode()
    headers, body = response_text.split("\r\n\r\n", 1)

    # Parse and return the response body with BeautifulSoup
    return BeautifulSoup(body, "html.parser")


# Hostname and path for the target URL
hostname = 'kawaiicat.md'
path = '/jucarii'

# Fetch and parse the page
soup = fetch_https_resource(hostname, path)

prod_url = ""
productDetails = []

# Extract JSON-LD data
json_ld_data = soup.find('script', type='application/ld+json')
for script in json_ld_data:
    script = script.string
    script = cleanSoup(script)
    print(script)
    data = json.loads(script)
