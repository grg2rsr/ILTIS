# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
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
                              'filter_targe':'raw',
                              'ROI_type':'circle',
                              'ROI_diameter':8
                              }
                              
        self.view = {'show_flags':sp.ones(self.Main.Data.nFiles,dtype='bool'),
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
                       
#        self.verbose = True
#        self.stimulus_onset = 25
#        self.stimulus_offset = 75
#        self.filter_xy = 0.8
#        self.filter_z = 2
#        self.filter_target = 'raw'
#        self.ROI_diameter = 8
#        self.ROI_type = 'circle'
#        self.composition_mode = 'Screen'
#        self.export_format = 'csv'
#        self.export_data = 'dFF'
#        self.last_selected = 0
#        self.flags = {'show_dFF':False,
#              'show_avg':False,
#              'monochrome_mode':False,
#              'lst_was_read':False,
#              'global_levels':False}
#
#        self.dFF_frames = (0,20)
#        self.show_flags = )
#        self.path = self.Main.MainWindow.path
        pass

    def load_options(self):
        pass
    
    def save_options(self):
        """ """
        pass
    
    def init_data(self):
        """ resets the options object. Look for one attached to the dataset, and
        if not, load defaults.
        For future: can also load from .ids"""
        if self.options_filepath != None:
            if os.path.exists(self.options_filepath):
                if self.Main.verbose:
                    print "loading options file from ", self.options_filepath
                    self.load_options_file(self.options_filepath)
        else:
            if self.Main.verbose:
                print "loading default options"
                self.load_default_options()
            
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