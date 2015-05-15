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

class MainWindow_Widget(QtGui.QMainWindow):

    def __init__(self,parent):
        super(MainWindow_Widget,self).__init__()
        # fields
        self.Main = parent

        self.MenuBar = None
        self.ToolBar = None
        self.StatusBar = None
        self.Data_Display = None
        self.Front_Control_Panel = None
        self.Options_Control = None

        # layout
        self.Container = None
        self.Splitter = None
        
        # initializations
        self.setup_Actions()
        self.setup_MenuBar()
        self.setup_ToolBar()
        self.setup_StatusBar()

        # init
        self.init_UI()
        pass

    def init_UI(self):
        """ """
        # own layout
#        DesktopWidget = QtGui.QDesktopWidget()
#        qrect = DesktopWidget.screenGeometry()
#        height, width = qrect.height(), qrect.width()

#        self.resize(width*0.7,height*0.7)
#        self.move(width/15,height/15)
        self.showMaximized()
        
        # ini
        self.Data_Display = Data_Display_Widget(self.Main,self)
        self.Front_Control_Panel = Front_Control_Panel_Widget(self.Main,self)
        self.Container = QtGui.QWidget()
        self.Options_Control = Options_Control_Widget(self.Main,self)
#        
#        # splitter variant
        self.Splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.Splitter.addWidget(self.Data_Display)
        self.Splitter.addWidget(self.Front_Control_Panel)
        
#        self.Splitter = QtGui.QWidget(self)
        self.setCentralWidget(self.Splitter)
        
#        self.setWindowIcon(QtGui.QIcon(self.Main.graphics_path + os.path.sep + )) ### FIXME
        self.setWindowTitle('ILTIS')
        
        frac = 0.8
        self.Splitter.setSizes([int(self.Splitter.size().height() * frac), int(self.Splitter.size().height() * (1-frac))])
        # note: http://stackoverflow.com/questions/16280323/qt-set-size-of-qmainwindow
        
        self.show() 

        pass
    
    def setup_MenuBar(self):

        self.Menubar = self.menuBar()
        Open = self.Menubar.addMenu('&Open')
        Open.addAction(self.OpenAction)
        Open.addAction(self.ReadROIAction)
        Open.addAction(self.ReadLSTAction)
        Open.addAction(self.ReadTrialLabelsAction)
        
        Save = self.Menubar.addMenu('&Save')
        Save.addAction(self.WriteROIAction)
        Save.addAction(self.WriteMovieAction)
        Save.addAction(self.WriteTracesAction)
        
        Converters = self.Menubar.addMenu('&Convert')
        Converters.addAction(self.log2lstAction)
#        Options = self.Menubar.addMenu('&Options')
#        Options.addAction(self.OpenOptionsAction)
        
        Process = self.Menubar.addMenu('&Process')
        Process.addAction(self.ApplyFilterAction)
#        Process.addAction(self.RunMocoSingleAction)
#        Process.addAction(self.RunMocoAlignAction)
#        Process.addAction(self.RunSegmentationAction)
        
        Help = self.Menubar.addMenu('&Help')
        
        pass
    
    def setup_ToolBar(self):
        
        # spacer widget for right, have to be two different objects
        spacers = [QtGui.QWidget(),QtGui.QWidget()]
        for spacer in spacers:
            spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.ToolBar = self.addToolBar('Hide')
        self.ToolBar.addWidget(spacers[0])
        self.ToolBar.addAction(self.toggledFFAction)
        self.ToolBar.addAction(self.toggleMonochromeAction)
        self.ToolBar.addAction(self.toggleAvgAction)
        self.ToolBar.addAction(self.toggleGlobalLevels)
        self.ToolBar.addAction(self.OpenOptionsAction)
        self.ToolBar.addWidget(spacers[1])
        pass
    
    def setup_StatusBar(self):
        self.StatusBar = self.statusBar()
        pass
    
    def setup_Actions(self):
        """ generate actions """
        self.Actions = {
        
#==============================================================================
# readers        
#==============================================================================
                        'OpenAction':{'label':'load data',
                                      'status_tip':'Read data from disk',
                                      'icon':None,
                                      'func':self.Main.IO.init_data,
                                      'checkable':False,
                                      'no_data_disabled':False},
                                    
                        'ReadROIAction':{'label':'Load .roi file',
                                          'status_tip':'Read .roi file from disk',
                                          'icon':None,
                                          'func':self.Main.IO.load_ROIs,
                                          'checkable':False,
                                          'no_data_disabled':True},
                                    
                        'ReadLSTAction':{'label':'Load .lst file',
                                         'status_tip':'Read .lst file from disk',
                                         'icon':None,
                                         'func':self.Main.IO.load_lst,
                                         'checkable':False,
                                         'no_data_disabled':True},

                        'ReadTrialLabelsAction':{'label':'Load trial labels file',
                                                 'status_tip':'Read trial labels from text file',
                                                 'icon':self.Main.graphics_path + os.path.sep + 'icons' + os.path.sep +  'tags.svg',
                                                 'func':self.Main.IO.load_trial_labels,
                                                 'checkable':False,
                                                 'no_data_disabled':True},                                    

#==============================================================================
# Writers      
#==============================================================================

                        'WriteROIAction':{'label':'save ROIs',
                                          'status_tip':'save current ROIs as specified in options',
                                          'icon':None,
                                          'func':self.Main.IO.write_extraction_mask,
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
                                             'func':self.Main.IO.export_traces,
                                             'checkable':False,
                                             'no_data_disabled':True},


#==============================================================================
# Display switches
#==============================================================================

                        'toggledFFAction':{'label':'Display dFF',
                                           'status_tip':'Toggles dF/F',
                                           'icon':self.Main.graphics_path + os.path.sep + 'icons' + os.path.sep +  'calc_dFF.png',
                                           'func':self.toggle_dFF,
                                           'checkable':True,
                                           'no_data_disabled':True},
                                    
                        'toggleGlobalLevels':{'label':'use global levels',
                                              'status_tip':'toggles global levels use',
                                              'icon':self.Main.graphics_path + os.path.sep + 'icons' + os.path.sep +  'globe-alt.svg',
                                              'func':self.toggle_global_levels,
                                              'checkable':True,
                                              'no_data_disabled':True},
                                    
                        'toggleAvgAction':{'label':'Display time average',
                                           'status_tip':'toggles display time average use',
                                           'icon':self.Main.graphics_path + os.path.sep + 'icons' + os.path.sep +  'Average_Image.svg',
                                           'func':self.toggle_avg_img,
                                           'checkable':True,
                                           'no_data_disabled':True},

                        'toggleMonochromeAction':{'label':'Monochrome mode',
                                                  'status_tip':'toggles monochrome mode',
                                                  'icon':self.Main.graphics_path + os.path.sep + 'icons' + os.path.sep +  'adjust.svg',
                                                  'func':self.toggle_monochrome_mode,
                                                  'checkable':True,
                                                  'no_data_disabled':True},
        
#==============================================================================
#         opening extra widgets
#==============================================================================

                        'OpenOptionsAction':{'label':'Options',
                                             'status_tip':'Edit options',
                                             'icon':self.Main.graphics_path + os.path.sep + 'icons' + os.path.sep +  'sliders.svg',
                                             'func':self.open_Options_Widget,
                                             'checkable':False,
                                             'no_data_disabled':True},
                                             
#==============================================================================
#           processing action
#==============================================================================

                        'ApplyFilterAction':{'label':'Smooth data set',
                                             'status_tip':'Apply set filter to the data set',
                                             'icon':None,
                                             'func':self.Main.Processing.calc_gaussian_smooth,
                                             'checkable':False,
                                             'no_data_disabled':True},
                                    

#==============================================================================
#           Converters action
#==============================================================================

                        'log2lstAction':{'label':'Generate .lst from .vws.log',
                                         'status_tip':'reads a .vws.log from till vision imaging setups and generates a .lst file',
                                         'icon':None,
                                         'func':self.Main.IO.convert_log2lst,
                                         'checkable':False,
                                         'no_data_disabled':False}
                                             
                        }



        # programatically generate Actions from self.Actions
        def setup_action(self,name,settings):
            """ helper functtion """
            if settings['icon']:
                Action = QtGui.QAction(QtGui.QIcon(settings['icon']), settings['label'],self)
            else:
                Action = QtGui.QAction(settings['label'],self)
            Action.setStatusTip(settings['status_tip'])
            if settings['func']:
                Action.triggered.connect(settings['func'])
            Action.setCheckable(settings['checkable'])
            Action.setDisabled(settings['no_data_disabled'])
            return Action

        for name,settings in self.Actions.iteritems():
            Action = setup_action(self,name,settings)
            setattr(self,name,Action)

        
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

    ### togglers view mode
    def toggle_dFF(self):     
        """ toggles the dFF show flag, button on the toolbar """
        self.Main.Options.view['show_dFF'] = not(self.Main.Options.view['show_dFF'])
        self.Main.Signals.updateDisplaySettingsSignal.emit()
        self.Main.Data_Display.Traces_Visualizer.update_traces()
        self.Main.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
           
    def toggle_avg_img(self):
        """ toggles display time-average image """
        self.Main.Options.view['show_avg'] = not(self.Main.Options.view['show_avg'])
        self.Main.Signals.updateDisplaySettingsSignal.emit()
#        
    def toggle_global_levels(self):
        """ toggles the use of global level setting """
        self.Main.Options.view['use_global_levels'] = not(self.Main.Options.view['use_global_levels'])
#        
    def toggle_monochrome_mode(self):
        """ toggles display in color merges or only one in monochrome 1 trial """
        self.Main.Options.view['show_monochrome'] = not(self.Main.Options.view['show_monochrome']) # the toggle

        # this should have a signal
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.update_selection()
        self.Main.Signals.updateDisplaySettingsSignal.emit()
        
        self.Main.Data_Display.Traces_Visualizer.update_traces()
        self.Main.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
        

    def open_Options_Widget(self):
        self.Options_Control.show()
        self.Options_Control.raise_()
        pass
        
    def closeEvent(self,event): # reimplementation
        reply=QtGui.QMessageBox.question(self,'Message',"Are you sure to quit?",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if reply==QtGui.QMessageBox.Yes:
#            self.Main.IO.save_options()
            self.Options_Control.close()
            ### FIXME add cleanup!
            event.accept()
        else:
            event.ignore()



if __name__ == '__main__':
    import Main
    Main.main()
    pass
