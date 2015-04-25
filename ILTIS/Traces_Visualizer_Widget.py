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
#        self.Main.Traces_Visualizer = self        
        self.Data_Display = parent
        
        self.plotWidget = []        
        self.traces = []
        self.stim_regions = []
        self.init_UI()


    def init_UI(self):
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.plotItem = self.addPlot()
        self.plotItem.setLabel('left','F')
        self.plotItem.setLabel('bottom','frame #')
        self.plotItem.showGrid(x=True,y=True,alpha=0.5)
                
        self.vline = self.plotItem.addLine(x=self.Data_Display.Frame_Visualizer.frame,movable=True)
        self.vline.sigPositionChanged.connect(self.update_vline) # add interactivity

        pass
    
    def init_data(self):
        
        ### plot
        self.vline.setBounds((0, self.Main.Data.nFrames -1))

        for n in range(self.Main.Data.nTrials):
            pen = pg.mkPen(self.Main.Options.view['colors'][n], width=2)
            trace = self.plotItem.plot(pen=pen)
            self.traces.append(trace)
            
        self.plotItem.setRange(xRange=[0, self.Main.Data.nFrames], disableAutoRange=False)
        
        # color stimulus regions
        for stim_id in range(self.Main.Options.preprocessing['nStimuli']):
            stim_frames = self.Main.Options.preprocessing['stimuli'][stim_id]
            stim_region = pg.LinearRegionItem(values=stim_frames,movable=False,brush=pg.mkBrush([50,50,50,100]))
            for line in stim_region.lines:
                line.hide()
            stim_region.setZValue(-1000)
            self.plotItem.addItem(stim_region)
            self.stim_regions.append(stim_region)
            pass
    
    def update_display_settings(self):
        """ this is handled via signal/slot mechanism"""
        for n,val in enumerate(self.Main.Options.view['show_flags']):
            if val == True:
                self.traces[n].show()
            else:
                self.traces[n].hide()
                    
        # update stim marker
        for i,stim_region in enumerate(self.stim_regions):
            stim_frames = self.Main.Options.preprocessing['stimuli'][i]
            stim_region.setRegion(stim_frames)
    
        # plot labels
        if self.Main.Options.view['show_dFF'] == True:
            self.plotItem.setLabel('left','dF/F')
            
        if self.Main.Options.view['show_dFF'] == False:
            self.plotItem.setLabel('left','F [au]')
        
        pass
    
    def update_traces(self):
        """ update traces - for speed reasons via direct call"""
        
        # do not run if no ROIs

        if (self.Main.ROIs.nROIs > 0 and self.Main.Options.ROI['active_ROI_id'] != None):
            active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
            # sp.where(self.Main.Options.view['show_flags'] # this should work for the slicing and actually contains inds
                
            # implementation using the pyqtgraph internal slicing
            """ fix idea: after this is a local copy, then the get_ROI_mask func can be put into the ROI class"""
            ROI = self.Main.ROIs.ROI_list[self.Main.Options.ROI['active_ROI_id']]
            
            # func bool mask slicing
            mask, inds = self.Main.ROIs.get_ROI_mask(ROI)  ### FIXME signal needed?
            
            if self.Main.Options.view['show_dFF']:
                sliced = self.Main.Data.dFF[mask,:,:][:,:,active_inds]
            else:
                sliced = self.Main.Data.raw[mask,:,:][:,:,active_inds]
    
            Traces = sp.average(sliced,axis=0)

            
            for n,ind in enumerate(active_inds):
                self.traces[ind].setData(Traces[:,n])
            
            
    def reset(self):
        for trace in self.traces:
            trace.clear()
        self.traces = []

    def update_vline(self,evt):
        """ updater for the zlayer change caused by the vline """
        vline = evt
        pos = int(vline.pos().x())
        self.Main.Data_Display.Frame_Visualizer.frame = pos
        self.Main.Data_Display.Frame_Visualizer.update_frame()    
#        self.vline.setValue(evt.pos().x()) # this is for the keypress event
        
        # update all lines of Traces_Visualizer_Stimsorted
        for vline in self.Main.Data_Display.Traces_Visualizer_Stimsorted.vlines:
            vline.blockSignals(True)
            vline.setValue(pos)
            vline.blockSignals(False)
#        for vline in self.Main.Data_Display.Traces_Visualizer_Stimsorted.vlines:
#            vline.setValue(pos)
        
        

    pass

if __name__ == '__main__':
    import Main
    Main.main()
    pass