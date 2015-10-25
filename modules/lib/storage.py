__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from ..lib.helper import Helper
from pymongo import MongoClient

class Storage(object):

    def __init__(self, host='localhost', port=27017):
        #Helper.log("Initializing storage..")
        self.host = host
        self.port = port

    def connect(self, db_name):
        self.__client = MongoClient(self.host, self.port)
        self.__db = self.__client[db_name]

    def get_db(self):
        return self.__db

    def set_collection(self, collection_name):
        self.__collection = self.__db[collection_name]
        return self.__collection

    def insert_documents(self, documents):
        self.__collection.insert_many(documents)

    def insert(self, document):
        self.__collection.insert_one(document)

    def retrieve_all_documents(self):
        documents = self.__collection.find()
        return documents
