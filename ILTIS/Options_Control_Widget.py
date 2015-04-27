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

    ### UI generation
    def init_UI(self):
        """ deactivate all Qt Signals from this object during init_UI 
        definition of options_string: row_label"""
        self.setWindowTitle('Options')    

        ### general
        FormLayout = self.make_tab('General')
        FormLayout.addRow('verbose mode',BooleanChoiceWidget(self,'general','verbose'))
#        FormLayout.addRow('options filepath',self.BooleanChoiceWidget(self))
#        options filepath
#        cwd
        ### preprocessing
        FormLayout = self.make_tab('Preprocessing')
#        nStimuli
#        FormLayout.addRow('number of stimuli',SingleValueWidget(self,'preprocessing','nStimuli','i'))
        FormLayout.addRow('start/stop frames of stimuli',StimRegionWidget(self,'preprocessing','stimuli',self.Main.Options.preprocessing['nStimuli'],2,'i'))
#        FormLayout.addRow('start/stop frames of stimuli',ArrayWidget(self,'preprocessing','stimuli',self.Main.Options.preprocessing['nStimuli'],2,'i'))
        FormLayout.addRow('start/stop frames for background calculation',VectorWidget(self,'preprocessing','dFF_frames',2,'i'))
        FormLayout.addRow('[xy,t] filter size',VectorWidget(self,'preprocessing','filter_size',2,'f'))

        ### view
        FormLayout = self.make_tab('View')
        FormLayout.addRow('image composition mode',StringChoiceWidget(self,'view','composition_mode',choices=self.Main.Options.QtCompositionModes))
        FormLayout.addRow('show trial labels on stim-sorted traces',BooleanChoiceWidget(self,'view','trial_labels_on_traces_vis'))
      
        ### ROI
        FormLayout = self.make_tab('ROI')
        FormLayout.addRow('ROI default diameter',SingleValueWidget(self,'ROI','diameter','i'))
        FormLayout.addRow('ROI type',StringChoiceWidget(self,'ROI','type',choices=['circle','polygon']))
        FormLayout.addRow('show ROI labels',BooleanChoiceWidget(self,'ROI','show_labels'))

        ### export
        FormLayout = self.make_tab('Export')
        FormLayout.addRow('Export traces from',StringChoiceWidget(self,'export','data',choices=['raw','dFF']))
        FormLayout.addRow('Export format',StringChoiceWidget(self,'export','format',choices=['.csv','.gloDatamix']))

        self.get_options()
        self.nStimuli_old = self.Main.Options.preprocessing['nStimuli']
        for row in self.get_rows():
            row[1].connect()
        
    def reset_UI(self):
        """ if number of stim changes, redo the whole UI with the new settable 
        ones """
        print "resetting UI"
        for tab_ind in range(self.count()):
            self.removeTab(0) # removes all ... 
        self.rows = []

        
        self.init_UI()
        pass
    
    def get_rows(self):
        """ helper, generates a list with [label,widget] of all settables 
        over all tabs """
        rows = []
        # iterate over tabs
        for tab_ind in range(self.count()):
#            tab = self.setCurrentIndex(tab_ind)
            tab = self.widget(tab_ind)
            FormLayout = tab.layout()
            for row_ind in range(FormLayout.rowCount()):
                label = FormLayout.itemAt(row_ind,0).widget()
                widget = FormLayout.itemAt(row_ind,1).widget()
                rows.append([label,widget])
        return rows
                
        # iterate over rows
    def make_tab(self,tab_label):
        """ helper: makes a tab page, pace QFormLayout inside and return it """
        tab_widget = QtGui.QWidget(self)
        self.addTab(tab_widget,tab_label)
        FormLayout = QtGui.QFormLayout(tab_widget)
        FormLayout.setVerticalSpacing(10)
        FormLayout.setLabelAlignment(QtCore.Qt.AlignRight)
        tab_widget.setLayout(FormLayout)
        return FormLayout

    def UI_changed(self):
        # set changes to the Options_object
        self.set_options()

        # check if number of stim has changed
#        nStimuli = self.Main.Options.preprocessing['nStimuli']
#        if nStimuli != self.nStimuli_old:
#            row_ind = [row[1].param_name for row in self.get_rows()].index('stimuli')
##            self.widget(1).layout().setRowCount(5)
#            table = self.get_rows()[row_ind][1]
#            table.insertRow(table.rowCount())
#            self.widget(1).layout().insertRow(row_ind,'replace',ArrayWidget(self,'preprocessing','stimuli',self.Main.Options.preprocessing['nStimuli'],2,'i'))
            
            
#            if nStimuli == 1:
#                self.Main.Options.preprocessing['stimuli'] = sp.array([self.Main.Options.preprocessing['stimuli'][0,:]])
#            if nStimuli > 1:
#                for i in range(1,nStimuli):
#                    new_stim = sp.zeros((nStimuli,2),dtype='int32')
#                    new_stim[i,0] = self.Main.Options.preprocessing['stimuli'][0,0] * i
#                    new_stim[i,1] = self.Main.Options.preprocessing['stimuli'][0,1] * i
#                self.Main.Options.preprocessing['stimuli'] = new_stim
            
#            self.reset_UI()
#            self.setCurrentIndex(1)
#            self.nStimuli_old = nStimuli # set n stim
            
            
        self.Main.Signals.updateDisplaySettingsSignal.emit()
        pass
    
    def get_options(self):
        for row in self.get_rows():
            widget = row[1]
            widget.blockSignals(True)
            widget.set_value(getattr(self.Main.Options,widget.dict_name)[widget.param_name])
            widget.blockSignals(False)
    
    def set_options(self):
        for row in self.get_rows():
            widget = row[1]
            getattr(self.Main.Options,widget.dict_name)[widget.param_name] = widget.get_value()
            

#==============================================================================
# Custom Widgets
#==============================================================================

class StringChoiceWidget(QtGui.QComboBox):
    def __init__(self,parent,dict_name,param_name,choices):
        super(StringChoiceWidget,self).__init__(parent=parent)
        self.dict_name = dict_name
        self.param_name = param_name
        self.choices = choices
        self.parent = parent
        for choice in self.choices:
            self.addItem(choice)
        
    def connect(self):
        self.currentIndexChanged.connect(self.parent.UI_changed)
        
    def get_value(self):
        return self.choices[self.currentIndex()]
    
    def set_value(self,value):
        self.setCurrentIndex(self.choices.index(value))
        
        
class BooleanChoiceWidget(QtGui.QComboBox):
    def __init__(self,parent,dict_name,param_name,choices=['Yes','No']):
        super(BooleanChoiceWidget,self).__init__(parent=parent)
        self.dict_name = dict_name
        self.param_name = param_name
        self.choices = choices
        self.parent = parent
        for choice in self.choices:
            self.addItem(choice)
        
    def connect(self):
        self.currentIndexChanged.connect(self.parent.UI_changed)
        
    def get_value(self):
        if self.choices[self.currentIndex()] == 'Yes':
            return True
        else:
            return False
    
    def set_value(self,value):
        if value == True:
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(1)
     
       
class SingleValueWidget(QtGui.QLineEdit):
    def __init__(self,parent,dict_name,param_name,dtype):
        super(SingleValueWidget,self).__init__(parent=parent)
        self.parent = parent
        self.dict_name = dict_name
        self.param_name = param_name
        self.dtype = dtype

    
    def connect(self):
        self.editingFinished.connect(self.parent.UI_changed)
        
    def get_value(self):
        return sp.array(str(self.text())).astype(self.dtype)
    
    def set_value(self,value):
        value = sp.array(value)
        if value.dtype.kind != self.dtype:
            raise ValueError('trying to set a Options_Control UI field with the wrong datatype!')
        self.setText(str(value)) # rounding?
        
        
class VectorWidget(QtGui.QTableWidget):
    def __init__(self,parent,dict_name,param_name,columns,dtype):
        super(VectorWidget,self).__init__(1,columns,parent=parent)
        self.parent = parent
        self.dict_name = dict_name
        self.param_name = param_name
        self.dtype = dtype

        self.parent = parent
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        
        self.setFixedHeight(self.rowHeight(0) * self.rowCount())
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch) 
        
        for col_ind in range(self.columnCount()):
            self.setItem(0,col_ind,QtGui.QTableWidgetItem(''))

    def connect(self):
        self.cellChanged.connect(self.parent.UI_changed)
        
    def get_value(self):
        value = sp.zeros(self.columnCount(),dtype=self.dtype)
        for col_ind in range(self.columnCount()):
            value[col_ind] = sp.array(str(self.item(0,col_ind).text())).astype(self.dtype)
            
        return value
    
    def set_value(self,value):
        value = sp.array(value)
        if value.dtype.kind != self.dtype:
            raise ValueError('trying to set a Options_Control UI field with the wrong datatype!')
        for col_ind in range(self.columnCount()):
            self.item(0,col_ind).setText(str(value[col_ind]))
    
    
class ArrayWidget(QtGui.QTableWidget):
    def __init__(self,parent,dict_name,param_name,rows,columns,dtype):
        super(ArrayWidget,self).__init__(rows,columns,parent=parent)
        self.dict_name = dict_name
        self.param_name = param_name
        self.dtype = dtype
        self.parent = parent

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        
        self.setFixedHeight(self.rowHeight(0) * self.rowCount())
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        for row_ind in range(self.rowCount()):
            for col_ind in range(self.columnCount()):
                self.setItem(row_ind,col_ind,QtGui.QTableWidgetItem(''))

    def connect(self):
        self.cellChanged.connect(self.parent.UI_changed)
        
    def get_value(self):
        value = sp.zeros((self.rowCount(),self.columnCount()),dtype=self.dtype)
        for row_ind in range(self.rowCount()):
            for col_ind in range(self.columnCount()):
                value[row_ind,col_ind] = sp.array(str(self.item(row_ind,col_ind).text())).astype(self.dtype)
        return value
    
    def set_value(self,value):
        value = sp.array(value)
        if value.dtype.kind != self.dtype:
            raise ValueError('trying to set a Options_Control UI field with the wrong datatype!')
        for row_ind in range(self.rowCount()):
            for col_ind in range(self.columnCount()):
                self.item(row_ind,col_ind).setText(str(value[row_ind,col_ind]))
                
class PathSelectWidget(QtGui.QWidget):
    def __init__(self,parent,dict_name,param_name,label='select path',FileDialogOptions=None):
        super(PathSelectWidget,self).__init__(parent=parent)
        self.dict_name = dict_name
        self.param_name = param_name

        self.parent = parent
        self.FileDialogOptions = FileDialogOptions
        
        self.Button = QtGui.QPushButton(self,label)
        self.PathDisplay = QtGui.QLineEdit(self)
        
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.Button)
        layout.addWidget(self.PathDisplay)

        self.path = None

    def connect(self):
        self.Button.clicked.connect(self.clicked)
        
    def clicked(self):
#        path = self.Main.IO.OpenFileDialog(self.FileDialogOptions)
        self.path = self.Main.IO.OpenFileDialog() # FIXME
        self.set_value(self.path)
        self.parent.UI_changed()
        
    def get_value(self):
        return self.path
        
    def set_value(self,value):
        self.PathDisplay.setText(value)

class StimRegionWidget(QtGui.QWidget):
    """ just an ArrayWidget with a plus and a minus button above to add / remove
    stimuli """
    def __init__(self,parent,dict_name,param_name,rows,columns,dtype):
        super(StimRegionWidget,self).__init__(parent=parent)
        
        self.parent = parent
        self.dict_name = dict_name
        self.param_name = param_name
        
        self.StimTable = ArrayWidget(parent,dict_name,param_name,rows,columns,dtype)
        self.PlusButton = QtGui.QPushButton('+')
        self.MinusButton = QtGui.QPushButton('-')
        
        BtnLayout = QtGui.QHBoxLayout()
        BtnLayout.addWidget(self.PlusButton)
        BtnLayout.addWidget(self.MinusButton)
#        
        AllLayout = QtGui.QVBoxLayout()
        AllLayout.addLayout(BtnLayout)
        AllLayout.addWidget(self.StimTable)
        
        self.setLayout(AllLayout)

    def connect(self):
        self.StimTable.connect()
        self.PlusButton.clicked.connect(self.addRow)
        self.MinusButton.clicked.connect(self.removeRow)
    
    def addRow(self):
        stimuli = self.get_value()
        self.StimTable.blockSignals(True)
        self.StimTable.insertRow(self.StimTable.rowCount())
        a = stimuli[-1,0]
        b = stimuli[-1,1]
        self.StimTable.setItem(self.StimTable.rowCount()-1,0,QtGui.QTableWidgetItem(str(b + (b-a))))
        self.StimTable.setItem(self.StimTable.rowCount()-1,1,QtGui.QTableWidgetItem(str(b + 2*(b-a))))
        self.StimTable.blockSignals(False)
        
        self.parent.UI_changed()
        pass
    
    def removeRow(self):
        stimuli = self.get_value()
        self.StimTable.removeRow(self.StimTable.rowCount()-1)
        self.set_value(stimuli[:-1,:])
        self.parent.UI_changed()
        pass
    
    def get_value(self):
        return self.StimTable.get_value()
    
    def set_value(self,value):
        self.StimTable.set_value(value)
        pass
    
        
if __name__ == '__main__':
    import Main
    Main.main()
    pass
