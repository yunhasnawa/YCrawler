__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

class Crawlset(object):
    def __init__(self, level, link, content = ''):
        self.level = level
        self.link = link
        self.content = content