"""
Created on Wed Apr  1 13:15:52 2015

@author: georg
"""

import os

class Data_Object(object):
    """ 
    specification of a Data Object:    
    """
    def __init__(self):
#        self.Main = parent # never needs to access anything, therefore no parent
        self.raw = None
        self.dFF = None
        self.Traces = None
        self.extraction_mask = None
        self.Metadata = None
        self.nTrials = None # number of files = number of trials
        self.nFrames = None
        pass
    
    def infer(self):
        """ infer some fields, self.raw and Metadata.paths have to be set """
        self.Metadata.trial_labels = [os.path.basename(path) for path in self.Metadata.paths]
        self.nTrials = len(self.Metadata.paths)
        self.nFrames = self.raw.shape[2]
    pass

class Metadata_Object(object):
    def __init__(self,parent):
        super(Metadata_Object,self).__init__()
        self.Data = parent
        self.paths = None
        self.trial_labels = None
        self.LSTdata = None
        pass


if __name__ == '__main__':
    pass