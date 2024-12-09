import requests
from bs4 import BeautifulSoup
import json
from functools import reduce
import datetime
import ssl
import socket
import xml.dom.minidom as xml

def clean_price(price_str):
    allowed_chars = "0123456789."
    return ''.join([char for char in price_str if char in allowed_chars])
# validation 3


def eliminate_repetitions(product_name, version):
    product_name = product_name + ' ' + version
    return product_name
# validation 2


def clean_product(product_name):
    result = ''
    inside_parentheses = False
    for char in product_name:
        if char == '(':
            inside_parentheses = True
        elif char == ')':
            inside_parentheses = False
        elif not inside_parentheses:
            result += char
    return result
# validation 1


def convert_to_eur(product):
    name, price, url, rating = product
    price = round((price / 19.3), 2)  #round the price
    product = name, price, url, rating
    return product


def im_poor(product):
    _, price, _, _ = product
    if price < 15:
        return price
    return False

def cleanItem(script):
    script = script.replace("4000", "")
    anomaly = script.find("description")
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
    if anomaly != -1 and normal == -1:
        script = script[:anomaly-4] + script[anomaly:]
    return script

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

def serialize_to_json(data):
    string = '{\n'
    string += '  "filtered products": [\n'
    for product in data[0]:
        string += '    {\n'
        string += f'      "name": "{product[0]}",\n'
        string += f'      "price": {product[1]},\n'
        string += f'      "url": "{product[2]}",\n'
        string += f'      "rating": "{product[3]}"\n'
        string += '    },\n'
    string = string.strip(',\n')  # Remove trailing comma for the last product
    string += '\n  ],\n'
    string += f'  "total price": {data[1]},\n'
    string += f'  "timestamp": "{data[2]}"\n'
    string += '}'
    return string


def serialize_to_xml(data):
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += '<root>\n'
    xml_str += '  <filtered_products>\n'
    for product in data[0]:
        xml_str += '    <product>\n'
        xml_str += f'      <name>{product[0]}</name>\n'
        xml_str += f'      <price>{product[1]}</price>\n'
        xml_str += f'      <url>{product[2]}</url>\n'
        xml_str += f'      <rating>{product[3]}</rating>\n'
        xml_str += '    </product>\n'
    xml_str += '  </filtered_products>\n'
    xml_str += f'  <total_price>{data[1]}</total_price>\n'
    xml_str += f'  <timestamp>{data[2]}</timestamp>\n'
    xml_str += '</root>'
    return xml_str

# Send a request to the URL and get the page content
url = 'https://kawaiicat.md/jucarii'
page = requests.get(url)
hostname = "kawaiicat.md"
path = "/jucarii"
soup = fetch_https_resource(hostname, path)

prod_url = ""
productDetails = []
json_ld_data = soup.find('script', type='application/ld+json')
# Extract data from each JSON-LD script
for script in json_ld_data:
    script = script.string
    script = cleanSoup(script)
    data = json.loads(script)  # Parse JSON data
    if data.get('@type') == 'ItemList':  # Check if it's the right type (ItemList)
        for item in data.get('itemListElement'):
            name = item.get('name')
            name = clean_product(name)  # remove random product details, the site had a lot of ex: name (60cm)
            price = item.get('offers', {}).get('price')
            price = clean_price(price)  # Remove non-numeric characters
            price = float(price)
            url = item.get('url')
            productList = [name, price, url]
            productDetails.append(productList)
            # print(f"Product Name: {productList[0]}, Price: {productList[1]}")  #Checkpoint 3

productLimit = 10
productDetails = productDetails[:productLimit]

for x in range(0, productLimit-1):
    if productDetails[x][0] == productDetails[x + 1][0]:
        productDetails[x + 1][0] = eliminate_repetitions(productDetails[x + 1][0], 'v1')

    if x + 2 < productLimit and productDetails[x][0] == productDetails[x + 2][0]:
        productDetails[x + 2][0] = eliminate_repetitions(productDetails[x + 2][0], 'v2')
# Differentiates between 2 objects of the same name

for product in productDetails:

    hostname = "kawaiicat.md"
    path = product[2][19:]
    soup = fetch_https_resource(hostname, path)

    json_ld_data = soup.find('script', type='application/ld+json')

    for script in json_ld_data:
        script = script.string
        script = cleanItem(script)
        data = json.loads(script)
        if data.get('@type') == 'Product':
            aggregate_rating = data.get('aggregateRating', {})
            rating_value = aggregate_rating.get('ratingValue', 'No rating')
            product.append(rating_value)


'''for product in productDetails:
    print(f"Product Name: {product[0]}, Price: {product[1]}, Url: {product[2]} Rating: {product[3]} ")'''  # Checkpoint 4


# checkpoint 6
convertedProducts = list(map(convert_to_eur, productDetails))

filteredProducts = list(filter(im_poor, convertedProducts))
print('Visualization of the filtered products:')

'''for product in convertedProducts:
    if product in filteredProducts:
        print(product)'''

totalPrice = reduce(lambda acc, product: acc + product[1], filteredProducts, 0)





final_data = [
    filteredProducts,
    totalPrice,
    datetime.datetime.utcnow().isoformat(),
]

# print(final_data)
json_output = serialize_to_json(final_data)
print("JSON Output:\n", json_output)

xml_output = serialize_to_xml(final_data)
print("XML Output:\n", xml_output)
json.loads(json_output)
xml.parseString(xml_output)


