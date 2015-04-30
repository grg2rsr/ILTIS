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
        self.load_data() # opens filedialog, sets meta_data.paths

        # initialize Data display again
        self.Main.Signals.initDataSignal.emit()
        
        # and emit an update Signal
        self.Main.Signals.updateSignal.emit()      
        

        pass

    def reset(self):
        """ deletes data object """
        self.Main.Data = None # take care that no extra references are generated and kept!
        pass

    ### Dialogs
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
        
#==============================================================================
#     ### reading data sets
#==============================================================================

    """ get paths to load. determine file format. open appropriate reader """
    def load_data(self):

        # Data init        
        self.Main.Data = Data_Object(self.Main)
        self.Main.Data.Metadata = Metadata_Object(self.Main,self.Main.Data)
        
        # get paths
        paths = self.get_paths_to_read()
        if paths == None:
            return None
        
        # determine format
        file_format = self.determine_format(paths)
        
        # open appropriate reader
        if file_format == '.tif':
            self.load_tif(paths)
            
        if file_format == '.ids':
            if len(paths) > 1:
                print "trying to load multiple ids files, raise Exception"
            path = paths[0]
            self.load_ids(path)
            
        if file_format == '.lsm':
            tifpaths = self.convert_lsm2tif(paths)
            self.load_tif(tifpaths)
        
    def get_paths_to_read(self):
        paths = self.OpenFileDialog(title='Open data set', default_dir=self.Main.Options.general['cwd'], extension='(*.tif *.ids *.lsm)')
        return paths
        
    def determine_format(self,paths):
        """ goes through the paths and raises an exception if there are incompatibilities """
        # check for mixed file formats
        endings = sp.array([os.path.splitext(path)[1] for path in paths])
        if not(sp.all(endings[0] == endings)):
            print "raise error here, not all fileformats are equal"
        return endings[0]
    
    def load_tif(self,paths):
        """ read tifs found at paths (list with paths) """
        
        # reading
        x,y,t = io.read_tiffstack(paths[0]).shape
        n = len(paths)
        
        self.Main.Data.raw = sp.zeros((x,y,t,n),dtype='uint16')
        self.Main.Data.dFF = sp.zeros((x,y,t,n),dtype='float32')
        
        for n,path in enumerate(paths):
            print "loading dataset from " + path
            print "Dataset size: " + str(os.stat(path).st_size / 1000000.0) + ' MB'
            self.Main.MainWindow.statusBar().showMessage("loading dataset: " + path)
            self.Main.Data.raw[:,:,:,n] = io.read_tiffstack(path)
        self.Main.MainWindow.statusBar().clearMessage()
            
        # default settings if no metadata is read
        self.Main.Data.Metadata.paths = paths
        self.Main.Data.Metadata.trial_labels = [os.path.basename(path) for path in paths]
        
        self.Main.Data.nTrials = len(paths)
        self.Main.Data.nFrames = self.Main.Data.raw.shape[2]
    
    def load_ids(path):
        pass
        
    def convert_lsm2tif(paths):
        """ batch convert .lsm files to tiffs """
        pass
    
    
    
#    def read_Data(self):
#        """ data loader: opens a file dialog asking for  """
#        # paths = self.OpenFileDialog(title='Open data set', default_dir=self.Main.Options.general['cwd'], extension='(*.tif *.ids *.lsm)')
#        
#        ### FIXME hacked in for fast testing start!
#        paths = ['/home/georg/Dropbox/python/ILTIS/testdata/EXP6DO_R01_GR1_B1.tif','/home/georg/Dropbox/python/ILTIS/testdata/EXP6DO_R03_GR1_B1.tif','/home/georg/Dropbox/python/ILTIS/testdata/EXP6DO_R04_GR1_B1.tif']
#
#        if len(paths) == 0:
#            return None
#        if len(paths) == 1:
#            if paths[0].endswith('.ids'):
#                print "load ids"
#            else:
#                pass
#            
#        if len(paths) > 1:
#            # take care of: no mixed data formats
#            # no multiple ids
#            if any([path.endswith('.ids') for path in paths]):
#                print "reading multiple .ids files is not supported because of possible metadata conflict"
#                return None
#            
#            self.Main.Data = Data_Object(self.Main)
#            
#            # FIXME hacked in tif read
#            self.read_tifs(paths)
#            
#            # FIXME hacked in for now, initialize empty metadata object 
#            self.Main.Data.Metadata = Metadata_Object(self.Main,self.Main.Data)
#            self.Main.Data.Metadata.paths = paths
#            self.Main.Data.Metadata.trial_labels = [os.path.basename(path) for path in paths]
#            
#            # FIXME think about where this will fit best
#            self.Main.Data.nTrials = len(paths)
#            self.Main.Data.nFrames = self.Main.Data.raw.shape[2]
#        
#        return None
#        
#    def read_tifs(self,paths):
#        """ read tifs found at paths (list with paths) """
#        # reading
#        x,y,t = io.read_tiffstack(paths[0]).shape
#        n = len(paths)
#        
#        self.Main.Data.raw = sp.zeros((x,y,t,n),dtype='uint16')
#        self.Main.Data.dFF = sp.zeros((x,y,t,n),dtype='float32')
#        
#        for n,path in enumerate(paths):
#            print "loading dataset from " + path
#            print "Dataset size: " + str(os.stat(path).st_size / 1000000.0) + ' MB'
##            self.Main.MainWindow.statusBar().showMessage("loading dataset: " + path) ### FIXME signal needed
#            t_stack = io.read_tiffstack(path)
#            self.Main.Data.raw[:,:,:,n] = t_stack
#            
#        pass

    def read_trial_labels(self):
        filepath = self.OpenFileDialog(title='load a textfile with trial labels',default_dir=self.Main.Options.general['cwd'])
        filepath = filepath[0]
        self.load_trial_labels(filepath)
        pass
        
    def load_trial_labels(self,filepath):
        with open(filepath, 'r') as fh:
            labels = [label.strip() for label in fh.readlines()]
        self.Main.Data.Metadata.labels = labels
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.set_current_labels(labels)
        pass
    
    def load_options(self):
        """ load options from options_filepath """
        pass
        
    def save_options(self):
        """ save options to options_filepath """
        pass