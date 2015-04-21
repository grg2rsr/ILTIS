# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:30:14 2015

@author: georg
"""

from PyQt4 import QtCore

class Signals(QtCore.QObject):
 
   # global signals
    updateSignal = QtCore.pyqtSignal()
    updateTracesSignal = QtCore.pyqtSignal() # this not used because of speed reasons
    updateFrameSignal = QtCore.pyqtSignal() # this is not used because of speed reasons
    LUTchangedSignal = QtCore.pyqtSignal() # this is not used because of speed reasons

    updateDisplaySettingsSignal = QtCore.pyqtSignal()

    optionsUpdateSignal = QtCore.pyqtSignal()    
    
    resetSignal = QtCore.pyqtSignal()
    initDataSignal= QtCore.pyqtSignal()

    
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
        

#        # update signal
#        update_slots = [self.Main.MainWindow.Data_Display.Frame_Visualizer.update,
#                        self.Main.MainWindow.Data_Display.LUT_Controlers.update,
#                        self.Main.MainWindow.Data_Display.Traces_Visualizer.update,
#                        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update,
#                        self.Main.MainWindow.Front_Control_Panel.Data_Selector.update, # unclear if needed
#                        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update # unclear if needed
#                        ]
#
#        for GUI_object in self.GUI_Objects:
#            if not(GUI_object == self.Main.Options_Control):
#            self.updateSignal.connect(slot)
        
        
        # update Traces signal
#        self.updateTracesSignal.connect(self.Main.MainWindow.Data_Display.Traces_Visualizer.update)
#        self.updateTracesSignal.connect(self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update)
        
        # update Frame
#        self.updateFrameSignal.connect(self.Main.MainWindow.Data_Display.Frame_Visualizer.update)
        
        # init_data and update
        for GUI_object in self.GUI_Objects:
            if not(GUI_object == self.Main.Options_Control):
                self.initDataSignal.connect(GUI_object.init_data)
                self.updateSignal.connect(GUI_object.update)
        self.initDataSignal.connect(self.Main.MainWindow.enable_actions)
                
        # display settings
        slots = [self.Main.MainWindow.Data_Display.Frame_Visualizer.update_display_settings,
                 self.Main.MainWindow.Data_Display.Traces_Visualizer.update_display_settings,
                 self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_display_settings,
                 self.Main.MainWindow.Data_Display.LUT_Controlers.update_display_settings,
                 self.Main.Processing.first_time_dFF]
                 
        for slot in slots:
            self.updateDisplaySettingsSignal.connect(slot)
                 

    pass