# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 15:00:08 2015

@author: georg
"""
from PyQt5 import QtWidgets
import pyqtgraph as pg
import scipy as sp
import numpy as np


class Traces_Visualizer_Stimsorted_Widget(QtWidgets.QWidget):
    """ plots the current traces, trial sorted with avg
    2 do: speed issues, maybe disable other trace updater?
    implement in main window?
    implement stim region
    """
    def __init__(self, Main, parent):
        super(Traces_Visualizer_Stimsorted_Widget, self).__init__()

        self.Data_Display = parent
        self.Main = Main

        self.plotItems = []
        self.traces = []
        self.stim_regions = None # is a list of stimclass holding a list of stim_regions
        self.vlines = []

        self.init_UI()

    def init_UI(self):
        self.plotWidget = pg.GraphicsLayoutWidget(self)
        self.plotWidget.wheelEvent = self.wheelEvent  # quite hacky ...
        self.Layout = QtWidgets.QHBoxLayout(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.setSpacing(0)
        self.setLayout(self.Layout)
        pass

    def init_data(self):
        self.reset()

        # some preparations
        self.trial_labels = self.Main.Data.Metadata.trial_labels
        self.trial_indices = list(range(self.Main.Data.nTrials))
        self.trial_labels_unique = sp.unique(self.trial_labels)
        self.nStimClasses = len(self.trial_labels_unique)
        self.nRepetitions = self.trial_labels.count(self.trial_labels[0]) # FIXME: this imposes a fixed number of repetitions per trial. this should be changed into a vector holding values for each stim

        # generating the UI
        # looping over StimClasses
        for i, StimClass in enumerate(range(self.nStimClasses)):
            if self.Main.Options.view['trial_labels_on_traces_vis']:
                print(self.Main.Options.view['trial_labels_on_traces_vis'])
                plot = self.plotWidget.addPlot(title=self.trial_labels_unique[StimClass])
            else:
                plot = self.plotWidget.addPlot(title=None) # for inheriting from QWidget
            plot.setLabel('left', 'F')
            plot.setLabel('bottom', 'frame #')
            plot.showGrid(x=True, y=True, alpha=0.5)

            # link for common axes
            if i != 0:
                plot.setYLink(self.plotItems[0])
                plot.setXLink(self.plotItems[0])

            # vlines
            vline = plot.addLine(x=self.Data_Display.Frame_Visualizer.frame, movable=True)
            vline.setBounds((0, self.Main.Data.nFrames -1))
            self.vlines.append(vline)

            # add the plot to the list of plots
            self.plotItems.append(plot)

        # set the layout
        self.update_stim_regions()
        self.Layout.addWidget(self.plotWidget)

    def init_traces(self):
        """ creates the traces, depending on the number of ROIs selected. """
        # delete all present
        [trace.clear() for trace in self.traces]
        self.traces = []

        for trial in self.trial_indices:
            # draw the trace in the correct panel
            stimClass = self.trial_labels[trial]
            correct_panel_index = sp.where(self.trial_labels_unique == stimClass)[0][0]
            # with the correct pen
            pen = pg.mkPen(self.Main.Options.view['colors'][trial], width=2)

            self.traces.append(self.plotItems[correct_panel_index].plot(pen=pen))

        self.update_traces()
        pass

    def update_stim_regions(self):
        """ delete all possibly present stimulus regions and draw new ones """
        # delete preset
        if self.stim_regions is not None:
            for i in range(self.nStimClasses):
                for stim_region in self.stim_regions[i]:
                    self.plotItems[i].removeItem(stim_region)
        self.stim_regions = []

        # draw new ones
        for i, StimClass in enumerate(range(self.nStimClasses)):
            self.stim_regions.append([])
            for stim_id in range(self.Main.Options.preprocessing['stimuli'].shape[0]):
                stim_frames = self.Main.Options.preprocessing['stimuli'][stim_id]
                stim_region = pg.LinearRegionItem(values=stim_frames, movable=False,
                                                  brush=pg.mkBrush([50, 50, 50, 100]))
                for line in stim_region.lines:
                    line.hide()
                stim_region.setZValue(-1000)
                self.plotItems[i].addItem(stim_region)
                self.stim_regions[i].append(stim_region)

    def update_display_settings(self):
        """ this is handled via signal/slot mechanism"""

        for i,StimClass in enumerate(range(self.nStimClasses)):
            if self.Main.Options.view['trial_labels_on_traces_vis']:
                self.plotItems[i].setTitle(self.trial_labels_unique[StimClass])
            else:
                self.plotItems[i].setTitle(None)

            # plot labels
            if self.Main.Options.view['show_dFF'] is True:
                self.plotItems[i].setLabel('left', 'dF/F')

            if self.Main.Options.view['show_dFF'] is False:
                self.plotItems[i].setLabel('left', 'F [au]')

        # update stim regions
        self.update_stim_regions()

        # update_traces
        self.update_traces()

    def get_traces(self, ROI):
        """ helper for calculating the traces matrix """
        active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
        # func bool mask slicing
        mask, inds = self.Main.ROIs.get_ROI_mask(ROI)  ### FIXME signal needed?

        if self.Main.Options.view['show_dFF']:
            sliced = self.Main.Data.dFF[mask,:,:][:,:,active_inds]
        else:
            sliced = self.Main.Data.raw[mask,:,:][:,:,active_inds]
        Traces = sp.average(sliced,axis=0)
        return Traces

    def update_traces(self):
        """ is called upon all ROI and Dataset changes """
        if len(self.Main.Options.ROI['active_ROIs']) >= 1 and \
           len(self.Main.ROIs.ROI_list) > 0 and \
           self.Main.Options.ROI['last_active'] is not None:

#            ROI_ind = self.Main.Options.ROI['last_active']
#
#            try:
#                ROI = self.Main.ROIs.ROI_list[ROI_ind]
#            except IndexError:
#                print "error with" , ROI_ind

            ROI = self.Main.Options.ROI['last_active']
            active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
            Traces = self.get_traces(ROI)

            for n, ind in enumerate(active_inds):
                self.traces[ind].setData(Traces[:,n])
        else:
            [trace.hide() for trace in self.traces]

    def reset(self):
        for item in self.plotItems:
            self.plotWidget.removeItem(item)
        self.plotItems = []

#        for trace in self.traces:
#            trace.clear()
        self.traces = []
        self.stim_regions = None
        self.vlines = []
        pass

    def vline_pos_changed(self, evt):
        """ updater for the zlayer change caused by the vline """
        vline = evt
        pos = int(np.clip(vline.pos().x(), 0, self.Main.Data.nFrames))
        self.Main.Data_Display.Frame_Visualizer.frame = pos
        self.Main.Data_Display.Frame_Visualizer.update_frame()
        self.update_vline(pos)

    def update_vline(self, pos):
        """ handles sigPositionChanged """
        # update all other lines in this widget as well
        for vline in self.vlines:
            vline.blockSignals(True)
            vline.setValue(pos)
            vline.blockSignals(False)

        # update the line of the other traces widget
        self.Main.Data_Display.Traces_Visualizer.vline.setValue(pos)

    def wheelEvent(self, evt): # reimplementation
        d = sp.around(evt.angleDelta().y() / 120.0)  # check this on different machines how much it is
        updated_frame = self.Main.Data_Display.Frame_Visualizer.frame - d
        if 0 <= updated_frame < self.Main.Data.nFrames:
            self.Main.Data_Display.Frame_Visualizer.frame -= d
            self.update_vline(self.Main.Data_Display.Frame_Visualizer.frame)
            self.Main.Data_Display.Frame_Visualizer.update_frame()


if __name__ == '__main__':
    from .. import Main
    Main.main()
    pass
