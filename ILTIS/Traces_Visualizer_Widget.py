# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:59:11 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import scipy as sp

class Traces_Visualizer_Widget(pg.GraphicsLayoutWidget):
    def __init__(self,Main,parent):
        super(Traces_Visualizer_Widget,self).__init__()
        
        self.Main = Main
        self.Data_Display = parent
        
        self.plotWidget = []        
        self.traces = []
        self.stim_regions = []
        self.init_UI()


    def init_UI(self):
        """ inits empty plot """
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.plotItem = self.addPlot()
        self.plotItem.setLabel('left','F')
        self.plotItem.setLabel('bottom','frame #')
        self.plotItem.showGrid(x=True,y=True,alpha=0.5)
                
        self.vline = self.plotItem.addLine(x=self.Data_Display.Frame_Visualizer.frame,movable=True)
        self.vline.sigPositionChanged.connect(self.vline_pos_changed) # add interactivity
        
    def reset(self):
        for trace in self.traces:
            trace.clear()
        self.traces = []        
        
    def init_data(self):
        """ sets all info that is gained after loading a dataset """
        self.vline.setBounds((0, self.Main.Data.nFrames -1))
        self.plotItem.setRange(xRange=[0, self.Main.Data.nFrames], disableAutoRange=False)
        self.update_stim_regions()
        
    def init_traces(self):
        """ creates the traces, depending on the selected number of ROIs and 
        datasets. """
        nActiveROIs = len(self.Main.Options.ROI['active_ROIs'])
        nActiveTrials = sp.sum(self.Main.Options.view['show_flags'])
        trial_inds = sp.where(self.Main.Options.view['show_flags'])[0]
        
        # delete all present if any
        if len(self.traces) > 0:
            self.reset()
        
        # one ROI active, normal mode: traces overlaid, colored to stim class
        # this causes traces to be trial1, trial2, trial4 for active: (1,2,4)
        if nActiveROIs == 1:
            colors = self.Main.Options.view['colors']
            for n in range(nActiveTrials):
                pen = pg.mkPen(colors[trial_inds[n]], width=2)
                trace = self.plotItem.plot(pen=pen)
                self.traces.append(trace)
                
        # multiple ROI active, traces colored to ROI
        # this results traces to contain roi1 trial1, roi1 trail2, roi1 trial4, roi2 trial1 roi2 trial2, roi2 trial4 for ROI (1,2) trials (1,2,4)
        if nActiveROIs > 1:
            colors = self.Main.Processing.calc_colors(nActiveROIs)
            for i,ROI_id in enumerate(self.Main.Options.ROI['active_ROIs']):
                for n in range(nActiveTrials):
                    pen = pg.mkPen(colors[i], width=2)
                    trace = self.plotItem.plot(pen=pen)
                    self.traces.append(trace)
        
        self.update_traces()

    def update_traces(self):
        """ update traces - for speed reasons via direct call"""
        active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
        nActiveTrials = sp.sum(self.Main.Options.view['show_flags'])
        nActiveROIs = len(self.Main.Options.ROI['active_ROIs'])
        
        # do not run if no ROIs
        if len(self.Main.ROIs.ROI_list) > 0:
            
            # if only one is selected: normal mode
            if nActiveROIs == 1:
                ROI = self.Main.ROIs.ROI_list[self.Main.Options.ROI['active_ROIs'][0]]
                Traces = self.get_traces(ROI)
                
                for i in range(Traces.shape[1]):
                    self.traces[i].setData(Traces[:,i])
    
#                for n,ind in enumerate(active_inds): # this becomes obsolete through the init_traces function. self.traces will always have the same shape as get_traces()
#                    self.traces[ind].setData(Traces[:,n])
                    
            # if more than one: multi_ROI_mode
            if nActiveROIs > 1:
                for i,ROI_id in enumerate(self.Main.Options.ROI['active_ROIs']):

                    ROI = self.Main.ROIs.ROI_list[ROI_id]
                    Traces = self.get_traces(ROI)
                    for j in range(Traces.shape[1]):
                        
                        self.traces[j+i*nActiveTrials].setData(Traces[:,j])
#                        self.traces[j + i*nActiveROIs].setData(Traces[:,i])
#                    for n,ind in enumerate(active_inds):
#                        mapped_ind = ind + i * len(active_inds)
#                        self.traces[mapped_ind].setData(Traces[:,n])
                
        
        # if no ROIs, hide all
        else:
            [trace.hide() for trace in self.traces]
            
    def get_traces(self,ROI):
        """ helper for calculating the traces matrix """
        active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
        # func bool mask slicing
        mask, inds = self.Main.ROIs.get_ROI_mask(ROI)  ### FIXME signal needed?
        
        if self.Main.Options.view['show_dFF']:
            sliced = self.Main.Data.dFF[mask,:,:][:,:,active_inds]
        else:
            sliced = self.Main.Data.raw[mask,:,:][:,:,active_inds]
        Traces = sp.average(sliced,axis=0)
        return Traces
    
    def update_stim_regions(self):
        """ delete all possibly present stimulus regions and draw new ones """
        # delete preset if any
        for stim_region in self.stim_regions:
            self.plotItem.removeItem(stim_region)
            
        self.stim_regions = []

        # gray stimulus regions
        for stim_id in range(self.Main.Options.preprocessing['stimuli'].shape[0]):
            stim_frames = self.Main.Options.preprocessing['stimuli'][stim_id,:]
            stim_region = pg.LinearRegionItem(values=stim_frames,movable=False,brush=pg.mkBrush([50,50,50,100]))
            for line in stim_region.lines:
                line.hide()
            stim_region.setZValue(-1000)
            self.plotItem.addItem(stim_region)
            self.stim_regions.append(stim_region)
            pass
                    
    def update_display_settings(self):
        """ this is handled via signal/slot mechanism"""
#        if len(self.Main.Options.ROI['active_ROIs']) > 0:
#            for n,val in enumerate(self.Main.Options.view['show_flags']):
#                if val == True:
#                    self.traces[n].show()
#                else:
#                    self.traces[n].hide()

        # plot labels
        if self.Main.Options.view['show_dFF'] == True:
            self.plotItem.setLabel('left','dF/F')
            
        if self.Main.Options.view['show_dFF'] == False:
            self.plotItem.setLabel('left','F [au]')
            
        # update stim_regions
        self.update_stim_regions()
        
        pass
    

    def vline_pos_changed(self,evt):
        """ updater for the zlayer change caused by the vline """
        vline = evt
        pos = int(vline.pos().x())
        self.Main.Data_Display.Frame_Visualizer.frame = pos
        self.Main.Data_Display.Frame_Visualizer.update_frame()
        self.update_vline(pos)

    def update_vline(self,pos):
        self.vline.setValue(pos) # this is for the keypress event
        
        # update all lines of Traces_Visualizer_Stimsorted
        for vline in self.Main.Data_Display.Traces_Visualizer_Stimsorted.vlines:
            vline.blockSignals(True)
            vline.setValue(pos)
            vline.blockSignals(False)
            
    def wheelEvent(self,evt): # reimplementation
        d = sp.around(evt.delta() / 120.0) # check this on different machines how much it is
        self.Main.Data_Display.Frame_Visualizer.frame -= d
        self.update_vline(self.Main.Data_Display.Frame_Visualizer.frame)
        self.Main.Data_Display.Frame_Visualizer.update_frame()
        
    pass

if __name__ == '__main__':
    from . import Main
    Main.main()
    pass