import scrapy


class AnimeSpider(scrapy.Spider):
    name = "animespider"
    allowed_domains = ["monoschinos2.com"]
    start_urls = ["https://monoschinos2.com"]

    def parse(self, response):
            anime_links = response.css('a[title][href*="ver"]')
            for link in anime_links:
                href = link.attrib['href']
                title = link.css('.animetitles ::text').get()
                
                yield {
                    'title': title,
                    'link': href
                }

