# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:21:29 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import scipy as sp

class ROIs_Object(QtCore.QObject):
    """ top level class of all ROIs. Contains all functionality that acts upon
    all ROIs together, like calculating the extraction mask.
    
    also contains the QSignalMapper and takes care of connecting the ROIs

    Also contains all the ROIs    
    
    method missing: reinstantiation of ROIs upon loading
    
    method missing: conversion binary mask - parametric mask
    """
    def __init__(self,Main):
        super(ROIs_Object,self).__init__()
                
        self.Main = Main

        self.ROI_list = []
        self.proxies = []
        
        pass
    
    def request_ROI_placement(self, evt):
        """ for ROI placement
        add functionality: watch for ROI placing toggle/switch        
        """
        if pg.graphicsItems.ViewBox.ViewBox == type(evt.currentItem): # this is the fix for the ROI in the corners bug
            if evt.button() == 1:
                # get correct position of mouse click
                pos = self.Main.Data_Display.Frame_Visualizer.ViewBox.mapToView(evt.pos())
                self.add_ROI(pos=sp.array([pos.x(),pos.y()]))
    
    def add_ROI(self,label=None,kind=None,pos=None,ROI_diameter=None,pos_list=None):
        """ this function is called and takes care of the proper ROI instantiation 
        kind etc. """
        
           
        if label == None:
            label = str(len(self.ROI_list) + 1)
        if kind == None:
            kind = self.Main.Options.ROI['type']
        if pos == None:
            ### FIXME raise error
            print "trying to instantiate ROI without position!"
        if ROI_diameter == None:
            ROI_diameter = self.Main.Options.ROI['diameter']
        
        # color the ROI according to the "active" dataset
        current_pen = pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8)

        if kind == 'circle':
            pos = pos - ROI_diameter / 2 # empirically determined - not understood - minus is correct ... 
            ROI = myCircleROI(self.Main,pos, [ROI_diameter,ROI_diameter], label, removable=True, pen=current_pen)
            
        if kind == 'polygon':
            if pos_list == None:
                pos_list = [[pos[0]-ROI_diameter,pos[1]-ROI_diameter], [pos[0]+ROI_diameter,pos[1]-ROI_diameter], [pos[0]+ROI_diameter,pos[1]+ROI_diameter], [pos[0]-ROI_diameter,pos[1]+ROI_diameter]]
                ROI = myPolyLineROI(self.Main, pos_list, label,  closed=True, removable=True, pen=current_pen)
        
        
            
        # link signals
        ROI.sigRemoveRequested.connect(self.remove_ROI)
        ROI.sigRegionChanged.connect(self.ROI_region_changed)        
#        ROI.sigHoverEvent.connect(self.ROI_hover)
        ROI.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        ROI.sigClicked.connect(self.ROI_clicked)
        
        # rate limit movement
        self.proxies.append(pg.SignalProxy(ROI.sigRegionChanged, rateLimit=30, slot=self.ROI_region_changed)) # FIXME this creates more and more proxies which are never destroyed

        # set only the current ROI active
        [roi.deactivate() for roi in self.ROI_list]
        ROI.activate()
        
        #
        self.ROI_list.append(ROI)
        self.Main.Data_Display.Frame_Visualizer.ViewBox.addItem(ROI)
        
        self.set_active_ROIs()
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
        
#        self.Main.Options.ROI['active_ROIs'] = self.get_active_ROIs()[1]
#        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()

        
    def remove_ROI(self,evt):
        """ remove a ROI, right click from popup menu"""
        ROI = evt.sender()
        self.Main.Data_Display.Frame_Visualizer.scene().removeItem(ROI)  ### FIXME signal needed
        ROI.removeTimer.stop() # fix from luke campagnola (pyqtgraph mailinglist) # seems to be unnecessary now?
        self.ROI_list.remove(ROI)
        self.Main.Options.ROI['active_ROIs'] = self.get_active_ROIs()[1]
        
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
               
    def get_active_ROIs(self):
        """ returns both boolean vector and indices """
        boolvec = [ROI.active for ROI in self.ROI_list]
        inds = sp.where(boolvec)[0]
        return boolvec,inds
        
    def set_active_ROIs(self):
        """ sets the ROI['active_ROIs'] """
        self.Main.Options.ROI['active_ROIs'] = self.get_active_ROIs()[1]
        self.Main.MainWindow.Data_Display.Traces_Visualizer.init_traces()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.init_traces()
        
        
    def ROI_label_change(self,evt): # find out where this stub is from and why it is needed
        """ connected to ROI manager textChange """
        self.ROI_list[evt.row()].label = evt.text()
        

                    
    def get_ROI_mask(self,ROI):
        """ helper for slicing the pixels out of the image below a ROI 
        calculates a boolean mask containing true if pixel inside ROI """
        mask = sp.zeros((self.Main.Data.raw.shape[0],self.Main.Data.raw.shape[1]),dtype='bool')
        
        # getArraySlice gets 1) array to slice 2) ImageItem
        inds = ROI.getArraySlice(self.Main.Data.raw[:,:,0,0], self.Main.Data_Display.Frame_Visualizer.ImageItems[0], returnSlice=False)[0]
        valinds = sp.where(ROI.getArrayRegion(self.Main.Data.raw[:,:,0,0], self.Main.Data_Display.Frame_Visualizer.ImageItems[0]) != 0)
        inds = sp.array([inds[0],inds[1]])
       
        true_inds = sp.array([valinds[0] + inds[0,0],valinds[1] + inds[1,0]])
        mask[true_inds[0],true_inds[1]] = True
        
        return mask,true_inds
    
    def ROI_region_changed(self,evt):
        """ interactive dragging of the ROI causes traces update """
        if type(evt) == myCircleROI or type(evt) == myPolyLineROI:
            return None

        ROI = evt[0]
        if not(ROI.active):
            [roi.deactivate() for roi in self.ROI_list]
            ROI.activate()
            self.set_active_ROIs()
            
        self.Main.Options.ROI['active_ROI_id'] = self.ROI_list.index(ROI)
        
        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
        
#    def ROI_hover(self,evt): # this one can be reimplemented
#        """ on ROI hover: update traces with the ROI hovered """
#        print "hovered"
#        ROI = evt.sender()
#        self.Main.Options.ROI['active_ROI_id'] = self.ROI_list.index(ROI)        
#        
#        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
        
    def ROI_clicked(self,evt):
        """ ROI gets activated upon click, if shift click multiple active can be
        selected """
        ROI = evt.sender()
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            ROI.toggle_state()
            "shift clicked"
            pass
        else:
            [roi.deactivate() for roi in self.ROI_list]
            "normal clicked"
            ROI.toggle_state()
        self.set_active_ROIs()
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
#        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.selection_changed()
        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
#        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
        

class myROI(object):
    def __init__(self,Main,label):
        self.Main = Main
        self.label = label
        self.active = False
        self.textItem = pg.TextItem(text=label)
        
    def activate(self):
        self.active = True
        self.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
    
    def deactivate(self):
        self.active = False
        self.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
    
    def toggle_state(self):
        if self.active == True:
            self.deactivate()
        if self.active == False:
            self.activate()
        pass
        
        
class myCircleROI(pg.CircleROI,myROI):
    def __init__(self,Main,pos,size,label,**kwargs):
        pg.CircleROI.__init__(self,pos,size,**kwargs)
        myROI.__init__(self, Main, label)
        
#        super(myCircleROI,self).__init__(pos,size,**kwargs)
        pass
    pass
        
class myPolyLineROI(pg.PolyLineROI,myROI):
    def __init__(self,Main,positions,label,**kwargs):
        pg.PolyLineROI.__init__(self, positions,**kwargs)
        myROI.__init__(self, Main, label)
#        super(myPolyLineROI,self).__init__(positions,**kwargs)

    def activate(self):
        print "now I am called"
        self.active = True
        for segment in self.segments:
            segment.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
    
    def deactivate(self):
        print "now I am called deactivaged"
        self.active = False
        for segment in self.segments:
            segment.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
        pass
    pass


#class myCircleROI(pg.CircleROI):
#    def __init__(self,Main,pos,size,label,**kwargs):
#        super(myCircleROI,self).__init__(pos,size,**kwargs)
#        self.Main = Main
#        self.id = None
#        self.label = label
#        self.active = False
#        
#        self.textItem = pg.TextItem(text=label)
#        
#    def activate(self):
#        self.active = True
#        self.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
#    
#    def deactivate(self):
#        self.active = False
#        self.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
#    
#    def toggle_state(self):
#        if self.active == True:
#            self.deactivate()
#        if self.active == False:
#            self.activate()
#        pass
#    
##    def get_ROI_center(self,ROI): # obsolete?
##        """ returns ROI center, used for label show """
##        pos = ROI.getState()['pos']
##        pos = sp.array([pos.x(),pos.y()])
##        pos = pos + self.Main.Options.ROI['diameter'] / 2.0 # here is is a plus. probably a ROI has it's coordinate 0,0 at the upper left corner, whereas the image 0,0 is bottom left
##        return pos
#    pass
#
#class myPolyLineROI(pg.PolyLineROI):
#    def __init__(self,Main,positions,label,**kwargs):
#        super(myPolyLineROI,self).__init__(positions,**kwargs)
#        self.Main = Main
#        self.id = None
#        self.label = label
#        self.active = False
#
#    def activate(self):
#        self.active = True
#        for segment in self.segments:
#            self.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
#    
#    def deactivate(self):
#        self.active = False
#        for segment in self.segments:
#            self.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
#        pass
#    
#    def toggle_state(self):
#        if self.active == True:
#            self.deactivate()
#        if self.active == False:
#            self.activate()
#        pass
#    pass



if __name__ == '__main__':
    import Main
    Main.main()
    pass