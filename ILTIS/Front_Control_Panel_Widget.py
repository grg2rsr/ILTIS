# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:11:53 2015

@author: georg
"""

from PyQt4 import Qt, QtGui, QtCore
import scipy as sp
import pyqtgraph as pg
from ROIs_Object import myCircleROI,myPolyLineROI
from Signals import Signals

class Front_Control_Panel_Widget(QtGui.QWidget): # has to interit from some pg.widget
    
    def __init__(self,Main,parent):
        super(Front_Control_Panel_Widget,self).__init__()
        
        self.Main = Main
        self.Main.Front_Control_Panel = self
        
        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated' 
            print('%s: %s\n' % (self.objectName(), QtCore.QThread.currentThreadId()))
        
        self.MainWindow = parent
        self.Data_Selector = None
        self.ROI_Manager = None
        
        self.Signals = Signals()
        self.initUI()
            


    pass

    def initUI(self):
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
        
#        self.Container = QtGui.QVBoxLayout()
#        self.Container.addWidget(self.Data_Selector)
#        self.Container.addWidget(self.ROI_Manager)
#        self.setLayout(self.Container)
        
        
        pass


class Data_Selector_Widget(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(Data_Selector_Widget,self).__init__()

        self.Main = Main
        self.Main.Data_Selector = self

        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated'
            print('%s: %s\n' % (self.objectName(), QtCore.QThread.currentThreadId()))

        self.Front_Control_Panel = parent      
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['select data'])
        self.horizontalHeader().setStretchLastSection(True)
        
        self.Signals = Signals()
        slots = [self.Main.Data_Display.Frame_Visualizer.reset,
                 self.Main.Data_Display.LUT_Controlers.reset,
                 self.Main.Data_Display.Traces_Visualizer.reset,
                 self.Main.Data_Display.Traces_Visualizer_Stimsorted.reset]

        for slot in slots:
            self.Signals.display_settings_changed_signal.connect(slot)
    
    def init_data(self):
                
        self.paths = self.Main.paths
        self.setRowCount(len(self.paths))
        
        # table entries
        for n,path in enumerate(self.paths):
            self.setItem(n,0,QtGui.QTableWidgetItem(path))
            
            color = self.Main.Data_Display.colors[n]
            QColor = QtGui.QColor(*color)
            QColor.setAlpha(100)
            self.item(n,0).setBackgroundColor(QColor) # FIXME find color solution

            verticalHeader = QtGui.QTableWidgetItem(str(n))            
            verticalHeader.setBackgroundColor(QColor)
#            verticalHeader.setBackground(QtGui.QBrush(QColor))
            
            QColor.setAlpha(255)
            verticalHeader.setForeground(QColor)
            
            self.setVerticalHeaderItem(n,verticalHeader)

        # connect
        self.itemSelectionChanged.connect(self.selection_changed)
        
        # select all on startup
        selection = QtGui.QTableWidgetSelectionRange(0,0,len(self.paths)-1,0)
        self.setRangeSelected(selection,True)
        
        self.verticalHeader().setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        pass
    
    def selection_changed(self):     
        selection = [item.row() for item in self.selectedItems()]
        if len(selection) > 0:
            last_selected = selection[-1] # FIXME this sometimes throws errors
            show_flags_updated = sp.zeros(len(self.paths),dtype='bool')
            show_flags_updated[selection] = 1
            self.Main.Options.view['show_flags'] = show_flags_updated
            self.Main.Options.view['last_selected'] = last_selected
            self.Signals.display_settings_changed_signal.emit()
            
        pass

    def mode_update(self):
        """ connected to monochrome toggler """
        ## from monochrome toggler        
        if self.Main.Options.view['show_monochrome'] == True:
            # disable all except the last selected dataset
            self.clearSelection()
            self.selectRow(self.Main.Options.view['last_selected'])
            self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)

        if self.Main.Options.view['show_monochrome'] == False:        
            """ fix: emit set_selection_mode_signal('multicolor') """
            self.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection) 

    def reset(self):
        pass
    
    
    
    pass

    

class ROI_Manager_Widget(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(ROI_Manager_Widget,self).__init__()
        
        self.Main = Main
        self.Main.ROI_Manager = self
        
        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated'     
            print('%s: %s\n' % (self.objectName(), QtCore.QThread.currentThreadId()))

        self.Front_Control_Panel = parent
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['ROI label'])
        self.itemChanged.connect(self.Main.ROIs.ROI_label_change)
        self.cellClicked.connect(self.clicked)
        self.horizontalHeader().setStretchLastSection(True)
        
    def init():
        pass
    
               
    def update(self):
        self.setRowCount(len(self.Main.ROIs.ROI_list))
        for i,ROI in enumerate(self.Main.ROIs.ROI_list):
            self.setItem(i,0,QtGui.QTableWidgetItem(ROI.label))

            if i == self.Main.ROIs.active_ROI_id:
                if type(ROI) == myCircleROI:
                    ROI.setPen(pg.mkPen(pg.mkColor('y'),width=1.8)) ### FIXME layer pen and highlight pen
                if type(ROI) == myPolyLineROI:
                    for segment in ROI.segments:
                        segment.setPen(pg.mkPen(pg.mkColor('y'),width=1.8)) ### FIXME layer pen and highlight pen
            else:
                if type(ROI) == myCircleROI:
                    ROI.setPen(pg.mkPen(self.Main.Data_Display.colors[ROI.layer],width=1.8))
                if type(ROI) == myPolyLineROI:
                    for segment in ROI.segments:
                        segment.setPen(pg.mkPen(self.Main.Data_Display.colors[ROI.layer],width=1.8))
                    
        self.selectRow(self.Main.ROIs.active_ROI_id)
        
    def clicked(self,row,col):
        self.Main.ROIs.active_ROI_id = row
        self.update()
        self.Main.Data_Display.Traces_Visualizer.update()  ### FIXME signal needed
         
    




if __name__ == '__main__':
    pass


### control panel on the right side
        # syntax is define - connect - add
        # load data
#        self.load_labels_btn = QtGui.QPushButton('load trial labels',self)
#        self.load_labels_btn.clicked.connect(self.rename_checkboxes)
#        self.control_panel_layout.addWidget(self.load_labels_btn)
        
        # checkboxes for datasets
#        self.control_panel_layout.addStretch()


