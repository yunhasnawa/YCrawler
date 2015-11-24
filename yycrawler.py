#!python2.7
# -*- coding: utf-8 -*-
'''
Author: Yoppy Yunhasnawa of FUNlab at Chang Gung University
(yunhasnawa@gmail.com)
YCrawler
Crawls website up to user given level from the starting URL.
You can set the site address and crawl level in the main method at the bottom of th file.
What's new (31/10/2015):
- Fixed: Content always empty
- Output named with  URL ID if exists. Else, with Crawlset ID
What's new (30/10/2015):
- Completely new rewrite!
- Faster!
- Python 2.7 compatible
- Crawl level not limited anymore
- Able to detect redundant URL
- Able to detect invalid destination file in URL, e.g. image and other binary files
- The code now is more optimized, dramatically reduce unnecessary loops.
- Able to save JSON output in folder wise
- Grab URL in both href origin as well as from regex
- Get page's important parts and categorize them into dictionary based on given XPath setting
- Able to save all Helper.log to log.txt file
- Add some statistics log
'''

from lxml import html
import requests
import re
import time
import hashlib
import os
import json
import codecs
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'


class Page(object):
    def __init__(self, crawlset, site_name, xpath_pair):
        self.crawlset = crawlset
        self.site_name = site_name
        self.xpath_pair = xpath_pair
        self.xpath_root = self.__retrieve_xpath_root()
        self.parsed_url = self.__retrieve_parsed_url()

    def __retrieve_xpath_root(self):
        html_text = self.crawlset.content
        # print(html_text)
        root = None
        try:
            root = html.fromstring(html_text)
        except Exception as e:
            print('WARNING: Content is None for URL -> ' + self.crawlset.url)
            print(e)
        return root

    def __retrieve_parsed_url(self):
        raw = self.crawlset.url
        url = URL(raw, self.site_name)
        return url

    def _find_data(self, xpath_expression):
        exp = str(xpath_expression)
        data = None
        xpath_is_valid = xpath_expression is not '' and xpath_expression is not None
        if xpath_is_valid:
            forced_data = True if exp.startswith('!!!') else False
            if forced_data:
                data = exp[3:]
            elif exp == '<raw_url>':
                data = self.parsed_url.raw_url
            elif exp == '<domain>':
                data = self.parsed_url.domain
            elif exp == '<uri-0>':
                uri_0 = ''
                if self.parsed_url.uri_segments is not None:
                    if len(self.parsed_url.uri_segments) > 0:
                        uri_0 = self.parsed_url.uri_segments[0]
                data = uri_0
            else:
                if self.xpath_root is not None:  # Sometimes None due to invalid content
                    print('XPATH ROOT not None!')
                    found = self.xpath_root.xpath(exp)
                    if len(found) > 0:
                        data = found[0]
        if data is not None:
            data = data.replace('\r\n', '')
            data = data.replace('\t', '')
        return data

    def dictionary_representation(self, content_key=None):
        Helper.log("Examining URL", self.crawlset.url)
        dictionary = {}
        for key, value in self.xpath_pair.iteritems():
            is_array = isinstance(value, list)
            if is_array:
                print('MULTIPLE XPath detected!')
                for xp in value:
                    dictionary[key] = self._find_data(xp)
                    print('CONTENT FOUND!!')
                    print(dictionary[key])
                    if dictionary[key] is not None:
                        break
            else:
                dictionary[key] = self._find_data(value)
        if content_key is not None:
            content = dictionary[content_key]
            if content is not None:
                dictionary['has_content'] = True
            else:
                dictionary['has_content'] = False
        return dictionary

    def to_json_string(self, page_dict=None):
        page_dict = page_dict if page_dict is not None else self.dictionary_representation()
        json_string = json.dumps(page_dict, ensure_ascii=False, encoding='utf8')
        return json_string


class Helper(object):
    @staticmethod
    def log(label, value=None, append_log_file=False):
        message = '-- ' + label
        if value is not None:
            message += (': ' + str(value))
        print(message)
        if append_log_file:
            FileStorage.quick_append(message)

    @staticmethod
    def md5(text):
        m = hashlib.md5()
        m.update(text)
        return m.hexdigest()

    @staticmethod
    def module_dir():
        now = os.path.dirname(os.path.realpath("__file__"))
        module_dir = str(now)
        return module_dir


class FileStorage(object):
    def __init__(self, file_name, mode='w+'):
        self.file_name = file_name
        self.__file_handler = codecs.open(self.file_name, mode, 'utf-8-sig')

    def write(self, text):
        self.__file_handler.write(text)

    @staticmethod
    def file_storage_dir():
        module_dir = Helper.module_dir()
        file_storage_dir = module_dir + '/files/'
        return file_storage_dir

    @staticmethod
    def quick_write(text, f_name='log.txt'):
        f_dir = FileStorage.file_storage_dir()
        file_name = f_dir + f_name
        fs = FileStorage(file_name)
        fs.write(text)
        return file_name

    @staticmethod
    def quick_append(text, f_name='log.txt', newline=True):
        text = ('\n' + text) if newline else text
        f_dir = FileStorage.file_storage_dir()
        exists = FileStorage.check_and_create_if_needed(f_dir)
        if not exists:
            FileStorage.quick_write('')
        file_name = f_dir + f_name
        fs = FileStorage(file_name, 'a')
        fs.write(text)
        return file_name

    @staticmethod
    def check_dir_and_write(text, f_dir, f_name):
        FileStorage.check_and_create_if_needed(f_dir)
        file_name = f_dir + f_name
        fs = FileStorage(file_name)
        fs.write(text)
        return file_name

    @staticmethod
    def check_and_create_if_needed(folder):
        exists = True
        if not os.path.exists(folder):
            os.makedirs(folder)
            exists = False
        return exists


class Crawlset(object):
    def __init__(self, level, url, content=None):
        self.level = level
        self.url = url
        self.content = content
        self.identifier = self.__generate_identifier()

    def __generate_identifier(self):
        timestamp = str(time.time())
        id_str = timestamp + self.url
        crawlset_id = Helper.md5(id_str)
        return crawlset_id

    def to_dictionary(self):
        dict_form = {'identifier': self.identifier, 'level': self.level, 'url': self.url, 'content': self.content}
        return dict_form

    def has_content(self):
        return self.content is not None


class URL(object):
    def __init__(self, valid_url, site_name):
        self.raw_url = valid_url
        self.site_name = site_name
        self.protocol = None
        self.root = None
        self.domain = None
        self.uri = None
        self.uri_segments = None
        self.destination_extension = None
        self.__parse()

    def __find_domain(self):
        name_pos = self.root.find(self.site_name)
        if name_pos > -1:
            self.domain = self.root[name_pos:]

    def __find_destination_extension(self):
        # Helper.log("URI", self.uri)
        if len(self.uri) > 1:
            uri_text = str(self.uri)
            uri_text_segments = uri_text.split('/')
            uri_text_segments_count = len(uri_text_segments)
            if uri_text_segments_count > 1:
                uri_text = uri_text_segments[(uri_text_segments_count - 1)]
            query_url = uri_text.split('?')
            if len(query_url) > 1:
                uri_text = query_url[0]
            segments = uri_text.split('.')
            self.destination_extension = segments[(len(segments) - 1)]
        else:
            self.destination_extension = ''
            # Helper.log("Found extension", self.destination_extension)

    def __parse(self):
        url_str = str(self.raw_url)
        segments = url_str.split('/')
        self.protocol = segments[0]
        segments_count = len(segments)
        if segments_count > 2:
            self.root = segments[2]
            self.__find_domain()
            if segments_count > 3:
                join = ''
                self.uri_segments = []
                for x in range(3, segments_count):
                    join += ('/' + segments[x])
                    self.uri_segments.append(segments[x])
                self.uri = join
                self.__find_destination_extension()

    def find_param(self, param_id):
        param_value = None
        if self.uri_segments is not None:
            segments_count = len(self.uri_segments)
            if segments_count > 0:
                last_segment = self.uri_segments[(segments_count - 1)]
                if last_segment.find('?') != -1:
                    queries = last_segment.split('?')
                    # id=2700469&f=def
                    queries = queries[(len(queries) - 1)]
                    #pairs = []
                    if queries.find('&') != 1:
                        pairs = queries.split('&')
                    else:
                        pairs = [queries]
                    for pair in pairs:
                        if pair.find('=') != -1:
                            parts = pair.split('=')
                            param_id_found = parts[0]
                            value = parts[1]
                            if param_id_found == param_id:
                                param_value = value
                                break
        return param_value


class URLGrabber(object):
    ALLOWED_EXTENSIONS = ['', 'htm', 'html', 'shtml', 'php', 'phtml', 'asp', 'aspx', 'jsp', 'cgi', 'pl']

    def __init__(self, initial_url, site_name, site_domain, current_level=0, timeout=5):
        self.initial_url = initial_url
        self.site_name = site_name
        self.site_domain = site_domain
        self.current_level = current_level
        self.timeout = timeout
        self.raw_urls = []
        self.crawlsets = []
        self.initial_url_content = None
        self.total_processed_urls = 0

    @staticmethod
    def retrieve_content(url):
        content = None
        response = requests.get(url)
        if response.ok:
            content = response.text  # Does not need encoding anymore
        return content

    @staticmethod
    def add_domain_if_needed(url, domain, protocol='http'):
        url = str(url)
        # Helper.log("Checking URL", url)
        if not url.startswith(protocol):
            url = protocol + '://' + url
        segments = url.split('/')
        segments = filter(None, segments)
        segments_count = len(segments)
        if segments_count > 1:
            domain_segment = segments[1]
            domain_found = True if domain_segment.find(domain) != -1 else False
            if domain_found is not True:
                segments.insert(1, domain)
        elif segments_count == 1:
            segments.append(domain)
        segments[0] += '/'
        url = '/'.join(segments)
        return url

    def __find_urls_with_regex(self):
        # Clean Javascript function
        html_text = self.initial_url_content
        html_text = html_text.replace(r"')", '')
        html_text = html_text.replace(r"';", '')
        # Get URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html_text)
        return urls

    def __find_href_urls(self, regex_urls):
        html_text = self.initial_url_content
        root = html.fromstring(html_text)
        all_href = root.xpath('//td[@class="mys-elastic mys-left"]/a')
        urls = []
        for href in all_href:
            url = href.attrib['href']
            url = URLGrabber.add_domain_if_needed(url, self.site_domain)
            if url not in regex_urls:
                urls.append(url)
        return urls

    def __validate_url(self, parsed_url):
        Helper.log("Validating URL", parsed_url.raw_url)
        is_valid = False
        # print(parsed_url.root)
        if parsed_url.root.find(self.site_name) != -1:
            ext = parsed_url.destination_extension
            # print('Checking extension -> ' + ext)
            if ext is None or ext in URLGrabber.ALLOWED_EXTENSIONS:
                # print('ext -> ' + ext)
                is_valid = True
        Helper.log("Is valid?", is_valid)
        return is_valid

    def __generate_crawlsets(self):
        uris = []
        for raw in self.raw_urls:
            parsed_url = URL(raw, self.site_name)
            if parsed_url.uri not in uris:
                if self.__validate_url(parsed_url) is True:
                    uris.append(parsed_url.uri)
                    crawlset = Crawlset((self.current_level + 1), parsed_url.raw_url)
                    self.crawlsets.append(crawlset)

    def __find_urls(self):
        regex_urls = self.__find_urls_with_regex()
        a_urls = self.__find_href_urls(regex_urls)
        self.raw_urls = [self.initial_url] + regex_urls + a_urls
        self.total_processed_urls = len(self.raw_urls)
        self.__generate_crawlsets()

    def __retrieve_parent_crawlset(self):
        parent_crawlset = Crawlset(self.current_level, self.initial_url, self.initial_url_content)
        self.crawlsets.append(parent_crawlset)

    def grab(self):
        Helper.log('Start grabbing URLs from', self.initial_url)
        content = URLGrabber.retrieve_content(self.initial_url)
        if content is not None:
            self.initial_url_content = content
            self.__retrieve_parent_crawlset()
            self.__find_urls()
        msg = 'URLs found at level #' + str(self.current_level)
        Helper.log(msg, str(len(self.crawlsets)))
        return self.crawlsets


class YYCrawler(object):
    def __init__(self, level, url, site_name, site_domain, timeout=5):
        self.level = level
        self.url = url
        self.site_name = site_name
        self.site_domain = site_domain
        self.timeout = timeout
        self.current_depth = 0
        self.__crawlset_bucket = []
        self.__start_time = None
        self.__finish_time = None
        self.__total_processed_urls = 0

    def __fill_crawlset_bucket(self, crawlsets):
        if self.current_depth >= self.level:
            return
        self.current_depth += 1
        new_crawlsets = []
        for crawlset in crawlsets:
            grabber = URLGrabber(crawlset.url, self.site_name, self.site_domain, self.current_depth, self.timeout)
            new_crawlsets = grabber.grab()
            self.__crawlset_bucket += new_crawlsets
            self.__total_processed_urls += grabber.total_processed_urls
        self.__fill_crawlset_bucket(new_crawlsets)

    def __count_all_levels(self):
        level_counts = []
        for x in range(0, self.level):
            count = self.__count_level(x)
            level_counts.append(count)
        print(level_counts)

    def __count_level(self, level):
        count = 0
        for crawlset in self.__crawlset_bucket:
            if crawlset.level == level:
                count += 1
        return count

    def __clear_redundant_links(self):
        checked_urls = []
        filled_crawlsets = []  # Has content
        empty_crawlsets = []  # No content
        for crawlset in self.__crawlset_bucket:
            # Helper.log('Level --', crawlset.level)
            if crawlset.has_content():
                if crawlset.url not in checked_urls:
                    Helper.log('Has content', crawlset.url)
                    Helper.log('Level', crawlset.level)
                    filled_crawlsets.append(crawlset)
                    checked_urls.append(crawlset.url)
            else:
                empty_crawlsets.append(crawlset)
        # Give content to legitimate empty crawlsets
        for empty_crawlset in empty_crawlsets:
            if empty_crawlset.url not in checked_urls:
                Helper.log('No content, downloading..', empty_crawlset.url)
                Helper.log('Level', empty_crawlset.level)
                empty_crawlset.content = URLGrabber.retrieve_content(empty_crawlset.url)
                filled_crawlsets.append(empty_crawlset)
                checked_urls.append(empty_crawlset.url)
        self.__crawlset_bucket = filled_crawlsets

    @staticmethod
    def generate_single_crawlset(url):
        content = URLGrabber.retrieve_content(url)
        # print(content)
        crawlset = Crawlset(0, url, content)
        return crawlset

    def crawl(self):
        Helper.log('Processing site with total level', self.level)
        grabber = URLGrabber(self.url, self.site_name, self.site_domain, self.current_depth, self.timeout)
        crawlsets = grabber.grab()
        self.__crawlset_bucket += crawlsets
        self.__fill_crawlset_bucket(crawlsets)
        self.__clear_redundant_links()

    @staticmethod
    def __handle_url_dump(url_dump):
        Helper.log('Dumping URLs...')
        file_path = FileStorage.quick_write(url_dump, 'crawled_urls.txt')
        Helper.log('Successfully dumping URL to', file_path)

    def begin_statistics(self):
        self.__start_time = time.time()
        Helper.log('Starting Time', self.__start_time, True)

    def end_statistics(self):
        self.__finish_time = time.time()
        Helper.log('Finished', self.__finish_time, True)
        total_time = self.__finish_time - self.__start_time
        total_bucket = len(self.__crawlset_bucket)
        Helper.log('Processing total URL number', self.__total_processed_urls, True)
        Helper.log('Processing valid URL', total_bucket, True)
        Helper.log('Total time', total_time, True)

    def save_to_files(self, xpath_pair):
        # crawlset_single1 = YYCrawler.generate_single_crawlset(
        #    'http://www.taiwannews.com.tw/etn/news_content.php?id=2828055')
        # crawlset_single2 = YYCrawler.generate_single_crawlset(
        #    'http://www.taiwannews.com.tw/etn/news_content.php?id=2700469')
        # crawlset_dummy = [crawlset_single1, crawlset_single2]
        f_dir = FileStorage.file_storage_dir() + 'page_contents/'
        url_dump = ''
        # for crawlset in crawlset_dummy:
        for crawlset in self.__crawlset_bucket:
            parsed_url = URL(crawlset.url, self.site_name)
            url_id = parsed_url.find_param('id')
            section = ''
            if parsed_url.uri_segments is not None:
                if len(parsed_url.uri_segments) > 0:
                    if str(parsed_url.uri_segments[0]).isalnum():
                        section = parsed_url.uri_segments[0]
            file_directory = f_dir + section
            file_name = url_id if url_id is not None and url_id is not '' else str(crawlset.identifier)
            file_name = '/' + file_name + '.json'
            page = Page(crawlset, self.site_name, xpath_pair)
            page_dict = page.dictionary_representation('articleContent')
            if page_dict['has_content']:
                json_string = page.to_json_string()
                file_path = FileStorage.check_dir_and_write(json_string, file_directory, file_name)
                Helper.log("Successfully wrote output to", file_path)
                url_dump += parsed_url.raw_url
        YYCrawler.__handle_url_dump(url_dump)


def get_xpath_pair():
    xpath_pair = {
        'title': [".//*[@id='mail_title1']/text()", ".//*[@id='mail_title1']/text()"],
        'sourceType': "!!!News",  # News, Forum, or SocialMedia
        'sourceWebsite': "<domain>",  # Site name
        'sourceBoard': "<uri-0>",  # The site version
        'url': "<raw_url>",  # Full URL
        'author': ".//*[@id='mail_source']/text()",  # Author name
        'cTimeObject': ".//*[@id='mail_source']/span/text()",  # The published time of article. Format: yyyymmdd_hh: mm
        'cDate': ".//*[@id='mail_source']/span/text()",  # The date of article. Format: yyyymmdd
        'cTime': ".//*[@id='mail_source']/span/text()",  # The published time of article. Format: hh: mm
        'articleContent': [".//*[@id='fw']/text()", ".//*[@id='fullstory']/div/p/text()"],
        # Article contents
        'quoteFrom': [".//*[@id='fw']/text()", ".//*[@id='fullstory']/div/p/text()"],
        # The quoting article, PTT unique, green font part)
        'pushIDArray': "",  # Up-vote ID. ['cn9a2002', 'ErnestKou', ...]
        'pushContentArray': "",  # Up-vote content. ["K8 or TT supplies renewed battles
        # five years to upgrade the safety of the car and then
        # closed," "to see if there Premio, supplies average
        # should be running on the road currently the
        #  cheapest car ", ...]
        'pushTimeArray': "",  # Up-vote time.
        # ['20140316_16: 38', '20140316_17: 21', ...]
        'messageNum': "",  # Message number
        'pushNum': ""  # The number of up-vote. PTT "Push" Count 1, the same as
        # the rest of the site and the number of messages
    }
    return xpath_pair


def main():
    # url = 'http://www.elinivana.com'
    # site_name = 'elinivana'
    # site_domain = 'elinivana.com'
    level = 3
    # url = 'http://5550555.tw/chinanews/chinanews_list.php?page_1=a&s_key=1&start_year=2015&start_month=9&start_day=29'
    # site_name = '5550555'
    # site_domain = '5550555.tw'
    url = 'http://www.taiwannews.com.tw/etn/index_ch.php'
    site_name = 'taiwannews'
    site_domain = 'taiwannews.com.tw'
    timeout = 3
    crawler = YYCrawler(level, url, site_name, site_domain, timeout)
    crawler.begin_statistics()
    crawler.crawl()
    crawler.save_to_files(get_xpath_pair())
    crawler.end_statistics()


main()
