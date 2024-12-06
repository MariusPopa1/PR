import requests
from bs4 import BeautifulSoup
import json
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

# Send a request to the URL and get the page content
url = 'https://kawaiicat.md/jucarii'
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

# Find all JSON-LD schema tags in the HTML

prod_url = ""
productDetails = []
json_ld_data = soup.find_all('script', type='application/ld+json')
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


for product in productDetails:
    print(f"Product Name: {product[0]}, Price: {product[1]}, Url: {product[2]} Rating: {product[3]} ")  # Checkpoint 4


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
