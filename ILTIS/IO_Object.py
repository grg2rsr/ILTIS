# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:52:50 2015

@author: georg
"""

from PyQt4 import QtGui, QtCore # for the dialogs
from lib import IOtools as io
from Data_Object import Data_Object, Metadata_Object
import os
import sys
import scipy as sp
import pandas as pd

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
        self.Main.Options_Control.init_UI()

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
        
        if os.path.splitext(path)[1] != extension:
            path = path + '.gloDatamix'
            
        return path
        
#==============================================================================
    ### reading data sets
#==============================================================================

    """ get paths to load. determine file format. open appropriate reader """
    def load_data(self):

        # Data init        
        self.Main.Data = Data_Object()
        self.Main.Data.Metadata = Metadata_Object(self.Main.Data)
        
        # get paths
        paths = self.get_paths_to_read()
        if paths == None:
            pass
        
        # determine format
        file_format = self.determine_format(paths)
        
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
            
        # default settings if no metadata is read
        self.Main.Data.Metadata.paths = paths
        
        # infer some Meta information
        self.Main.Data.infer()

        # load options
        self.load_options(auto=True)
        
    def get_paths_to_read(self):
#        paths = self.OpenFileDialog(title='Open data set', default_dir=self.Main.Options.general['cwd'], extension='(*.tif *.ids *.lsm)')
        paths = self.OpenFileDialog(title='Open data set', default_dir=self.Main.Options.general['cwd'], extension='(*.tif *.lsm)')
        return paths
        
    def determine_format(self,paths):
        """ goes through the paths and raises an exception if there are incompatibilities """
        # check for mixed file formats
        endings = sp.array([os.path.splitext(path)[1] for path in paths])
        if not(sp.all(endings[0] == endings)):
            print "raise error here, not all fileformats are equal"
        return endings[0]
    
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
            

        
    
#    def load_ids(path):
#        pass


#==============================================================================
    ### writing datasets         
#==============================================================================
#    def save_ids(self):
#        pass
    
    def save_tif(self):
        pass
    
#==============================================================================
    ### exporting traces
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
        
        
        ## exporting to csv
        if self.Main.Options.export['format'] == '.csv':
            if self.Main.verbose:
                print "extracting traces and writing to .csv"
            
            labels = [ROI.label for ROI in self.Main.ROIs.ROI_list]
            labels.insert(0,'time [s]')
            
            tvec = sp.linspace(0,self.Main.Data.Traces.shape[0]/self.Main.Options.preprocessing['dt'],self.Main.Data.Traces.shape[0])
            tvec = tvec - self.Main.Options.preprocessing['stimuli'][0,0] * self.Main.Options.preprocessing['dt']
            
            for n in range(self.Main.Data.nTrials):
                outpath = os.path.splitext(self.Main.Data.Metadata.paths[n])[0] + '_traces_' + str(n+1) + '.csv'
                data = sp.concatenate((tvec[:,sp.newaxis],self.Main.Data.Traces[:,:,n]),axis=1)
                pd.DataFrame(data,columns=labels).to_csv(outpath,delimiter=',')
                
                if self.Main.verbose:
                    print 'written: ', outpath

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

            outpath = self.SaveFileDialog(title='saving to .gloDatamix',default_dir=self.Main.cwd)    

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
            
        
        pass
#==============================================================================
    ### LST related
#==============================================================================
        
    def map_lst_inds_to_path_inds(self):
        """ establishes a mapping between the order of the datasets in paths
        and their corresponding rows in the lst file 
        this parser is now with added flexibility to deal with aljas vs michis
        lst styles."""
        
        ind_map = []
                
        for n,path in enumerate(self.Main.Data.Metadata.paths):            
            filename = os.path.splitext(os.path.split(path)[1])[0]
            ### FIXME BUG this kills if there is no _whatever shit appended...
            filename = '_'.join(filename.split('_')[:-1]) # dirty dirty hack to remove the _affine.tif or the _full.tif. Will not work with two underscores like _bspline_transformed.tif
            
            myInd = None
            for ind in self.Main.Data.Metadata.LSTdata.index:
                info = self.Main.Data.Metadata.LSTdata['DBB1'][ind].strip().split('\\')
                if len(info) == 3: # here is the compatibility Aljas .lst vs Michis .lst files
                    Tanimal, tmp, Experiment = info
                if len(info) == 2:
                    Tanimal, Experiment
                Experiment = os.path.splitext(Experiment)[0]
                if Experiment == filename:
                    myInd = ind
                    ind_map.append(ind)
                    
            if myInd == None:
                print "Experiment not found in the .lst file!"
                print Experiment, filename
        return ind_map
        

    def load_lst(self):
        """ opens a file dialoge and asks for a lst file. when it's read, 
        update the names that are shown next to the viewboxes with the names of
        the odors """
        
        lst_path = self.OpenFileDialog(title='load lst',default_dir=self.Main.cwd,extension='*.lst')[0]
        LSTdata = pd.read_csv(lst_path,header=0,delimiter='\t')
                    
        # remove the weird random amount of whitespaces in the column names
        columns = []
        for col in LSTdata.columns:
            columns.append(col.strip())
            pass
        LSTdata.columns = columns
        
        # store
        self.Main.Data.Metadata.LSTdata = LSTdata
        self.Main.Options.flags['LST_was_read'] = True
        
        # update labels
        ind_map = self.map_lst_inds_to_path_inds()

        self.Main.Data.Metadata.trial_labels = [LSTdata.loc[ind_map[n]]['Odour'] for n in range(self.Main.Data.nTrials)]
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.set_current_labels(self.Main.Data.Metadata.trial_labels)
        pass
#==============================================================================
    ### trial labels
#==============================================================================

    
    def load_trial_labels(self):
        """ opens a file dialog and runs read_trial_labels with the selected path """
        filepath = self.OpenFileDialog(title='load a textfile with trial labels',default_dir=self.Main.Options.general['cwd'])
        filepath = filepath[0]
        self.read_trial_labels(filepath)
        pass
        
    def read_trial_labels(self,filepath):
        """ reads the labels from the text file at path (newline separated) """
        with open(filepath, 'r') as fh:
            labels = [label.strip() for label in fh.readlines()]
        self.Main.Data.Metadata.labels = labels
        self.Main.MainWindow.Front_Control_Panel.Data_Selector.set_current_labels(labels)
        pass
#==============================================================================
    ### Options
#==============================================================================
    def load_options(self,auto=True):
        """ get the options filepath and run read_options """
        self.Main.Options.load_default_options()        
#        if auto==True: # check for options file in the same path, if not, default
        
#            self.Main.IO.load_options() 
    
            # and this code is then moved to IO        
#            if self.Main.options_filepath != None:
#                if os.path.exists(self.options_filepath):
#                    if self.Main.verbose:
#                        print "loading options file from ", self.options_filepath
#                        self.Main.IO.load_options()
#            pass
        
#        else: # open filedialog and execute read options
#            pass
        pass
    
    def read_options(self):
        """ options fileformat has yet to be specified ... """
        pass
        
    def save_options(self):
        """ save options to options_filepath """
        pass
    
#==============================================================================
    ### helpers
#==============================================================================

    
    def convert_lsm2tif(paths):
        """ batch convert .lsm files to tiffs """
        # FIXME
        pass