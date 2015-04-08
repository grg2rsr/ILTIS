# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:11:53 2015

@author: georg
"""

from PyQt4 import QtGui, QtCore
import os
import scipy as sp
import pyqtgraph as pg
from ROI import myCircleROI,myPolyLineROI

class Front_Control_Panel(QtGui.QWidget): # has to interit from some pg.widget
    def __init__(self,Main,parent):
        super(Front_Control_Panel,self).__init__()
        
        self.Main = Main
        self.Main.Front_Control_Panel = self
        
        self.MainWindow = parent
        self.Data_Selector = None
        self.ROI_Manager = None
    
        self.initUI()
        
    pass

    def initUI(self):
        # ini
        self.Data_Selector = Data_Selector(self.Main,self)
        self.ROI_Manager = ROI_Manager(self.Main,self)
        
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


class Data_Selector(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(Data_Selector,self).__init__()

        self.Main = Main
        self.Main.Data_Selector = self
        
        self.Front_Control_Panel = parent      
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['select data'])
        self.horizontalHeader().setStretchLastSection(True)
        
        self.view_checkboxes = []

        pass
    
    def init_data(self):
        self.paths = self.Main.paths
        self.setRowCount(len(self.paths))
        ### checkboxes
        for n,path in enumerate(self.paths):
            checkbox = QtGui.QCheckBox(os.path.split(path)[1],self)
            checkbox.setCheckState(QtCore.Qt.Checked)
            self.setItem(n,0,QtGui.QTableWidgetItem(path))
            
            color = self.Main.Data_Display.colors[n]
            QColor = QtGui.QColor(*color)
            QColor.setAlpha(100)
            self.item(n,0).setBackgroundColor(QColor) # FIXME find color solutionQ

        self.itemSelectionChanged.connect(self.selection_changed)
        pass
    
    def selection_changed(self):
        selection = [item.row() for item in self.selectedItems()]
        last_selected = selection[-1]
        show_flags_updated = sp.zeros(len(self.paths),dtype='bool')
        show_flags_updated[selection] = 1
        self.Main.Options.view['show_flags'] = show_flags_updated
        self.Main.Options.view['last_selected'] = last_selected

        self.Main.LUT_Controlers.LUTwidgets.setCurrentWidget(self.Main.LUT_Controlers.LUTwidgets.widget(last_selected))
        self.Main.LUT_Controlers.LUTwidgets_dFF.setCurrentWidget(self.Main.LUT_Controlers.LUTwidgets_dFF.widget(last_selected))
        
        self.Main.Data_Display.update()        
        pass
    
    def reset(self):
        for checkbox in self.view_checkboxes:
            self.Container.removeWidget(checkbox)
            checkbox.deleteLater()
            checkbox = None
        self.checkboxes = []
        self.view_checkboxes = []
        pass
        
    pass

    

class ROI_Manager(QtGui.QTableWidget): # has to inherit from pg.widget
    def __init__(self,Main,parent):
        super(ROI_Manager,self).__init__()
        
        self.Main = Main
        self.Main.ROI_Manager = self
        
        self.Front_Control_Panel = parent
#        self.setRowCount(len(self.Main.ROIs.ROI_list))
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
        self.Main.Data_Display.Traces_Visualizer.update()
         
    




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


