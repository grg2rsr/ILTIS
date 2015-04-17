"""
Created on Wed Apr  1 13:15:52 2015

@author: georg
"""

from Metadata_Object import Metadata_Object


""" note: communication with statusBar is just commented out. no signal provided
yet, waiting for stackoverlow answer """

class Data_Object():
    """ 
    specification of a Data Object:    
    """
    def __init__(self,parent):
        self.Main = parent
        self.raw = None
        self.dFF = None
        self.Traces = None
        self.extraction_mask = None
        self.Metadata = None
        self.nTrials = None # number of files = number of trials
        self.nFrames = None
        pass
    pass


if __name__ == '__main__':
    pass