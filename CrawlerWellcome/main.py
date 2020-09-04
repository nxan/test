# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from bs4 import BeautifulSoup
import urllib3
import urllib.request
from requests_html import HTMLSession
import psycopg2
from psycopg2.extras import RealDictCursor

class Banner:
    def __init__(self, title, src):
        self.title = title
        self.src = src

class Product:
    def __init__(self, brand, product_name, description, price, link, image_name):
        self.brand = brand
        self.product_name = product_name
        self.description = description
        self.price = price
        self.link = link
        self.image_name = image_name

class Store:
    def __init__(self, store_name, address, telephone, opening_hours):
        self.store_name = store_name
        self.address = address
        self.telephone = telephone
        self.opening_hours = opening_hours

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

con = psycopg2.connect(database="WellCome", user="postgres", password="kieu", host="127.0.0.1", port="5432")
print("Database opened successfully")

list_banner = []
list_link_item = []
list_products = []; product_new = []; product_old = []; list_product_name = []
list_stores = []

##---------------------------- CRUD Banner ----------------------------###

def getBannerFromDatabase():
    cur = con.cursor(cursor_factory=RealDictCursor)
    postgres_select_query = "SELECT title FROM banner"
    cur.execute(postgres_select_query)
    result = [item['title'] for item in cur.fetchall()]
    return result

def saveBanner(title, src):
    cur = con.cursor()
    postgres_insert_query = "INSERT INTO banner(title, src, enable) VALUES (%s, %s, %s)"
    record_to_insert = (title, src, True)
    cur.execute(postgres_insert_query, record_to_insert)
    con.commit()
    print("Record inserted successfully")
    return

def updateBanner(title, enable):
    cur = con.cursor()
    postgres_update_query = "UPDATE banner SET enable = %s WHERE title = %s"
    record_to_insert = (enable, title)
    cur.execute(postgres_update_query, record_to_insert)
    con.commit()
    print("Update successfully")
    return

##---------------------------- CRUD Store ----------------------------###

def getStoreFromDatabase():
    cur = con.cursor(cursor_factory=RealDictCursor)
    postgres_select_query = "SELECT store_name FROM store"
    cur.execute(postgres_select_query)
    result = [item['store_name'] for item in cur.fetchall()]
    return result

def saveStore(store_name, address, telephone, opening_hours, price, link):
    cur = con.cursor()
    postgres_insert_query = "INSERT INTO store(store_name, address, telephone, opening_hours, price, link, enable) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    record_to_insert = (store_name, address, telephone, opening_hours, price, link, True)
    cur.execute(postgres_insert_query, record_to_insert)
    con.commit()
    print("Record inserted successfully")
    return

def updateStore(store_name, enable):
    cur = con.cursor()
    postgres_update_query = "UPDATE store SET enable = %s WHERE store_name = %s"
    record_to_insert = (enable, store_name)
    cur.execute(postgres_update_query, record_to_insert)
    con.commit()
    print("Update successfully")
    return

##---------------------------- CRUD Product ----------------------------###

def getProductFromDatabase():
    cur = con.cursor(cursor_factory=RealDictCursor)
    postgres_select_query = "SELECT product_name FROM product"
    cur.execute(postgres_select_query)
    result = [item['product_name'] for item in cur.fetchall()]
    return result

def saveProduct(brand, product_name, description, price, link, image_name):
    cur = con.cursor()
    postgres_insert_query = "INSERT INTO product(brand, product_name, description, price, link, image_name, enable) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    record_to_insert = (brand, product_name, description, price, link, image_name, True)
    cur.execute(postgres_insert_query, record_to_insert)
    con.commit()
    print("Record inserted successfully")
    return

def updateProduct(product_name, enable):
    cur = con.cursor()
    postgres_update_query = "UPDATE product SET enable = %s WHERE product_name = %s"
    record_to_insert = (enable, product_name)
    cur.execute(postgres_update_query, record_to_insert)
    con.commit()
    print("Update successfully")
    return

def disableProduct():
    cur = con.cursor()
    postgres_update_query = "UPDATE product SET enable = False"
    cur.execute(postgres_update_query)
    con.commit()
    print("Disable Product")
    return

##---------------------------- Crawler Banner ----------------------------###

def crawlBanner():
    list_banner_title = []
    list_banner_new_edit = []
    banner_old = []
    session = HTMLSession()
    resp = session.get("https://www.wellcome.com.hk/wd2shop/en/html/index.html")
    resp.html.render()
    html = resp.html.html
    page_soup = BeautifulSoup(html, 'html.parser')

    list_tag_li = page_soup.findAll('li', class_='slick-slide')
    for value in list_tag_li:
        if value.find('img')['title'] not in list_banner_title:
            list_banner_title.append(value.find('img')['title'])
            list_banner.append(Banner(value.find('img')['title'], value.find('img')['src']))
    session.close()
    print(len(list_banner))

    banner_new = [x for x in list_banner_title if x not in getBannerFromDatabase()]
    banner_old = [x for x in getBannerFromDatabase() if x not in list_banner_title]

    if len(banner_new) != 0:
        for i in list_banner:
            for j in banner_new:
                if i.title == j:
                    list_banner_new_edit.append(i)

    if len(list_banner_new_edit) != 0:
        for value in list_banner_new_edit:
            saveBanner(title=value.title, src=value.src)
        for value in banner_old:
            updateBanner(enable=False, title=value)

    if len(getBannerFromDatabase()) == 0:
        for value in list_banner:
            saveBanner(title=value.title, src=value.src)
    return

##---------------------------- Crawler Product ----------------------------###

def crawlListLinkProduct():
    session = HTMLSession()
    resp = session.get("https://www.wellcome.com.hk/wd2shop/html/promotions/BOGO_theme4.html#/hs_dept_id=804")
    resp.html.render()
    html = resp.html.html
    page_soup = BeautifulSoup(html, 'html.parser')

    if page_soup.find('div', class_='comingSoon empty') is None:
        list_items = page_soup.find('div', class_='items clearfix').findAll('div', class_='item')
        for value in list_items:
            list_link_item.append("https://www.wellcome.com.hk" + value.find('span', class_='brand').find('a')['href'])
    else:
        disableProduct()
        print("Product not found...")
    session.close()

    return

def crawlProduct( link_product ):
    session = HTMLSession()
    description = []; brand = ""; product_name = ""; product_item = ""; image_name = ""
    list_description = []

    resp = session.get(link_product)
    resp.html.render()
    html = resp.html.html
    page_soup = BeautifulSoup(html, 'html.parser')

    product_item = page_soup.find('div', class_='productItem')
    product_name = product_item.find('span', class_='desc').text + " " + product_item.find('span', class_='weight').text
    product_price = product_item.find('span', class_='price').text
    image_name = product_item.find('img')['title']
    link_image = product_item.find('img')['src']
    list_product_name.append(product_name)

    if product_item.find('span', class_='brand') is not None:
        brand = product_item.find('span', class_='brand').text

    if product_item.find('ul', class_='clearfix') is not None:
        list_description = product_item.find('ul', class_='clearfix').findAll('li')
        for value in list_description:
            description.append(value.text)

    urllib.request.urlretrieve("https://www.wellcome.com.hk" + link_image, image_name + ".jpg")

    product = Product(brand, product_name, description, product_price, link_product, image_name)
    list_products.append(product)

    print("Product Name: " + product.product_name)
    print("Brand: " + product.brand)
    print("Description: ")
    for value in product.description:
        print("- " + value)
    print("Price: " + product.price)
    print("Link: " + product.link)
    print("Image Name: " + product.image_name)
    print("=======================")
    session.close()

    saveProduct(brand = product.brand, product_name = product.product_name, description = product.description, price = product.price,
                link = product.link, image_name= product.image_name)

    return

crawlProduct(link_product="https://www.wellcome.com.hk/wd2shop/en/html/shop/detail.html?bj_pdt_id=103698")

def crawlListProduct():
    list_product_new_edit = []

    crawlListLinkProduct()
    for value in list_link_item:
        crawlProduct(link_product = value)

    product_new = [x for x in list_product_name if x not in getProductFromDatabase()]
    product_old = [x for x in getProductFromDatabase() if x not in list_product_name]

    if len(product_new) != 0:
        for i in list_products:
            for j in product_new:
                if i.product_name == j:
                    list_product_new_edit.append(i)

    if len(list_product_new_edit) != 0:
        for value in list_product_new_edit:
            saveProduct(brand = value.brand, product_name = value.product_name, description = value.description, price = value.price, link = value.link, image_name = value.image_name)
        for value in product_old:
            updateProduct(enable=False, product_name=value)

    if len(getProductFromDatabase()) == 0:
        for value in list_products:
            saveProduct(brand = value.brand, product_name = value.product_name, description = value.description, price = value.price, link = value.link, image_name = value.image_name)
    return

##---------------------------- Crawler Store ----------------------------###

def crawlListSore():
    list_store_name = []
    list_store_new_edit = []

    session = HTMLSession()
    resp = session.get("https://www.wellcome.com.hk/wd2shop/en/html/customer-services/store-locator.html")
    resp.html.render()
    html = resp.html.html
    page_soup = BeautifulSoup(html, 'html.parser')
    store_item = page_soup.findAll('dl', class_='locatorBody')
    for value in store_item:
        list_store_name.append(value.find('dd', class_='store').text)
        list_stores.append(Store(value.find('dd', class_='store').text, value.find('dd', class_='address').text,
                           value.find('dd', class_='telephone').text, value.find('dd', class_='openingHours').text))
    print(len(list_stores))
    session.close()

    store_new = [x for x in list_store_name if x not in getStoreFromDatabase()]
    store_old = [x for x in getStoreFromDatabase() if x not in list_store_name]

    print(store_new)
    print(store_old)

    if len(store_new) != 0:
        for i in list_stores:
            for j in store_new:
                if i.store_name == j:
                    list_store_new_edit.append(i)

    if len(list_store_new_edit) != 0:
        for value in list_store_new_edit:
            saveStore(store_name = value.store_name, address = value.address, telephone = value.telephone, opening_hours = value.opening_hours)
        for value in store_old:
            updateStore(enable=False, store_name=value)

    if len(getStoreFromDatabase()) == 0:
        for value in list_stores:
            saveStore(store_name = value.store_name, address = value.address, telephone = value.telephone, opening_hours = value.opening_hours)
    return

# crawlBanner()
# crawlListSore()
# crawlListProduct()
# print(len(list_products))

con.close()
