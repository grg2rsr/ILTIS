# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:02:55 2015

@author: georg
"""

class Metadata_Object(object):
    def __init__(self,Main,parent):
        super(Metadata_Object,self).__init__()
        self.Data = parent
        self.Main = Main
        
        self.paths = None
        self.trial_labels = None
        pass

if __name__ == '__main__':
    pass
