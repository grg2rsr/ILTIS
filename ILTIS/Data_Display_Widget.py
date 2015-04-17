# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:10:05 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

from Frame_Visualizer_Widget import Frame_Visualizer_Widget
from LUT_Controlers_Widget import LUT_Controlers_Widget
from Traces_Visualizer_Widget import Traces_Visualizer_Widget
from Traces_Visualizer_Stimsorted_Widget import Traces_Visualizer_Stimsorted_Widget

class Data_Display_Widget(QtGui.QMainWindow): # needs to be a QMainWindow to have dockable floating Widgets
    def __init__(self,Main,parent):
        super(Data_Display_Widget,self).__init__()

        self.Main = Main
#        self.Main.Data_Display = self
        self.MainWindow = parent
        
        self.Frame_Visualizer = None
        self.LUT_Controlers = None
        self.Traces_Visualizer = None
        self.Traces_Visualizer_Stimsorted = None
        
#        self.color_maps = None
#        self.colors = None
        
        self.init_UI()
        pass
        
    def init_UI(self):
        # ini the widgets
        self.Frame_Visualizer = Frame_Visualizer_Widget(self.Main,self)
        self.LUT_Controlers = LUT_Controlers_Widget(self.Main,self)
        self.Traces_Visualizer = Traces_Visualizer_Widget(self.Main,self)
        self.Traces_Visualizer_Stimsorted = Traces_Visualizer_Stimsorted_Widget(self.Main,self)
        
        ### possible implement darker background color
#        palette = QtGui.QPalette(QtGui.QColor(90,90,90,90))
#        self.setPalette(palette)
        
        ### layout
        # The main Layout: Stacks Frame_Visualizer (+ LUT_Controlers) and Traces_Visualizer
        
        # Frame_Visualizer + LUT_Controlers
        self.FrameWidget = QtGui.QWidget(self)
        self.FrameLayout = QtGui.QHBoxLayout()
        self.FrameLayout.setMargin(0)
        self.FrameLayout.setSpacing(0)
        self.FrameLayout.addWidget(self.Frame_Visualizer)
        self.FrameLayout.addWidget(self.LUT_Controlers)
        self.FrameLayout.setStretchFactor(self.Frame_Visualizer,5)
        self.FrameLayout.setStretchFactor(self.LUT_Controlers,1)
        self.FrameWidget.setLayout(self.FrameLayout)

        self.setCentralWidget(self.FrameWidget)

        self.Traces_Dock = QtGui.QDockWidget(self)
        self.Traces_Tabbed = QtGui.QTabWidget(self)
        
        self.Traces_Tabbed.addTab(self.Traces_Visualizer,'common timebase')
        self.Traces_Tabbed.addTab(self.Traces_Visualizer_Stimsorted,'sorted to stimulus class')
        tabBar = self.Traces_Tabbed.tabBar()
        for i in range(2):
            tabBar.setTabTextColor(i,QtGui.QColor(0,0,0,255)) # no idea why, but it defaults to white ... 
            
        self.Traces_Dock.setWidget(self.Traces_Tabbed)
        self.Traces_Dock.setFloating(False)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.Traces_Dock)
           

if __name__ == '__main__':
    pass