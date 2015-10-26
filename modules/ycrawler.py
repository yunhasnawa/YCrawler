__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.web.urlgrabber import UrlGrabber
from modules.lib.helper import Helper
from modules.lib.storage import Storage
from modules.lib.filestorage import FileStorage

class YCrawler(object):
    def __init__(self, level, site_url, site_root):
        self.level = level
        self.site_url = site_url
        self.site_root = site_root
        self.crawlset_bucket = []

    # Get URLs, currently only support up to 2-level grab.
    # Quite tricky, if you don't understand email me at yunhasnawa@gmail.com
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
                    # Level 3
                    if current_depth < self.level:
                        current_depth += 1
                        for set2 in crawlsets2:
                            set2 = (set2)
                            Helper.log('Depth', current_depth)
                            grabber3 = UrlGrabber(current_depth, set2.link, self.site_root)
                            crawlsets3 = grabber3.grab()
                            if crawlsets3 is not None:
                                self.crawlset_bucket.extend(crawlsets3)
                            # Level 4
                            if current_depth < self.level:
                                current_depth += 1
                                for set3 in crawlsets3:
                                    set3 = (set3)
                                    Helper.log('Depth', current_depth)
                                    grabber4 = UrlGrabber(current_depth, set3.link, self.site_root)
                                    crawlsets4 = grabber4.grab()
                                    if crawlsets4 is not None:
                                        self.crawlset_bucket.extend(crawlsets4)

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
    def __save_bucket(self, to_db=True):
        if to_db == True:
            storage = Storage()
            storage.connect('crawldb')
            storage.set_collection('crawlset')
            Helper.log("Insert count", len(self.crawlset_bucket))
            storage.insert_documents(self.crawlset_bucket)
        else:
            FileStorage.bulk_write(self.crawlset_bucket, 'content')

    def __save_urls(self):
        str_urls = ''
        for crawlset in self.crawlset_bucket:
            url = crawlset['link']
            str_urls += url
            str_urls += '\n'
        file_name = FileStorage.file_storage_dir() + '00_url_list.txt'
        fs = FileStorage(file_name)
        fs.write(str_urls)

    def crawl(self):
        self.__fill_crawlset_bucket()
        self.__finalize_crawlset_bucket()
        self.__save_bucket(False)
        self.__save_urls()