#!/usr/local/bin/python3
__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.lib.helper import Helper
from modules.ycrawler import YCrawler

def main():
    Helper.html_header()
    ycrawler = YCrawler(4, 'http://5550555.tw/chinanews/chinanews_list.php?page_1=a&s_key=1&start_year=2015&start_month=9&start_day=29', '5550555')
    ycrawler.crawl()

# Invoke main method
main()