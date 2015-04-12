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
        
        self.rows = []
        self.initUI()
        
        """ note: options object exists at time of instantiation """
        pass

    def initUI(self):
        self.setWindowTitle('Options')    
        for row_index,options_string in enumerate(self.Main.Options.settable_options):
            self.make_row(row_index,*options_string)
         
    
    def make_row(self,row_index,var_name,page,label,kind,nfields,choices):
        """ programatically generates the whole options_control GUI from a list
        of variables defined in options. this is for flexible extension of the 
        options. DOCUMENT MORE """
        
        
        """ implementation idea for keeping all the connections of the changed 
        values: connection dict? 
        
        whenever something has changed, call the update function
        this one then iterates over all rows and reads the values
        has to determine what kind of row and how many fields """
        
        
        input_field = QtGui.QWidget(self)
        input_field_layout = QtGui.QHBoxLayout(input_field)            
        for i in range(nfields):
            if kind == 'int' or kind == 'float':
                LineEdit = QtGui.QLineEdit(input_field)
                input_field_layout.addWidget(LineEdit)
                LineEdit.textChanged.connect(self.Main.Options.update)
            if kind == 'bool':
                ComboBox = QtGui.QComboBox(input_field)
                for state in ['True','False']:
                    ComboBox.addItem(state)
                ComboBox.currentIndexChanged.connect(self.Main.Options.update)
                input_field_layout.addWidget(ComboBox)
            if kind == 'string':
                ComboBox = QtGui.QComboBox(input_field)
                for choice in choices:
                    ComboBox.addItem(choice)
                ComboBox.currentIndexChanged.connect(self.Main.Options.update)
                input_field_layout.addWidget(ComboBox)
            if kind == 'path':
                Button = QtGui.QPushButton(input_field)
                input_field_layout.addWidget(Button)
                Button.clicked.connect(self.Main.Options.update)
        
        input_field.setLayout(input_field_layout)
        
        tab_labels = [self.tabText(i) for i in range(self.count())]

        if not(page in tab_labels):
            PageWidget = QtGui.QWidget(self)
            self.addTab(PageWidget,page)
            FormLayout = QtGui.QFormLayout(PageWidget)
            FormLayout.setVerticalSpacing(10)
            FormLayout.setLabelAlignment(QtCore.Qt.AlignRight)
            PageWidget.setLayout(FormLayout)
            
        tab_labels = [self.tabText(i) for i in range(self.count())] # now it is updated
        self.setCurrentIndex(tab_labels.index(page))
        # get QFormLayout
        FormLayout = self.widget(tab_labels.index(page)).layout()
        
        # add row
        FormLayout.addRow(label,input_field)

        self.rows.append(input_field)
    pass

if __name__ == '__main__':
    pass