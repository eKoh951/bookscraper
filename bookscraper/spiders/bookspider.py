import scrapy
from urllib.parse import urlencode
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com", "proxy.scrapeops.io"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        'FEEDS': {
            'booksdata.json': {
                'format': 'json',
                'overwrite': True
            },
        }
    }
    
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], self.parse)

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()

            if relative_url is not None:
                if 'catalogue/' in relative_url:
                    book_url = 'https://books.toscrape.com/' + relative_url
                else:
                    book_url = 'https://books.toscrape.com/catalogue/' + relative_url

                yield scrapy.Request(book_url, callback=self.parse_book_page)

        next_page = response.css('li.next a ::attr(href)').get()

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        table_rows = response.css('table tr')
        book_item = BookItem()

        book_item['url'] = response.url,
        book_item['title'] = response.css('.product_main h1::text').get(),
        book_item['upc'] = table_rows[0].css('td ::text').get(),
        book_item['product_type'] = table_rows[1].css('td ::text').get(),
        book_item['price_excl_tax'] = table_rows[2].css('td ::text').get(),
        book_item['price_incl_tax'] = table_rows[3].css('td ::text').get(),
        book_item['tax'] = table_rows[4].css('td ::text').get(),
        book_item['availability'] = table_rows[5].css('td ::text').get(),
        book_item['num_reviews'] = table_rows[6].css('td ::text').get(),
        book_item['stars'] = response.css('p.star-rating ::attr(class)').get(),
        book_item['category'] = response.xpath(
            '/html/body/div/div/ul/li[3]/a/text()').get(),
        book_item['description'] = response.xpath(
            '/html/body/div/div/div[2]/div[2]/article/p/text()').get(),
        book_item['price'] = response.css('p.price_color ::text').get(),

        yield book_item
