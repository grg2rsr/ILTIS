# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:21:29 2015

@author: georg
"""
import pyqtgraph as pg
import scipy as sp

class ROIs_Object(object):
    """ top level class of all ROIs. Contains all functionality that acts upon
    all ROIs together, like calculating the extraction mask.
    
    also contains the QSignalMapper and takes care of connecting the ROIs

    Also contains all the ROIs    
    
    method missing: reinstantiation of ROIs upon loading
    
    method missing: conversion binary mask - parametric mask
    """
    def __init__(self,Main):
                
        self.Main = Main
        self.Main.ROIs = self
        
        # print instantiation
        if self.Main.verbose:
            print type(self), ' was instantiated'        

        
        self.ROI_list = []
        self.nROIs = 0
        self.proxies = []
        
        pass
    
    def add_ROI(self,label=None,layer=None,kind=None,pos=None,ROI_diameter=None,pos_list=None):
        """ this function is called and takes care of the proper ROI instantiation 
        kind etc. """
        
        if layer == None:
            if self.Main.Options.ROI['place_in_layer'] == 'last active':
                layer = self.Main.Options.view['last_selected']
            if self.Main.Options.ROI['place_in_layer'] == 'default layer':
                layer = self.Main.Options.ROI['default_layer']
            
            
        if label == None:
            label = str(self.nROIs + 1)
        if kind == None:
            kind = self.Main.Options.ROI['type']
        if pos == None:
            ### FIXME raise error
            print "trying to instantiate ROI without position!"
        if ROI_diameter == None:
            ROI_diameter = self.Main.Options.ROI['diameter']
        
        # color the ROI according to the "active" dataset
        current_pen = pg.mkPen(self.Main.Data_Display.colors[layer],width=1.8)

        if kind == 'circle':
            pos = pos - ROI_diameter / 2 # empirically determined - not understood - minus is correct ... 
            ROI = myCircleROI(pos, [ROI_diameter,ROI_diameter], label, layer, removable=True, pen=current_pen)
            
        if kind == 'polygon':
            if pos_list == None:
                pos_list = [[pos[0]-ROI_diameter,pos[1]-ROI_diameter], [pos[0]+ROI_diameter,pos[1]-ROI_diameter], [pos[0]+ROI_diameter,pos[1]+ROI_diameter], [pos[0]-ROI_diameter,pos[1]+ROI_diameter]]
                ROI = myPolyLineROI(pos_list, label, layer, closed=True, removable=True, pen=current_pen)
        
        
            
        # link signals
        ROI.sigRemoveRequested.connect(self.remove_ROI)
        ROI.sigRegionChanged.connect(self.ROI_region_changed)        
        ROI.sigHoverEvent.connect(self.ROI_hover) # also her needs to be the ROI_manager clicked thing
        
        # rate limit movement
        self.proxies.append(pg.SignalProxy(ROI.sigRegionChanged, rateLimit=30, slot=self.ROI_region_changed)) # FIXME this creates more and more proxies which are never destroyed

        self.ROI_list.append(ROI)
        self.active_ROI_id = len(self.ROI_list) - 1
        self.Main.Data_Display.Frame_Visualizer.ViewBox.addItem(ROI)  ### FIXME signal needed
        
        self.nROIs += 1
        self.Main.ROI_Manager.update()  ### FIXME signal needed
        
    def remove_ROI(self,evt):
        """ remove a ROI, right click from popup menu"""
        ROI = evt.sender()
        self.Main.Data_Display.Frame_Visualizer.scene().removeItem(ROI)  ### FIXME signal needed
        ROI.removeTimer.stop() # fix from luke campagnola (pyqtgraph mailinglist) # seems to be unnecessary now?
        self.ROI_list.remove(ROI)
        self.active_ROI_id = self.active_ROI_id - 1 ### FIXME
        self.nROIs = self.nROIs - 1
        self.Main.ROI_Manager.update()  ### FIXME signal needed
        
    def get_ROI_position(self,ROI): # obsolete, never called?
        """ returns ROI position. check if it makes any sense with polygon ROIs"""
        pos = ROI.getState()['pos']
        pos = sp.array([pos.x(),pos.y()])
        pos = pos + self.Main.Options.ROI['diameter'] / 2.0 # here is is a plus. probably a ROI has it's coordinate 0,0 at the upper left corner, whereas the image 0,0 is bottom left
        return pos
        

    def ROI_label_change(self,evt):
        self.ROI_list[evt.row()].label = evt.text()
        
                    
    def get_ROI_mask(self,ROI):
        """ helper for slicing the pixels out of the image below a ROI 
        calculates a boolean mask containing true if pixel inside ROI """
        mask = sp.zeros((self.Main.Data.raw.shape[0],self.Main.Data.raw.shape[1]),dtype='bool')
        
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
        self.active_ROI_id = self.ROI_list.index(ROI)
        
#        if ROI == pg.graphicsItems.ROI.CircleROI:
#            print self.OptionsWindow.O
#            diameter = ROI.getState()['size'].x()
#            self.OptionsWindow.Options['ROI_diameter'] = diameter
#            self.OptionsWindow.ROI_diameter_edit.setText(str(sp.around(diameter,decimals=2)))
#            self.OptionsWindow.update_options()

#        pos = self.get_ROI_position(ROI)
        
        self.Main.Data_Display.Traces_Visualizer.update()  ### FIXME signal needed
        self.Main.Data_Display.Traces_Visualizer_Stimsorted.update()  ### FIXME signal needed
        
    def ROI_hover(self,evt): # this one can be reimplemented
        """ on ROI hover: update traces with the ROI hovered """
        ROI = evt.sender()
        self.active_ROI_id = self.ROI_list.index(ROI)        
        
#        pos = self.get_ROI_position(ROI)         
        
        self.Main.Data_Display.Traces_Visualizer.update()  ### FIXME signal needed
        self.Main.ROI_Manager.update()  ### FIXME signal needed
    pass



class myCircleROI(pg.CircleROI):
    def __init__(self,pos,size,label,layer,**kwargs):
        super(myCircleROI,self).__init__(pos,size,**kwargs)

        self.id = None
        self.label = label
        self.layer = layer
        
        
        pass
    pass

class myPolyLineROI(pg.PolyLineROI):
    def __init__(self,positions,label,layer,**kwargs):
        super(myPolyLineROI,self).__init__(positions,**kwargs)
        
        self.id = None
        self.label = label
        self.layer = layer

        
        
        pass
    pass
    

if __name__ == '__main__':
    pass