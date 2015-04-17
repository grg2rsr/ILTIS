# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:11:53 2015

@author: georg
"""

from PyQt4 import Qt, QtGui, QtCore
import scipy as sp
import pyqtgraph as pg
from Data_Selector_Widget import Data_Selector_Widget
from ROI_Manager_Widget import ROI_Manager_Widget

class Front_Control_Panel_Widget(QtGui.QWidget): # has to interit from some pg.widget
    
    def __init__(self,Main,parent):
        super(Front_Control_Panel_Widget,self).__init__()
        
        self.Main = Main
#        self.Main.Front_Control_Panel = self
                
        self.MainWindow = parent
        self.Data_Selector = None
        self.ROI_Manager = None
        
        self.init_UI()

    pass

    def init_UI(self):
        # ini
        self.Data_Selector = Data_Selector_Widget(self.Main,self)
        self.ROI_Manager = ROI_Manager_Widget(self.Main,self)
        
        # layout
        self.Container = QtGui.QHBoxLayout()
        Splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        Splitter.addWidget(self.Data_Selector)
        Splitter.addWidget(self.ROI_Manager)
        self.Container.addWidget(Splitter)
        self.setLayout(self.Container)
        pass


if __name__ == '__main__':
    pass


