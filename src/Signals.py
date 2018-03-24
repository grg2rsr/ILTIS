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
    activeROIsChangedSignal = QtCore.pyqtSignal()
    
    updateDisplaySettingsSignal = QtCore.pyqtSignal()

#    optionsUpdateSignal = QtCore.pyqtSignal()    
    
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
            self.Main.MainWindow.Options_Control]
            
        self.non_GUI_Objects = [
            self.Main.Options,
            self.Main.Processing,
            self.Main.IO,
            self.Main.Data,
            self.Main.ROIs]
                

        # reset signal
        for GUI_Object in self.GUI_Objects:
            self.resetSignal.connect(GUI_Object.reset)
        self.resetSignal.connect(self.Main.ROIs.reset)
        
        
        # init_data and update
        for GUI_Object in self.GUI_Objects:
            if not(GUI_Object == self.Main.MainWindow.Options_Control):
                self.initDataSignal.connect(GUI_Object.init_data)
                self.updateSignal.connect(GUI_Object.update)
        self.initDataSignal.connect(self.Main.MainWindow.enable_actions)
        self.initDataSignal.connect(self.Main.Options.init_data)
                
                
        # display settings
        slots = [self.Main.MainWindow.Data_Display.Frame_Visualizer.update_display_settings,
                 self.Main.MainWindow.Data_Display.Traces_Visualizer.update_display_settings,
                 self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_display_settings,
                 self.Main.MainWindow.Data_Display.LUT_Controlers.update_display_settings,
                 self.Main.ROIs.update_display_settings,
                 self.Main.Processing.first_time_dFF]
                 
        for slot in slots:
            self.updateDisplaySettingsSignal.connect(slot)
            
            
        # active ROIs changed
        slots = [self.Main.MainWindow.Data_Display.Traces_Visualizer.init_traces,
                 self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.init_traces]
                 
        for slot in slots:
            self.activeROIsChangedSignal.connect(slot)
                 

    pass