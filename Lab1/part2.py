import socket
import ssl
import datetime
import json
from functools import reduce
from bs4 import BeautifulSoup


def clean_price(price_str):
    allowed_chars = "0123456789."
    return ''.join([char for char in price_str if char in allowed_chars])


def eliminate_repetitions(product_name, version):
    product_name = product_name + ' ' + version
    return product_name


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


def convert_to_eur(product):
    name, price, url, rating = product
    price = round((price / 19.3), 2)  # Round the price
    product = name, price, url, rating
    return product


def im_poor(product):
    _, price, _, _ = product
    if price < 15:
        return price
    return False


def send_https_request(host, port, request):
    # Create a socket and wrap it with SSL to handle HTTPS
    context = ssl.create_default_context()
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            # Send the HTTP request
            ssock.sendall(request.encode('utf-8'))

            # Receive the HTTP response (using a buffer to get a chunk of the response)
            response = b""
            while True:
                chunk = ssock.recv(4096)
                if not chunk:
                    break
                response += chunk

    return response.decode('utf-8')


# HTTP request setup
url = 'https://kawaiicat.md/jucarii'
host = 'kawaiicat.md'
port = 443
http_request = """GET /jucarii HTTP/1.1\r
Host: kawaiicat.md\r
Connection: close\r\n\r\n"""

# Send the HTTP request via TCP socket and SSL
response_html = send_https_request(host, port, http_request)

# Now, use BeautifulSoup to parse the response
soup = BeautifulSoup(response_html, "html.parser")

prod_url = ""
productDetails = []
json_ld_data = soup.find_all('script', type='application/ld+json')

# Extract data from each JSON-LD script
for script in json_ld_data:
    try:
        data = json.loads(script.string)  # Parse JSON data
        if data.get('@type') == 'ItemList':  # Check if it's the right type (ItemList)
            for item in data.get('itemListElement'):
                name = item.get('name')
                name = clean_product(name)  # Remove random product details
                price = item.get('offers', {}).get('price')
                price = clean_price(price)  # Remove non-numeric characters
                price = float(price)
                url = item.get('url')
                productList = [name, price, url]
                productDetails.append(productList)
    except (json.JSONDecodeError, AttributeError) as e:
        # Log the error and continue parsing
        print(f"Error parsing JSON or accessing attributes in script: {e}")
        continue

productLimit = 3
productDetails = productDetails[:productLimit]
print(productDetails)
for x in range(0, productLimit - 1):
    if productDetails[x][0] == productDetails[x + 1][0]:
        productDetails[x + 1][0] = eliminate_repetitions(productDetails[x + 1][0], 'v1')

    if x + 2 < productLimit and productDetails[x][0] == productDetails[x + 2][0]:
        productDetails[x + 2][0] = eliminate_repetitions(productDetails[x + 2][0], 'v2')

# Differentiates between 2 objects of the same name
for product in productDetails:
    try:
        page = send_https_request(host, port, f"GET {product[2]} HTTP/1.1\r\nHost: kawaiicat.md\r\nConnection: close\r\n\r\n")
        soup = BeautifulSoup(page, "html.parser")
        json_ld_data = soup.find_all('script', type='application/ld+json')

        for script in json_ld_data:
            try:
                json_ld_data = script.string.strip()
                json_string = json_ld_data.replace("\n", "")
                data = json.loads(json_string)
                if data.get('@type') == 'Product':
                    aggregate_rating = data.get('aggregateRating', {})
                    rating_value = aggregate_rating.get('ratingValue', 'No rating')
                    product.append(rating_value)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in product page: {e}")
                continue
    except Exception as e:
        print(f"Error fetching product page {product[2]}: {e}")
        continue

for product in productDetails:
    print(f"Product Name: {product[0]}, Price: {product[1]}, Url: {product[2]} Rating: {product[3]} ")

# checkpoint 6
convertedProducts = list(map(convert_to_eur, productDetails))
print(convertedProducts)
filteredProducts = list(filter(im_poor, convertedProducts))
print('Visualization of the filtered products:')
for product in convertedProducts:
    if product in filteredProducts:
        print(product)

totalPrice = reduce(lambda acc, product: acc + product[1], filteredProducts, 0)

final_data = {
    "filtered products": filteredProducts,
    "total price": totalPrice,
    "timestamp": datetime.datetime.utcnow().isoformat(),
}
print(final_data)
