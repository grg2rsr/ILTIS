# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
import sys
import os
import scipy as sp
from PyQt4 import Qt

class Options_Object():
    """ no gui, holds only the options! """
    def __init__(self,Main,options_filepath=None):
        """ """
        self.Main = Main
        self.Main.Options = self
        self.options_filepath = options_filepath
        
        self.general = {} # all options associated w os interaction
        self.view = {} # all options involved in data display 
        self.preprocessing = {} # all options that actually metadata but needed for vis (stimulus frame)
        self.registration = {} # all options for elasitx
        self.segmentation = {} # all options for js ncc
        self.export = {} # all export options
        self.ROI = {} # all ROI related options
        
        self.load_default_options()
        self.make_settable_options()
             

        pass
    pass

    def load_default_options(self):
        self.general = {'verbose':True,
                        'options_filepath':None,
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
                     'use_global_levels':False
                     }
                     
        self.ROI = {'type':'circle',
                    'diameter':8}
                    
        self.export = {'format':'csv',
                       'data':'dFF',
                       }
                       
        pass
    
    def make_settable_options(self):
        """ 
        var, page, label, kind, nfields=1,choices=None
        kind: bool, int, float, string, path
        for string, choices must be set
        for path, path selector needed
        note: for fetchers, string and path are equal
        
        """
        self.settable_options = [
                                ["general['verbose']",'General','verbose mode','bool',1,None],
                                ["general['options_filepath']",'General','options filepath','path',1,None],
                                ["preprocessing['stimulus_onset']",'Preprocessing','stimulus onset frame','int',1,None],
                                ["preprocessing['stimulus_offset']",'Preprocessing','stimulus offset frame','int',1,None],
                                ["preprocessing['dFF_frames']",'Preprocessing','frames for background calculation','int',2,None],
                                ["preprocessing['filter_size']",'Preprocessing','xy t filter size','float',2,None],
                                ["preprocessing['filter_target']",'Preprocessing','apply filter to','string',1,['raw','dFF']],
                                ["view['composition_mode']",'View','image composition mode','string',1,['SourceOver','DestinationOver','Clear','Source','Destination','SourceIn','DestinationIn','SourceOut','DestinationOut','SourceAtop','DestinationAtop','Xor','Plus','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','ColorBurn','HardLight','SoftLight','Difference','Exclusion','SourceOrDestination','SourceAndDestination','SourceXorDestination','NotSourceAndNotDestination','NotSourceOrNotDestination','NotSourceXorDestination','NotSource','NotSourceAndDestination','SourceAndNotDestination']],
                                ["ROI['diameter']",'View','ROI diameter','float',1,None],
                                ["ROI['type']",'View','ROI type','string',1,['circular','polygon']],
                                ["export['data']",'Export','Export traces from','string',1,['raw','dFF']],
                                ["export['format']",'Export','Export format','string',1,['.csv','.gloDatamix']]
                                ]
        pass
    
    def send_options_to_Options_Control(self):
        """ sets the Options_Control GUI to the values that are in this object
        this function will be needed at ini and at options loading """
        for row_index, row in enumerate(self.Main.Options_Control.rows):
            kind = self.settable_options[row_index][3] # type
            nFields = self.settable_options[row_index][4] # nFileds
            choices = self.settable_options[row_index][5] # choices
            
            for i in range(nFields):
                # converting from user input to variable format
                if kind == 'int' or kind == 'float':
                    val = getattr(self,self.settable_options[row_index][0])
                    if kind == 'int':
                        val = str(val)
                    if kind == 'float':
                        val = str(sp.around(val,2))
                        
                    row.children()[i+1].setText(val) # first child is the layout, the following are the input fields
                    
                    
                        
                if kind == 'bool':
                    val = ['True','False'][row.children()[1].currentIndex()]
  
                if kind == 'string':
                    val = choices[row.children()[1].currentIndex()]
                    pass
                
                if kind == 'path':
                    pass

                
        pass
    
    def fetch_options_from_Options_Control(self):
        """ reads from the Options_Control widget the currently present user
        defined values for the variables """
        
        """ iterate over rows in Options_Control """        
        
#        for var in self.settable_options[:][0]:
        for row_index, row in enumerate(self.Main.Options_Control.rows):
            kind = self.settable_options[row_index][3] # type
            nFields = self.settable_options[row_index][4] # nFileds
            choices = self.settable_options[row_index][5] # choices
            
            for i in range(nFields):
                # converting from user input to variable format
                if kind == 'int' or kind == 'float':
                    string = row.children()[i+1].text() # first child is the layout, the following are the input fields
                    
                    if kind == 'int':
                        val = sp.int32(string)
                    if kind == 'float':
                        val = sp.float32(string)
                        
                if kind == 'bool':
                    val = ['True','False'][row.children()[1].currentIndex()]
  
                if kind == 'string':
                    val = choices[row.children()[1].currentIndex()]
                    pass
                
                if kind == 'path':
                    pass
  
                # setting the values          
                if nFields == 1:
                    setattr(self,self.settable_options[row_index][0],val)
                if nFields < 1:
                    setattr(self,self.settable_options[row_index][0][i],val)
            
            
        pass
    
    def init_data(self):
        """ resets the options object. Look for one attached to the dataset, and
        if not, load defaults.
        For future: can also load from .ids"""
        if self.options_filepath != None:
            if os.path.exists(self.options_filepath):
                if self.Main.verbose:
                    print "loading options file from ", self.options_filepath
                    self.load_options()
#        else:
#            if self.Main.verbose:
#                print "loading default options"
#                self.load_default_options()
    
    def update(self):
        """ currently just executes the fetch function """
        self.fetch_options_from_Options_Control()
        pass


#==============================================================================
    ### IO        
#==============================================================================
    def load_options(self):
        """ load options from options_filepath """
        pass
    
    def save_options(self):
        """ save options to options_filepath """
        pass
    
    ### togglers view mode
    def toggle_dFF(self):     
        """ toggles the dFF show flag, button on the toolbar """
        self.view['show_dFF'] = not(self.view['show_dFF'])
        if self.view['show_dFF'] == True:
            if not(self.general['dFF_was_calc']): # first time display, calc dFF
                self.Main.Data.calc_dFF()
                self.Main.Data_Display.LUT_Controlers.reset_levels()
            self.Main.Traces_Visualizer.plotItem.setLabel('left','dF/F')
        if self.view['show_dFF'] == False:
            self.Main.Traces_Visualizer.plotItem.setLabel('left','F [au]')
        self.Main.MainWindow.Data_Display.update()
           
    def toggle_avg_img(self):
        """ toggles display time-average image """
        self.view['show_avg'] = not(self.view['show_avg'])
        self.Main.MainWindow.Data_Display.update()
        
    def toggle_global_levels(self):
        """ toggles the use of global level setting """
        self.view['use_global_levels'] = not(self.view['use_global_levels'])
        
    def toggle_monochrome_mode(self):
        """ toggles display in color merges or only one in monochrome 1 trial """
        self.view['show_monochrome'] = not(self.view['show_monochrome']) # the toggle
        
        if self.view['show_monochrome'] == True:
            # disable all except the last selected dataset
            self.Main.Data_Selector.clearSelection()
            self.Main.Data_Selector.selectRow(self.view['last_selected'])
            
            # change selection model
            self.Main.Data_Selector.setSelectionMode(Qt.QAbstractItemView.SingleSelection)

            # set the colormaps to monochrome + glow
            for i in range(self.Main.Data.nFiles):
                self.Main.LUT_Controlers.LUTwidgets.widget(i).item.gradient.setColorMap(self.Main.Data_Display.graymap)
                self.Main.LUT_Controlers.LUTwidgets_dFF.widget(i).item.gradient.setColorMap(self.Main.Data_Display.heatmap)
                        
        if self.view['show_monochrome'] == False:
            # restore colors
            for i in range(self.Main.Data.nFiles):
                self.Main.LUT_Controlers.LUTwidgets.widget(i).item.gradient.setColorMap(self.Main.Data_Display.color_maps[i])
                self.Main.LUT_Controlers.LUTwidgets_dFF.widget(i).item.gradient.setColorMap(self.Main.Data_Display.color_maps[i])
            # back to multi selection model
            self.Main.Data_Selector.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)

        self.Main.Data_Display.update()

if __name__ == '__main__':
    pass