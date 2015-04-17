# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:30:14 2015

@author: georg
"""

from PyQt4 import QtCore

class Signals(QtCore.QObject):
 
   # global signals
    updateSignal = QtCore.pyqtSignal() # can have 'all','traces','frame'
    resetSignal = QtCore.pyqtSignal()
    initUISignal = QtCore.pyqtSignal()
    initDataSignal= QtCore.pyqtSignal()
    LUTchangedSignal = QtCore.pyqtSignal()

    # roi changed
    # lut changed
    # mouseClicked
    # lut levels changed
    #

    
    def __init__(self,parent):
        super(Signals,self).__init__()
        
        self.Main = parent

        self.GUI_Objects = [
            self.Main.MainWindow.Data_Display.Frame_Visualizer,
            self.Main.MainWindow.Data_Display.LUT_Controlers,
            self.Main.MainWindow.Data_Display.Traces_Visualizer,
            self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted,
            self.Main.MainWindow.Front_Control_Panel.Data_Selector,
            self.Main.MainWindow.Front_Control_Panel.ROI_Manager,
            self.Main.Options_Control]
            
        self.non_GUI_objects = [
            self.Main.Options,
            self.Main.Processing,
            self.Main.IO,
            self.Main.Data,
            self.Main.ROIs]
        

        # update signal
        update_slots = [self.Main.MainWindow.Data_Display.Frame_Visualizer.update,
                        self.Main.MainWindow.Data_Display.LUT_Controlers.update,
                        self.Main.MainWindow.Data_Display.Traces_Visualizer.update,
                        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update
#                        self.Main.MainWindow.Front_Control.Data_selector.update, # unclear if needed
#                        self.Main.MainWindow.Front_Control.ROI_Manager.update # unclear if needed
                        ]

        for slot in update_slots:
            self.updateSignal.connect(slot)
            
        # init_data
        for GUI_object in self.GUI_Objects:
            if not(GUI_object == self.Main.Options_Control):
                self.initDataSignal.connect(GUI_object.init_data)
                
        # LUTchanged
        self.LUTchangedSignal.connect(self.Main.Data_Display.Frame_Visualizer.update)

    pass