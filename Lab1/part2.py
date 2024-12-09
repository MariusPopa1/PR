import requests
from bs4 import BeautifulSoup
import json
import xml.dom.minidom as xml
from functools import reduce
import datetime


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


# Serialize final data to JSON format


# Send a request to the URL and get the page content
url = 'https://kawaiicat.md/jucarii'
page = requests.get(url)

soup = BeautifulSoup(page.text, "html.parser")

prod_url = ""
productDetails = []
json_ld_data = soup.find('script', type='application/ld+json')
# Extract data from each JSON-LD script
for script in json_ld_data:
    data = json.loads(script.string)  # Parse JSON data
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
    page = requests.get(product[2])  # Visit the product page URL
    soup = BeautifulSoup(page.text, "html.parser")
    json_ld_data = soup.find_all('script', type='application/ld+json')

    for script in json_ld_data:
        json_ld_data = script.string.strip()
        json_string = json_ld_data.replace("\n", "")
        data = json.loads(json_string)
        if data.get('@type') == 'Product':
            aggregate_rating = data.get('aggregateRating', {})
            rating_value = aggregate_rating.get('ratingValue', 'No rating')
            product.append(rating_value)


'''
for product in productDetails:
    print(f"Product Name: {product[0]}, Price: {product[1]}, Url: {product[2]} Rating: {product[3]} ")  # Checkpoint 4\

'''

# checkpoint 6
convertedProducts = list(map(convert_to_eur, productDetails))

filteredProducts = list(filter(im_poor, convertedProducts))

'''
print('Visualization of the filtered products:')
for product in convertedProducts:
    if product in filteredProducts:
        print(product, '\n')
'''
totalPrice = reduce(lambda acc, product: acc + product[1], filteredProducts, 0)

final_data = [
    filteredProducts,
    totalPrice,
    datetime.datetime.utcnow().isoformat(),
]


json_output = serialize_to_json(final_data)
print("JSON Output:\n", json_output)

xml_output = serialize_to_xml(final_data)
print("XML Output:\n", xml_output)
json.loads(json_output)
xml.parseString(xml_output)

