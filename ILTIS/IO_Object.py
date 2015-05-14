# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:52:50 2015

@author: georg
"""

from PyQt4 import QtGui, QtCore # for the dialogs
from lib import IOtools as io
from Data_Object import Data_Object, Metadata_Object
from ROIs_Object import myCircleROI,myPolyLineROI
import os
import sys
import scipy as sp
import pandas as pd
import pickle
import re
import time

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
        """ reads a .roifile and updates the ROIs """
        self.Main.ROIs.reset()
                
        roi_file_path = self.OpenFileDialog(title='load ROIs',default_dir = self.Main.Options.general['cwd'], extension='*.roi')[0]
        
        with open(roi_file_path, 'r') as fh:
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
#        io.save_tstack(self.ex_mask.astype('uint16'),outpath)
#        print "saved ROIs in .tif format to", outpath
        
        pass
    
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
                self.load_lst()
            
            # preparing the write
            labels = ['NGloTag','NConc','NStimON','NStimOff','NNoFrames','NFrameTime','TGloInfo','TOdour','T_dbb1','Tcomment','TLabel','Tanimal']
            data_labels = ['data'] * self.Main.Data.nFrames
            for i,l in enumerate(data_labels):
                labels.append(l+str(i))

            outpath = self.SaveFileDialog(title='saving to .gloDatamix',default_dir=self.Main.Options.general['cwd'])   
            
            outpath = self.append_extension(outpath,'.gloDatamix')

            fh = open(outpath,'w')
            fh.write('\t'.join(labels))
            fh.write('\n')

            for n,path in enumerate(self.Main.Data.Metadata.paths):            
                inds_map = self.map_lst_inds_to_path_inds()
                for i in range(len(self.Main.ROIs.ROI_list)):
                    myInd = inds_map[n]
#                    NGloTag = str(Coors[i,2])
                    NGloTag = str(self.Main.ROIs.ROI_list[i].label)
                    NOConc = str(self.Main.Data.Metadata.LSTdata.loc[myInd]['OConc'])
                    NStimON = str(self.Main.Data.Metadata.LSTdata.loc[myInd]['StimON'])
                    NStimOFF = str(self.Main.Data.Metadata.LSTdata.loc[myInd]['StimOFF'])
                    NNoFrames = str(self.Main.Data.nFrames)
                    NFrameTime = 'dt' ### FIXME
                    pos = self.Main.ROIs.ROI_list[i].get_center()
                    TGloInfo = 'Coor' + str(int(sp.around(pos[0],decimals=0))) + ':' + str(int(sp.around(pos[1],decimals=0)))
                    TOdour = self.Main.Data.Metadata.LSTdata.loc[myInd]['Odour']
                    T_dbb1 = self.Main.Data.Metadata.LSTdata.loc[myInd]['DBB1']
                    Tcomment = self.Main.Data.Metadata.LSTdata.loc[myInd]['Comment']
                    TLabel = self.Main.Data.Metadata.LSTdata.loc[myInd]['Label']
                    Tanimal = self.Main.Data.Metadata.LSTdata['DBB1'][myInd].strip().split('\\')[0] # see above, is the animal
                    
                    tmp = [NGloTag,NOConc,NStimON,NStimOFF,NNoFrames,NFrameTime,TGloInfo,TOdour,T_dbb1,Tcomment,TLabel,Tanimal]
                    tmp = tmp + self.Main.Data.Traces[:,i,n].astype('S20').tolist()
                    values = '\t'.join(tmp)

                    fh.write(values)
                    fh.write('\n')
                
            fh.close()
            print "gloDatamix written to ", outpath
            
        



#==============================================================================
    ### lst parser / gloDatamix compatibility
#==============================================================================
        
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
            suffixes = ['affine','full','fullaffineglobal','fullbsplineglobal']          
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
        
        lst_path = self.OpenFileDialog(title='load lst',default_dir=self.Main.Options.general['cwd'],extension='*.lst')[0]
        
        # read
        self.Main.Data.Metadata.LSTdata = self.read_lst(lst_path)
        self.Main.Options.flags['LST_was_read'] = True
        
        # update labels
        ind_map = self.map_lst_inds_to_path_inds()
        
        #concentration
        concs = [str(self.Main.Data.Metadata.LSTdata.loc[ind_map[n]]['OConc']) for n in range(self.Main.Data.nTrials)]
        new_concs = []        
        for conc in concs:
            if sp.int32(conc) > 0: # info is in dilutions
                new_conc = str(-1 * sp.around(sp.log10(sp.int32(conc))))
                new_concs.append(new_conc)
            else:
                new_concs.append(conc)
                
        # label
        labels = [self.Main.Data.Metadata.LSTdata.loc[ind_map[n]]['Odour'] for n in range(self.Main.Data.nTrials)]

        # combine
        new_labels = [labels[i]+new_concs[i] for i in range(len(labels))]
        
#        self.Main.Data.Metadata.trial_labels = [self.Main.Data.Metadata.LSTdata.loc[ind_map[n]]['Odour']+str(self.Main.Data.Metadata.LSTdata.loc[ind_map[n]]['OConc']) for n in range(self.Main.Data.nTrials)]
        self.Main.Data.Metadata.trial_labels = new_labels
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.set_current_labels(self.Main.Data.Metadata.trial_labels)
        
        pass
    
    def read_lst(self,lst_path):
        """ reads the .lst file at lst_path to a pd.DataFrame """
        LSTdata = pd.read_csv(lst_path,header=0,delimiter='\t')
                    
        # remove the weird random amount of whitespaces in the column names
        columns = []
        for col in LSTdata.columns:
            columns.append(col.strip())
            pass
        LSTdata.columns = columns
        
        return LSTdata
        
        
    def convert_log2lst(self):
        """ opens file dialog to chose a log file to convert """
        log_path = self.OpenFileDialog(title='load .vws.log',default_dir=self.Main.Options.general['cwd'],extension='*.log')[0]
        self.log2lst(log_path)
        
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
    
    def log2lst(self,fname):
        """ converts a till photonics .vws.log into a lst """
        
        # some constants and declarations
        block_starts = []
        block_names = []
        read_length = 18 # const
        lst_labels = ["Measu","Label","Odour","DBB1","Cycle","MTime","OConc","Control","StimON","StimOFF","Pharma","PhTime","PhConc","Comment","ShiftX","ShiftY","StimISI","setting","dbb2","dbb3","PxSzX","PxSzY","PosZ","Lambda","Countl","slvFlip","Stim2ON","Stim2OFF","Age","Analyze"]
        last_time = 0
        lst_fname = os.path.splitext(os.path.splitext(fname)[0])[0] + '.lst'
        
        # read log and parse
        with open(fname, 'r') as fh:
            lines = [line.strip() for line in fh.readlines()]
        
        for i,line in enumerate(lines):
            match = re.search('^\[(.*)\]',line)
            if match:
                block_starts.append(i)
                block_names.append(match.group(1))
                
        valid_blocks = []
        for i,name in enumerate(block_names):
            if name.count('Snapshot') > 0 or name.count('Delta') > 0:
                pass
            else:
                valid_blocks.append([i,block_starts[i],name])
        
        Measurements = []
        for i,block_info in enumerate(valid_blocks):
            Measurements.append({'index':block_info[0],'label':block_info[2]})
            
            ind = block_info[1]
            block = lines[ind+1:ind+read_length]
        
            for line in block:
                line_split = line.split(':')
                if len(line_split) == 2:
                    key,value = line_split
                if len(line_split) > 2:
                    key = line_split[0]
                    value = ':'.join(line_split[1:]).strip()
                Measurements[i][key] = value
        
        # loop and write
        lst_handle = open(lst_fname,'w')  
        lst_handle.write('\t'.join(lst_labels))
        
        for Measurement in Measurements:
            label_split = Measurement['label'].split('_')
            if len(label_split) == 3:
                setting,Odour, OConc = label_split
            if len(label_split) == 2:
                setting,OConc = label_split
                Odour = 'Missing'
        
            # time
            """ it is unclear what mtime is exactly supposed to be. In this calc, there
            is some kind of bug, leaving a 1s approx offst """
            try:
                times = Measurement['timing [ms]'].strip()
                times = sp.array(times.split(' '),dtype='int32')
                times_hhmmss = [time.strftime('%H:%M:%S',time.gmtime((t+last_time)/1000.0)) for t in times]
                last_time = times[-1] + last_time
                mtime = times_hhmmss[len(times)/2]
                dt = str(sp.diff(times)[0])
            except:
                mtime = '-1'
                dt = '-1'
        
            # location, check if pst, else -1
            ext = os.path.splitext(Measurement['Location'])[1]
            if ext != '.pst':
                Location = '-1'
            else:
                tanimal = os.path.splitext(os.path.splitext(os.path.basename(fname))[0])[0] # tanimal
                dbb = os.path.splitext(Measurement['Location'].split('\\')[-1])[0] # dbb wo pst
                Location = '\\'.join([tanimal + '.pst',dbb])
                
            # Countl
            Countl = 'subloop,\''+str(Measurement['index']+1)+'\';  '+Measurement['label']
            
            Measu = str(Measurement['index']+1)
            Label = Measurement['label']
            Odour = Odour
            DBB1 = Location
            Cycle = dt
            MTime = mtime
            OConc = OConc
            Control = '0'
            StimON = '24'
            StimOFF = '28'
            Pharma = 'Ringer'
            PhTime = mtime
            PhConc = '0'
            Comment = 'log2lst.py'
            ShiftX = '0'
            ShiftY = '0'
            StimISI = '0'
            setting = setting
            dbb2 = 'noDBB2'
            dbb3 = 'noDBB3'
            PxSzX = '1.57'
            PxSzY = '1.57'
            PosZ = '0'
            Lambda = Measurement['Monochromator wavelength [nm]'].strip()
            Countl = Countl
            slvFlip = '0'
            Stim2ON = '36'
            Stim2OFF = '40'
            Age = '-1'
            Analyze = '-2'
            
            values = '\t'.join([Measu,Label,Odour,DBB1,Cycle,MTime,OConc,Control,StimON,StimOFF,Pharma,PhTime,PhConc,Comment,ShiftX,ShiftY,StimISI,setting,dbb2,dbb3,PxSzX,PxSzY,PosZ,Lambda,Countl,slvFlip,Stim2ON,Stim2OFF,Age,Analyze])
            lst_handle.write('\n')
            lst_handle.write(values)
            
        lst_handle.close()