# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:54:33 2015

@author: georg
"""
import scipy as sp
from scipy import ndimage
from PyQt4 import QtGui,QtCore
import pyqtgraph as pg
from Metadata_Object import Metadata_Object

class Processing_Object(object):
    def __init__(self,Main):
        self.Main = Main
        self.Data = None

        # calculate colormaps here, but store in Options.view['colormaps']        
        pos = sp.array([1,0.66,0.33,0])
        cols = sp.array([[255,255,255,255],[255,220,0,255],[185,0,0,255],[0,0,0,0]],dtype=sp.ubyte)
        self.Main.Options.view['heatmap'] = pg.ColorMap(pos,cols)
        
        pos = sp.array([1,0])
        cols = sp.array([[255,255,255,255],[0,0,0,255]],dtype=sp.ubyte)
        self.Main.Options.view['graymap'] = pg.ColorMap(pos,cols)
        pass


    ### calculations
    def calc_extraction_mask(self):
        """ calculate the extraction mask based on ROIs """
        pass
    
    def calc_traces(self):
        """ """
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
        
        self.Signals.reset_levels_signal.emit()
        """ called upon first time dFF """
        self.Main.Data_Display.LUT_Controlers.reset_levels()  ### FIXME signal needed
 
    def calc_dFF(self):
        """ calculates:
        data = x,y,t
        frames = (f1,f2) frames to consider, background is calculated avg(f1:f2)
        
        deltaF / F = (F - F_background) / F_background
        works on 3d version for memory efficiency. When this function is called,
        it has to be explicitly iterated over the datasets
        """
        x,y,t,n = self.raw.shape
        self.dFF = sp.zeros((x,y,t,n),dtype='float32')
        
        data = self.raw
        frames = self.Main.Options.preprocessing['dFF_frames']
        
        if sp.any(data == 0): # add offset if 0 intensity pixels exist
            data_tmp = data + 100
        else:
            data_tmp = data
            
        bck = sp.average(data_tmp[:,:,frames[0]:frames[1],:],axis=2)[:,:,sp.newaxis,:]
        self.dFF = (data_tmp - bck) / bck
        self.Main.Options.general['dFF_was_calc'] = True


    def calc_colormaps(self,nColors,hot=False):
        """ generate evenly spaced colors on the HSV wheel """
        h = sp.linspace(0,360,nColors,endpoint=False).astype('int').tolist()
        s = [255] * nColors
        v = [255] * nColors
        color_maps = []
        colors = []
        for n in range(nColors):
            Color = QtGui.QColor()
            Color.setHsv(h[n],s[n],v[n])
            rgb = Color.getRgb()
            if hot == False:
                pos = sp.array([1,0])
                cols = sp.array([rgb,[0,0,0,0]],dtype=sp.ubyte)
                cmap = pg.ColorMap(pos,cols)
                colors.append(rgb)
                color_maps.append(cmap)
                pass
            if hot == True:
                pos = sp.array([1,0.8,0])
                cols = sp.array([[255,255,255,255],rgb,[0,0,0,255]],dtype=sp.ubyte)
                cmap = pg.ColorMap(pos,cols)
                colors.append(rgb)
                color_maps.append(cmap)
                pass
            pass
        return colors, color_maps
    
    pass
        
    ### readers / loaders
    def load(self):
        """ load all """ 
        pass
    
    def load_multi_stack_data(self):
        """ load the data from disk """
        pass
    
    def load_traces_data(self):
        """ load the data from disk """
        pass

    def read_tifs(self,paths):
        """ read tifs found at paths (list with paths) """
        # reading
        x,y,t = io.read_tiffstack(paths[0]).shape
        n = len(paths)
        self.raw = sp.zeros((x,y,t,n),dtype='uint16')
        self.dFF = sp.zeros((x,y,t,n),dtype='float32')

        for n,path in enumerate(paths):
            print "loading dataset from " + path
            print "Dataset size: " + str(os.stat(path).st_size / 1000000.0) + ' MB'
#            self.Main.MainWindow.statusBar().showMessage("loading dataset: " + path)  ### FIXME signal needed
            t_stack = io.read_tiffstack(path)
            self.raw[:,:,:,n] = t_stack
            
#            self.dFF[:,:,:,n] = self.calc_dFF(t_stack,self.Main.Options.preprocessing['dFF_frames'])
        
        self.nTrials = len(paths)
        self.nFrames = self.raw.shape[2]
#        self.Main.MainWindow.statusBar().clearMessage()  ### FIXME signal needed
        
        # hacking in metadata. FIXME
        self.Metadata = Metadata_Object(self.Main,self)
        self.Metadata.paths = paths
        self.Metadata.trial_labels = paths
        
        self.Main.Options.view['show_flags'] = sp.ones(self.Main.Data.nTrials,dtype='bool')
        pass
    
    def associate_metadata(self,meta_data,recalc=True):
        """ link meta_data to this dataset, per default do recalculations of
        dFF, traces, filters etc """
        pass
    
    ### writers / savers
    def write_data_object(self,path):
        pass
    
    def save(self):
        pass
