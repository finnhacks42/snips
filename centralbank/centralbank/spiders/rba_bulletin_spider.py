import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from pathlib import Path
import hashlib


class RbaBulletinSpiderSpider(CrawlSpider):
    name = 'rba_bulletin_spider'
    allowed_domains = ['www.rba.gov.au']
    start_urls = ['https://www.rba.gov.au/publications/bulletin']
    htmldir = Path('/home/finn/dev/devday/data/rba_bulletin_html')

    rules = (
        Rule(LinkExtractor(
            allow=(r'https:\/\/www.rba.gov.au\/publications\/bulletin\/20\d{2}')),
            callback='parse_item', 
            follow = True,
        ),
    )

    def parse_item(self, response):
        #response.xpath("//div[@id='content']")
        #ABSTRACT response.xpath("//div[@id='content']//div[@class='box-abstract']//p//text()").getall()
        # BIBLIO response.xpath("//div[@id='content']//div[@id='bibliography']//p//text()").getall()
        
        content = response.xpath("//div[@id='content']").get()
        abstract = response.xpath("//div[@id='content']//div[@class='box-abstract']//p//text()").getall()
        references = response.xpath("//div[@id='content']//div[@id='bibliography']//p//text()").getall()
        pubdate = response.xpath("//div[@id='content']//time//@datetime").get()


        if len(references) > 0 or len(abstract) > 0:
            url = response.url
            urlhash = hashlib.md5(url.encode('utf8')).hexdigest()
            filename = f'{urlhash}.html'
            with open(self.htmldir/filename,'w') as f:
                f.write(content)

            item = {}
            item['pubdate'] = pubdate
            item['abstract'] = abstract
            item['references'] = references
            item['htmlfile'] = filename 

            return item
#'https:\/\/www.bankofengland.co.uk\/working-paper\/\d+\/(\w+|-)+')), 