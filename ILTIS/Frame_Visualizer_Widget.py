# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:59:05 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import scipy as sp

class Frame_Visualizer_Widget(pg.GraphicsView):

    def __init__(self,Main,parent):
        super(Frame_Visualizer_Widget,self).__init__()
        
        self.Main = Main
#        self.Main.Frame_Visualizer = self
        self.Main.Data_Display = parent
        
        self.ImageItems = [] # list with the image items
        self.ImageItems_dFF = [] # list with the image items

        self.frame = 0
        
        # weakrefs to data object and Options object
        self.init_UI()
        pass

    def init_UI(self):
        # UI
        self.ViewBox = pg.ViewBox()
        self.ViewBox.setAspectLocked()
        self.ViewBox.setAcceptDrops(True) # for drag and drop interaction? put it to the Data Selector!
        self.setCentralItem(self.ViewBox)
        
        # mouse interaction
        self.scene().sigMouseClicked.connect(self.Main.ROIs.request_ROI_placement)
        pass
    
    def init_data(self):
        ### initializing image and LUTwidget
        for n in range(self.Main.Data.nTrials):
            ImageItem_raw = pg.ImageItem(self.Main.Data.raw[:,:,self.frame,n])
            self.ViewBox.addItem(ImageItem_raw)
            self.ImageItems.append(ImageItem_raw)
            
            ImageItem_dFF = pg.ImageItem(self.Main.Data.dFF[:,:,self.frame,n])
            self.ViewBox.addItem(ImageItem_dFF)
            self.ImageItems_dFF.append(ImageItem_dFF)
        
        self.ViewBox.autoRange()
        pass    
        
    def update(self):
        """ former set image data."""
        """ 
        has to check: -is average? -is dFF? -flag to show? -only one?
       
        average behaviour: take all that are active, average and overlay
        
        dFF behaviour: if multiple channels are active, the dFF are over
        layed and colored according to their channel

        if only one channel is active:        
        raw is in grayscale, dFF is in glow color map
        """

        for n in range(self.Main.Data.nTrials):
            
            # hide inactive
            if self.Main.Options.view['show_flags'][n] == False: 
                self.ImageItems[n].hide()
                self.ImageItems_dFF[n].hide()

            # work only on those that are active
            if self.Main.Options.view['show_flags'][n] == True: 
                
                # when showing dFF
                if self.Main.Options.view['show_dFF']: 
                
                    # when in monochrome mode show
                    if self.Main.Options.view['show_monochrome']: 
                        self.ImageItems[n].show()
                    else:
                        self.ImageItems[n].hide()
                        
                    # when showing dFF avg
                    if self.Main.Options.view['show_avg']: 
                        self.ImageItems_dFF[n].setImage(sp.average(self.Main.Data.dFF[:,:,:,n],axis=2))
                        self.ImageItems[n].setImage(sp.average(self.Main.Data.raw[:,:,:,n],axis=2))
                    else: 
                        self.ImageItems_dFF[n].setImage(self.Main.Data.dFF[:,:,self.frame,n])
                        self.ImageItems[n].setImage(self.Main.Data.raw[:,:,self.frame,n])

                    self.ImageItems_dFF[n].show()
                    
                else: # when showing raw
                    self.ImageItems_dFF[n].hide()
                    # when showing raw avg
                    if self.Main.Options.view['show_avg']:
                        self.ImageItems[n].setImage(sp.average(self.Main.Data.raw[:,:,:,n],axis=2))
                    else:
                        self.ImageItems[n].setImage(self.Main.Data.raw[:,:,self.frame,n])
                        
                    self.ImageItems[n].show()
                
                # setting the corresponding levels
                self.ImageItems[n].setLevels(self.Main.Data_Display.LUT_Controlers.raw_levels[n])
                self.ImageItems_dFF[n].setLevels(self.Main.Data_Display.LUT_Controlers.dFF_levels[n])        
        
        self.set_composition_mode(12) ### FIXME
        pass
    
    def reset(self):
        ### clearing the GUI if it has been initialized before
        for item in self.ImageItems:
            self.ViewBox.removeItem(item)
        self.ImageItems = []
        for item in self.ImageItems_dFF:
            self.ViewBox.removeItem(item)
        self.ImageItems_dFF = []
        pass

       
    def set_composition_mode(self,n):
        """ set the composition mode for different blending properties """
        for ImageItem in self.ImageItems:
            ImageItem.setCompositionMode(n)
            
        for ImageItem in self.ImageItems_dFF:
            ImageItem.setCompositionMode(n)              
        

    
    pass