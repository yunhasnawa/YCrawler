#!/usr/local/bin/python3
__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.lib.helper import Helper
from modules.lib.storage import Storage
from modules.web.crawlset import Crawlset

def retrieve_crawlsets():
    storage = Storage()
    storage.connect('crawldb')
    storage.set_collection('crawlset')
    documents = storage.retrieve_all_documents()
    crawlsets = Crawlset.list_from_documents(documents)
    return crawlsets

def generate_html_table(crawlsets):
    html = '<html><head><title>Crawl Results</title></head><body><table>'
    for crawlset in crawlsets:
        html += '<tr>'
        html += '<td>' + str(crawlset.level) + '</td>'
        html += '<td><a href="#">' + crawlset.link + '</a></td>'
        html += '</tr>'
    html += '</table></body></html>'
    return html

def main():
    Helper.html_header()
    crawlsets = retrieve_crawlsets()
    html = generate_html_table(crawlsets)
    print(html)

main()