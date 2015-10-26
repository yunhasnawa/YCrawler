__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from ..lib.helper import Helper
from ..web.crawlset import Crawlset
import urllib.request
import re
import gzip

class UrlGrabber(object):

    def __init__(self, current_depth, site_address, site_root):
        self.current_depth = current_depth
        self.site_address = site_address
        self.site_root = site_root
        self.__site_address_content = None

    @staticmethod
    def retrieve_html(address):
        try:
            with urllib.request.urlopen(address, timeout=5) as resp:
                html = resp.read().decode('utf-8')
                if resp.info().get('Content-Encoding') == 'gzip':
                    html = gzip.decompress(html)
            html = str(html)
        except Exception:
            html = None
        return html

    def __find_links(self, address):
        html = UrlGrabber.retrieve_html(address)
        if html is None:
            return None
        self.__site_address_content = html
        #links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html)
        Helper.log('Pattern found', len(links))
        # Remove duplicates
        links = set(links)
        # Fix missing HTTP & remove external links
        links = self.__create_crawlset_lists(links)
        return links

    def __create_crawlset_lists(self, links):
        new_links = []
        for link in links:
            Helper.log('Checking Pattern', link)
            link = Helper.normalize_url_slashes(link)
            # Quick fixes, dirty..
            link = link.replace("')", '')
            link = link.replace('><img', '')
            if link.find(self.site_root) != -1: # Remove external links
                # Convert to a crawlset object
                crawlset = Crawlset(self.current_depth, link)
                new_links.append(crawlset)
        Helper.log('Fixed URL', len(new_links))
        return new_links

    def __create_parent_crawlset(self):
        crawlset = Crawlset(self.current_depth, self.site_address, self.__site_address_content)
        return crawlset

    # Start grabbing the URL at given address
    # Quite tricky, if you don't understand email me at yunhasnawa@gmail.com
    def grab(self):
        crawlset_list = self.__find_links(self.site_address)
        if crawlset_list is None:
            return None
        count = 0
        for crawlset in crawlset_list:
            print(str(count) + ') Level: ' + str(crawlset.level) + ' ' + crawlset.link)
            count += 1
        parent_crawlset = self.__create_parent_crawlset()
        crawlset_list = [parent_crawlset] + crawlset_list
        return crawlset_list