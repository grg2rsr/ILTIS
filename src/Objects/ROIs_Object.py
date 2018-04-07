# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:21:29 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
# import lib.pyqtgraph.pyqtgraph as pg
from lib import pyqtgraph as pg
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
            self.Main.MainWindow.Data_Display.Frame_Visualizer.scene().removeItem(ROI)
            self.Main.MainWindow.Data_Display.Frame_Visualizer.scene().removeItem(ROI.labelItem)

        self.Main.Options.ROI['last_active'] = None

    def add_ROI_request(self, evt):
        """ for ROI placement
        add functionality: watch for ROI placing toggle/switch
        """
        if pg.graphicsItems.ViewBox.ViewBox == type(evt.currentItem): # this is the fix for the ROI in the corners bug
            if evt.button() == 1:
                # get correct position of mouse click
                pos = self.Main.MainWindow.Data_Display.Frame_Visualizer.ViewBox.mapToView(evt.pos())
                self.add_ROI(pos=sp.array([pos.x(),pos.y()]))

    def remove_ROI_request(self,evt):
        """ for ROI removal, clicked from popup menu """
        ROI = evt.sender()
        self.remove_ROI(ROI)
        pass


    def add_ROI(self,label=None,kind=None,pos=None,ROI_diameter=None,pos_list=None,contour=None,mask=None):
        """ this function is called and takes care of the proper ROI instantiation
        kind etc. """


        if label == None:
            label = str(len(self.ROI_list) + 1)
        if kind == None:
            kind = self.Main.Options.ROI['type']
#        if pos == None and pos_list == None and contour==None:
#            ### FIXME raise error
#            print "trying to instantiate ROI without position!"
        if ROI_diameter == None:
            ROI_diameter = self.Main.Options.ROI['diameter']

        # color the ROI according to the "active" dataset
        current_pen = pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8)
        common_kwargs = {'parent':self.Main.MainWindow.Data_Display.Frame_Visualizer.ViewBox,
                         'pen':current_pen,
                         'removable':True,
                         'Main':self.Main,
                         'label':label}

        if kind == 'circle':
            pos = pos - ROI_diameter / 2 # empirically determined - not understood - minus is correct ...
            ROI = myCircleROI(pos, [ROI_diameter,ROI_diameter], **common_kwargs)

        if kind == 'polygon':
            if pos_list == None:
                pos_list = [[pos[0]-ROI_diameter,pos[1]-ROI_diameter], [pos[0]+ROI_diameter,pos[1]-ROI_diameter], [pos[0]+ROI_diameter,pos[1]+ROI_diameter], [pos[0]-ROI_diameter,pos[1]+ROI_diameter]]
            ROI = myPolyLineROI(pos_list, closed=True, **common_kwargs)

        if kind == 'nonparametric':
            # reusing PolyLineROI
#            ROI = myPolyLineROI(self.Main, pos_list, label,  closed=True, removable=True, pen=current_pen, movable=False)
#            [handle.hide() for handle in ROI.getHandles()]

            # own implementation
            ROI = myNonParametricROI(mask, contour, movable=False, **common_kwargs)

        # set only the current ROI active
        [roi.deactivate() for roi in self.ROI_list]
        ROI.activate()

        # add ROI
        self.ROI_list.append(ROI)
        self.Main.Options.ROI['last_active'] = ROI
        self.Main.MainWindow.Data_Display.Frame_Visualizer.ViewBox.addItem(ROI)

        # update
        self.Main.MainWindow.Front_Control_Panel.ROI_Manager.update()
        self.update_active_ROIs()


    def remove_ROI(self,ROI):
        """ remove a ROI, update all necessary  """

        # remove from scene
        for child in ROI.children:
            self.Main.MainWindow.Data_Display.Frame_Visualizer.scene().removeItem(child)
        self.Main.MainWindow.Data_Display.Frame_Visualizer.scene().removeItem(ROI)
#        self.Main.MainWindow.Data_Display.Frame_Visualizer.scene().removeItem(ROI.labelItem)

        # fix suggestion from luke campagnola (pyqtgraph mailinglist)
        # problem: ROI object doensn't have a removeTimer on all machines!
        try:
            ROI.removeTimer.stop()
        except:
            pass

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
        if type(ROI) != myNonParametricROI:
            mask = sp.zeros((self.Main.Data.raw.shape[0],self.Main.Data.raw.shape[1]),dtype='bool')

            # getArraySlice gets 1) array to slice 2) ImageItem
            inds = ROI.getArraySlice(self.Main.Data.raw[:,:,0,0], self.Main.MainWindow.Data_Display.Frame_Visualizer.ImageItems[0], returnSlice=False)[0]

            val_inds = sp.where(ROI.getArrayRegion(self.Main.Data.raw[:,:,0,0], self.Main.MainWindow.Data_Display.Frame_Visualizer.ImageItems[0]) != 0)
            inds = sp.array([inds[0],inds[1]])

            true_inds = sp.array([val_inds[0] + inds[0,0],val_inds[1] + inds[1,0]])
            mask[true_inds[0],true_inds[1]] = True
        else:
            mask = ROI.mask
            true_inds = sp.where(mask)

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

    def ROI_clicked_handler(self,evt):
        """ handles the click event """
        ROI = evt.sender()
        self.ROI_clicked(ROI)
        pass

    def ROI_clicked(self,ROI):
        """ ROI gets activated upon click, if shift click multiple active can be
        selected """

        modifiers = QtGui.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ShiftModifier:
            ROI.toggle_state()
        else:
            [roi.deactivate() for roi in self.ROI_list]
            ROI.toggle_state()

        self.Main.Options.ROI['last_active'] = ROI
        self.update_active_ROIs()
        self.update_display_settings()
        pass

#    def ROI_hover_handler(self,evt):
#        ROI = evt.sender()
#        self.ROI_hover(self,ROI)
#        pass
#
#    def ROI_hover(self,ROI):
#
#        pass

    def update_display_settings(self):
        """ sets the colors for the ROIs and whether or not to show the label """
        # handle the labels
        if self.Main.Options.ROI['show_labels'] == True:
            [ROI.labelItem.show() for ROI in self.ROI_list]
        if self.Main.Options.ROI['show_labels'] == False:
            [ROI.labelItem.hide() for ROI in self.ROI_list]

        # handle the ROI colors
        nActiveROIs = len(self.Main.Options.ROI['active_ROIs'])

        # one ROI active, active/inactive color scheme
        if nActiveROIs <= 1:
            for ROI in self.ROI_list:
                if ROI.active == True:
                    pen = pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8)
                if ROI.active == False:
                    pen = pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8)
                ROI.set_Pen(pen)

        # multiple ROI active, traces colored to ROI
        if nActiveROIs > 1:
            colors = self.Main.Processing.calc_colors(nActiveROIs)
            for i,ROI_id in enumerate(self.Main.Options.ROI['active_ROIs']):
                ROI = self.ROI_list[ROI_id]
                pen = pg.mkPen(colors[i],width=1.8)
                ROI.set_Pen(pen)
        pass

class myROI(object):
    def __init__(self,Main=None,label=None,ViewBox=None):
#        super(myROI,self).__init__()
        self.Main = Main
        self.label = label
        self.ViewBox = self.parentItem()
        self.children = [] # a list of GraphicsItems

        self.active = False
        self.center = self.get_center()
        self.labelItem = pg.TextItem(text=label,anchor=(0.5,0.5))
        self.update_center()

        self.ViewBox.addItem(self.labelItem)
        self.children.append(self.labelItem)

        # link signals
        self.sigRemoveRequested.connect(self.Main.ROIs.remove_ROI_request)
        self.proxy = pg.SignalProxy(self.sigRegionChanged, rateLimit=30, slot=self.Main.ROIs.ROI_region_changed) # rate limit movement
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.sigClicked.connect(self.Main.ROIs.ROI_clicked_handler)
#        self.sigHoverEvent.connect(self.Main.ROIs.ROI_hover_handler)

        # pens
        self.active_pen = pg.mkPen(self.Main.Options.ROI['active_color'],width=1.8)
        self.inactive_pen = pg.mkPen(self.Main.Options.ROI['inactive_color'],width=1.8)
        self.hover_pen = pg.mkPen(255,255,0,width=1)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def toggle_state(self):
        if self.active == True:
            self.deactivate()
        elif self.active == False:
            self.activate()

    def update_center(self):
        self.center = self.get_center()
        self.labelItem.setPos(self.center[0],self.center[1])

    def update_label(self,text):
        self.label = text
        self.labelItem.setText(self.label)


class myCircleROI(pg.CircleROI,myROI):
    def __init__(self,pos,size,**kwargs):
        non_pg_kws = ['Main','label']
        non_pg_vals = [kwargs.pop(key) for key in non_pg_kws]
        pg.CircleROI.__init__(self,pos,size,**kwargs)
        myROI.__init__(self, **dict(list(zip(non_pg_kws,non_pg_vals))))
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

    def set_Pen(self,pen):
        self.setPen(pen)


class myPolyLineROI(pg.PolyLineROI,myROI):
    def __init__(self,positions,**kwargs):
        non_pg_kws = ['Main','label']
        non_pg_vals = [kwargs.pop(key) for key in non_pg_kws]
        pg.PolyLineROI.__init__(self, positions,**kwargs)
        myROI.__init__(self, **dict(list(zip(non_pg_kws,non_pg_vals))))

        # also workaround for the weird first_call bug
        self.center = self.get_center(first_call=True)
        self.labelItem.setPos(self.center[0],self.center[1])

    def set_Pen(self,pen):
        for segment in self.segments:
            segment.setPen(pen)

    def get_center(self,first_call=False):
        """ returns ROI centroid, used for label show
        first_call kw for handling the weird bug upon first call to mapToView:
        this returns wrong coordinates"""
        handle_pos = [tup[1] for tup in self.getSceneHandlePositions()]
        pos_mapped = [self.ViewBox.mapToView(pos) for pos in handle_pos]
        if first_call == True:
            h_pos = sp.array([[p.x(),p.y()] for p in handle_pos])
        else:
            h_pos = sp.array([[p.x(),p.y()] for p in pos_mapped])
        pos = sp.average(h_pos,axis=0)
        return pos
    pass

class myNonParametricROI(pg.ROI,myROI):
    """ function that need to be reimplemented:
    click, hover, return mask (is passed) """

    def __init__(self,mask,contour,**kwargs):
        non_pg_kws = ['Main','label']
        non_pg_vals = [kwargs.pop(key) for key in non_pg_kws]
        # pg.ROI needs a pos as the constructor. center of largest segment
        pos = sp.average(contour[sp.argmax([cont.shape[0] for cont in contour])],axis=0)
        self.contour = contour
        self.mask = mask

        pg.ROI.__init__(self,pos,size=(0,0),**kwargs)
        myROI.__init__(self,**dict(list(zip(non_pg_kws,non_pg_vals))))

        self.sigClicked.connect(self.clicked)
#        self.sigHoverEvent.connect(self.hover)

        # line
        self.lines = []
        for segment in self.contour:
            x = segment[:,0]
            y = segment[:,1]

#            from itertools import chain
#            coords = list(chain.from_iterable(zip(x, y)))
            coords = list(zip(x,y))
            ### polygon
            #        # polygon

#            QPointList = [QtCore.QPoint(*coord) for coord in coords]
#            polygon = QtGui.QPolygonF(QPointList)
#            PolyItem = myQGraphicsPolygonItem(polygon,parent=self)
#            PolyItem.setPen(self.inactive_pen)
#            self.Main.MainWindow.Data_Display.Frame_Visualizer.ViewBox.addItem(PolyItem)


            ## line
#            line = myPlotDataItem(parent=self,pxMode=True,pen=self.inactive_pen)
#            line.setData(x=x,y=y)
            path = pg.arrayToQPath(x,y,connect='all')
            polygon = path.toFillPolygon()
            PolyItem = myQGraphicsPolygonItem(polygon,parent=self)
            PolyItem.setPen(self.inactive_pen)
            self.Main.MainWindow.Data_Display.Frame_Visualizer.ViewBox.addItem(PolyItem)
            self.lines.append(PolyItem)
            self.children.append(PolyItem)

    def hover(self,evt):
        print("hovering over", self.label)

    def set_hover(self,val):
        """ """
        if val == True:
            self.set_Pen(self.hover_pen)
        if val == False:
            if self.active:
                self.set_Pen(self.active_pen)
            else:
                self.set_Pen(self.inactive_pen)

    def clicked(self,evt):
        print(evt.button())
        if evt.button() == QtCore.Qt.MiddleButton:
            self.Main.ROIs.remove_ROI(self)

        if evt.button() == QtCore.Qt.LeftButton:
            self.Main.ROIs.ROI_clicked(self)

    def get_center(self):
        """ pos is the centroid """
        return sp.average(self.contour[sp.argmax([cont.shape[0] for cont in self.contour])],axis=0)

    def set_Pen(self,pen):
        for line in self.lines:
            line.setPen(pen)

class myQGraphicsPolygonItem(QtGui.QGraphicsPolygonItem):
    def __init__(self,*args,**kwargs):
        super(myQGraphicsPolygonItem,self).__init__(*args,**kwargs)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(QtCore.Qt.RightButton and QtCore.Qt.LeftButton and QtCore.Qt.MiddleButton)
        self.parent = kwargs['parent'] # parent is the nonparametric ROI class

    def hoverEnterEvent(self,evt):
        self.parent.set_hover(True)
#
    def hoverLeaveEvent(self,evt):
        self.parent.set_hover(False)

    def mousePressEvent(self,evt):
        self.parent.clicked(evt)

if __name__ == '__main__':
    from . import Main
    Main.main()
