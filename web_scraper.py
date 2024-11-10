import logging
import os
import pandas as pd
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from googlesearch import search


def web_scraper(tag, n, language, path, reject=[]):
    logging.getLogger('scrapy').propagate = False

    def get_urls(tag, n, language):
        urls = [url for url in search(tag, stop=n, lang=language)][:n]
        return urls

    class MailSpider(scrapy.Spider):
        name = 'email_spider'

        def __init__(self, start_urls, path, reject):
            self.start_urls = start_urls
            self.path = path
            self.reject = reject
            super().__init__()

        def parse(self, response):
            links = LxmlLinkExtractor(allow=()).extract_links(response)
            links = [str(link.url) for link in links]
            links.append(str(response.url))

            for link in links:
                yield scrapy.Request(url=link, callback=self.parse_link)

        def parse_link(self, response):
            for word in self.reject:
                if word in str(response.url):
                    return

            html_text = str(response.text)
            mail_list = re.findall(r'\w+@\w+\.\w+', html_text)

            if mail_list:
                dic = {'email': mail_list, 'link': [response.url] * len(mail_list)}
                df = pd.DataFrame(dic)
                df.to_csv(self.path, mode='a', header=False, index=False)

    def create_file(path):
        if os.path.exists(path):
            os.remove(path)
        df = pd.DataFrame(columns=['email', 'link'])
        df.to_csv(path, mode='w', header=True, index=False)
        return True

    if not create_file(path):
        return

    print('Collecting Google URLs...')
    google_urls = get_urls(tag, n, language)

    print('Searching for emails...')
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
    process.crawl(MailSpider, start_urls=google_urls, path=path, reject=reject)
    process.start()

    print('Cleaning emails...')
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset='email')
    df = df.reset_index(drop=True)
    df = df.drop_duplicates(subset='email', keep='first')
    df.to_csv(path, mode='w', header=True, index=False)

    print(f"Emails saved to '{path}'")
    return df

