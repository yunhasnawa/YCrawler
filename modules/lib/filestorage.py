__author__ = 'Yoppy Yunhasnawa (yunhasnawa@gmail.com)'

from .helper import Helper

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
            file_name = file_name_key if file_name_key is not None else str(counter)
            full_name = file_path + file_name + '.' + extension
            Helper.log("Writing to", full_name)
            fs = FileStorage(full_name)
            #try:
            if text is not None: fs.write(text)
            #except Exception:
                #fs.write('Cannot write the string!')
            counter += 1




