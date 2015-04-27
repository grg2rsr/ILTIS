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
        """ inits empty plot """
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.plotItem = self.addPlot()
        self.plotItem.setLabel('left','F')
        self.plotItem.setLabel('bottom','frame #')
        self.plotItem.showGrid(x=True,y=True,alpha=0.5)
                
        self.vline = self.plotItem.addLine(x=self.Data_Display.Frame_Visualizer.frame,movable=True)
        self.vline.sigPositionChanged.connect(self.update_vline) # add interactivity

        pass
    
    def init_data(self):
        """ sets all info that is gained after loading a dataset """
        self.vline.setBounds((0, self.Main.Data.nFrames -1))
        self.plotItem.setRange(xRange=[0, self.Main.Data.nFrames], disableAutoRange=False)
        self.update_stim_regions()
        
    def init_traces(self):
        """ creates the traces, depending on the number of ROIs selected. """
        nActiveROIs = len(self.Main.Options.ROI['active_ROIs'])
        
        # one ROI active, normal mode: traces overlaid, colored to stim class
        if nActiveROIs == 1:
            for n in range(self.Main.Data.nTrials):
                pen = pg.mkPen(self.Main.Options.view['colors'][n], width=2)
                trace = self.plotItem.plot(pen=pen)
                self.traces.append(trace)
                
        # multiple ROI active, traces colored to ROI
        if nActiveROIs > 1:
            colors = self.Main.Processing.calc_colormaps(nActiveROIs)
            for i,ROI_id in enumerate(self.Main.Options.ROI['active_ROIs']):
                for n in range(self.Main.Data.nTrials):
                    pen = pg.mkPen(colors[i], width=2)
                    trace = self.plotItem.plot(pen=pen)
                    self.traces.append(trace)
        pass
    
    def update_stim_regions(self):
        """ delete all possibly present stimulus regions and draw new ones """
        # delete preset if any
        for stim_region in self.stim_regions:
            self.plotItem.removeItem(stim_region)
            
        self.stim_regions = []

        # color stimulus regions
        for stim_id in range(self.Main.Options.preprocessing['stimuli'].shape[0]):
            stim_frames = self.Main.Options.preprocessing['stimuli'][stim_id,:]
            stim_region = pg.LinearRegionItem(values=stim_frames,movable=False,brush=pg.mkBrush([50,50,50,100]))
            for line in stim_region.lines:
                line.hide()
            stim_region.setZValue(-1000)
            self.plotItem.addItem(stim_region)
            self.stim_regions.append(stim_region)
            pass

#                            
#        # update stim marker
#        for i,stim_region in enumerate(self.stim_regions):
#            stim_frames = self.Main.Options.preprocessing['stimuli'][i]
#            stim_region.setRegion(stim_frames)
            
                    
    def update_display_settings(self):
        """ this is handled via signal/slot mechanism"""
        for n,val in enumerate(self.Main.Options.view['show_flags']):
            if val == True:
                self.traces[n].show()
            else:
                self.traces[n].hide()

        # plot labels
        if self.Main.Options.view['show_dFF'] == True:
            self.plotItem.setLabel('left','dF/F')
            
        if self.Main.Options.view['show_dFF'] == False:
            self.plotItem.setLabel('left','F [au]')
            
        # update stim_regions
        self.update_stim_regions()
        
        pass
    
    def update_traces(self):
        """ update traces - for speed reasons via direct call"""
        active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
        nActiveROIs = len(self.Main.Options.ROI['active_ROIs'])
        
        # do not run if no ROIs
        if len(self.Main.ROIs.ROI_list) > 0:
            
            # if only one is selected: normal mode
            if nActiveROIs == 1:
                ROI = self.Main.ROIs.ROI_list[self.Main.Options.ROI['active_ROIs'][0]]
                Traces = self.get_traces(ROI)
    
                for n,ind in enumerate(active_inds):
                    self.traces[ind].setData(Traces[:,n])
                    
            # if more than one: multi_ROI_mode
            if nActiveROIs > 1:
                for i,ROI_id in enumerate(self.Main.Options.ROI['active_ROIs']):
                    ROI = self.Main.ROIs.ROI_list[ROI_id]
                    Traces = self.get_traces(ROI)
                    
                    for n,ind in enumerate(active_inds):
                        mapped_ind = ind + i * len(active_inds)
                        self.traces[mapped_ind].setData(Traces[:,n])
                
        
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