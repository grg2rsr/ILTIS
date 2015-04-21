# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:52:50 2015

@author: georg
"""

from PyQt4 import QtGui, QtCore # for the dialogs
from lib import IOtools as io
from Data_Object import Data_Object
from Metadata_Object import Metadata_Object
import os
import sys
import scipy as sp

class IO_Object(object):
    """ holds all IO functionality """
    def __init__(self,Main):
        self.Main = Main
        pass

    def init_data(self):
        """ 
        emit reset signal
        load data
        emit init data signal
        
        DO NOT connect this init_data to the initDataSignal slot, this one
        has to be called seperately
        """
        self.Main.Signals.resetSignal.emit()
      
        # read in new data
        self.read_Data() # opens filedialog, sets meta_data.paths

        # initialize Data display again
        self.Main.Signals.initDataSignal.emit()
        
        # and emit an update Signal
        self.Main.Signals.updateSignal.emit()      
        

        pass

    def reset(self):
        """ deletes data object """
        self.Main.Data = None # take care that no extra references are generated and kept!
        pass

    def OpenFileDialog(self,title=None,default_dir=None,extension='*'):
        """ Opens a Qt Filedialoge window to read files from disk """
        
        if default_dir==None:
            default_dir = os.getcwd()
        if title==None:
            title='Open File'
        
        qpaths = QtGui.QFileDialog.getOpenFileNames(parent=self.Main.MainWindow, caption=title, directory=default_dir, filter=extension)
        paths = []
        for i in range(len(qpaths)):            
            paths.append(str(qpaths[i]))

        return paths
        
    def SaveFileDialog(self,title=None,default_dir=None,extension='*'):
        """ Opens a Qt SaveFileName Dialog """
        if default_dir==None:
            default_dir = os.getcwd()
        if title==None:
            title='Save File'
            
        qpath = QtGui.QFileDialog.getSaveFileName(self.Main, title, default_dir,extension)
        path = str(qpath)
        return path
    
    def read_Data(self):
        """ data loader: opens a file dialog asking for  """
        paths = self.OpenFileDialog(title='Open data set', default_dir=self.Main.Options.general['cwd'], extension='(*.tif *.ids *.lsm)')
        
        if len(paths) == 0:
            return None
        if len(paths) == 1:
            if paths[0].endswith('.ids'):
                print "load ids"
            else:
                pass
            
        if len(paths) > 1:
            # take care of: no mixed data formats
            # no multiple ids
            if any([path.endswith('.ids') for path in paths]):
                print "reading multiple .ids files is not supported because of possible metadata conflict"
                return None
            
            self.Main.Data = Data_Object(self.Main)
            
            # FIXME hacked in tif read
            self.read_tifs(paths)
            
            # FIXME hacked in for now, initialize empty metadata object 
            self.Main.Data.Metadata = Metadata_Object(self.Main,self.Main.Data)
            self.Main.Data.Metadata.paths = paths
            self.Main.Data.Metadata.trial_labels = paths
            
            # FIXME think about where this will fit best
            self.Main.Data.nTrials = len(paths)
            self.Main.Data.nFrames = self.Main.Data.raw.shape[2]
        
        return None
        
    def read_tifs(self,paths):
        """ read tifs found at paths (list with paths) """
        # reading
        x,y,t = io.read_tiffstack(paths[0]).shape
        n = len(paths)
        
        self.Main.Data.raw = sp.zeros((x,y,t,n),dtype='uint16')
        self.Main.Data.dFF = sp.zeros((x,y,t,n),dtype='float32')
        
        for n,path in enumerate(paths):
            print "loading dataset from " + path
            print "Dataset size: " + str(os.stat(path).st_size / 1000000.0) + ' MB'
#            self.Main.MainWindow.statusBar().showMessage("loading dataset: " + path) ### FIXME signal needed
            t_stack = io.read_tiffstack(path)
            self.Main.Data.raw[:,:,:,n] = t_stack
            
        pass


    def load_options(self):
        """ load options from options_filepath """
        pass
        
    def save_options(self):
        """ save options to options_filepath """
        pass