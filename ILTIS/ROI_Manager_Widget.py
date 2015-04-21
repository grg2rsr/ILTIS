# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:58:09 2015

@author: georg
"""
from PyQt4 import Qt, QtGui, QtCore
import pyqtgraph as pg
from Signals import Signals
from ROIs_Object import myCircleROI,myPolyLineROI


class ROI_Manager_Widget(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(ROI_Manager_Widget,self).__init__()
        
        self.Main = Main
        self.Front_Control_Panel = parent
        
        self.init_UI()
        
    def init_UI(self):
        
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['ROI label'])
        self.itemChanged.connect(self.Main.ROIs.ROI_label_change)
        self.cellClicked.connect(self.clicked)
        self.horizontalHeader().setStretchLastSection(True)
        pass

    def init_data(self):
        pass    
               
    def update(self):
        self.setRowCount(len(self.Main.ROIs.ROI_list))
        for i,ROI in enumerate(self.Main.ROIs.ROI_list):
            self.setItem(i,0,QtGui.QTableWidgetItem(ROI.label))

            if i == self.Main.Options.ROI['active_ROI_id']:
                if type(ROI) == myCircleROI:
                    ROI.setPen(pg.mkPen(pg.mkColor('y'),width=1.8)) ### FIXME layer pen and highlight pen
                if type(ROI) == myPolyLineROI:
                    for segment in ROI.segments:
                        segment.setPen(pg.mkPen(pg.mkColor('y'),width=1.8)) ### FIXME layer pen and highlight pen
            else:
                if type(ROI) == myCircleROI:
                    ROI.setPen(pg.mkPen(self.Main.Options.view['colors'][ROI.layer],width=1.8))
                if type(ROI) == myPolyLineROI:
                    for segment in ROI.segments:
                        segment.setPen(pg.mkPen(self.Main.Options.view['colors'][ROI.layer],width=1.8))
        
        if self.Main.Options.ROI['active_ROI_id'] != None:
            self.selectRow(self.Main.Options.ROI['active_ROI_id'])
        
    def reset(self):
        pass

    def clicked(self,row,col):
        self.Main.Options.ROI['active_ROI_id'] = row
        self.update()
        self.Main.Data_Display.Traces_Visualizer.update()  ### FIXME signal needed
         
    

if __name__ == '__main__':
    pass