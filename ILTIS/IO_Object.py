# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:52:50 2015

@author: georg
"""

from PyQt4 import QtGui, QtCore # for the dialogs
from lib import IOtools as io
from lib import gioIO as gio
from Data_Object import Data_Object, Metadata_Object
from ROIs_Object import myCircleROI,myPolyLineROI
import os
import sys
import scipy as sp
import pandas as pd
import pickle
import re
import time
from collections import OrderedDict

from skimage.measure import label as sklabel
from skimage.measure import find_contours

class IO_Object(object):
    """ holds all IO functionality """
    def __init__(self,Main):
        self.Main = Main
        pass

    def init_data(self):
        """ 
        emit reset signal
        load data
        emit init data signal
        
        DO NOT connect this init_data to the initDataSignal slot, this one
        has to be called seperately
        """
        self.Main.Signals.resetSignal.emit()
      
        # read in new data
        self.load_data() # opens filedialog, sets meta_data.paths

        # init the UI of Options Control
        self.Main.MainWindow.Options_Control.init_UI()

        # initialize Data display again
        self.Main.Signals.initDataSignal.emit()

        # and emit an update Signal
        self.Main.Signals.updateSignal.emit()      
        

        pass

    def reset(self):
        """ deletes data object """
        self.Main.Data = None # take care that no extra references are generated and kept!
        pass

#==============================================================================
    ### Dialogs
#==============================================================================
    def OpenFileDialog(self,title=None,default_dir=None,extension='*'):
        """ Opens a Qt Filedialoge window to read files from disk """
        
        if default_dir==None:
            default_dir = os.getcwd()
        if title==None:
            title='Open File'
            
        qpaths = QtGui.QFileDialog.getOpenFileNames(parent=self.Main.MainWindow, caption=title, directory=default_dir, filter=extension)
        paths = []
        for i in range(len(qpaths)):            
            paths.append(str(qpaths[i]))

        return paths
        
    def SaveFileDialog(self,title=None,default_dir=None,extension='*'):
        """ Opens a Qt SaveFileName Dialog """
        if default_dir==None:
            default_dir = os.getcwd()
        if title==None:
            title='Save File'
            
        qpath = QtGui.QFileDialog.getSaveFileName(parent=self.Main.MainWindow, caption=title, directory=default_dir, filter=extension)
        path = str(qpath)
            
        return path
        
#==============================================================================
    ### General reading
#==============================================================================

   
    def load_data(self):
        """ get paths to load. determine file format. open appropriate reader """

        # Data init        
        self.Main.Data = Data_Object()
        self.Main.Data.Metadata = Metadata_Object(self.Main.Data)
        
        # get paths
        paths = self.OpenFileDialog(title='Open data set', default_dir=self.Main.Options.general['cwd'], extension='(*.tif *.lsm *.pst)')
        if paths == None:
            pass
        
        # determine format
        endings = sp.array([os.path.splitext(path)[1] for path in paths])
        if not(sp.all(endings[0] == endings)):
            raise "not all file formats are equal!"
        file_format = endings[0]
        
        # open appropriate reader
        if file_format == '.tif':
            self.load_tif(paths)
            
#        if file_format == '.ids':
#            if len(paths) > 1:
#                print "trying to load multiple ids files, raise Exception"
#            path = paths[0]
#            self.load_ids(path)
            
        if file_format == '.lsm':
            tifpaths = self.convert_lsm2tif(paths)
            self.load_tif(tifpaths)
        
        if file_format == '.pst':
            tifpaths = self.convert_pst2tif(paths)
            self.load_tif(tifpaths)
            
        # default settings if no metadata is read
        self.Main.Data.Metadata.paths = paths
        
        # update cwd
        self.Main.cwd = os.path.dirname(paths[0])
        self.Main.Options.general['cwd'] = os.path.dirname(paths[0])
        
        # infer some Meta information
        self.Main.Data.infer()

        # load options
        self.load_options(reset=True)
        

    
    def load_tif(self,paths):
        """ read tifs found at paths (list with paths) """
        
        # reading
        x,y,t = io.read_tiffstack(paths[0]).shape
        n = len(paths)
        
        self.Main.Data.raw = sp.zeros((x,y,t,n),dtype='uint16')
        self.Main.Data.dFF = sp.zeros((x,y,t,n),dtype='float32')
        
        for n,path in enumerate(paths):
            print "loading dataset from " + path
            print "Dataset size: " + str(os.stat(path).st_size / 1000000.0) + ' MB'
            self.Main.MainWindow.statusBar().showMessage("loading dataset: " + path)
            self.Main.Data.raw[:,:,:,n] = io.read_tiffstack(path)
        self.Main.MainWindow.statusBar().clearMessage()
            



#==============================================================================
    ### writing datasets         
#==============================================================================
#    def save_ids(self):
#        pass
    
    def save_tif(self):
        """ rgb color merge, crop """
        pass
    
    
#==============================================================================
    ### ROI IO
#==============================================================================
    def load_ROIs(self):
        """ reads a .roi or .coor file and updates the ROIs """
        self.Main.ROIs.reset()
        file_path = self.OpenFileDialog(title='load ROIs',default_dir = self.Main.Options.general['cwd'], extension='*.roi *.coor')[0]
        
        kind = os.path.splitext(file_path)[1]
        
        if kind == '.roi': # new style
            with open(file_path, 'r') as fh:
                for line in fh.readlines():
                    line = line.strip().split('\t')
                    
                    kind = line[0]
                    label = line[1]
                    
                    info = sp.array(line[2:],dtype=float)
                    if kind == 'circle':
                        self.Main.ROIs.add_ROI(kind='circle',label=label,pos=(info[0],info[1]),ROI_diameter=info[2])
                    if kind == 'polygon':
                        pos_list = []
                        for i in range(0,info.shape[0],2):
                            pos = self.Main.Data_Display.Frame_Visualizer.ViewBox.mapToView(QtCore.QPointF(info[i],info[i+1]))
                            pos_list.append([pos.x(),pos.y()])
                            pass
                        self.Main.ROIs.add_ROI(kind='polygon',label=label,pos_list=pos_list)
                        pass
                    pass
                
        if kind == '.coor': # old style compatibility 
            fh = open(file_path,'r')
            for line in fh.readlines():
                line = line.strip().split('\t')
                kind = int(line[0])
                label = line[1]
                layer = int(line[2]) # deprecated 
                info = sp.array(line[3:],dtype=float)
                if kind == 0:
                    self.Main.ROIs.add_ROI(kind='circle',label=label,pos=(info[0],info[1]),ROI_diameter=info[2])
                if kind == 1:
                    pos_list = []
                    for i in range(0,info.shape[0],2):
                        pos = self.Main.Data_Display.Frame_Visualizer.ViewBox.mapToView(QtCore.QPointF(info[i],info[i+1]))
                        pos_list.append([pos.x(),pos.y()])
                        pass
                    self.Main.ROIs.add_ROI(kind='polygon',label=label,pos_list=pos_list)
                    pass
                pass
        
    def write_extraction_mask(self):
        """ write both the .roi file and the tif pages
        ROI file format specification: each row a ROI,
        first col: kw for roi type
        if circle: label, layer, pos x, pos y, diameter
        if poly: label, layer, pos x_1, pos_y1, ... pos x_n, pos y_n
        """
        outpath = self.SaveFileDialog(title='saving ROIs',default_dir = self.Main.Options.general['cwd'], extension='*.roi')
        outpath = self.append_extension(outpath, '.roi')
            
        fh = open(outpath,'w')
        
        # iterate over ROIs
        for i,ROI in enumerate(self.Main.ROIs.ROI_list):
            label = str(ROI.label)
            
            if type(ROI) == myCircleROI:
#                pos = sp.array([ROI.pos().x(),ROI.pos().y()])
#                pos = self.get_ROI_position(ROI)
                x = str(sp.around(ROI.center[0],decimals=2))
                y = str(sp.around(ROI.center[1],decimals=2))
                d = str(sp.around(ROI.diameter,decimals=2))
                
                fh.write('\t'.join(['circle',label,x,y,d,'\n']))
                
            if type(ROI) == myPolyLineROI:
                 fh.write('\t'.join(['polygon',label]))
                 fh.write('\t')
                 for j in range(len(ROI.getSceneHandlePositions())):

                     pos = self.Main.Data_Display.Frame_Visualizer.mapFromScene(ROI.getSceneHandlePositions()[j][1])
                     x = pos.x()
                     y = pos.y()

                     fh.write('\t'.join([str(sp.around(x,decimals=2)),str(sp.around(y,decimals=2))]))
                     fh.write('\t')
                 fh.write('\n')
                 
        fh.close()
        
        print "saved ROIs in .roi format to", outpath
#        outpath = os.path.splitext(outpath)[0] + '_mask.tif'
#        outpath = self.MainWindow.SaveFileDialog(title='saving ROIs',defaultdir=self.path,extension='.tif')
        
        # extraction mask
        self.Main.Processing.calc_extraction_mask()
        io.save_tstack(self.Main.Data.extraction_mask.astype('uint16'),os.path.splitext(outpath)[0] + '_mask.tif')
        print "saved ROIs in .tif format to", outpath
        
        pass

    def load_nonparametric_ROIs(self,size_filter=None,thresh=0.5):
        """ reads a *_mask.tif 
        size_filter can be a tuple and segments with an area smaller than 
        size_filter[0] or larger size_filter[1] are considered to be valid ROIs
        """
        self.Main.ROIs.reset()    
        
        # get mask data
        file_path = self.OpenFileDialog(title='load nonparametric ROIs',default_dir = self.Main.Options.general['cwd'], extension='*.tif')[0]
        masks = io.read_tiffstack(file_path)
        
        
        
        # skimage based segmentation
        masks_thresh = masks > thresh
        masks_label = sp.zeros(masks_thresh.shape)
        for i in range(masks_thresh.shape[2]):
            masks_label[:,:,i] = sklabel(masks_thresh[:,:,i])
    
        # split into a array of submasks
        Nsubmasks = [int(masks_label[:,:,i].max()) for i in range(masks_label.shape[2])]
        submasks = sp.zeros((masks.shape[0],masks.shape[1],sum(Nsubmasks)),dtype='bool')
        
        i = 0
        for j in range(masks_label.shape[2]):
            mask = masks_label[:,:,j]
            for l in range(1,Nsubmasks[j]+1):
                submasks[mask == l,i] = True
                i += 1

        # for each mask, calculate a contour
        contours = []
        for i in range(submasks.shape[2]):
            contour = find_contours(submasks[:,:,i],level=0.5)
            contours.append(contour)

        
        # add PolyLineROI
        for i in range(submasks.shape[2]):
            self.Main.ROIs.add_ROI(kind='nonparametric',label=str(i),contour=contours[i],mask=submasks[:,:,i])
            pass
            
            
#        
#        
#        label = 0
#        # iterate over masks
#        for i in range(masks.shape[2]):
#            mask = masks[:,:,i]
#            
#            submasks = self.Main.Processing.find_submasks(mask,level=0.2)
#            # find contour
#            segments = self.Main.Processing.find_contour(mask,level=0.2)
#                        
#            for seg in segments:
#                
#                # FIXME! KC and image dimension specific code!
#                # kick if area is below or above a threshold
#                if size_filter: # KC 30/600 ?
#                    area = self.Main.Processing.calc_segment_area(seg)
#                    if area < size_filter[0] or area > size_filter[1]:
#                        continue
#                
#                label = label + 1
#                
#                # convert to coordinates            
##                pos_list = []
##                for i in range(len(X)):
##                    x = X[i]
##                    y = Y[i]
##                    pos = self.Main.Data_Display.Frame_Visualizer.ViewBox.mapToView(QtCore.QPointF(x,y))
##                    pos_list.append([pos.x(),pos.y()])
#    
#                # add PolyLineROI
#                downsample = 1
#                X = seg[::downsample,0]
#                Y = seg[::downsample,1]
#                pos_list = zip(X,Y)
#                self.Main.ROIs.add_ROI(kind='nonparametric',label=str(label),pos_list=pos_list,mask=submask)
#                pass
            
#        import pdb
#        pdb.set_trace()

        # remove all handles
#        for ROI in self.Main.ROIs.ROI_list:
#            [handle.hide() for handle in ROI.getHandles()]
            
            
        
        
#==============================================================================
    ### Traces IO
#==============================================================================
    
    def export_traces(self):
        """
        calculate extraction mask
        extract traces
        save to disk
        """
        
        # calculate extraction mask
        self.Main.Processing.calc_extraction_mask()
        
        # extract traces
        self.Main.Processing.calc_traces(self.Main.Data.extraction_mask)
        
        # calculate time vector
        self.Main.Processing.calc_tvec()
        
        ## exporting to csv
        if self.Main.Options.export['format'] == '.csv - normal':
            if self.Main.verbose:
                print "extracting traces and writing to .csv"
            
            labels = [ROI.label for ROI in self.Main.ROIs.ROI_list]
            labels.insert(0,'time [s]')
            
            tvec = self.Main.Data.Metadata.tvec
            
            for n in range(self.Main.Data.nTrials):
                outpath = os.path.splitext(self.Main.Data.Metadata.paths[n])[0] + '_traces_' + str(n+1) + '.csv'
                data = sp.concatenate((tvec[:,sp.newaxis],self.Main.Data.Traces[:,:,n]),axis=1)
                pd.DataFrame(data,columns=labels).to_csv(outpath,delimiter=',')
                
                if self.Main.verbose:
                    print 'written: ', outpath


        ## exporting sorted csv
        if self.Main.Options.export['format'] == '.csv - sorted':
            if self.Main.verbose:
                pass
            
            # sort traces
            self.Main.Processing.sort_traces()
            
            # prepare
            ROI_labels = [ROI.label for ROI in self.Main.ROIs.ROI_list]
            unique_trial_labels = sp.unique(self.Main.Data.Metadata.trial_labels)
            nStims = unique_trial_labels.shape[0]
            nReps = len(self.Main.Data.Metadata.trial_labels) / nStims
            
            tvec = self.Main.Data.Metadata.tvec
            
            for ROI_id,ROI_label in enumerate(ROI_labels):
                for trial_ind,trial_label in enumerate(unique_trial_labels):
                    data = self.Main.Data.Traces_sorted[:,ROI_id,trial_ind,:]
                    data = sp.concatenate((tvec[:,sp.newaxis],data),axis=1)
                    cols = ['time [s]'] + [str(ind+1) for ind in range(nReps)]
                    outpath = self.Main.Options.general['cwd'] + os.path.sep + self.Main.Options.general['experiment_name'] + '_' + trial_label + '_' + ROI_label + '.csv'
                    pd.DataFrame(data,columns=cols).to_csv(outpath,delimiter=',')
            
            
        ## exporting to gloDatamix
        if self.Main.Options.export['format'] == '.gloDatamix':
            if self.Main.verbose:
                print "extracting traces and writing to .gloDatamix format"
                
            # if no .lst has been read, do so now
            if self.Main.Options.flags['LST_was_read'] == False:
                QtGui.QMessageBox.question(self.Main.MainWindow,'Message',"No .lst file has been loaded yet, you have to do so now",QtGui.QMessageBox.Yes)
                self.load_lst()
                
            outpath = self.SaveFileDialog(title='saving to .gloDatamix',default_dir=self.Main.Options.general['cwd'])   
            outpath = self.append_extension(outpath,'.gloDatamix')                

            # metadata
            gloMeta = self.generate_gloDatamix_Meta()

            # resorted traces
            traces = self.glo_sort_traces()
            
            gio.write_gloDatamix(gloMeta,traces,outpath)
                



#==============================================================================
    ### lst parser / gloDatamix compatibility
#==============================================================================

    def generate_gloDatamix_Meta(self):
        """ generates a pd.Dataframe with the Metadata ordered in such a way that
        it fits the .gloDatamix definition. """
        
        # preparations
        gloMeta = []
        inds_map = self.map_lst_inds_to_path_inds()
        
        for n,path in enumerate(self.Main.Data.Metadata.paths):            
            for i in range(len(self.Main.ROIs.ROI_list)):
                
                lst_values = self.Main.Data.Metadata.LSTdata.loc[inds_map[n]]                


                # roi centroid                
                pos = self.Main.ROIs.ROI_list[i].get_center()
                
                # stim                
                if self.Main.Options.preprocessing['stimuli'].shape[0] == 2:
                    stim2on,stim2off = self.Main.Options.preprocessing['stimuli'][1,:]
                else:
                    stim2on,stim2off = ['-1','-1']
                    
                # age
                if lst_values['Age'] != -1:
                    try:
                        NAge,NAgeMax = lst_values['Age'].split('-')
                    except:
                        NAge = '-1'
                        NAgeMax = '-1'
                else:
                    NAge = '-1'
                    NAgeMax = '-1'
                    
                row = OrderedDict()
                row['NGloTag'] = str(self.Main.ROIs.ROI_list[i].label)
                row['NOdorNr'] = '-999'
                row['NOConc'] = str(lst_values['OConc'])
                row['NStim_ON'] = str(self.Main.Options.preprocessing['stimuli'][0,0])
                row['NStim_Off'] = str(self.Main.Options.preprocessing['stimuli'][0,1])
                row['NNoFrames'] = str(self.Main.Data.nFrames)
                row['NFrameTime'] = str(sp.int32(self.Main.Options.preprocessing['dt'] * 1000))
                row['NRealTime'] = str(lst_values['MTime'])
                row['NPhConc'] = str(lst_values['PhConc'])
                row['NshiftX'] = str(lst_values['ShiftX'])
                row['NshiftY'] = str(lst_values['ShiftY'])
                row['NcontMeasu'] = '0'
                row['NNumMeasu'] = '0'
                row['Nstim_ISI'] = '0'
                row['NodorN'] = '1'
                row['Nstim2ON'] = str(stim2on)
                row['Nstim2OFF'] = str(stim2off)
                row['NAge'] = str(NAge)
                row['NAgeMax'] = str(NAgeMax)
                row['TGloInfo'] = 'Coor' + str(int(sp.around(pos[0],decimals=0))) + ':' + str(int(sp.around(pos[1],decimals=0)))
                row['TOdour'] = str(lst_values['Odour'])
                row['T_dbb1'] = str(lst_values['DBB1'])
                row['Tcomment'] = str(lst_values['Comment'])
                row['TPharma'] = str(lst_values['Pharma'])
                row['TPhtime'] = str(lst_values['PhTime'])
                row['Tos9time'] = str(lst_values['PhTime'])
                row['TLabel'] = lst_values['Label']
                row['Tanimal'] = lst_values['DBB1'].strip().split('\\')[0]
                row['T_dbb2'] = 'noDBB2'
                      
                gloMeta.append(row)
                
        # make a pd.DataFrame out of it:
        gloMetaDF = pd.DataFrame(columns=gloMeta[0].keys())
        for i in range(len(gloMeta)):
            gloMetaDF = gloMetaDF.append(pd.Series(gloMeta[i]),ignore_index=True)

        return gloMetaDF
                
                
    def map_lst_inds_to_path_inds(self):
        """ establishes a mapping between the order of the datasets in paths
        and their corresponding rows in the lst file 
        this parser is now with added flexibility to deal with aljas vs michis
        lst styles."""
        
        ind_map = []
                       
        for n,path in enumerate(self.Main.Data.Metadata.paths):            
            filename = os.path.splitext(os.path.split(path)[1])[0]
            
            # this parser is specifically designed to handle 
            # a) lsm style .lst files
            # b) tillvision wide-field .lst files
            # c) output of the motion correction scripts

            # moco compatibility
            suffixes = ['affine','full','fullglobal','fullaffineglobal','affineaffineglobal','fullbsplineglobal','correctedVflip','corrected']          
            if os.path.splitext(filename.split('_')[-1])[0] in suffixes:
                filename = '_'.join(filename.split('_')[:-1])
            
#            import pdb
#            pdb.set_trace()
            
            myInd = None
            for ind in self.Main.Data.Metadata.LSTdata.index:
                info = self.Main.Data.Metadata.LSTdata['DBB1'][ind].strip().split('\\')
                if len(info) == 3: # here is the compatibility lsm vs tillvision
                    Tanimal, tmp, Experiment = info
                if len(info) == 2:
                    Tanimal, Experiment = info
                Experiment = os.path.splitext(Experiment)[0]
                Tanimal = os.path.splitext(Tanimal)[0]
                if Experiment == filename:
                    myInd = ind
                    ind_map.append(ind)
                    
            if myInd == None:
                print "Experiment not found in the .lst file!"
                print Experiment, filename
        return ind_map
        

    def load_lst(self):
        """ reads metadata from a .lst file. Needed to generate output in the
        .gloDatamix format """

        try:        
            lst_path = self.OpenFileDialog(title='load lst',default_dir=self.Main.Options.general['cwd'],extension='*.lst')[0]
        except:
            return

        # read
        self.Main.Data.Metadata.LSTdata = gio.read_lst(lst_path)
        self.Main.Options.flags['LST_was_read'] = True
        
        # update labels
        ind_map = self.map_lst_inds_to_path_inds()
                       
        #concentration
        concs = [self.Main.Data.Metadata.LSTdata.loc[ind_map[n]]['OConc'] for n in range(self.Main.Data.nTrials)]
        new_concs = []
        
        for conc in concs:
            if conc > 0: # info is in dilutions
                new_conc = str(-1 * sp.around(sp.log10(sp.int32(conc))))
                new_concs.append(new_conc)
            else:
                new_concs.append(conc)
                
        # label
        labels = [self.Main.Data.Metadata.LSTdata.loc[ind_map[n]]['Odour'] for n in range(self.Main.Data.nTrials)]

        # combine
        new_labels = [labels[i]+new_concs[i] for i in range(len(labels))]
        
        self.Main.Data.Metadata.trial_labels = new_labels
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.set_current_labels(self.Main.Data.Metadata.trial_labels)
        
        # set stimulus timing
        # cycle time
        
        pass
        
        
    def convert_log2lst(self):
        """ opens file dialog to chose a log file to convert """
        log_path = self.OpenFileDialog(title='load .vws.log',default_dir=self.Main.Options.general['cwd'],extension='*.log')[0]
        gio.log2lst(log_path)
        
#==============================================================================
    ### trial labels as text files
#==============================================================================
    
    def load_trial_labels(self):
        """ if only one string per line, then the order of lines corresponds the 
        order of the stimulus presentations, and the filenames contain this 
        ordering in their alphabetical / alphanumeric structure.
        
        Alternatively, a line can contain 2 strings (comma separated), then the 
        first is the filename without extension, and the second is the label """

        # get filepath per UI
        filepath = self.OpenFileDialog(title='load a textfile with trial labels',default_dir=self.Main.Options.general['cwd'])
        filepath = filepath[0]
        
        # check which whay to parse
        with open(filepath,'r') as fh:
            firstline = fh.readline()
            
        if len(firstline.split(',')) == 1:
            mode = 'single'
        if len(firstline.split(',')) == 2:
            mode = 'mappable'
        if len(firstline.split(',')) > 2:
            raise "trial labels file contains more than 2 strings per line, cannot parse that."
            
        labels = self.read_trial_labels(filepath,mode=mode)
        self.Main.Data.Metadata.labels = labels
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.set_current_labels(labels)
        pass
        
    def read_trial_labels(self,filepath,mode='single'):
        """ reads the labels from the text file at path (newline separated) """
        
        if mode == 'single':
            with open(filepath, 'r') as fh:
                labels = [label.strip() for label in fh.readlines()]
        
        if mode == 'mappable':
            with open(filepath, 'r') as fh:
                lines = [line.strip() for line in fh.readlines()]
                ordered = [line.split(',') for line in lines]
                names = [entries[0] for entries in ordered]
                labels = [entries[1] for entries in ordered]
        
        return labels
    
#==============================================================================
    ### Options
#==============================================================================
    
    def load_options(self,reset=True):
        if not(reset):
            print "restoring last options"
            try:
                self.Main.IO.read_options() 
            except:
                print "no options to restore found, defaulting"
                self.Main.Options.load_default_options()
        else:
            print "default options"
            self.Main.Options.load_default_options()
            pass
    
    def read_options(self):
        """ unpickles the options dicts from ./settings """

        # this is for reading all defaults
        self.Main.Options.load_default_options() 
        
        # and then replace
        dict_list = ['general','preprocessing','ROI','export']
        for d in dict_list:
            dict_path = self.Main.program_dir + os.path.sep + 'settings' + os.path.sep + d
            with open(dict_path,'r') as fh:
                setattr(self.Main.Options,d,pickle.load(fh))
                
        # some fixes because these values have to be reset
        self.Main.Options.ROI['active_ROIs'] = []
        self.Main.Options.ROI['last_active'] =  None
        pass
        
    def save_options(self):
        """ pickle the current options dicts into the settings subfolder """
        dict_list = ['general','preprocessing','ROI','export']
        for d in dict_list:
            outpath = self.Main.program_dir + os.path.sep + 'settings' + os.path.sep + d
            with open(outpath,'w') as fh:
                pickle.dump(getattr(self.Main.Options,d),fh)
        pass
    
#==============================================================================
    ### helpers
#==============================================================================

    
    def convert_lsm2tif(self,paths):
        """ batch convert .lsm files to tiffs """
        for path in paths:
            io.lsm2tiff(path)
        
        tifpaths = [os.path.splitext(path)[0]+'.tif' for path in paths]
        return tifpaths
    
    def convert_pst2tif(self,paths):
        """ batch convert .lsm files to tiffs """
        for path in paths:
            io.pst2tiff(path)
            
        tifpaths = [os.path.splitext(path)[0]+'.tif' for path in paths]
        return tifpaths
        
    def append_extension(self,fname,ext):
        """ if filename does not end with extension, append it """
        if os.path.splitext(fname)[1] == '':
            fname = fname + ext
        return fname

        
    
    def glo_sort_traces(self):
        """ converts a Traces np.array from the definition (t,ROI,trial) into the 
        .gloDatamix style (ROI/trial,t) where iteration is first over ROI and then
        over trial """
        
        Traces_conv = sp.zeros((len(self.Main.ROIs.ROI_list) * self.Main.Data.nTrials , self.Main.Data.nFrames))
        
        k = 0
        for n in range(self.Main.Data.nTrials):
            for i in range(len(self.Main.ROIs.ROI_list)):            
                Traces_conv[k,:] = self.Main.Data.Traces[:,i,n]
                k = k +1

        return Traces_conv

