__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

class Helper(object):

    @staticmethod
    def html_header():
        print('Content-type:text/html\r\n\r\n')

    @staticmethod
    def log(label, value):
        print('-- ' + label + ': ' + str(value))
