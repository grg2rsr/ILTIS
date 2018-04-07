# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:58:09 2015

@author: georg
"""
from PyQt4 import Qt, QtGui, QtCore
import lib.pyqtgraph as pg
import scipy as sp


class ROI_Manager_Widget(QtGui.QTableWidget):
    def __init__(self,Main,parent):
        super(ROI_Manager_Widget,self).__init__()

        self.Main = Main
        self.Front_Control_Panel = parent
        self.init_UI()

    def init_UI(self):
        # UI
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['ROI label'])
        self.horizontalHeader().setStretchLastSection(True)

        # connect
        self.itemSelectionChanged.connect(self.selection_changed)
        self.itemChanged.connect(self.Main.ROIs.ROI_label_change) # move function to this class?

        pass

    def connect(self):
        pass

    def init_data(self):
        pass

    def update(self):
        # redraw the table
        self.blockSignals(True) # signal block because itemSelectionChange would be emitted
        self.setRowCount(len(self.Main.ROIs.ROI_list))
        for i,ROI in enumerate(self.Main.ROIs.ROI_list):
            self.setItem(i,0,QtGui.QTableWidgetItem(ROI.label))
        self.blockSignals(False) # signal block because itemSelectionChange would be emitted
#        self.set_current_selection(self.Main.Options.ROI['active_ROIs'])

    def reset(self):
        """ remove all rows ... """
        pass

    def get_current_selection(self):
        """ returns the current selection as a boolean vector """
        selected = [item.row() for item in self.selectedItems()]
        boolvec = sp.zeros(self.rowCount(),dtype='bool')
        boolvec[selected] = True
        return boolvec

    def set_current_selection(self):
        """ sets the current displayed selection based on the ROI states """

        self.blockSignals(True) # signal block because itemSelectionChange would be emitted
        for i,state in enumerate(self.Main.ROIs.get_active_ROIs()[0]):
            self.item(i,0).setSelected(state)
        self.blockSignals(False)

    def selection_changed(self):
        """ ONLY used upon click in the table
        but: a removed active ROI also causes a itemSelectionChanged to be emitted"""
        selection = self.get_current_selection()

        # dirty hack but when the last ROI is removed, the len
        for i,state in enumerate(selection):
            self.Main.ROIs.ROI_list[i].active = state

        # write active selection to options and calls self.update through the emission of activeROIsChangedSignal
        self.Main.ROIs.update_active_ROIs()
        pass



if __name__ == '__main__':
    from . import Main
    Main.main()
    pass
