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
#        """ checks if nStimuli has changed , if yes 1) expand self.preprocessing
#        and settable_options, always gets the values from the Options
#        Control and emits the updateD splaySettingsSignal """
#

#
#
#
#        
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
    
#    def make_settable_options(self):
#        """ 
#        this one needs a good doc
#        kind can be: infer,choices,path
#        """
#        self.settable_options = [
#                                {'dict_name':'general','param_name':'verbose','tab_label':'General','row_label':'verbose mode','kind':'choices','choices':['True','False']},
#                                {'dict_name':'general','param_name':'options_filepath','tab_label':'General','row_label':'options filepath','kind':'path'},
#                                {'dict_name':'general','param_name':'cwd','tab_label':'General','row_label':'current working directory','kind':'path'},
#        
#                                {'dict_name':'preprocessing','param_name':'nStimuli','tab_label':'Preprocessing','row_label':'Number of stimuli per trial','kind':'infer'},
#                                {'dict_name':'preprocessing','param_name':'stimuli','tab_label':'Preprocessing','row_label':'start/stop frame of stimuli','kind':'infer'},
#                                {'dict_name':'preprocessing','param_name':'dFF_frames','tab_label':'Preprocessing','row_label':'frames for background calculation','kind':'infer'},
#                                {'dict_name':'preprocessing','param_name':'filter_size','tab_label':'Preprocessing','row_label':'xy t filter size','kind':'infer'},
#                                
#                                {'dict_name':'preprocessing','param_name':'filter_target','tab_label':'General','row_label':'apply filter to','kind':'choices','choices':['raw','dFF']},
#                                {'dict_name':'view','param_name':'composition_mode','tab_label':'View','row_label':'image composition mode','kind':'choices','choices':self.QtCompositionModes},
#                                
#                                {'dict_name':'view','param_name':'trial_labels_on_traces_vis','tab_label':'View','row_label':'show trial labels on stim sorted traces','kind':'choices','choices':['True','False']},
#                                
#                                {'dict_name':'ROI','param_name':'diameter','tab_label':'View','row_label':'ROI diameter','kind':'infer'},
#                                {'dict_name':'ROI','param_name':'type','tab_label':'View','row_label':'ROI type','kind':'choices','choices':['circle','polygon']},
#                                {'dict_name':'ROI','param_name':'place_in_layer','tab_label':'View','row_label':'place ROI in layer','kind':'infer'},
#                                {'dict_name':'ROI','param_name':'default_layer','tab_label':'View','row_label':'ROI default layer','kind':'infer'},
#                                
#                                {'dict_name':'export','param_name':'data','tab_label':'Export','row_label':'Export traces from','kind':'choices','choices':['raw','dFF']},
#                                {'dict_name':'export','param_name':'format','tab_label':'Export','row_label':'Export format','kind':'choices','choices':['.csv','.gloDatamix']}
#                                ]
#
#                                        
#        # multi stim support
#        
##        
##        for i in range(self.preprocessing['nStimuli']):
##            stim_list = [['preprocessing','stimulus'+str(i+1)],'Preprocessing','stimulus '+str(i)+' onset/offset frame',['int']*2,None]
##            self.settable_options.append(stim_list)            
#
#        pass
    
    
#    def get_options_from_UI_and_set(self):
#        """ reads from the Options_Control widget the currently present user
#        defined values for the variables """
#        
#        """ iterate over rows in Options_Control """        
#        
#
#        widgets = [row[2] for row in self.Main.Options_Control.rows]
#        
#        for i,widget in enumerate(widgets):
#            dict_name = self.Main.Options_Control.rows[i][0]
#            param_name = self.Main.Options_Control.rows[i][1]
#            
#            # QComboBox            
#            if type(widget) == QtGui.QComboBox:
#                if self.settable_options[i]['choices'] == ['True','False']:
#                    choices = [True,False]
#                else:
#                    choices = self.settable_options[i]['choices']
#                getattr(self,dict_name)[param_name] = choices[widget.currentIndex()]
#
#            # QTableWidget            
#            if type(widget) == QtGui.QTableWidget:
#                var = sp.array(getattr(self,dict_name)[param_name])
#                dtype = var.dtype.kind # needs np dtype!
#                dim = var.shape
#                nDim = len(dim)
#                                
#                if nDim == 0:
#                    getattr(self,dict_name)[param_name] = sp.array(str(widget.item(0,0).text())).astype(dtype)
#                    pass
#                
#                if nDim == 1:
#                    for c in range(widget.columnCount()):
#                        getattr(self,dict_name)[param_name][c] = sp.array(str(widget.item(0,c).text())).astype(dtype)
#                if nDim == 2:
#                    for r in range(widget.rowCount()):
#                        for c in range(widget.columnCount()):
##                            import pdb
##                            pdb.set_trace()
#                            getattr(self,dict_name)[param_name][r,c] = sp.array(str(widget.item(r,c).text())).astype(dtype)




        
#        for row_index, row in enumerate(self.Main.Options_Control.rows):
#            kind = self.settable_options[row_index][3] # type
#            nFields = len(kind)
#            choices = self.settable_options[row_index][4] # choices
#            
#            dict_name = self.settable_options[row_index][0][0]
#            param_name = self.settable_options[row_index][0][1]
#            
#            try:
#                for i in range(nFields):
#                    # converting from user input to variable format
#                    if kind[i] == 'int':
#                        string = row.children()[i+1].text() # first child is the layout, the following are the input fields
#                        string = str(string) # to convert from QString to normal string, QString causes problems upon scipy cast
#                        val = sp.int32(string)
#    
#                    if kind[i] == 'float':
#                        string = row.children()[i+1].text() # first child is the layout, the following are the input fields
#                        string = str(string) # to convert from QString to normal string, QString causes problems upon scipy cast
#                        val = sp.float32(string)
#                        
#                    if kind[i] == 'bool':
#                        val = ['True','False'][row.children()[1].currentIndex()]
#                        if val == 'True':                        
#                            val = True
#                        elif val == 'False':
#                            val = False
#      
#                    if kind[i] == 'string':
#                        val = choices[row.children()[1].currentIndex()]
#                        pass
#                    
#                    if kind[i] == 'path':
#                        val = ''
#                        pass
#      
#                    # setting the values          
#                    if nFields == 1:
#                        getattr(self,dict_name)[param_name] = val
#                    if nFields > 1:
#                        getattr(self,dict_name)[param_name][i] = val
#                        
#            except: # this is because '' cant be converted to int etc. FIXME
#                pass
#        pass
    




    


if __name__ == '__main__':
    import Main
    Main.main()
    pass