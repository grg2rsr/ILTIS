# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import os

class Options_Control_Widget(QtGui.QTabWidget):
    """ the GUI widget to set the options, possibly one with tabs """
    def __init__(self,Main,parent):
        super(Options_Control_Widget,self).__init__()
        self.MainWindow = parent
        self.Main = Main
        self.Main.Options_Control = self
        
        self.initUI()
        """ note: options object exists at time of instantiation """
        pass

    def initUI(self):
        self.setWindowTitle('Options')    
        
#==============================================================================
#         # General Options        
#==============================================================================
        
        page1 = QtGui.QWidget()        
        self.addTab(page1,'General') # add select working directory, reset data
        Form = QtGui.QFormLayout()
        
        self.select_cwd_btn = QtGui.QPushButton('Select directory')
        Form.addRow('Select current working directory',self.select_cwd_btn)

        self.reset_data_btn = QtGui.QPushButton('Reset Data',self)                
        Form.addRow('Reload (=reset) current data set',self.reset_data_btn)

        self.recalc_dFF_btn = QtGui.QPushButton('Recalc dFF',self)   
        Form.addRow('Recalculate dFF',self.recalc_dFF_btn)
        
        self.store_options_btn = QtGui.QPushButton('Store')
        Form.addRow('Store current settings as default',self.store_options_btn)
        
        # layout
        
        page1.setLayout(Form) 
        
#==============================================================================
#         ### Metadata settings
#==============================================================================
        page2 = QtGui.QWidget()
        self.addTab(page2,'Metadata')      
        Form = QtGui.QFormLayout()
        
        self.stimulus_onset_edit = QtGui.QLineEdit()
#        self.stimulus_onset_edit.setText(str(self.Main.Options.stimulus_onset))
        Form.addRow('Stimulus onset frame',self.stimulus_onset_edit)
        
        self.stimulus_offset_edit = QtGui.QLineEdit()
#        self.stimulus_offset_edit.setText(str(self.Main.Options.stimulus_offset))
        Form.addRow('Stimulus offset frame',self.stimulus_offset_edit)
        
        # FIXME general Metadata editor
        page2.setLayout(Form)
        
#==============================================================================
#         ### View setings        
#==============================================================================
        page3 = QtGui.QWidget()
        self.addTab(page3,'View') # Image composition mode, color maps
        Form = QtGui.QFormLayout()

        label = QtGui.QLabel('ROI settings')
        label.setAlignment(QtCore.Qt.AlignCenter)
        Form.addRow(label)
        
        self.ROI_diameter_edit = QtGui.QLineEdit()
        Form.addRow('ROI diameter',self.ROI_diameter_edit)
        
        # ROI type selection combo
        self.ROI_selection_combo = QtGui.QComboBox(self)
        self.ROI_typelist = ['circular','polygon']
        for mode in self.ROI_typelist:
            self.ROI_selection_combo.addItem(mode,self)
        Form.addRow('ROI type',self.ROI_selection_combo)

        # Image composition mode
        self.composition_combo = QtGui.QComboBox(self)
        self.composition_modeslist = ['SourceOver','DestinationOver','Clear','Source','Destination','SourceIn','DestinationIn','SourceOut','DestinationOut','SourceAtop','DestinationAtop','Xor','Plus','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','ColorBurn','HardLight','SoftLight','Difference','Exclusion','SourceOrDestination','SourceAndDestination','SourceXorDestination','NotSourceAndNotDestination','NotSourceOrNotDestination','NotSourceXorDestination','NotSource','NotSourceAndDestination','SourceAndNotDestination']
        for mode in self.composition_modeslist:
            self.composition_combo.addItem(mode,self)


        label = QtGui.QLabel('Frame display')
        label.setAlignment(QtCore.Qt.AlignCenter)
        Form.addRow(label)
        
        Form.addRow('Image composition mode',self.composition_combo)
        Form.addRow('color maps',None)
        
        for key, value in self.Main.Options.general:
            Form.addRow(key,QtGui.QLabel(value))

        
        # ROIs

        page3.setLayout(Form)
        
#==============================================================================
#         ### Processing
#==============================================================================
        page4 = QtGui.QWidget()
        self.addTab(page4,'Processing') # filter radius, apply filter on, recalc dFF, Jan Soelters code parameters
        Form = QtGui.QFormLayout()
        
        ### Filter options
        label = QtGui.QLabel('Frame display')
        label.setAlignment(QtCore.Qt.AlignCenter)
        Form.addRow(label)
        Form.addRow(None,None)
        
        self.filter_xy_edit = QtGui.QLineEdit()
        self.filter_t_edit = QtGui.QLineEdit()
        Form.addRow('Gaussian filter size [xy]', self.filter_xy_edit)
        Form.addRow('Gaussian filter size [t]', self.filter_t_edit)

        self.filter_options_combo = QtGui.QComboBox(self)
        self.filter_target_list = ['raw','dFF']
        for target in self.filter_target_list:
            self.filter_options_combo.addItem(target,self)        
        Form.addRow('Apply filter to',self.filter_options_combo)

        # moco settings # FIXME
        label = QtGui.QLabel('Motion correction settings')
        label.setAlignment(QtCore.Qt.AlignCenter)
        Form.addRow(label)
        # Jan Soelters Stuff  # FIXME

        # layout
        
        page4.setLayout(Form)

#==============================================================================
#         ### Exporting        
#==============================================================================
        page5 = QtGui.QWidget()
        self.addTab(page5,'Exporting') # add editing of OmDL object XML
        Form = QtGui.QFormLayout()
        
        self.export_label = QtGui.QLabel('Traces export (what/how)')
        self.export_data_combo = QtGui.QComboBox(self)
        self.export_data_list = ['raw','dFF']
        for export_data in self.export_data_list:
            self.export_data_combo.addItem(export_data)
        Form.addRow('Traces export data selection',self.export_data_combo)
            
        self.export_format_combo = QtGui.QComboBox(self)
        self.export_format_list = ['.csv','.gloDatamix']
        for export_format in self.export_format_list:
            self.export_format_combo.addItem(export_format)
        Form.addRow('Traces export format selection',self.export_format_combo)
        
        Form.addRow('Movie export options',None)
        Form.addRow('Frame rate',None)
        Form.addRow('export format',None)

        # layout
        page5.setLayout(Form)
        pass
    pass

if __name__ == '__main__':
    pass