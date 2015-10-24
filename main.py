#!/usr/bin/python3
__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.lib.helper import Helper
from modules.ycrawler import YCrawler

def main():
    Helper.html_header()
    ycrawler = YCrawler(2, 'http://www.google.com', 'google.com')
    ycrawler.crawl()

# Invoke main method
main()