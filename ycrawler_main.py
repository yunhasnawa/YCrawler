#!/usr/local/bin/python3

'''
Author: Yoppy Yunhasnawa of FUNlab at Chang Gung University
YCrawler
Crawls website up to 5 levels from the starting URL.
You can set the site address and crawl level in the main method at the bottom of th file.
'''
__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from html.parser import HTMLParser
import urllib.request
import gzip
import re
import os

## Custom HTML parser
class YCrawlerParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.title_found = False
        self.body_found = False
        self.title = None
        self.body = None

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.title_found = True
        elif tag == 'body':
            self.body_found = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.title_found = False
        elif tag == 'body':
            self.body_found = False

    def handle_data(self, data):
        if self.title_found == True:
            self.title = data
        elif self.body_found == True:
            if self.body is None:
                self.body = ''
            self.body += data

class Helper(object):

    @staticmethod
    def html_header():
        print('Content-type:text/html\r\n\r\n')

    @staticmethod
    def log(label, value = None):
        if value is not None:
            print('-- ' + label + ': ' + str(value))
        else:
            print('-- ' + label)

    @staticmethod
    def normalize_url_slashes(url, protocol = 'http'):
        url = str(url)
        normalized_url = url
        segments = url.split('/')
        if len(segments) > 1:
            correct_segments = []
            for segment in segments:
                if segment != '':
                    correct_segments.append(segment)
            if len(correct_segments) > 0:
                first_segment = str(correct_segments[0])
                if first_segment.find(protocol) == -1:
                    correct_segments = [(protocol + ':')] + correct_segments
                correct_segments[0] = correct_segments[0] + '/'
                normalized_url = '/'.join(correct_segments)
        return normalized_url

    @staticmethod
    def current_address():
        url = os.environ['HTTP_HOST']
        uri = os.environ['REQUEST_URI']
        return url + uri

    @staticmethod
    def current_uri():
        uri = os.environ['REQUEST_URI']
        return uri

    @staticmethod
    def url_params(url):
        params = url.split("?")[1]
        params = params.split('=')
        pairs = zip(params[0::2], params[1::2])
        answer = dict((k,v) for k,v in pairs)
        return answer

    @staticmethod
    def module_dir():
        now = os.path.dirname(os.path.realpath("__file__"))
        module_dir = str(now)
        return module_dir

class FileStorage(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.__file = open(self.file_name, 'w+', encoding='utf-8-sig') # If not exists

    def write(self, text):
        self.__file.write(text)

    @staticmethod
    def file_storage_dir():
        module_dir = Helper.module_dir()
        file_storage_dir = module_dir + '/files/'
        return file_storage_dir

    @staticmethod
    def bulk_write(data_list, text_key, file_name_key=None, extension = 'html'):
        file_path = FileStorage.file_storage_dir()
        counter = 0
        for data in data_list:
            text = data[text_key]
            file_name = data[file_name_key] if file_name_key is not None else str(counter)
            full_name = file_path + file_name + '.' + extension
            Helper.log("Writing to", full_name)
            fs = FileStorage(full_name)
            #try:
            if text is not None: fs.write(text)
            #except Exception:
                #fs.write('Cannot write the string!')
            counter += 1

class Crawlset(object):
    def __init__(self, level, link, content = ''):
        self.level = level
        self.link = link
        self.content = content

    def to_json_string(self):
        json_level = str(self.level) if self.level is not None else 'null'
        json_link = self.link if self.link is not None else 'null'
        json_content = self.content if self.content is not None else 'null'
        json = '{"level":' + json_level + ',"link":"' + json_link + '","content":"' + json_content + '"}'
        return json

    def to_dictionary(self):
        dictionary = {"level":self.level, "link":self.link, "content":self.content}
        return dictionary

    def content_json_string(self):
        level = str(self.level)
        link = self.link
        parser = YCrawlerParser()
        parser.feed(self.content)
        title = parser.title if parser.title is not None else 'No title found'
        body = parser.body if parser.body is not None else 'No body found'
        json = '{level:' + level + ',link:"' + link + '",content:{title:"' + title + '",body:"' + body + '"}}'
        return json

    @staticmethod
    def from_dictionary(dictionary):
        level = dictionary['level']
        link = dictionary['link']
        content = dictionary['content']
        crawlset = Crawlset(level, link, content)
        return crawlset

    @staticmethod
    def list_from_documents(documents):
        crawlsets = []
        for document in documents:
            crawlset = Crawlset(document['level'], document['link'], document['content'])
            crawlsets.append(crawlset)
        return crawlsets

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
            Helper.log('OK!')
        except Exception:
            html = ''
            Helper.log('Fail..')
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
        Helper.log('Total valid links', len(new_links))
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

class YCrawler(object):
    def __init__(self, level, site_url, site_root):
        self.level = level
        self.site_url = site_url
        self.site_root = site_root
        self.crawlset_bucket = []

    # Get URLs, currently only support up to 2-level grab.
    # Quite tricky, if you don't understand email me at yunhasnawa@gmail.com
    def __fill_crawlset_bucket(self):
        current_depth = 0
        # Level 1
        if current_depth < self.level:
            current_depth += 1
            Helper.log('Depth', current_depth)
            grabber1 = UrlGrabber(current_depth, self.site_url, self.site_root)
            crawlsets1 = grabber1.grab()
            if crawlsets1 is not None:
                self.crawlset_bucket.extend(crawlsets1)
            # Level 2
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
                                    # Level 5
                                    if current_depth < self.level:
                                        current_depth += 1
                                        for set4 in crawlsets4:
                                            set4 = (set4)
                                            Helper.log('Depth', current_depth)
                                            grabber5 = UrlGrabber(current_depth, set4.link, self.site_root)
                                            crawlsets5 = grabber5.grab()
                                            if crawlsets5 is not None:
                                                self.crawlset_bucket.extend(crawlsets5)

    # Add content to any crawlset that doesn't have one
    def __finalize_crawlset_bucket(self):
        Helper.log("Adding content..")
        self.crawlset_bucket = set(self.crawlset_bucket)
        json_bucket = []
        for crawlset in self.crawlset_bucket:
            if crawlset.content == '':
                Helper.log('Downloading content for URL', crawlset.link)
                crawlset.content = UrlGrabber.retrieve_html(crawlset.link)
            json_bucket.append(crawlset.to_dictionary())
        self.crawlset_bucket = json_bucket

    # Save to storage
    def __save_bucket(self):
        json_content = []
        str_urls = ''
        counter = 0
        for dictionary in self.crawlset_bucket:
            crawlset = Crawlset.from_dictionary(dictionary)
            str_urls += crawlset.link + '\n'
            name = 'site_' + str(counter) + '_level_' + str(crawlset.level)
            json = {'file_name' : name, 'content' : crawlset.content_json_string()}
            json_content.append(json)
            counter += 1
        FileStorage.bulk_write(json_content, 'content', 'file_name', 'json')
        urls_file_name = FileStorage.file_storage_dir() + '00_url_list.txt'
        fs = FileStorage(urls_file_name)
        fs.write(str_urls)

    def crawl(self):
        self.__fill_crawlset_bucket()
        self.__finalize_crawlset_bucket()
        self.__save_bucket()


def main():
    Helper.html_header()
    ycrawler = YCrawler(5, 'http://5550555.tw/chinanews/chinanews_list.php?page_1=a&s_key=1&start_year=2015&start_month=9&start_day=29', '5550555')
    ycrawler.crawl()

main()