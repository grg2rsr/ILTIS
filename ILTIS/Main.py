# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:29:30 2015

@author: georg
"""
import os
import sys

# quite ugly setting of proper imports
this_dir = os.path.split(os.path.realpath(__file__))[0] # this directroy
par_dir = os.path.sep.join([this_dir,os.pardir])
sys.path.append(par_dir)

# this is necessary for machines that have pyqtgraph already installed as it enforces import of the one from local lib
# pyqtgraph_path = os.path.sep.join([par_dir,'lib','pyqtgraph-master']) # path to the local pg
# sys.path.insert(0,pyqtgraph_path)

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
print 'using pyqtgraph at', pg.__file__
from Options_Object import Options_Object

from Processing_Object import Processing_Object
from MainWindow_Widget import MainWindow_Widget
from ROIs_Object import ROIs_Object
from IO_Object import IO_Object

import scipy as sp
from Signals import Signals


#pg.setConfigOption("useOpenGL", True)
pg.setConfigOptions(antialias=True)

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

        self.initialize_paths()
        self.print_startup_msg()

        # ini
        self.IO = IO_Object(self)
        self.Options = Options_Object(self)
        self.Processing = Processing_Object(self)
        self.ROIs = ROIs_Object(self)

        self.MainWindow = MainWindow_Widget(self)

        # centrally managed signals
        self.Signals = Signals(self)


    ### initializers
    def initialize_paths(self):
        """ initializes current working directory, path of the program
        path to the graphics files, path to tmp """

        self.cwd = os.getcwd()
        self.program_dir = os.path.split(os.path.realpath(__file__))[0] # of the dir where this code is executed from!
        self.graphics_path = self.program_dir + os.path.sep + 'graphics'
        if os.name == 'posix':
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
