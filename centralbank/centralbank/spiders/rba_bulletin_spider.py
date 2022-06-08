import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class RbaBulletinSpiderSpider(CrawlSpider):
    name = 'rba_bulletin_spider'
    allowed_domains = ['www.rba.gov.au']
    start_urls = ['http://www.rba.gov.au/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),

        # TODO don't let the link have an arbitrary number of slashes (to avoid ending up with all equations)
        # TODO note how format of pages has changed over time
        # TODO only include years from 2000 onwards
        
    )

    def parse_item(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item
