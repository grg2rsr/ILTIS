# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:54:33 2015

@author: georg
"""
import scipy as sp
from scipy import ndimage
#from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import QColor
from pyqtgraph import ColorMap as PGColorMap
#import pyqtgraph as pg
#from Metadata_Object import Metadata_Object
#from lib import IOtools as io
#import os

class Processing_Object(object):
    def __init__(self,Main):
        self.Main = Main
        self.Data = None
        
        heatmap, graymap = self.calc_preset_colormaps()
        self.Main.Options.view['heatmap'] = heatmap
        self.Main.Options.view['graymap'] = graymap
        pass


    
    def calc_gaussian_smooth(self):
        """ apply gaussian """
        xy = sp.float32(self.OptionsWindow.Options['filter_xy'])
        z = sp.float32(self.OptionsWindow.Options['filter_z'])
        filter_size = (xy,xy,z)
        
        for n in range(self.nTrials):
#            self.Main.MainWindow.statusBar().showMessage("calculating gaussian smooth on Dataset " + str(n))  ### FIXME signal needed
            if self.Main.Options.filter_target == 'raw':
                self.raw[:,:,:,n] = ndimage.gaussian_filter(self.data[:,:,:,n],filter_size)
            if self.Main.Options.filter_target == 'dFF':
                self.dFF[:,:,:,n] = ndimage.gaussian_filter(self.dFF[:,:,:,n],filter_size)
            pass
#        self.Main.MainWindow.statusBar().clearMessage()  ### FIXME signal needed
        pass
    
    def first_time_dFF(self):
        """ is connected to ... and executed upon dFF toggle. If dFF is zeros,
        then calc it now. """
        ## from dFF toggler
        if self.Main.Options.view['show_dFF'] == True:
            # if no dFF has been calculated, do so now. 
            if not(self.Main.Options.general['dFF_was_calc']):

                self.calc_dFF()
                self.Main.Options.general['dFF_was_calc'] = True
                self.Main.Data_Display.LUT_Controlers.reset_levels()
        
 
    def calc_dFF(self):
        """ calculates:
        data = x,y,t
        frames = (f1,f2) frames to consider, background is calculated avg(f1:f2)
        
        deltaF / F = (F - F_background) / F_background
        works on 3d version for memory efficiency. When this function is called,
        it has to be explicitly iterated over the datasets
        """

        f_start,f_stop = self.Main.Options.preprocessing['dFF_frames']
        
        if sp.any(self.Main.Data.raw == 0): # add offset if 0 intensity pixels exist
            data_tmp = self.Main.Data.raw + 100
        else:
            data_tmp = self.Main.Data.raw
            
        bck = sp.average(data_tmp[:,:,f_start:f_stop,:],axis=2)[:,:,sp.newaxis,:]
        self.Main.Data.dFF = (data_tmp - bck) / bck
        self.Main.Options.general['dFF_was_calc'] = True

#==============================================================================
    ### dataset extraction related 
#==============================================================================
    def calc_extraction_mask(self):
        """ calculate the extraction mask based on ROIs """
        pass
    
    def calc_traces(self):
        """ """
        pass

#==============================================================================
    ### color calculations
#==============================================================================
    def calc_colormaps(self,nColors,HSVsubset=(0,360),HSVoffset=0):
        colors = self.calc_colors(nColors,HSVsubset,HSVoffset)
        color_maps = [self.calc_colormap(color) for color in colors]
        return colors, color_maps
        
    def calc_colors(self,nColors,HSVsubset=(0,360),HSVoffset=0):
        h = sp.linspace(0,360,nColors,endpoint=False).astype('int')
        h = self.add_circular_offset(h,HSVoffset,HSVsubset[1]).tolist()
        s = [255] * nColors
        v = [255] * nColors
        colors = []
        for n in range(nColors):
            Color = QColor()
            Color.setHsv(h[n],s[n],v[n])
            colors.append(Color.getRgb())
        return colors
    
    def calc_colormap(self,rgba):
        """ input is a rgb(a) tuple returns PGColorMap """
        pos = sp.array([1,0])
        cols = sp.array([rgba,[0,0,0,0]],dtype=sp.ubyte)
        cmap = PGColorMap(pos,cols)
        return cmap
        
    def calc_preset_colormaps(self):
        pos = sp.array([1,0.66,0.33,0])
        cols = sp.array([[255,255,255,255],[255,220,0,255],[185,0,0,255],[0,0,0,0]],dtype=sp.ubyte)
        heatmap = PGColorMap(pos,cols)

        pos = sp.array([1,0])
        cols = sp.array([[255,255,255,255],[0,0,0,255]],dtype=sp.ubyte)
        graymap = PGColorMap(pos,cols)
        
        return heatmap, graymap
        
    
    def add_circular_offset(self,array,offset,bound):
        """ helper function to rotate the color wheel"""
        rotated = sp.array([val % bound if val > bound else val for val in (array + offset)])
        return rotated
    pass
        

if __name__ == '__main__':
    import Main
    Main.main()
    pass