# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:02:55 2015

@author: georg
"""
from qtpy import QtGui, QtCore
import os
from Data_Display_Widget import Data_Display_Widget
from Front_Control_Panel_Widget import Front_Control_Panel_Widget
from Options_Control_Widget import Options_Control_Widget
import qtawesome as qta

class MainWindow_Widget(QtGui.QMainWindow):
    def __init__(self,parent):
        super(MainWindow_Widget,self).__init__()
        
        # fields
        self.Main = parent
        self.Main.MainWindow = self
        
        self.MenuBar = None
        self.ToolBar = None
        self.StatusBar = None
        self.Data_Display = None
        self.Front_Control_Panel = None
        self.Options_Control = None

        # actions
        self.toggleMonochromeAction = None
        self.ReadCoorAction = None
        self.toggleGlobalLevels = None
        self.WriteTracesAction = None
        self.WriteROIAction = None
        self.WriteMovieAction = None
        self.WriteTracesAction = None
        self.OpenAction = None
        self.ReadCoorAction = None
        self.ReadLSTAction = None
        self.ReadTrialLabelsAction = None
        self.toggleAvgAction = None
        self.toggleMonochromeAction = None
        
        # layout
        self.Container = None
        self.Splitter = None
        
        # initializations
        self.setup_Actions()
        self.setup_MenuBar()
        self.setup_ToolBar()
        self.setup_StatusBar()
        

        self.initUI()

        pass

    def initUI(self):
        """ """
        # ini
        self.Data_Display = Data_Display_Widget(self.Main,self)
        self.Front_Control_Panel = Front_Control_Panel_Widget(self.Main,self)
        self.Container = QtGui.QWidget()
        
        # splitter variant
        self.Splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.Splitter.addWidget(self.Data_Display)
        self.Splitter.addWidget(self.Front_Control_Panel)
        
        self.setCentralWidget(self.Splitter)
        
#        self.setWindowIcon(QtGui.QIcon(self.Main.graphics_path + os.path.sep + )) ### FIXME
        self.setWindowTitle('ILTIS')

        # extra Widgets
        self.Options_Control = Options_Control_Widget(self.Main,self)
        self.show()
        pass
    
    def setup_MenuBar(self):

        self.Menubar = self.menuBar()
        Open = self.Menubar.addMenu('&Open')
        Open.addAction(self.OpenAction)
        Open.addAction(self.ReadCoorAction)
        Open.addAction(self.ReadLSTAction)
        Open.addAction(self.ReadTrialLabelsAction)
        
        Save = self.Menubar.addMenu('&Save')
        Save.addAction(self.WriteROIAction)
        Save.addAction(self.WriteMovieAction)
        Save.addAction(self.WriteTracesAction)
        
        Options = self.Menubar.addMenu('&Options')
        Options.addAction(self.OpenOptions)
        
        Process = self.Menubar.addMenu('&Process')
        Process.addAction(self.ApplyFilterAction)
        Process.addAction(self.RunMocoSingleAction)
        Process.addAction(self.RunMocoAlignAction)
        Process.addAction(self.RunSegmentationAction)
        
        Help = self.Menubar.addMenu('&Help')

        
        pass
    
    def setup_ToolBar(self):
        self.ToolBar = self.addToolBar('Exit')
        self.ToolBar.addAction(self.toggledFFAction)
        self.ToolBar.addAction(self.toggleMonochromeAction)
        self.ToolBar.addAction(self.toggleAvgAction)
        self.ToolBar.addAction(self.toggleGlobalLevels)

        pass
    
    def setup_StatusBar(self):
        self.StatusBar = self.statusBar()
        pass
    
    def setup_action(self,action_dict,disable=False):
        Action = QtGui.QAction(QtGui.QIcon(action_dict['icon']), action_dict['label'],self)
        Action.setStatusTip(action_dict['status_tip'])
        if disable:
            Action.setDisabled(True)
        return Action
        
    def setup_Actions(self):
        
#==============================================================================
# Readers
#==============================================================================
        OpenActionDict = {'name':'OpenAction',
                          'label':'Load Data',
                          'status_tip':'Read data from disk',
                          'icon':'',
                          'func':''} # for future use w connect
        
        self.OpenAction = self.setup_action(OpenActionDict)
        self.OpenAction.triggered.connect(self.Main.initialize_dataset)
#        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()')) # exact statement
        
        ### load .coor
        ReadCoorDict = {'name':'ReadCoorAction',
                        'label':'Load .coor file',
                        'status_tip':'Read .coor file from disk',
                        'icon':self.Main.graphics_path + os.path.sep + 'open_coor.png',
                        'func':''} # for future use w connect
        self.ReadCoorAction = self.setup_action(ReadCoorDict,disable=True)
#        self.load_coor.triggered.connect(self.BTT.load_coors)
        
        ### load .lst
        ReadLSTDict = {'name':'ReadLSTAction',
                        'label':'Load .lst file',
                        'status_tip':'Read .lst file from disk',
                        'icon':self.Main.graphics_path + os.path.sep + 'open_lst.png',
                        'func':''} # for future use w connect
        self.ReadLSTAction = self.setup_action(ReadLSTDict,disable=True)
        
#        self.load_lst.triggered.connect(self.BTT.read_lst)

        ### load .lst
        ReadTrialLabelsDict = {
                        'name':'ReadTrialLabelsAction',
                        'label':'Load trial labels file',
                        'status_tip':'Read trial labels from text file',
                        'icon':self.Main.graphics_path + os.path.sep + 'open_lst.png',
                        'func':''} # for future use w connect
                        
        self.ReadTrialLabelsAction = self.setup_action(ReadTrialLabelsDict,disable=True)
        
#        self.load_lst.triggered.connect(self.BTT.read_lst)
        
#==============================================================================
# Writers      
#==============================================================================
        ### export ROIs
        WriteROIDict = {
                        'name':'WriteROIAction',
                        'label':'save ROIs',
                        'status_tip':'save current ROIs as a .roi file',
                        'icon':self.Main.graphics_path + os.path.sep + 'write_coor.png', ### FIXME proper rename of image
                        'func':''} # for future use w connect
        self.WriteROIAction = self.setup_action(WriteROIDict,disable=True)
#        self.write_coor.triggered.connect(self.BTT.write_extraction_mask)
        
        ### export movie
        WriteMovieDict = {
                        'name':'WriteMovieDict',
                        'label':'save Movie',
                        'status_tip':'save a movie of the current view',
                        'icon':self.Main.graphics_path + os.path.sep + 'write_movie.png', 
                        'func':''} # for future use w connect
        self.WriteMovieAction = self.setup_action(WriteMovieDict,disable=True)
#        self.write_movie.triggered.connect(self.BTT.export_movie)
        
        ### export traces
        WriteTracesDict = {
                        'name':'WriteTracesDict',
                        'label':'save traces',
                        'status_tip':'extract traces from the current ROIs and save them',
                        'icon':self.Main.graphics_path + os.path.sep + 'write_traces.png', 
                        'func':''} # for future use w connect
        self.WriteTracesAction = self.setup_action(WriteTracesDict,disable=True)
#        self.write_traces.triggered.connect(self.BTT.export_traces)
        pass


#==============================================================================
# Display switches
#==============================================================================
        ### display dF/F
        self.toggledFFAction = QtGui.QAction(qta.icon('fa.folder-open'), 'Display dFF',self)        
#        self.toggledFFAction = QtGui.QAction(QtGui.QIcon(self.Main.graphics_path + os.path.sep + 'calc_dFF.png'), 'Display dFF',self)
        self.toggledFFAction.setStatusTip('Toggles dF/F')       
        self.toggledFFAction.setCheckable(True)
        self.toggledFFAction.triggered.connect(self.Main.Options.toggle_dFF)
        
        ### global Levels control
        self.toggleGlobalLevels = QtGui.QAction(QtGui.QIcon(self.Main.graphics_path + os.path.sep + 'globe.png'), 'toggle global level use',self)
        self.toggleGlobalLevels.setStatusTip('Global Levels control')
        self.toggleGlobalLevels.setCheckable(True)
        self.toggleGlobalLevels.triggered.connect(self.Main.Options.toggle_global_levels)
        
        ### display average frame
        self.toggleAvgAction = QtGui.QAction(QtGui.QIcon(self.Main.graphics_path + os.path.sep + 'avg.png'),'Display Avg',self)
        self.toggleAvgAction.setStatusTip('Toggles avg')
        self.toggleAvgAction.setCheckable(True)
        self.toggleAvgAction.triggered.connect(self.Main.Options.toggle_avg_img)
        
        ### Monochrome mode
        self.toggleMonochromeAction = QtGui.QAction(QtGui.QIcon(self.Main.graphics_path + os.path.sep + 'toggle_color.png'),'Monochrome',self)
        self.toggleMonochromeAction.setStatusTip('Toggles Monochrome mode')      
        self.toggleMonochromeAction.setCheckable(True)
        self.toggleMonochromeAction.triggered.connect(self.Main.Options.toggle_monochrome_mode)
        
        
        
#==============================================================================
#         opening extra widgets
#==============================================================================
        
        ### set options
        self.OpenOptions = QtGui.QAction(QtGui.QIcon(self.Main.graphics_path + os.path.sep + 'options.png'), 'Options', self)
        self.OpenOptions.setStatusTip('Edit Options')
        self.OpenOptions.triggered.connect(self.OpenOptionsWidget)


#==============================================================================
#           processing action
#==============================================================================
    
        ### Apply Filter    
        self.ApplyFilterAction = QtGui.QAction('Filter data set',self)
        self.ApplyFilterAction.setStatusTip('Apply selected filter of selected size to the data set')
        
        ### Moco Single
        self.RunMocoSingleAction =  QtGui.QAction('Movement correct trials',self)
        self.RunMocoSingleAction.setStatusTip('Align selected trials to their own background')
        
        ### Moco Mulit
        self.RunMocoAlignAction = QtGui.QAction('Align measurements',self)
        self.RunMocoAlignAction.setStatusTip('Align selected trials to the background of the last selected data set')
        
        ### Segmentation
        self.RunSegmentationAction = QtGui.QAction('Filter data set',self)
        self.RunSegmentationAction.setStatusTip('dummy')
        
    def OpenOptionsWidget(self):
        self.Options_Control.show()
        self.Options_Control.raise_()
        pass
        
    def closeEvent(self,event): # reimplementation
        reply=QtGui.QMessageBox.question(self,'Message',"Are you sure to quit?",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if reply==QtGui.QMessageBox.Yes:
#            self.OptionsWindow.write_options_file(self.OptionsWindow.options_filepath)
#            self.OptionsWindow.close()
#            if self.BTT.Traces_Inspector_exists_flag:
#                self.BTT.Traces_Inspector_Widget.close()
            self.Main.cleanup()
            event.accept()
        else:
            event.ignore()



if __name__ == '__main__':
    pass
