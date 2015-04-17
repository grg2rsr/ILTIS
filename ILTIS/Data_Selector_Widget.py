# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:57:18 2015

@author: georg
"""
from PyQt4 import Qt, QtGui, QtCore
import scipy as sp

class Data_Selector_Widget(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(Data_Selector_Widget,self).__init__()

        self.Main = Main
#        self.Main.Data_Selector = self
        self.Front_Control_Panel = parent
        self.init_UI()
        
    def init_UI(self):
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['select data'])
        self.horizontalHeader().setStretchLastSection(True)
        pass
    
    def init_data(self):
                
        self.paths = self.Main.Data.Metadata.paths
        self.setRowCount(len(self.paths))
        
        # table entries
        for n,path in enumerate(self.paths):
            self.setItem(n,0,QtGui.QTableWidgetItem(path))
            
            color = self.Main.Options.view['colors'][n]
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
        
        self.verticalHeader().setStyle(QtGui.QStyleFactory.create('Cleanlooks')) # check on windows machines
        pass
    
    def update(self):
        # from monochrome toggler        
        if self.Main.Options.view['show_monochrome'] == True:
            # disable all except the last selected dataset
            self.clearSelection()
            self.selectRow(self.Main.Options.view['last_selected'])
            self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)

        if self.Main.Options.view['show_monochrome'] == False:        
            self.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection) 
    
    def reset(self):
        """ emtpy table """
        for n,path in enumerate(self.paths):
            item = self.takeItem(n,0)
            item = None
        pass
    
    def selection_changed(self):     
        selection = [item.row() for item in self.selectedItems()]
        if len(selection) > 0:
            last_selected = selection[-1] # FIXME this sometimes throws errors
            show_flags_updated = sp.zeros(len(self.paths),dtype='bool')
            show_flags_updated[selection] = 1
            self.Main.Options.view['show_flags'] = show_flags_updated
            self.Main.Options.view['last_selected'] = last_selected
            self.Main.Signals.updateSignal.emit()
            
        pass

    
    pass