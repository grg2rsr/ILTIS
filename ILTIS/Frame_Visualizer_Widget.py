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
        self.active_inds = []
        
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
        self.scene().sigMouseClicked.connect(self.Main.ROIs.add_ROI_request)
#        self.scene().sigMouseMoved.connect(self.mouseMoved) # keep for debug
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

    def update_display_settings(self):
        """ is a slot. called via/connected to: selection changed signal of
        ROI_manager, all togglers """

        self.active_inds = sp.where(self.Main.Options.view['show_flags'])[0]

        # hide inactive
        for ind,val in enumerate(self.Main.Options.view['show_flags']):

            # hide all inactive
            if val == False:
                self.ImageItems[ind].hide()
                self.ImageItems_dFF[ind].hide()

            # for the active ones, show depending on show flags
            if val == True:
                if not(self.Main.Options.view['show_monochrome']) and not(self.Main.Options.view['show_dFF']):
                    self.ImageItems_dFF[ind].hide()
                    self.ImageItems[ind].show()

                if self.Main.Options.view['show_monochrome'] and not(self.Main.Options.view['show_dFF']):
                    self.ImageItems_dFF[ind].hide()
                    self.ImageItems[ind].show()

                if not(self.Main.Options.view['show_monochrome']) and self.Main.Options.view['show_dFF']:
                    self.ImageItems_dFF[ind].show()
                    self.ImageItems[ind].hide()

                if self.Main.Options.view['show_monochrome'] and self.Main.Options.view['show_dFF']:
                    self.ImageItems_dFF[ind].show()
                    self.ImageItems[ind].show()

                pass
            pass

        # set composition mode
        self.set_composition_mode(self.Main.Options.QtCompositionModes.index(self.Main.Options.view['composition_mode'])) ### FIXME
        ### FIXME set to default mode source atop if in monochrome mode
        self.update_frame()
        pass

    def update_levels(self):
        """ called from LUT_Controlers when it has levels changed """
        for ind in self.active_inds:
            self.ImageItems[ind].setLevels(self.Main.Data_Display.LUT_Controlers.raw_levels[ind])
            self.ImageItems_dFF[ind].setLevels(self.Main.Data_Display.LUT_Controlers.dFF_levels[ind])
            pass

    def update_frame(self):
        for ind in self.active_inds:
            if self.Main.Options.view['show_avg']:
                self.ImageItems_dFF[ind].setImage(sp.average(self.Main.Data.dFF[:,:,:,ind],axis=2))
                self.ImageItems[ind].setImage(sp.average(self.Main.Data.raw[:,:,:,ind],axis=2))
            else:
                self.ImageItems_dFF[ind].setImage(self.Main.Data.dFF[:,:,self.frame,ind])
                self.ImageItems[ind].setImage(self.Main.Data.raw[:,:,self.frame,ind])

        self.update_levels()
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

    def mouseMoved(self, evt):
        """ keep for debug """
        print("scene coordinates:", evt, "imageItem coordinates", self.ViewBox.mapToView(evt))
