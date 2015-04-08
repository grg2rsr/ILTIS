# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:29:30 2015

@author: georg
"""
import os
import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from Options_Object import Options_Object
from Data_Object import Data_Object
from MainWindow_Widget import MainWindow_Widget
from ROIs_Object import ROIs_Object
import IOtools as io
import scipy as sp

pg.setConfigOptions(antialias=True)

class Main():
    def __init__(self,verbose=False):
        
        # fields
        self.cwd = None
        self.program_path = None
        self.graphics_path = None # move to MainWindow
        self.tmp_path = None
        self.Data = None
        self.verbose = verbose
        
        # initialize
        self.version = os.path.splitext(__file__)[0][-3:] # FIXME
        
        self.initialize_paths()
        self.print_startup_msg()

        self.Options = Options_Object(self)
        self.ROIs = ROIs_Object(self)
        self.MainWindow = MainWindow_Widget(self)
        pass


    ### File Dialogs
    def OpenFileDialog(self,title=None,default_dir=None,extension='*'):
        """ Opens a Qt Filedialoge window to read files from disk """
        
        if default_dir==None:
            default_dir = os.getcwd()
        if title==None:
            title='Open File'
        
        qpaths = QtGui.QFileDialog.getOpenFileNames(self.MainWindow, title, default_dir,extension)
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
            
        qpath = QtGui.QFileDialog.getSaveFileName(self, title, default_dir,extension)
        path = str(qpath)
        return path
    
    ### readers/loaders
    def read_Data(self):
        """ data loader: opens a file dialog asking for  """
        ### FIXME !!
        self.paths = self.OpenFileDialog(title='Open data set', default_dir=self.cwd, extension='(*.tif *.ids *.lsm)')
        
        if len(self.paths) == 0:
            return None
        if len(self.paths) == 1:
            if self.paths[0].endswith('.ids'):
                print "load ids"
            else:
                pass
        if len(self.paths) > 1:
            # take care of: no mixed data formats
            # no multiple ids
            if any([path.endswith('.ids') for path in self.paths]):
                print "reading multiple .ids files is not supported because of possible metadata conflict"
                return None
            
            self.Data = Data_Object(self)
            self.Data.read_tifs(self.paths)
            
        return None
    
    ### writers/savers
    
    ### initializers
    def initialize_paths(self):
        """ initializes current working directory, path of the program
        path to the graphics files, path to tmp """
        
        self.cwd = os.getcwd()
        self.cwd = '/home/georg/python/better_than_turner/testdata/testdata_multi' # FIXME
        self.program_path = os.path.split(os.path.realpath(__file__))[0] # of the dir where this code is executed from!
        self.graphics_path = self.program_path + os.path.sep + 'graphics' 
        if os.name == 'posix': ### FIXME mac?
            self.tmp_path = '/tmp'
        else:
            self.tmp_path = 'C:\\Windows\\temp'
        pass
    
    def initialize_dataset(self):
        """ replaces old prepare_dataset"""
        # delete old data if present
        if self.Data != None:
            self.Data = None # take care that no extra references are generated and kept!
      
      # reset Data Display and Data Selector
        self.MainWindow.Data_Display.reset()
        self.MainWindow.Front_Control_Panel.Data_Selector.reset()
        
        # read in new data
        self.read_Data()
        
        # initialize Data display again
        self.Options.init_data()
        self.Data_Display.init_data()
        self.Data_Selector.init_data()
        pass
    
    ### messages
    def print_startup_msg(self):
        print
        print "this is ILTIS version" + self.version
        print "os type: ", os.name
        print "Process ID: ", os.getpid()

            
    def cleanup(self):
        """ remove tmp files """
        for dirpath, dirnames, filenames in os.walk(self.tmp_path):
            for filename in [f for f in filenames if f.endswith('.npa')]:
                filepath = os.path.join(dirpath, filename)
                if self.Options.general['verbose']:
                    print "removing file: ",filepath
                os.remove(filepath)
    pass


    pass

def main():
    # run application
    app = QtGui.QApplication(sys.argv)
    Iltis = Main(verbose=True)
   
    return_code = app.exec_()
    
    
    if return_code != 0:
        print "exiting with return code: ", return_code
        
    # after closing MainWindow, do cleanup and exit
    pg.exit() # the exit hammer
    pass


    
if __name__ == '__main__':
    main()
