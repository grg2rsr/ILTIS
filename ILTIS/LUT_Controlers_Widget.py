# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:59:08 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import scipy as sp
from scipy import random

class LUT_Controlers_Widget(QtGui.QWidget):
    def __init__(self,Main,parent):
        super(LUT_Controlers_Widget,self).__init__()
        
        self.Main = Main
#        self.Main.LUT_Controlers = self
        
        self.Data_Display = parent

        self.raw_levels = []
        self.dFF_levels = []
        
        self.init_UI()
        pass
    
    def init_UI(self):
        self.LUTwidgets = QtGui.QStackedWidget()
        self.LUTwidgets_dFF = QtGui.QStackedWidget()
        
        # layout
        self.Layout = QtGui.QHBoxLayout()
        self.Layout.addWidget(self.LUTwidgets)
        self.Layout.addWidget(self.LUTwidgets_dFF)
        self.Layout.setMargin(0)
        self.Layout.setSpacing(0)
        self.setLayout(self.Layout)
        pass
    
    def init_data(self):
        # calculating colors
        self.Main.Options.view['colors'],self.Main.Options.view['color_maps'] = self.Main.Processing.calc_colormaps(self.Main.Data.nTrials)
        # ini and connect
        for n in range(self.Main.Data.nTrials):
            # for raw
            self.raw_levels.append(self.calc_levels(self.Main.Data.raw[:,:,:,n],fraction=(0.3,0.9995),nbins=100,samples=2000))
            LUTwidget = pg.HistogramLUTWidget()
            LUTwidget.setImageItem(self.Data_Display.Frame_Visualizer.ImageItems[n])
            LUTwidget.item.setHistogramRange(self.Main.Data.raw.min(),self.Main.Data.raw.max()) # disables autoscaling
            LUTwidget.item.setLevels(self.raw_levels[n][0],self.raw_levels[n][1])
            LUTwidget.item.gradient.setColorMap(self.Main.Options.view['color_maps'][n])
            self.LUTwidgets.addWidget(LUTwidget)
    
            # for dFF        
            self.dFF_levels.append(self.calc_levels(self.Main.Data.dFF[:,:,:,n],fraction=(0.7,0.9995),nbins=100,samples=2000))
            LUTwidget = pg.HistogramLUTWidget()
            LUTwidget.setImageItem(self.Data_Display.Frame_Visualizer.ImageItems_dFF[n])
            LUTwidget.item.setHistogramRange(self.Main.Data.dFF.min(),self.Main.Data.dFF.max()) # disables autoscaling
            LUTwidget.item.setLevels(self.dFF_levels[n][0],self.dFF_levels[n][1])
            LUTwidget.item.gradient.setColorMap(self.Main.Options.view['color_maps'][n])
            self.LUTwidgets_dFF.addWidget(LUTwidget)
            pass
        
        for n in range(self.Main.Data.nTrials):
            self.LUTwidgets.widget(n).item.sigLevelsChanged.connect(self.LUT_changed)
            self.LUTwidgets_dFF.widget(n).item.sigLevelsChanged.connect(self.LUT_changed)
            pass
        pass
    
    def update(self):
        # set the colormaps to monochrome + glow
        if self.Main.Options.view['show_monochrome'] == True:
            for i in range(self.Main.Data.nTrials):
                self.LUTwidgets.widget(i).item.gradient.setColorMap(self.Main.Options.view['graymap'])
                self.LUTwidgets_dFF.widget(i).item.gradient.setColorMap(self.Main.Options.view['heatmap'])
                    
        if self.Main.Options.view['show_monochrome'] == False:
            # restore colors
            for i in range(self.Main.Data.nTrials):
                self.LUTwidgets.widget(i).item.gradient.setColorMap(self.Main.Options.view['color_maps'][i])
                self.LUTwidgets_dFF.widget(i).item.gradient.setColorMap(self.Main.Options.view['color_maps'][i])
        
        # actions from selection_changed
        self.LUTwidgets.setCurrentWidget(self.LUTwidgets.widget(self.Main.Options.view['last_selected']))
        self.LUTwidgets_dFF.setCurrentWidget(self.LUTwidgets_dFF.widget(self.Main.Options.view['last_selected']))
        pass

    def reset(self):
        """ reset function """
        self.raw_levels = []
        self.dFF_levels = []
        for n in range(self.LUTwidgets.count()):
            self.LUTwidgets.removeWidget(self.LUTwidgets.widget(0))
            self.LUTwidgets_dFF.removeWidget(self.LUTwidgets_dFF.widget(0))
        pass
    
    def LUT_changed(self):
        # if global levels: take LUT levels from active LUT widget and write it to all
        if self.Main.Options.view['use_global_levels']:
            current_lut = self.LUTwidgets.currentIndex()
            for n in range(self.Main.Data.nTrials):
                levels = self.LUTwidgets.widget(current_lut).item.getLevels()
                self.raw_levels[n] = levels
                self.LUTwidgets.widget(n).item.setLevels(levels[0],levels[1])
                
                dFF_levels = self.LUTwidgets_dFF.widget(current_lut).item.getLevels()
                self.dFF_levels[n] = dFF_levels
                self.LUTwidgets_dFF.widget(n).item.setLevels(dFF_levels[0],dFF_levels[1])
                
        else:
            # else just get the levels and write them to the levels list for later retrieval
            for n in range(self.Main.Data.nTrials):
                levels = self.LUTwidgets.widget(n).item.getLevels()
                self.raw_levels[n] = levels
                self.LUTwidgets.widget(n).item.setLevels(levels[0],levels[1])
                
                dFF_levels = self.LUTwidgets_dFF.widget(n).item.getLevels()
                self.dFF_levels[n] = dFF_levels
                self.LUTwidgets_dFF.widget(n).item.setLevels(dFF_levels[0],dFF_levels[1])
                
        self.Main.Signals.LUTchangedSignal.emit()
        pass

     
    def calc_levels(self,data,fraction=(0.1,0.9),nbins=100,samples=None):
        # this function could be part of processing as well ... 
        """ fraction is a tuple with (low, high) in the range of 0 to 1 
        nbins is the number of bins for the histogram resolution

        if samples: draw this number of samples (random inds) for faster
        calculation
        """
        if samples:
#            data = data.flatten()[random.permutation(sp.arange(sp.prod(data.shape)))[:samples]]
            data = data.flatten()[random.randint(sp.prod(data.shape),size=samples)]
        else:
            data = data.flatten()
        y,x = sp.histogram(data,bins=nbins)
        cy = sp.cumsum(y).astype('float32')
        cy = cy / cy.max()
        minInd = sp.argmin(sp.absolute(cy - fraction[0]))
        maxInd = sp.argmin(sp.absolute(cy - fraction[1]))
        levels = (x[minInd],x[maxInd])
        return levels
        
    def reset_levels(self,which='dFF'):
        """ (re)calculate levels and set them """
        for n in range(self.Main.Data.nTrials):
            if which == 'dFF':
                levels = self.calc_levels(self.Main.Data.dFF[:,:,:,n],fraction=(0.7,0.9995),nbins=100,samples=2000)
                self.dFF_levels[n] = levels
                self.LUTwidgets_dFF.widget(n).item.setLevels(levels[0],levels[1])
                pass
            
            if which == 'raw':
                levels = self.calc_levels(self.Main.Data.raw[:,:,:,n],fraction=(0.3,0.9995),nbins=100,samples=2000)
                self.dFF_levels[n] = levels
                self.LUTwidgets_dFF.widget(n).item.setLevels(levels[0],levels[1])                
                pass


    pass