# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                adapter[field_name] = value[0].strip()
                
        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()
                
        ## Price --> convert to floar
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        ## Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0]) 
        
        ## Reviews --> convert string to number
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)

        ## Stars --> convert string to number
        stars_string = adapter.get('stars')
        split_stars_arra = stars_string.split(' ')
        stars_text_value = split_stars_arra[1].lower()
        
        if stars_text_value == 'zero':
            adapter['stars'] = 0
        elif stars_text_value == 'one':
            adapter['stars'] = 1
        elif stars_text_value == 'two':
            adapter['stars'] = 2
        elif stars_text_value == 'three':
            adapter['stars'] = 3
        elif stars_text_value == 'four':
            adapter['stars'] = 4
        elif stars_text_value == 'five':
            adapter['stars'] = 5
        
        return item

import mysql.connector

class SaveToMySQLPipeline:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='books'
        )
        
        ## Create cursor, use to execute commands
        self.cur = self.conn.cursor()
        
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                url VARCHAR(255),
                upc VARCHAR(50),
                product_type VARCHAR(50),
                price_excl_tax FLOAT,
                price_incl_tax FLOAT,
                tax FLOAT,
                availability INT,
                num_reviews INT,
                stars INT,
                category VARCHAR(50),
                description TEXT,
                price FLOAT
            )
        ''')
        
    def process_item(self, item, spider):
        self.cur.execute('''
                INSERT INTO books (
                    title,
                    url,
                    upc,
                    product_type,
                    price,
                    price_excl_tax,
                    price_incl_tax,
                    tax,
                    availability,
                    num_reviews,
                    stars,
                    category,
                    description
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )''', (
                    item['title'],
                    item['url'],
                    item['upc'],
                    item['product_type'],
                    item['price'],
                    item['price_excl_tax'],
                    item['price_incl_tax'],
                    item['tax'],
                    item['availability'],
                    item['num_reviews'],
                    item['stars'],
                    item['category'],
                    str(item['description'][0])
                )
            )
            
        ## Execute insert of data into database
        self.conn.commit()
        
        return item
    
    def close_spider(self, spider):
        
        ## Close cursor & connection to database
        self.cur.close()
        self.conn.close()