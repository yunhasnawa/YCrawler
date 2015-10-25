__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

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