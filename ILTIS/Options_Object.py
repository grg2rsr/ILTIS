# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
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
        
        self.QtCompositionModes = ['SourceOver','DestinationOver','Clear','Source','Destination','SourceIn','DestinationIn','SourceOut','DestinationOut','SourceAtop','DestinationAtop','Xor','Plus','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','ColorBurn','HardLight','SoftLight','Difference','Exclusion','SourceOrDestination','SourceAndDestination','SourceXorDestination','NotSourceAndNotDestination','NotSourceOrNotDestination','NotSourceXorDestination','NotSource','NotSourceAndDestination','SourceAndNotDestination']
        
        # temporarily included hack, removed later
        self.options_filepath = None
        self.load_default_options() ### FIXME
        
        # define user access for automatic generation of the Options_Control GUI
        self.make_settable_options()
            
        pass
    pass

    def init_data(self):
        """ IO reads the options_file from disk """
        self.load_default_options()
        
        # for future implementation
#        self.Main.IO.load_options() 

#        and this code is then moved to IO        
#        if self.Main.options_filepath != None:
#            if os.path.exists(self.options_filepath):
#                if self.Main.verbose:
#                    print "loading options file from ", self.options_filepath
#                    self.Main.IO.load_options()
    
    def update(self):
        """ currently just executes the fetch function """
        print "options update called"
        self.get_options_from_UI_and_set()
        self.Main.Signals.updateDisplaySettingsSignal.emit()
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
                        
        self.preprocessing = {'stimulus_onset':25,
                              'stimulus_offset':75,
                              'dFF_frames':(0,20),
                              'filter_xy':0.8,
                              'filter_t':1,
                              'filter_target':'raw',
                              'filter_size':(0.8,1)
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
                     'graymap':None
                     }
                     
        self.ROI = {'type':'circle',
                    'diameter':8,
                    'place_in_layer':'last active',
                    'default_layer':0,
                    'active_ROI_id':None}
                    
        self.export = {'format':'.csv',
                       'data':'dFF',
                       }
                       
        pass
    
    def make_settable_options(self):
        """ 
        this one needs a good doc
        
        """
        
        self.settable_options = [
                                [['general','verbose'],'General','verbose mode',['bool'],None],
                                [['general','options_filepath'],'General','options filepath',['path'],None],
                                [['general','cwd'],'General','current working directory',['path'],None],
                                [['preprocessing','stimulus_onset'],'Preprocessing','stimulus onset frame',['int'],None],
                                [['preprocessing','stimulus_offset'],'Preprocessing','stimulus offset frame',['int'],None],
                                [['preprocessing','dFF_frames'],'Preprocessing','frames for background calculation',['int']*2,None],
                                [['preprocessing','filter_size'],'Preprocessing','xy t filter size',['float']*2,None],
                                [['preprocessing','filter_target'],'Preprocessing','apply filter to',['string'],['raw','dFF']],
                                [['view','composition_mode'],'View','image composition mode',['string'],self.QtCompositionModes],
                                [['view','trial_labels_on_traces_vis'],'View','show trial labels on stim sorted traces',['bool'],None],
                                [['ROI','diameter'],'View','ROI diameter',['float'],None],
                                [['ROI','type'],'View','ROI type',['string'],['circle','polygon']],
                                [['ROI','place_in_layer'],'View','place ROI in layer',['string'],['last active','default layer']],
                                [['ROI','default_layer'],'View','ROI default layer',['int'],None],
                                [['export','data'],'Export','Export traces from',['string'],['raw','dFF']],
                                [['export','format'],'Export','Export format',['string'],['.csv','.gloDatamix']]
                                ]
        pass
    
    
    def get_options_from_UI_and_set(self):
        """ reads from the Options_Control widget the currently present user
        defined values for the variables """
        
        """ iterate over rows in Options_Control """        
        
#        print "fetching", self
        
        for row_index, row in enumerate(self.Main.Options_Control.rows):
            kind = self.settable_options[row_index][3] # type
            nFields = len(kind)
            choices = self.settable_options[row_index][4] # choices
            
            dict_name = self.settable_options[row_index][0][0]
            param_name = self.settable_options[row_index][0][1]
            
            try:
                for i in range(nFields):
                    # converting from user input to variable format
                    if kind[i] == 'int':
                        string = row.children()[i+1].text() # first child is the layout, the following are the input fields
                        string = str(string) # to convert from QString to normal string, QString causes problems upon scipy cast
                        val = sp.int32(string)
    
                    if kind[i] == 'float':
                        string = row.children()[i+1].text() # first child is the layout, the following are the input fields
                        string = str(string) # to convert from QString to normal string, QString causes problems upon scipy cast
                        val = sp.float32(string)
                        
                    if kind[i] == 'bool':
                        val = ['True','False'][row.children()[1].currentIndex()]
                        if val == 'True':                        
                            val = True
                        elif val == 'False':
                            val = False
      
                    if kind[i] == 'string':
                        val = choices[row.children()[1].currentIndex()]
                        pass
                    
                    if kind[i] == 'path':
                        val = ''
                        pass
      
                    # setting the values          
                    if nFields == 1:
                        getattr(self,dict_name)[param_name] = val
                    if nFields < 1:
                        getattr(self,dict_name)[param_name][i] = val
            except: # this is because '' cant be converted to int etc. FIXME
                pass
        pass
    




    


if __name__ == '__main__':
    import Main
    Main.main()
    pass