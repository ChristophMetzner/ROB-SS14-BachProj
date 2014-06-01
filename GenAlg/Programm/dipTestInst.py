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
    
    
    def __repr__(self):
        return "dipTest(__index=%r,__dip=%r,__p=%r)" % (self.__index, self.__dip, self.__p)
