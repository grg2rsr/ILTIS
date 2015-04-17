# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import os

class Options_Control_Widget(QtGui.QTabWidget):
    """ the GUI widget to set the options, possibly one with tabs """
    def __init__(self,Main):
        super(Options_Control_Widget,self).__init__()
        
        self.Main = Main
#        self.Main.Options_Control = self
        
        self.rows = []
        
    def init_UI(self):
        self.setWindowTitle('Options')    
        for row_index,options_string in enumerate(self.Main.Options.settable_options):
            self.make_row(row_index,*options_string)
        self.fetch_options()
    
    def make_row(self,row_index,var_name,page,label,kind,choices):
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
        
        nFields = len(kind) # because kind is [type]*n
        
        for i in range(nFields):
            if kind[i] == 'int' or kind[i] == 'float':
                LineEdit = QtGui.QLineEdit(input_field)
                input_field_layout.addWidget(LineEdit)
                LineEdit.textChanged.connect(self.Main.Options.update)
            if kind[i] == 'bool':
                ComboBox = QtGui.QComboBox(input_field)
                for state in ['True','False']:
                    ComboBox.addItem(state)
                ComboBox.currentIndexChanged.connect(self.Main.Options.update)
                input_field_layout.addWidget(ComboBox)
            if kind[i] == 'string':
                ComboBox = QtGui.QComboBox(input_field)
                for choice in choices:
                    ComboBox.addItem(choice)
                ComboBox.currentIndexChanged.connect(self.Main.Options.update)
                input_field_layout.addWidget(ComboBox)
            if kind[i] == 'path':
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
        
    def fetch_options(self):
        """ reads the current options from the Options Object and updates the
        GUI """

        for row_index, row in enumerate(self.rows):
            kind = self.Main.Options.settable_options[row_index][3] # type
            nFields = len(kind) # nFileds
            choices = self.Main.Options.settable_options[row_index][4] # choices

            dict_name = self.Main.Options.settable_options[row_index][0][0]
            param_name = self.Main.Options.settable_options[row_index][0][1]
            
            for i in range(nFields):
                # reading val
                if nFields == 1:
                    val = getattr(self.Main.Options,dict_name)[param_name]
                if nFields > 1:
                    val = getattr(self.Main.Options,dict_name)[param_name][i]
                    
                val = str(val)
                
                # converting from user input to variable format
                if kind[i] == 'int':
                    row.children()[i+1].setText(val) # first child is the layout, the following are the input fields                    
                    
                if kind[i] == 'float':
                    row.children()[i+1].setText(val) # first child is the layout, the following are the input fields                    
                        
                if kind[i] == 'bool':
                    row.children()[i+1].setCurrentIndex(['True','False'].index(val))
  
                if kind[i] == 'string':
                    row.children()[i+1].setCurrentIndex(choices.index(val))
                    pass
                
                if kind[i] == 'path':
                    pass
    pass

if __name__ == '__main__':
    pass