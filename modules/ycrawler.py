__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.web.urlgrabber import UrlGrabber
from modules.lib.helper import Helper

class YCrawler(object):
    def __init__(self, level, site_url, site_root):
        self.level = level
        self.site_url = site_url
        self.site_root = site_root
        self.crawlset_bucket = []

    def crawl(self):
        current_depth = -1
        if current_depth < self.level:
            current_depth += 1
            Helper.log('Depth', current_depth)
            grabber1 = UrlGrabber(current_depth, self.site_url, self.site_root)
            crawlsets1 = grabber1.start_grab()
            self.crawlset_bucket.extend(crawlsets1)
            current_depth += 1
            if current_depth < self.level:
                current_depth += 1
                for set1 in crawlsets1:
                    set1 = (set1)
                    Helper.log('Depth', current_depth)
                    grabber2 = UrlGrabber(current_depth, set1.link, self.site_root)
                    crawlsets2 = grabber2.start_grab()
                    self.crawlset_bucket.extend(crawlsets2)



