#! usr/local/lib/python2.7 python
# coding=utf-8
class dipTest(object):
    
    def __init__(self, index, dip, p):
        self.__index = index
        self.__dip = dip
        self.__p = p
    
    def get_index(self):
        return self.__index
        
    def get_dip(self):
        return self.__dip
        
    def get_p(self):
        return self.__p
