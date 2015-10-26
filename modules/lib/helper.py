__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

import os

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
            #Helper.log('Normalizing', url)
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
