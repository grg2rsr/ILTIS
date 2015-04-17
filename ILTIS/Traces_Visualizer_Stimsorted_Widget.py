# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 15:00:08 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import scipy as sp

class Traces_Visualizer_Stimsorted_Widget(QtGui.QWidget):
    """ plots the current traces, trial sorted with avg 
    2 do: speed issues, maybe disable other trace updater?
    implement in main window?
    implement stim region    
    """
    def __init__(self,Main,parent):
        super(Traces_Visualizer_Stimsorted_Widget, self).__init__()
    
        self.Data_Display = parent
        self.Main = Main
        
        self.plotItems = []
        self.traces = []
        
        self.init_UI()

    def init_UI(self):
        self.plotWidget = pg.GraphicsLayoutWidget()    
        pass
    
    def init_data(self):
        # some preparations
        self.trial_labels = self.Main.Data.Metadata.trial_labels
        self.trial_indices = range(self.Main.Data.nTrials)
        self.trial_labels_unique = sp.unique(self.trial_labels)
        self.nStimClasses = len(self.trial_labels_unique)
        self.nRepetitions = self.trial_labels.count(self.trial_labels[0]) # FIXME: this imposes a fixed number of repetitions per trial. this should be changed into a vector holding values for each stim

        # generating the UI
        # looping over StimClasses
        for i,StimClass in enumerate(range(self.nStimClasses)):
            plot = self.plotWidget.addPlot(title=self.trial_labels_unique[StimClass]) # for inheriting from QWidget
#            plot = self.addPlot(title=self.trial_labels_unique[StimClass]) # for inheriting form pg.GraphicsLayoutWidget directly
            plot.setLabel('left','F')
            plot.setLabel('bottom','frame #')
            plot.showGrid(x=True,y=True,alpha=0.5)
            
            # link for common axes
            if i != 0:
                plot.setYLink(self.plotItems[0])
                plot.setXLink(self.plotItems[0])
                
            # add the stimulus time marker
            stim_region = pg.LinearRegionItem(values=[self.Main.Options.preprocessing['stimulus_onset'],self.Main.Options.preprocessing['stimulus_offset']],movable=False,brush=pg.mkBrush([50,50,50,100]))
            for line in stim_region.lines:
                line.hide()
            stim_region.setZValue(-1000)
            plot.addItem(stim_region)
            
            # add the plot to the list of plots
            self.plotItems.append(plot)


        for trial in self.trial_indices:
            # draw the trace in the correct panel with the correct pen
            # in the correct panel
            stimClass = self.trial_labels[trial]
            correct_panel_index = sp.where(self.trial_labels_unique == stimClass)[0]
            
            # correct pen
            pen = pg.mkPen(self.Main.Options.view['colors'][trial],width=2)

            self.traces.append(self.plotItems[correct_panel_index].plot(pen=pen))
                                        
        # set the layout
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)
        
    def update(self):
        if self.Main.ROIs.nROIs != 0:
            for n in range(self.Main.Data.nTrials):
                # only work on active datasets
                if self.Main.Options.view['show_flags'][n] == True: 
                
                    # implementation using the pyqtgraph internal slicing
                    ROI = self.Main.ROIs.ROI_list[self.Main.ROIs.active_ROI_id]
                    
                    # func bool mask slicing
                    mask, inds = self.Main.ROIs.get_ROI_mask(ROI)  ### FIXME signal needed?
                    
                    if self.Main.Options.view['show_dFF']:
                        sliced = self.Main.Data.dFF[mask,:,n]
                    else:
                        sliced = self.Main.Data.raw[mask,:,n]
            
                    Trace = sp.average(sliced,axis=0)
                    self.traces[n].setData(Trace)
                    self.traces[n].show()
                else:
                    self.traces[n].hide()

    def reset(self):
        for trace in self.traces:
            trace.clear()
        self.traces = []
        
        pass