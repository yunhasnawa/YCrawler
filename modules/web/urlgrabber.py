__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from ..lib.helper import Helper
from ..web.crawlset import Crawlset
import urllib.request
import re

class UrlGrabber(object):

    def __init__(self, current_depth, site_address, site_root):
        self.current_depth = current_depth
        self.site_address = site_address
        self.site_root = site_root

    def __retrieve_html(self, address):
        correct_html = False
        try_count = 0
        html = ''
        while not correct_html:
            try_count += 1
            Helper.log('Try count', try_count)
            html = urllib.request.urlopen(address).read() # Sometimes returns weird strings.
            html = str(html)
            if(html.find('<html') != -1):
                correct_html = True
        Helper.log('HTML length', len(html))
        Helper.log('HTML content', html)
        return str(html)

    def __find_links(self, address):
        html = self.__retrieve_html(address)
        links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
        Helper.log('Pattern found', len(links))
        # Remove duplicates
        links = set(links)
        # Fix missing HTTP & remove external links
        links = self.__create_crawlset_lists(links)
        return links

    def __create_crawlset_lists(self, links):
        new_links = []
        for link in links:
            link = str(link)
            if not link.startswith('http'):
                link = 'http://' + link
                link.replace('http:///', 'http://')
            if link.find(self.site_root) != -1: # Remove external links
                # Convert to a crawlset object
                crawlset = Crawlset(self.current_depth, link)
                new_links.append(crawlset)
        Helper.log('Fixed URL', len(new_links))
        return new_links

    def start_grab(self):
        crawlset_list = self.__find_links(self.site_address)
        count = 0
        for crawlset in crawlset_list:
            print(str(count) + ') Level: ' + str(crawlset.level) + ' ' + crawlset.link)
            count += 1

        return crawlset_list