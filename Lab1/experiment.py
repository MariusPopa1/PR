import json
from bs4 import BeautifulSoup


def cleanString(script):
    script = script.replace("4000", "")
    script = script.replace("8000", "")

    new_string = ""
    quotation_counter = 0
    line = ""
    for i, char in enumerate(script):
        if char == '\n':
            # Check if the next and previous characters are valid (letters, numbers, or quotes)
            if (i - 1 >= 0 and script[i - 1] == '"') or (i + 1 < len(script) and script[i + 1] == '"'):
                continue

            # Handle open/close quotations for strings
            if (quotation_counter % 2) == 1:
                line += '"'

            # Add newline to the line


            # Check if the line contains any of the relevant JSON characters
            if '{' not in line and '}' not in line and '[' not in line and ']' not in line and ':' not in line:
                line = ""  # Clear line if no JSON structure is present
            if (':' in line) and (',' not in line) and ('{' not in line) and ('[' not in line)and ('}' not in line):
                line += ','
            # Append to the new string if the line is not empty
            line += '\n'
            if line:
                new_string += line

            # Reset line and quotation_counter
            line = ""
            quotation_counter = 0
        else:
            # Add the character to the line
            line += char
            # Track quotation marks
            if char == '"':
                quotation_counter += 1

    # Final check to add any remaining content in line (if necessary)
    if line:
        new_string += line

    script = new_string
    return script
# Fetch HTTPS resource using the custom function
def fetch_https_resource(hostname, path):
    """
    Fetches an HTTPS resource and returns the parsed HTML content.

    Args:
        hostname (str): The domain name of the server (e.g., 'kawaiicat.md').
        path (str): The path to the resource (e.g., '/jucarii/jucarie-acula-s-1').

    Returns:
        BeautifulSoup: Parsed HTML content of the response body.
    """
    import socket
    import ssl

    try:
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

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Hostname and path for the target URL
hostname = 'kawaiicat.md'
path = '/jucarii/jucarie-acula-s-1'

# Fetch and parse the page
soup = fetch_https_resource(hostname, path)

prod_url = ""
productDetails = []

    # Extract JSON-LD data
json_ld_data = soup.find('script', type='application/ld+json')
for script in json_ld_data:
    script = script.string
    script = cleanString(script)
    print(script)
    data = json.loads(script)



