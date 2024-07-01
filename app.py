from pony.orm import Database, Required, Optional, Set, db_session, select
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import requests
import string

URL = "https://www.xn--80ai9an.xn--p1ai"
safe_chars = f"-_.() {string.ascii_letters}{string.digits}"

# Инициализация базы данных
db = Database()

# Определение сущностей
class City(db.Entity):
    _table_ = 'product_city'
    name = Required(str)
    shops = Set('Shop')

class Shop(db.Entity):
    _table_ = 'product_shop'
    name = Required(str)
    city_id = Required(City)
    website = Optional(str)
    address = Optional(str)
    products = Set('Product')

class Category(db.Entity):
    _table_ = 'product_category'
    name = Required(str)
    products = Set('Product')

class Product(db.Entity):
    _table_ = 'product_product'
    name = Required(str)
    number = Required(int)
    category_id = Required(Category)
    shop_id = Required(Shop)
    price = Optional(str)
    product_link = Optional(str)
    image = Optional(str)

# Привязываем модели к базе данных
db.bind(provider='sqlite', filename='db.sqlite3', create_db=True)

# Генерируем схему базы данных
db.generate_mapping(create_tables=True)

# Функция для обработки товаров на странице АРДУ.РФ и добавления их в базу данных
@db_session
def process_products_1(page_source, shop_obj, website=URL):
    soup = BeautifulSoup(page_source, 'html.parser')
    category = soup.find('h3', {'id': 'cat-title'}).text
    cat_obj = Category.select(lambda c: c.name==category).first()
    if not cat_obj:
        cat_obj = Category(name=category)

    product_divs = soup.find_all('div', {'field': 'link'})

    if not product_divs:
        return

    product_number = 1  # Первый номер продукта
    for product_div in product_divs:
        product_name = product_div.text.strip()
        if not product_name:
            continue
        exists_tag = product_div.find_next_sibling('span', {'field': 'exists'})
        prod_obj = Product.select(lambda p: p.name==product_name and p.shop_id==shop_obj and p.category_id==cat_obj).first()
        if prod_obj and not (exists_tag and "Товар в наличии" in exists_tag.text):
            prod_obj.delete()

        elif exists_tag and "Товар в наличии" in exists_tag.text:
            image_div = product_div.find_previous('div', {'field': 'picture'})
            media_path = ''
            if image_div:
                image_link = website+image_div.find_next('img').get('src')
                media_path = f'{product_name}.jpg'
                media_path = 'media/' + media_path.translate(str.maketrans('', '', ''.join(set(string.punctuation) - set(safe_chars))))
                with open(media_path, 'wb') as f:
                    f.write(requests.get(image_link).content)
                image = Image.open(media_path)
                image = image.resize((200,200))
                image.save(media_path)
            price_span = product_div.find_next('span', {'field': 'price'})
            if price_span:
                price = price_span.text.strip()
            else:
                price = "Цена не указана."

            # Извлекаем ссылку на товар
            product_link_element = product_div.find('a')
            if product_link_element:
                product_link = product_link_element['href']
                full_product_link = website + product_link

                # Добавляем товар в базу данных
                if not prod_obj:
                    Product(name=product_name, number=product_number, category_id = cat_obj, shop_id=shop_obj, price=price, product_link=full_product_link, image=media_path)
                else:
                    prod_obj.number = product_number
                    prod_obj.price = price
                    prod_obj.product_link = full_product_link
                    prod_obj.image = media_path
            else:
                # Добавляем товар в базу данных без ссылки
                if not prod_obj:
                    Product(name=product_name, number=product_number, category_id=cat_obj, shop_id=shop_obj, price=price, image=media_path)
                else:
                    prod.obj.number = product_number
                    prod_obj.price = price
                    prod_obj.image = media_path

            product_number += 1  # Увеличиваем номер продукта

# Функция для обработки товаров на странице Радиодетали на Петропавловской и добавления их в базу данных
@db_session
def process_products_2(page_source, shop_obj, website):
    soup = BeautifulSoup(page_source, 'html.parser')
    category = "Другое"
    cat_obj = Category.select(lambda c: c.name==category).first()
    if not cat_obj:
        cat_obj = Category(name=category)

    product_divs = soup.find_all('div', {'class': 'blockdet'})
    if not product_divs:
        return


    product_number = 1
    for product_div in product_divs:
        product_name = product_div.find_next('div', {'class': 'namedet'}).text

        if not product_name:
            continue

        exists_tag = product_div.find_next('span', {'class': 'qsc2'})
        prod_obj = Product.select(lambda p: p.name==product_name and p.shop_id==shop_obj and p.category_id==cat_obj).first()
        if prod_obj and not (exists_tag and "В наличии" in exists_tag.text):
            prod_obj.delete()
        elif exists_tag and "В наличии" in exists_tag.text:
            image_div = product_div.find_next('div', {'class': 'imgdet'})
            media_path = ''
            if image_div:
                image_link = website+image_div.find_next('img').get('src').lstrip('.')
                media_path = f'{product_name}.jpg'
                media_path = 'media/' + media_path.translate(str.maketrans('', '', ''.join(set(string.punctuation) - set(safe_chars))))
                with open(media_path, 'wb') as f:
                    f.write(requests.get(image_link).content)
                image = Image.open(media_path)
                image = image.resize((200,200))
                image.save(media_path)

            price_span = product_div.find_next('table').find_next('td')
            if price_span:
                price = price_span.text.split(',')[0].strip().replace(' ', '')
            else:
                price = "Цена не указана."

            product_link = website + '/general/' + product_div.find_next('a')['href']

            # Добавляем товар в базу данных
            if not prod_obj:
                Product(name=product_name, number=product_number, category_id = cat_obj, shop_id=shop_obj, price=price, product_link=product_link, image=media_path)
            else:
                prod_obj.number = product_number
                prod_obj.price = price
                prod_obj.product_link = product_link
                prod_obj.image = media_path
        product_number += 1


# Настройка веб-драйвера Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL магазина в городе Перми
urls_1 = [
    "https://www.xn--80ai9an.xn--p1ai/shop/550",
    "https://www.xn--80ai9an.xn--p1ai/shop/549",
    "https://www.xn--80ai9an.xn--p1ai/shop/467",
    "https://www.xn--80ai9an.xn--p1ai/shop/552"
]

urls_2 = [
        "https://www.radiodetali.perm.ru/general/subcat.php?PG=1&LP=1&kID=100000146&gr=100000145",
        "https://www.radiodetali.perm.ru/general/subcat.php?PG=2&LP=1&kID=100000146&gr=100000145"
]
# Запускаем сеанс браузера и обрабатываем товары на каждой странице


#Словарь с метаинформацией о магазинах
cities = ("Пермь",)
shops = {cities[0]:[
 ("Арду.рф", URL, "Пермь, ул. Пушкина, 17", urls_1, process_products_1),
 ("Радиодетали на Петропавловской", "https://www.radiodetali.perm.ru", "г.Пермь, ул.Петропавловская, 15", urls_2, process_products_2),
 ]}
with db_session:
    for city in cities:
        city_obj = City.select(lambda c: c.name == city).first()
        if not city_obj:
            city_obj = City(name=city)

        for shop in shops.get(city):
            name, website, address, links, parser = shop
            shop_obj = Shop.select(lambda s: s.city_id==city_obj and s.name==name and s.address==address).first()
            if not shop_obj:
                shop_obj = Shop(name=name, city_id=city_obj, website=website, address=address)

            for url in links:
                driver.get(url)
                # Даем время на загрузку динамического контента
                driver.refresh()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div')))
                print(url)
                #Парсим данные
                parser(driver.page_source, shop_obj, website)

# Завершаем сеанс браузера
driver.quit()
