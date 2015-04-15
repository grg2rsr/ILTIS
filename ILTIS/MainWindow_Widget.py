# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:02:55 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import os
from Data_Display_Widget import Data_Display_Widget
from Front_Control_Panel_Widget import Front_Control_Panel_Widget
from Options_Control_Widget import Options_Control_Widget
from Signals import Signals

class MainWindow_Widget(QtGui.QMainWindow):

    def __init__(self,parent):
        super(MainWindow_Widget,self).__init__()

        # fields
        self.Main = parent
        self.Main.MainWindow = self

        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated'
            print('%s: %s\n' % (self.objectName(), QtCore.QThread.currentThreadId()))
        
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

#        self.display_settings_changed_signal = Signals.display_settings_changed_signal
        self.Signals = Signals()

        # init
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
        
        ### FIXME window size, keep following link in mind
        # http://stackoverflow.com/questions/16280323/qt-set-size-of-qmainwindow

        # extra Widgets
        self.Options_Control = Options_Control_Widget(self.Main,self)
        
        # connect signals
        slots = [self.Data_Display.Frame_Visualizer.update,
                 self.Data_Display.LUT_Controlers.update,
                 self.Data_Display.Traces_Visualizer.update,
                 self.Data_Display.Traces_Visualizer_Stimsorted.update]
                 
        for slot in slots:
            self.Signals.display_settings_changed_signal.connect(slot)
            
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
        Options.addAction(self.OpenOptionsAction)
        
        Process = self.Menubar.addMenu('&Process')
        Process.addAction(self.ApplyFilterAction)
#        Process.addAction(self.RunMocoSingleAction)
#        Process.addAction(self.RunMocoAlignAction)
#        Process.addAction(self.RunSegmentationAction)
        
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
    
    def setup_Actions(self):
        """ programatically generate actions """
        self.Actions = {
        
#==============================================================================
# readers        
#==============================================================================
                        'OpenAction':{'label':'load data',
                                      'status_tip':'Read data from disk',
                                      'icon':None,
                                      'func':self.Main.initialize_dataset,
                                      'checkable':False,
                                      'no_data_disabled':False},
                                    
                        'ReadCoorAction':{'label':'Load .coor file',
                                          'status_tip':'Read .coor file from disk',
                                          'icon':None,
                                          'func':None,
                                          'checkable':False,
                                          'no_data_disabled':True},
                                    
                        'ReadLSTAction':{'label':'Load .lst file',
                                         'status_tip':'Read .lst file from disk',
                                         'icon':None,
                                         'func':None,
                                         'checkable':False,
                                         'no_data_disabled':True},

                        'ReadTrialLabelsAction':{'label':'Load trial labels file',
                                                 'status_tip':'Read trial labels from text file',
                                                 'icon':None,
                                                 'func':None,
                                                 'checkable':False,
                                                 'no_data_disabled':True},                                    

#==============================================================================
# Writers      
#==============================================================================

                        'WriteROIAction':{'label':'save ROIs',
                                          'status_tip':'save current ROIs as specified in options',
                                          'icon':None,
                                          'func':None,
                                          'checkable':False,
                                          'no_data_disabled':True},

                        'WriteMovieAction':{'label':'export movie',
                                            'status_tip':'export current to movie file',
                                            'icon':None,
                                            'func':None,
                                            'checkable':False,
                                            'no_data_disabled':True},

                        'WriteTracesAction':{'label':'export traces based on ROIs',
                                             'status_tip':'slice datasets along time at ROIs and extract traces',
                                             'icon':None,
                                             'func':None,
                                             'checkable':False,
                                             'no_data_disabled':True},


#==============================================================================
# Display switches
#==============================================================================

                        'toggledFFAction':{'label':'Display dFF',
                                           'status_tip':'Toggles dF/F',
                                           'icon':None,
                                           'func':self.toggle_dFF,
                                           'checkable':True,
                                           'no_data_disabled':True},
                                    
                        'toggleGlobalLevels':{'label':'use global levels',
                                              'status_tip':'toggles global levels use',
                                              'icon':None,
                                              'func':self.toggle_global_levels,
                                              'checkable':True,
                                              'no_data_disabled':True},
                                    
                        'toggleAvgAction':{'label':'Display time average',
                                           'status_tip':'toggles display time average use',
                                           'icon':None,
                                           'func':self.toggle_avg_img,
                                           'checkable':True,
                                           'no_data_disabled':True},

                        'toggleMonochromeAction':{'label':'Monochrome mode',
                                                  'status_tip':'toggles monochrome mode',
                                                  'icon':None,
                                                  'func':self.toggle_monochrome_mode,
                                                  'checkable':True,
                                                  'no_data_disabled':True},
        
#==============================================================================
#         opening extra widgets
#==============================================================================

                        'OpenOptionsAction':{'label':'Options',
                                             'status_tip':'Edit options',
                                             'icon':None,
                                             'func':self.OpenOptionsWidget,
                                             'checkable':False,
                                             'no_data_disabled':False},
                                             
#==============================================================================
#           processing action
#==============================================================================

                        'ApplyFilterAction':{'label':'Smooth data set',
                                             'status_tip':'Apply set filter to the data set',
                                             'icon':None,
                                             'func':None,
                                             'checkable':False,
                                             'no_data_disabled':True}
        }
                                    

        # programatically generate Actions from self.Actions
        def setup_action(self,name,settings):
            """ helper functtion """
            Action = QtGui.QAction(QtGui.QIcon(settings['icon']), settings['label'],self)
            Action.setStatusTip(settings['status_tip'])
            if settings['func']:
                Action.triggered.connect(settings['func'])
            Action.setCheckable(settings['checkable'])
            Action.setDisabled(settings['no_data_disabled'])
            return Action

        for name,settings in self.Actions.iteritems():
            Action = setup_action(self,name,settings)
            setattr(self,name,Action)

        ### Apply Filter    
#        self.ApplyFilterAction = QtGui.QAction('Filter data set',self)
#        self.ApplyFilterAction.setStatusTip('Apply selected filter of selected size to the data set')
        
#        ### Moco Single
#        self.RunMocoSingleAction =  QtGui.QAction('Movement correct trials',self)
#        self.RunMocoSingleAction.setStatusTip('Align selected trials to their own background')
#        
#        ### Moco Mulit
#        self.RunMocoAlignAction = QtGui.QAction('Align measurements',self)
#        self.RunMocoAlignAction.setStatusTip('Align selected trials to the background of the last selected data set')
#        
#        ### Segmentation
#        self.RunSegmentationAction = QtGui.QAction('Filter data set',self)
#        self.RunSegmentationAction.setStatusTip('dummy')
        
    def enable_actions(self):
        """ enable disabled options """
        for name,settings in self.Actions.iteritems():
            if settings['no_data_disabled'] == True:
                getattr(self,name).setEnabled(True)


    """ fix idea: move all togglers to the MainWindow
    write all the changes to vars in the display widgets and request update """
    ### togglers view mode
    def toggle_dFF(self):     
        """ toggles the dFF show flag, button on the toolbar """
        self.view['show_dFF'] = not(self.view['show_dFF'])
        
        self.Signals.display_settings_changed_signal.emit()
           
    def toggle_avg_img(self):
        """ toggles display time-average image """
        self.view['show_avg'] = not(self.view['show_avg'])
        self.Signals.display_settings_changed_signal.emit()
#        
    def toggle_global_levels(self):
        """ toggles the use of global level setting """
        self.view['use_global_levels'] = not(self.view['use_global_levels'])
#        
    def toggle_monochrome_mode(self):
        """ toggles display in color merges or only one in monochrome 1 trial """
        self.view['show_monochrome'] = not(self.view['show_monochrome']) # the toggle
        """ fix: emit set_selection_mode_signal('monochrome') """
        self.Signals.display_settings_changed_signal.emit()
        

    def OpenOptionsWidget(self):
        self.Options_Control.show()
        self.Options_Control.raise_()
        pass
        
    def closeEvent(self,event): # reimplementation
        reply=QtGui.QMessageBox.question(self,'Message',"Are you sure to quit?",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if reply==QtGui.QMessageBox.Yes:
            ### FIXME add cleanup!
            event.accept()
        else:
            event.ignore()



if __name__ == '__main__':
    pass
