#!/usr/local/bin/python3
__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from modules.lib.helper import Helper
from modules.lib.storage import Storage

def get_id():
    uri = Helper.current_uri()
    params = Helper.url_params(uri)
    id = params['id']
    return id

def get_html(id):
    storage = Storage()
    storage.connect('crawldb')
    storage.set_collection('crawlset')
    document = storage.find_one_by_id(id)
    # TODO: Fix page encoding
    html = str(document['content'])
    html = html.replace(r"b'", '', 1)
    html = html.replace(r"\r\n", '')
    html = html.replace(r"\n", '')
    return html

def main():
    Helper.html_header()
    #id = '562cdf0fe4a4c906e73d4ee1'
    id = get_id()
    html = get_html(id)
    print(html)

main()
