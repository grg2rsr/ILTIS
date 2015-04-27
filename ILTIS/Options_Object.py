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
        self.general = {} # all options associated w os interaction
        self.view = {} # all options involved in data display 
        self.preprocessing = {} # all options that actually metadata but needed for vis (stimulus frame)
        self.registration = {} # all options for elasitx
        self.segmentation = {} # all options for js ncc
        self.export = {} # all export options
        self.ROI = {} # all ROI related options
        
        # needed to be visible
        self.QtCompositionModes = ['SourceOver','DestinationOver','Clear','Source','Destination','SourceIn','DestinationIn','SourceOut','DestinationOut','SourceAtop','DestinationAtop','Xor','Plus','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','ColorBurn','HardLight','SoftLight','Difference','Exclusion','SourceOrDestination','SourceAndDestination','SourceXorDestination','NotSourceAndNotDestination','NotSourceOrNotDestination','NotSourceXorDestination','NotSource','NotSourceAndDestination','SourceAndNotDestination']
#        self.nStimuli_old = None        
        
        # temporarily included hack, removed later
        self.options_filepath = None
        self.load_default_options() ### FIXME
#        self.nStimuli_old = self.preprocessing['nStimuli']
        
        # define user access for automatic generation of the Options_Control GUI
#        self.settable_options = []
#        self.make_settable_options()
            
        pass
    pass

    def init_data(self):
        """ IO reads the options_file from disk """
        self.load_default_options()
        print 'data default'
        self.nStimuli_old = self.preprocessing['nStimuli']
        
        # for future implementation
#        self.Main.IO.load_options() 

#        and this code is then moved to IO        
#        if self.Main.options_filepath != None:
#            if os.path.exists(self.options_filepath):
#                if self.Main.verbose:
#                    print "loading options file from ", self.options_filepath
#                    self.Main.IO.load_options()
    
    def update(self):
 
#        self.Main.Signals.updateDisplaySettingsSignal.emit()
        pass

    def reset(self):
        """ resets the object"""
        self.load_default_options()
        pass

    def load_default_options(self):
        self.general = {'verbose':True,
                        'options_filepath':None,
                        'cwd':None,
                        'lst_was_read':False,
                        'dFF_was_calc':False
                        }
                        
        self.preprocessing = {'stimuli':sp.array([[20,22],[25,27]]),
                              'nStimuli':2,
                              'dFF_frames':[0,20],
                              'filter_xy':0.8,
                              'filter_t':1,
                              'filter_target':'raw',
                              'filter_size':[0.8,1]
                              }
                              
        self.view = {'show_flags':[0],
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
                    'active_color':[255,255,255,255],
                    'inactive_color':[255,255,255,100]}
                    
        self.export = {'format':'.csv',
                       'data':'dFF',
                       }
                       
        pass
    





    


if __name__ == '__main__':
    import Main
    Main.main()
    pass