# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:23:18 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import os
import scipy as sp

class Options_Control_Widget(QtGui.QTabWidget):
    """ the GUI widget to set the options, possibly one with tabs """
    def __init__(self,Main):
        super(Options_Control_Widget,self).__init__()
        
        self.Main = Main
        self.parent = Main
        self.rows = []
    

    ### UI generation
    def init_UI(self):
        """ deactivate all Qt Signals from this object during init_UI 
        definition of options_string: row_label"""
        self.setWindowTitle('Options')    
        self.make_rows()
        self.get_options_and_set_UI()
        
    def reset_UI(self):
        """ if number of stim changes, then a) change the settable_options b)
        redo the whole UI with the new settable ones """
        
        for tab_ind in range(self.count()):
            self.removeTab(tab_ind)
        
        self.init_UI()
        pass
    

    
    def make_row(self,widget=None,dict_name=None,param_name=None,row_label=None,tab_label=None,**kwargs):
        """ generates a single row based on label and widget, and adds it to the 
        specified tab """
        
        # current tab labels
        tab_labels = [self.tabText(i) for i in range(self.count())]

        # if tab_label is first time, make the tab with a form layout inside
        if not(tab_label in tab_labels):
            tab_widget = QtGui.QWidget(self)
            self.addTab(tab_widget,tab_label)
            FormLayout = QtGui.QFormLayout(tab_widget)
            FormLayout.setVerticalSpacing(10)
            FormLayout.setLabelAlignment(QtCore.Qt.AlignRight)
            tab_widget.setLayout(FormLayout)
        
        # updated tab labels
        tab_labels = [self.tabText(i) for i in range(self.count())]
        self.setCurrentIndex(tab_labels.index(tab_label))
        
        # get QFormLayout ... 
        FormLayout = self.widget(tab_labels.index(tab_label)).layout()
        
        # .. and add row
        FormLayout.addRow(row_label,widget)
        self.rows.append([dict_name,param_name,widget]) # to be able to iterate over it, better: write a get_all_rows function
        pass
    
    def make_rows(self):
        """ iterate over settable_options """
        for row_index,options_dict in enumerate(self.Main.Options.settable_options):
            if options_dict['kind'] == 'infer':
                widget = self.infer_widget(**options_dict)
            if options_dict['kind'] == 'choices':
                widget = self.make_comboBox_widget(**options_dict)
            if options_dict['kind'] == 'path':
                widget = self.make_path_select_widget()
                pass
                
            self.make_row(widget=widget,**options_dict)
        pass

    def infer_widget(self,dict_name=None,param_name=None,**kwargs):
        """ infers the correct input type widget, based on data type and dimensionality """

        var = sp.array(getattr(self.Main.Options,dict_name)[param_name])
        dtype = var.dtype.kind # needs np dtype!
        dim = var.shape
        nDim = len(dim)
        
        if nDim == 0:
            InputWidget = QtGui.QTableWidget(1,1,parent=self)

        if nDim == 1:
            InputWidget = QtGui.QTableWidget(1,dim[0],parent=self)
        if nDim == 2:
            InputWidget = QtGui.QTableWidget(dim[0],dim[1],parent=self)
        InputWidget.cellChanged.connect(self.Main.Options.update)
        InputWidget.horizontalHeader().hide()
        
        InputWidget.setFixedHeight(InputWidget.rowHeight(0) * InputWidget.rowCount())
        InputWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch) 

#        InputWidget.resizeColumnsToContents()
        
        InputWidget.verticalHeader().hide()
        

        return InputWidget
    
    ### makers - put all custom widgets in here    
    def make_comboBox_widget(self,dict_name=None,param_name=None,choices=None,**kwargs):
        ComboBox = QtGui.QComboBox(parent=self)
        for choice in choices:
            ComboBox.addItem(choice)
        ComboBox.currentIndexChanged.connect(self.Main.Options.update)
        return ComboBox
        
    def make_path_select_widget(self):
        Button = QtGui.QPushButton('select path',parent=self)
        Button.clicked.connect(self.Main.IO.OpenFileDialog) # stub with dialogoptions
        return Button
    
    ### interaction w Option_Object    
    def get_options_and_set_UI(self):
        """ reads the current options from the Options Object and updates the
        GUI """

        widgets = [row[2] for row in self.rows]
        # deactivate signals, because this function is called in a circular manner from Options_Object
        [widget.blockSignals(True) for widget in widgets]
        
        for i,widget in enumerate(widgets):
            dict_name = self.rows[i][0]
            param_name = self.rows[i][1]
            # QComboBox            
            if type(widget) == QtGui.QComboBox:
                choices = self.Main.Options.settable_options[i]['choices']
                # hack for boolean
                if choices == ['True','False']:
                    choices = [True,False]
                val = getattr(self.Main.Options,dict_name)[param_name]
                widget.setCurrentIndex(choices.index(val))

            # QTableWidget            
            if type(widget) == QtGui.QTableWidget:
                var = sp.array(getattr(self.Main.Options,dict_name)[param_name])
                dtype = var.dtype.kind # needs np dtype!
                dim = var.shape
                nDim = len(dim)
#                import pdb
#                pdb.set_trace()
                if nDim == 0:
                    widget.setItem(0,0,QtGui.QTableWidgetItem(str(var)))
                    pass
                if nDim == 1:
                    for c in range(widget.columnCount()):
                        widget.setItem(0,c,QtGui.QTableWidgetItem(str(var[c])))
                    pass
                if nDim == 2:
                    for r in range(widget.rowCount()):
                        for c in range(widget.columnCount()):
                            widget.setItem(r,c,QtGui.QTableWidgetItem(str(var[r,c])))


        # reactivate signals
        [widget.blockSignals(False) for widget in widgets]
#        for row in self.rows:
#            widget = row[2]
#            for child in widget.children():
#                child.blockSignals(False)
    pass



if __name__ == '__main__':
    import Main
    Main.main()
    pass