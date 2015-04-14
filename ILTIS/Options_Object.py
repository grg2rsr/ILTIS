# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
import sys
import os
import scipy as sp
from PyQt4 import Qt

class Options_Object(object):
    """ no gui, holds only the options! """
    def __init__(self,Main,options_filepath=None):
        """ """
        self.Main = Main
        self.Main.Options = self
        self.options_filepath = options_filepath
        
        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated'        

        
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
                    'diameter':8,
                    'place_in_layer':'last active',
                    'default_layer':0}
                    
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
                                [['general','verbose'],'General','verbose mode',['bool'],None],
                                [['general','options_filepath'],'General','options filepath',['path'],None],
                                [['preprocessing','stimulus_onset'],'Preprocessing','stimulus onset frame',['int'],None],
                                [['preprocessing','stimulus_offset'],'Preprocessing','stimulus offset frame',['int'],None],
                                [['preprocessing','dFF_frames'],'Preprocessing','frames for background calculation',['int']*2,None],
                                [['preprocessing','filter_size'],'Preprocessing','xy t filter size',['float']*2,None],
                                [['preprocessing','filter_target'],'Preprocessing','apply filter to',['string'],['raw','dFF']],
                                [['view','composition_mode'],'View','image composition mode',['string'],['SourceOver','DestinationOver','Clear','Source','Destination','SourceIn','DestinationIn','SourceOut','DestinationOut','SourceAtop','DestinationAtop','Xor','Plus','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','ColorBurn','HardLight','SoftLight','Difference','Exclusion','SourceOrDestination','SourceAndDestination','SourceXorDestination','NotSourceAndNotDestination','NotSourceOrNotDestination','NotSourceXorDestination','NotSource','NotSourceAndDestination','SourceAndNotDestination']],
                                [['ROI','diameter'],'View','ROI diameter',['float'],None],
                                [['ROI','type'],'View','ROI type',['string'],['circle','polygon']],
                                [['ROI','place_in_layer'],'View','place ROI in layer',['string'],['last active','default layer']],
                                [['ROI','default_layer'],'View','ROI default layer',['int'],None],
                                [['export','data'],'Export','Export traces from',['string'],['raw','dFF']],
                                [['export','format'],'Export','Export format',['string'],['.csv','.gloDatamix']]
                                ]
        pass
    
#    def send_options_to_Options_Control(self):
#        """ sets the Options_Control GUI to the values that are in this object
#        this function will be needed at ini and at options loading """
##        print "sending"
#        for row_index, row in enumerate(self.Main.Options_Control.rows):
#            kind = self.settable_options[row_index][3] # type
#            nFields = len(kind) # nFileds
#            choices = self.settable_options[row_index][4] # choices
#
#            #  
#            dict_name = self.settable_options[row_index][0][0]
#            param_name = self.settable_options[row_index][0][1]
#
#            
#            for i in range(nFields):
##                print dict_name,param_name
#                # reading val
#                if nFields == 1:
#                    val = getattr(self,dict_name)[param_name]
#                if nFields > 1:
#                    val = getattr(self,dict_name)[param_name][i]
#                    
#                val = str(val)
#                
#                # converting from user input to variable format
#                if kind[i] == 'int':
#                    row.children()[i+1].setText(val) # first child is the layout, the following are the input fields                    
#                    
#                if kind[i] == 'float':
#                    row.children()[i+1].setText(val) # first child is the layout, the following are the input fields                    
#                        
#                if kind[i] == 'bool':
#                    row.children()[1].setCurrentIndex(['True','False'].index(val))
#  
#                if kind[i] == 'string':
##                    val = choices[row.children()[1].currentIndex()]
#                    pass
#                
#                if kind[i] == 'path':
#                    pass

                
        pass
    
    def fetch_options_from_Options_Control(self):
        """ reads from the Options_Control widget the currently present user
        defined values for the variables """
        
        """ iterate over rows in Options_Control """        
        
#        print "fetching", self
        
        for row_index, row in enumerate(self.Main.Options_Control.rows):
            kind = self.settable_options[row_index][3] # type
            nFields = len(kind)
            choices = self.settable_options[row_index][4] # choices
            
            # 
            dict_name = self.settable_options[row_index][0][0]
            param_name = self.settable_options[row_index][0][1]
            
            try:
                for i in range(nFields):
                    # converting from user input to variable format
                    if kind[i] == 'int' or kind[i] == 'float':
                        string = row.children()[i+1].text() # first child is the layout, the following are the input fields
                        string = str(string) # to convert from QString to normal string, QString causes problems upon scipy cast
                        if kind[i] == 'int':
                            val = sp.int32(string)
                        if kind[i] == 'float':
                            val = sp.float32(string)
                            
                    if kind[i] == 'bool':
                        val = ['True','False'][row.children()[1].currentIndex()]
      
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
                        getattr(self,dict_name)[param_name][0] = val
                        
            except:
                pass
            
            
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
        try:
            """ fix: emit update_requested signal """
            self.Main.Data_Display.update()  ### FIXME signal needed
        except:
            pass
        pass


#==============================================================================
    ### IO        
#==============================================================================
    def load_options(self):
        """ load options from options_filepath """
#        self.send_options_to_Options_Control()
        pass
    
    def save_options(self):
        """ save options to options_filepath """
        pass
    
    """ fix idea: move all togglers to the MainWindow
    write all the changes to vars in the display widgets and request update """
    ### togglers view mode
    def toggle_dFF(self):     
        """ toggles the dFF show flag, button on the toolbar """
        self.view['show_dFF'] = not(self.view['show_dFF'])
        if self.view['show_dFF'] == True:
            if not(self.general['dFF_was_calc']): # first time display, calc dFF
                self.Main.Data.calc_dFF()  ### FIXME signal needed
                self.Main.Data_Display.LUT_Controlers.reset_levels()  ### FIXME signal needed
            self.Main.Traces_Visualizer.plotItem.setLabel('left','dF/F')  ### FIXME signal needed
        if self.view['show_dFF'] == False:
            self.Main.Traces_Visualizer.plotItem.setLabel('left','F [au]')  ### FIXME signal needed
        self.Main.MainWindow.Data_Display.update()  ### FIXME signal needed
           
    def toggle_avg_img(self):
        """ toggles display time-average image """
        self.view['show_avg'] = not(self.view['show_avg'])
        """ fix: emit update_requested signal """
        self.Main.MainWindow.Data_Display.update()  ### FIXME signal needed
        
    def toggle_global_levels(self):
        """ toggles the use of global level setting """
        self.view['use_global_levels'] = not(self.view['use_global_levels'])
        
    def toggle_monochrome_mode(self):
        """ toggles display in color merges or only one in monochrome 1 trial """
        self.view['show_monochrome'] = not(self.view['show_monochrome']) # the toggle
        
        if self.view['show_monochrome'] == True:
            # disable all except the last selected dataset
            self.Main.Data_Selector.clearSelection()  ### FIXME signal needed
            self.Main.Data_Selector.selectRow(self.view['last_selected'])  ### FIXME signal needed
            
            # change selection model
            self.Main.Data_Selector.setSelectionMode(Qt.QAbstractItemView.SingleSelection)  ### FIXME signal needed

            # set the colormaps to monochrome + glow
            for i in range(self.Main.Data.nFiles):
                self.Main.LUT_Controlers.LUTwidgets.widget(i).item.gradient.setColorMap(self.Main.Data_Display.graymap)  ### FIXME signal needed
                self.Main.LUT_Controlers.LUTwidgets_dFF.widget(i).item.gradient.setColorMap(self.Main.Data_Display.heatmap)  ### FIXME signal needed
                        
        if self.view['show_monochrome'] == False:
            # restore colors
            for i in range(self.Main.Data.nFiles):
                self.Main.LUT_Controlers.LUTwidgets.widget(i).item.gradient.setColorMap(self.Main.Data_Display.color_maps[i])
                self.Main.LUT_Controlers.LUTwidgets_dFF.widget(i).item.gradient.setColorMap(self.Main.Data_Display.color_maps[i])
            # back to multi selection model
            self.Main.Data_Selector.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)  ### FIXME signal needed

        self.Main.Data_Display.update()  ### FIXME signal needed

if __name__ == '__main__':
    pass