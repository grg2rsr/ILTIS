"""
Created on Wed Apr  1 13:15:52 2015

@author: georg
"""

from lib import IOtools as io
import scipy as sp
import os
from scipy import ndimage
from Metadata_Object import Metadata_Object

class Data_Object(object):
    """ 
    specification of a Data Object:    
    """
    def __init__(self,parent):
        self.Main = parent
        
        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated'
            
        self.raw = None
        self.dFF = None
        self.Traces = None
        self.extraction_mask = None
        self.Metadata_Object = None
        self.nFiles = None # number of files = number of trials
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
        
        for n in range(self.nFiles):
            self.Main.MainWindow.statusBar().showMessage("calculating gaussian smooth on Dataset " + str(n))  ### FIXME signal needed
            if self.Main.Options.filter_target == 'raw':
                self.raw[:,:,:,n] = ndimage.gaussian_filter(self.data[:,:,:,n],filter_size)
            if self.Main.Options.filter_target == 'dFF':
                self.dFF[:,:,:,n] = ndimage.gaussian_filter(self.dFF[:,:,:,n],filter_size)
            pass
        self.Main.MainWindow.statusBar().clearMessage()  ### FIXME signal needed
        pass
 
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
            self.Main.MainWindow.statusBar().showMessage("loading dataset: " + path)  ### FIXME signal needed
            t_stack = io.read_tiffstack(path)
            self.raw[:,:,:,n] = t_stack
            
#            self.dFF[:,:,:,n] = self.calc_dFF(t_stack,self.Main.Options.preprocessing['dFF_frames'])
        
        self.nFiles = len(paths)
        self.nFrames = self.raw.shape[2]
        self.Main.MainWindow.statusBar().clearMessage()  ### FIXME signal needed
        
        # hacking in metadata. FIXME
        self.Metadata = Metadata_Object(self.Main,self)
        self.Metadata.paths = paths
        self.Metadata.trial_labels = paths
        
        self.Main.Options.view['show_flags'] = sp.ones(self.Main.Data.nFiles,dtype='bool')
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
    
    
    
    pass

if __name__ == '__main__':
    pass