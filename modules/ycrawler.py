__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.web.urlgrabber import UrlGrabber
from modules.lib.helper import Helper
from modules.lib.storage import Storage

class YCrawler(object):
    def __init__(self, level, site_url, site_root):
        self.level = level
        self.site_url = site_url
        self.site_root = site_root
        self.crawlset_bucket = []

    # Get URLs
    def __fill_crawlset_bucket(self):
        current_depth = -1
        if current_depth < self.level:
            current_depth += 1
            Helper.log('Depth', current_depth)
            grabber1 = UrlGrabber(current_depth, self.site_url, self.site_root)
            crawlsets1 = grabber1.grab()
            if crawlsets1 is not None:
                self.crawlset_bucket.extend(crawlsets1)
            current_depth += 1
            if current_depth < self.level:
                current_depth += 1
                for set1 in crawlsets1:
                    set1 = (set1)
                    Helper.log('Depth', current_depth)
                    grabber2 = UrlGrabber(current_depth, set1.link, self.site_root)
                    crawlsets2 = grabber2.grab()
                    if crawlsets2 is not None:
                        self.crawlset_bucket.extend(crawlsets2)

    # Add content to any crawlset that doesn't have one
    def __finalize_crawlset_bucket(self):
        Helper.log("Adding content..")
        self.crawlset_bucket = set(self.crawlset_bucket)
        json_bucket = []
        for crawlset in self.crawlset_bucket:
            if crawlset.content == '':
                Helper.log('Downloading content for URL', crawlset.link)
                crawlset.content = UrlGrabber.retrieve_html(crawlset.link)
                Helper.log('OK!')
            json_bucket.append(crawlset.to_dictionary())
        self.crawlset_bucket = json_bucket

    # Save to storage
    def __save_bucket(self):
        storage = Storage()
        storage.connect('crawldb')
        storage.set_collection('crawlset')
        Helper.log("Insert count", len(self.crawlset_bucket))
        storage.insert_documents(self.crawlset_bucket)

    def crawl(self):
        self.__fill_crawlset_bucket()
        self.__finalize_crawlset_bucket()
        self.__save_bucket()