# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
from PyQt4 import QtGui
import sys
import os
import scipy as sp
from PyQt4 import Qt,QtCore

class Options_Object(QtCore.QObject):
    """ no gui, holds only the options! """
    def __init__(self,Main):
        """ """
        self.Main = Main
        
        # emtpy dicts for all the options
        self.general = {'cwd':self.Main.cwd} # all options associated w os interaction
        self.view = {} # all options involved in data display 
        self.preprocessing = {} # all options that actually metadata but needed for vis (stimulus frame)
        self.registration = {} # all options for elasitx
        self.segmentation = {} # all options for js ncc
        self.export = {} # all export options
        self.ROI = {} # all ROI related options
        self.flags = {} # all misc flags
        
        # needed to be visible
        self.QtCompositionModes = ['SourceOver','DestinationOver','Clear','Source','Destination','SourceIn','DestinationIn','SourceOut','DestinationOut','SourceAtop','DestinationAtop','Xor','Plus','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','ColorBurn','HardLight','SoftLight','Difference','Exclusion','SourceOrDestination','SourceAndDestination','SourceXorDestination','NotSourceAndNotDestination','NotSourceOrNotDestination','NotSourceXorDestination','NotSource','NotSourceAndDestination','SourceAndNotDestination']
        
        # default options have to exist so the UI can be initialized
#        self.load_default_options()
           
        pass
    pass

    def init_data(self):
       pass
    
    def update(self):
        pass

    def reset(self):
        pass

    def load_default_options(self):
        if self.Main.verbose:
            print "loading default options"

        self.general = {'verbose':True,
                        'experiment_name':os.path.split(os.path.dirname(self.Main.Data.Metadata.paths[0]))[1], # defaults to folder name
                        'options_filepath':None,
                        'cwd':self.Main.cwd,
                        }
                        
        self.preprocessing = {'stimuli':sp.array([[20,22]]),
                              'nStimuli':1,
                              'dFF_frames':[0,20],
                              'avg_frames':[0,self.Main.Data.nFrames-1],
                              'filter_xy':0.8,
                              'filter_t':1,
                              'filter_target':'dFF',
                              'filter_size':[0.8,1],
                              'dt':0.24
                              }
                              
        self.view = {'show_flags':sp.ones(self.Main.Data.nTrials,dtype='bool'),
                     'composition_mode':'Screen',
                     'last_selected':0,
                     'show_dFF':False,
                     'show_avg':False,
                     'show_monochrome':False,
                     'use_global_levels':False,
                     'trial_labels_on_traces_vis':False,
                     'color_maps':None,
                     'colors':None,
                     'heatmap':None,
                     'graymap':None,
                     'jetmap':None,
                     }
                     
        self.ROI = {'type':'circle',
                    'diameter':8,
                    'active_ROIs':[],
                    'last_active': None,                                                  
                    'active_color':[255,255,255,255],
                    'inactive_color':[255,255,255,100],
                    'show_labels':True}
                    
        self.export = {'format':'.csv - normal',
                       'data':'dFF'
                       }
                       
        self.flags = {'LST_was_read':False,
                      'dFF_was_calc':False
                      }
                       
        self.nStimuli_old = self.preprocessing['nStimuli']       
        self.view['heatmap'], self.view['graymap'] = self.Main.Processing.calc_preset_colormaps()
        pass
    





    


if __name__ == '__main__':
    import Main
    Main.main()
    pass