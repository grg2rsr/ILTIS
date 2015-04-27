# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:29:30 2015

@author: georg
"""
import os
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0] + os.path.sep + os.pardir) # this fixes imoprt issues if run by script from a different folder
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from Options_Object import Options_Object
from Options_Control_Widget import Options_Control_Widget
from Processing_Object import Processing_Object
from MainWindow_Widget import MainWindow_Widget
from ROIs_Object import ROIs_Object
from IO_Object import IO_Object

import scipy as sp
from Signals import Signals

pg.setConfigOptions(antialias=True)


""" note: cleanup functionality is commented out. reimplement as soon as signal/
slot mechanism is running """

class Main(QtCore.QObject):
    
    def __init__(self,verbose=False):
        super(Main,self).__init__()
        
        # fields
        self.cwd = None
        self.program_dir = None
        self.graphics_path = None # move to MainWindow
        self.tmp_path = None
        self.Data = None
        self.verbose = verbose
        
        # initialize
#        self.version = os.path.splitext(__file__)[0][-3:] # FIXME
        
        self.initialize_paths()
        self.print_startup_msg()

        ## here is the ini order ...  first all nonGUI
        self.IO = IO_Object(self)
        self.Options = Options_Object(self)
        self.Options_Control = Options_Control_Widget(self)
        self.Options_Control.init_UI() # this is necessary because of a circular reference btw Options and Options_Control
        self.Processing = Processing_Object(self)
        self.ROIs = ROIs_Object(self)

        self.MainWindow = MainWindow_Widget(self)
        
        ## Signals # centrally managed connections work, and all slots are ready at this timepoint in the code
        self.Signals = Signals(self)
        
        ### HACKED IN FOR TESTINGS START
        self.IO.init_data()
    
    ### initializers
    def initialize_paths(self):
        """ initializes current working directory, path of the program
        path to the graphics files, path to tmp """
        
        self.cwd = os.getcwd()
        self.cwd = '/home/georg/python/better_than_turner/testdata/testdata_multi' # FIXME
        self.program_dir = os.path.split(os.path.realpath(__file__))[0] # of the dir where this code is executed from!
        self.graphics_path = self.program_dir + os.path.sep + 'graphics' 
        if os.name == 'posix': ### FIXME mac?
            self.tmp_path = '/tmp'
        else:
            self.tmp_path = 'C:\\Windows\\temp'
    
    
    ### messages
    def print_startup_msg(self):
        
        print "no startup msg set"
#        print "this is ILTIS version" + self.version
#        print "os type: ", os.name
#        print "Process ID: ", os.getpid()

            
#    def cleanup(self):
#        """ remove tmp files """
#        for dirpath, dirnames, filenames in os.walk(self.tmp_path):
#            for filename in [f for f in filenames if f.endswith('.npa')]:
#                filepath = os.path.join(dirpath, filename)
#                if self.Options.general['verbose']:
#                    print "removing file: ",filepath
#                os.remove(filepath)

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
