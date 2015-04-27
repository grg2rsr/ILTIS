# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:58:09 2015

@author: georg
"""
from PyQt4 import Qt, QtGui, QtCore
import pyqtgraph as pg


class ROI_Manager_Widget(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(ROI_Manager_Widget,self).__init__()
        
        self.Main = Main
        self.Front_Control_Panel = parent
        
        self.init_UI()
        
    def init_UI(self):
        
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['ROI label'])
        self.itemChanged.connect(self.Main.ROIs.ROI_label_change) # move function to this class?
        self.horizontalHeader().setStretchLastSection(True)
        
        # connect
        self.itemSelectionChanged.connect(self.selection_changed)
        
#        self.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection) 
        pass

    def init_data(self):

        pass    
               
    def update(self):
        """  """
        self.setRowCount(len(self.Main.ROIs.ROI_list))
        for i,ROI in enumerate(self.Main.ROIs.ROI_list):
            self.setItem(i,0,QtGui.QTableWidgetItem(ROI.label))

        [self.selectRow(i) for i in self.Main.Options.ROI['active_ROIs']]
        
    def reset(self):
        """ remove all rows ... """
        pass
        
    def selection_changed(self):     
        """ upon click in the table """
        selection = [item.row() for item in self.selectedItems()]
        if len(selection) == 1:
            [ROI.deactivate() for ROI in self.Main.ROIs.ROI_list]
        [ROI.activate() for ROI in [self.Main.ROIs.ROI_list[ind] for ind in selection]]
        self.Main.ROIs.set_active_ROIs()
        pass
         
    

if __name__ == '__main__':
    import Main
    Main.main()
    pass