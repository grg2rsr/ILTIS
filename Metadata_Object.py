# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:02:55 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
    
        self.menuBar
        self.statusBar
        self.Data_Display
        self.Front_Control_Panel
        
        self.setup_MenuBar()
        self.setup_ToolBar()
        self.setup_StatusBar()
    pass

    def setup_MenuBar():
        pass
    
    def setup_ToolBar():
        pass
    
    def setup_StatusBar():
        pass
    


if __name__ == '__main__':
    pass


#==============================================================================
# Interface stucture
# menu bar
# -Open
# --load dataset (=data object)
# --import tifs
# --coors
# --trial labels
# --lst
# 
# -Save
# --as dataset
# --as traces
# --as glodatamix
# 
# -preferences w tabs
# --general export options
# --movie export options
# --
# 
# -process
# --filter
# --jan soelters stuff
# 
# -help
# --help
# --about
# 
# view options on the toolbar
# -dff
# -avg
# -mono
# 
#
#ROI options in toolbar -write into options dict
#-shape
#-size
#==============================================================================
