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
        pass
    
    def reset(self):
        """ removes all ROIs """

        while len(self.ROI_list) > 0:
            ROI = self.ROI_list.pop()
            self.Main.Data_Display.Frame_Visualizer.scene().removeItem(ROI)
            self.Main.Data_Display.Frame_Visualizer.scene().removeItem(ROI.labelItem)
        
        self.Main.Options.ROI['last_active'] = None
                    
    def add_ROI_request(self, evt):
        """ for ROI placement
        add functionality: watch for ROI placing toggle/switch        
        """
        if pg.graphicsItems.ViewBox.ViewBox == type(evt.currentItem): # this is the fix for the ROI in the corners bug
            if evt.button() == 1:
                # get correct position of mouse click
                pos = self.Main.Data_Display.Frame_Visualizer.ViewBox.mapToView(evt.pos())
                self.add_ROI(pos=sp.array([pos.x(),pos.y()]))
                
    def remove_ROI_request(self,evt):
        """ for ROI removal, clicked from popup menu """
        ROI = evt.sender()
        self.remove_ROI(ROI)
        pass
        
    
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
        
            

        # set only the current ROI active
        [roi.deactivate() for roi in self.ROI_list]
        ROI.activate()
        
        # add ROI
        self.ROI_list.append(ROI)
        self.Main.Options.ROI['last_active'] = ROI
        self.Main.Data_Display.Frame_Visualizer.ViewBox.addItem(ROI)
        
        # update
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
        self.update_active_ROIs()
        
        
    def remove_ROI(self,ROI):
        """ remove a ROI, update all necessary  """
        
        self.Main.Data_Display.Frame_Visualizer.scene().removeItem(ROI)
        self.Main.Data_Display.Frame_Visualizer.scene().removeItem(ROI.labelItem)
        
        ROI.removeTimer.stop() # fix suggestion from luke campagnola (pyqtgraph mailinglist) # seems to be unnecessary now?
        
        # if the removed ROI was the last active, then set the var to none
        if ROI == self.Main.Options.ROI['last_active']:
            self.Main.Options.ROI['last_active'] = None
        
        # remove reference from ROI_list
        self.ROI_list.remove(ROI)
        
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.set_current_selection()
        self.update_active_ROIs()
        
        
    def get_active_ROIs(self):
        """ returns both boolean vector and indices """
        boolvec = [ROI.active for ROI in self.ROI_list]
        inds = sp.where(boolvec)[0]
        return boolvec,inds

        
    def update_active_ROIs(self):
        """ sets the ROI['active_ROIs'] """
        self.Main.Options.ROI['active_ROIs'] = self.get_active_ROIs()[1]
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.set_current_selection()
        
        self.update_display_settings()
        self.Main.MainWindow.Data_Display.Traces_Visualizer.init_traces()
        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.init_traces()
        
        
    def ROI_label_change(self,evt): # find out where this stub is from and why it is needed
        """ connected to ROI manager textChange """
        self.ROI_list[evt.row()].update_label(evt.text())
        

                    
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
        ROI = evt[0]
        if not(ROI.active):
            [roi.deactivate() for roi in self.ROI_list]
            ROI.activate()
            self.update_active_ROIs()
        
        ROI.update_center()
        self.Main.Options.ROI['last_active'] = ROI
        
        self.Main.MainWindow.Data_Display.Traces_Visualizer.update_traces()
        self.Main.MainWindow.Data_Display.Traces_Visualizer_Stimsorted.update_traces()
        
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
        else:
            [roi.deactivate() for roi in self.ROI_list]
            ROI.toggle_state()
        
        self.Main.Options.ROI['last_active'] = ROI
        self.update_active_ROIs()
        self.update_display_settings()
        
    def update_display_settings(self):
        # handle the labels
        if self.Main.Options.ROI['show_labels'] == True:
            [ROI.labelItem.show() for ROI in self.ROI_list]
        if self.Main.Options.ROI['show_labels'] == False:
            [ROI.labelItem.hide() for ROI in self.ROI_list]
            
        # handle the ROI colors
        nActiveROIs = len(self.Main.Options.ROI['active_ROIs'])
        
        # one ROI active, active/inactive color scheme
        if nActiveROIs == 1:
            for ROI in self.ROI_list:
                if ROI.active == True:
                    ROI.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
                if ROI.active == False:
                    ROI.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
                
        # multiple ROI active, traces colored to ROI
        if nActiveROIs > 1:
            colors = self.Main.Processing.calc_colors(nActiveROIs)
            for i,ROI_id in enumerate(self.Main.Options.ROI['active_ROIs']):
                self.ROI_list[ROI_id].setPen(pg.mkPen(colors[i],width=1.8))
                
        pass
    
class myROI(object):
    def __init__(self,Main,label):
        self.Main = Main
        self.label = label
        self.active = False
        self.center = self.get_center()
        self.labelItem = pg.TextItem(text=label,anchor=(0.5,0.5))
        self.update_center()
        self.Main.Data_Display.Frame_Visualizer.ViewBox.addItem(self.labelItem)
    
        # link signals
        self.sigRemoveRequested.connect(self.Main.ROIs.remove_ROI_request)
        self.proxy = pg.SignalProxy(self.sigRegionChanged, rateLimit=30, slot=self.Main.ROIs.ROI_region_changed) # rate limit movement
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.sigClicked.connect(self.Main.ROIs.ROI_clicked)
        

    def activate(self):
        self.active = True
        self.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
    
    def deactivate(self):
        self.active = False
        self.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
    
    def toggle_state(self):
        if self.active == True:
            self.deactivate()
        elif self.active == False:
            self.activate()
    
    def update_center(self):
        self.center = self.get_center()
        self.labelItem.setPos(self.center[0],self.center[1])
#        print self.center
        pass

    def update_label(self,text):
        self.label = text
        self.labelItem.setText(self.label)
        
       
        
class myCircleROI(pg.CircleROI,myROI):
    def __init__(self,Main,pos,size,label,**kwargs):
        pg.CircleROI.__init__(self,pos,size,**kwargs)
        myROI.__init__(self, Main, label)
        self.diameter = self.size()[0]
        
    def get_center(self):
        """ returns ROI center, used for label show """
        pos = self.getState()['pos']
        pos = sp.array([pos.x(),pos.y()])
        pos = pos + self.size()[0] / 2.0 # here is is a plus. probably a ROI has it's coordinate 0,0 at the upper left corner, whereas the image 0,0 is bottom left
        return pos
        
    def update_center(self):
        self.center = self.get_center()
        self.labelItem.setPos(self.center[0],self.center[1])
        self.diameter = self.size()[0]

        
class myPolyLineROI(pg.PolyLineROI,myROI):
    def __init__(self,Main,positions,label,**kwargs):
        pg.PolyLineROI.__init__(self, positions,**kwargs)
        myROI.__init__(self, Main, label)
        
        # also workaround for the weird first_call bug
        self.center = self.get_center(first_call=True)
        self.labelItem.setPos(self.center[0],self.center[1])

    def activate(self):
        self.active = True
        for segment in self.segments:
            segment.setPen(pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8))
    
    def deactivate(self):
        self.active = False
        for segment in self.segments:
            segment.setPen(pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8))
        pass
    
    def get_center(self,first_call=False):
        """ returns ROI center, used for label show 
        first_call kw for handling the weird bug upon first call to mapToView:
        this returns wrong coordinates"""
        handle_pos = [tup[1] for tup in self.getSceneHandlePositions()]
        pos_mapped = [self.Main.Data_Display.Frame_Visualizer.ViewBox.mapToView(pos) for pos in handle_pos]
        if first_call == True:
            h_pos = sp.array([[p.x(),p.y()] for p in handle_pos])
        else:
            h_pos = sp.array([[p.x(),p.y()] for p in pos_mapped])
        pos = sp.average(h_pos,axis=0)
        return pos
        
    pass


if __name__ == '__main__':
    import Main
    Main.main()
    pass