# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:10:05 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph import dockarea as pgd
from pyqtgraph.dockarea.Dock import DockLabel

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

        self.DockArea = pg.dockarea.DockArea()
        self.setCentralWidget(self.DockArea)

        self.FrameDock = pgd.Dock('current frame',size=(10,10),autoOrientation=False)
        self.TracesDock = pgd.Dock('traces with common time base',size=(10,10))
        self.TracesStimsortedDock = pgd.Dock('traces sorted to stim class',size=(10,10))
        
#        self.FrameDock = myDock('current frame',size=(10,10),autoOrientation=False)
#        self.TracesDock = myDock('traces with common time base',size=(10,10))
#        self.TracesStimsortedDock = myDock('traces sorted to stim class',size=(10,10))
       
        self.DockArea.addDock(dock=self.FrameDock,position='top')
        self.DockArea.addDock(dock=self.TracesDock,position='bottom')
        self.DockArea.addDock(dock=self.TracesStimsortedDock,position = 'below', relativeTo=self.TracesDock)
        
        self.FrameDock.addWidget(self.FrameWidget)
        self.TracesStimsortedDock.addWidget(self.Traces_Visualizer_Stimsorted)
        self.TracesDock.addWidget(self.Traces_Visualizer)

#        import pdb
#        pdb.set_trace()
#
#
#
#        self.setCentralWidget(self.FrameWidget)
#        
#        # Traces Visualizers as tabbed in a dockable
#        self.Traces_Dock = QtGui.QDockWidget(self)
#        self.Traces_Tabbed = Sized_Tab(self)        
#        self.Traces_Tabbed.addTab(self.Traces_Visualizer,'overlay')
#        self.Traces_Tabbed.addTab(self.Traces_Visualizer_Stimsorted,'sorted')
#        
#        tabBar = self.Traces_Tabbed.tabBar()
#        self.Traces_Tabbed.setTabPosition(2) # the 'west'
#        for i in range(2):
#            tabBar.setTabTextColor(i,QtGui.QColor(0,0,0,255)) # no idea why, but it defaults to white ... 
#            
#        self.Traces_Dock.setWidget(self.Traces_Tabbed)
#        self.Traces_Dock.setFloating(False)
##        self.Traces_Dock.setWindowTitle('rudel')
##        self.Traces_Dock.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar and QtGui.QDockWidget.DockWidgetMovable and QtGui.QDockWidget.DockWidgetClosable)
##        self.Traces_Dock.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar)
#
#        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.Traces_Dock)

class myDock(pgd.Dock):
    def __init__(self,name,**kwargs):
        super(myDock,self).__init__(name,**kwargs)
        self.label = myDockLabel(name,self)
        
class myDockLabel(DockLabel):
    def updateStyle(self):
        r = '3px'
        if self.dim:
            fg = '#aaa'
            bg = '#4aa'
            border = '#339'
        else:
            fg = '#fff'
            bg = '#66c'
            border = '#55B'
        
        if self.orientation == 'vertical':
            self.vStyle = """DockLabel { 
                background-color : %s; 
                color : %s; 
                border-top-right-radius: 0px; 
                border-top-left-radius: %s; 
                border-bottom-right-radius: 0px; 
                border-bottom-left-radius: %s; 
                border-width: 0px; 
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel { 
                background-color : %s; 
                color : %s; 
                border-top-right-radius: %s; 
                border-top-left-radius: %s; 
                border-bottom-right-radius: 0px; 
                border-bottom-left-radius: 0px; 
                border-width: 0px; 
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.hStyle)
            
class Sized_Tab(QtGui.QTabWidget):
    # from http://stackoverflow.com/a/13715893/4749250
    def sizeHint(self):
        return QtCore.QSize(200, 200)
        
if __name__ == '__main__':
    import Main
    Main.main()
    pass