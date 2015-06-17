# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:35:08 2014

@author: georg
"""



from __future__ import division
import scipy as sp
import tifffile
import os
import re

""" a collection of IO functions """ 

#==============================================================================
# helpers
#==============================================================================
### helpers
def get_np_dtype(mhd_dtype):
    """ maps mhd datatypes to np datatypes """
    
    dtype_map = {'MET_FLOAT': 'float32',
                 'MET_DOUBLE': 'float64',
                 'MET_UCHAR':' uint8',
                 'MET_CHAR': 'int8',
                 'MET_USHORT': 'uint16',
                 'MET_SHORT': 'int16',
                 'MET_UINT': 'uint32',
                 'MET_INT': 'int32',
                 'MET_ULONG': 'uint64',
                 'MET_LONG': 'int64'}
    
    return dtype_map[mhd_dtype]

def get_mhd_dtype(dtype):
    dtype_map = {'float32': 'MET_FLOAT',
                 'float64': 'MET_DOUBLE',
                 'uint8': 'MET_UCHAR',
                 'int8': 'MET_CHAR',
                 'uint16': 'MET_USHORT',
                 'int16': 'MET_SHORT',
                 'uint32': 'MET_UINT',
                 'int32': 'MET_INT',
                 'uint64': 'MET_ULONG',
                 'int64': 'MET_LONG'}
    
    return dtype_map[dtype]

#==============================================================================
# readers 
#==============================================================================
### readers

def read_tiff(path):
    """ reads a tiff file from the path as a np array and changes its 
    dimensions to x y """
    data = tifffile.imread(path)
    data = data.T
    return data
    
def read_tiffstack(path):
    """ converts a tiff stack (image x y dimensions, individual tiff pages t)
    into a 3d np array, dimensions are (x,y,t)"""
    
    data = tifffile.TIFFfile(path).asarray()
    data = data.swapaxes(0,2) # moves t to last dim. tifffile reads pages as first dim
    return data
    
def read_3dtiff(path):
    """ missing docstring """
    data = tifffile.TIFFfile(path).asarray()
    data = data.swapaxes(0,3) 
    data = data[:,0,:,:]
    return data
        
def read_lsm(path,color=False):
    """ takes a path to a lsm file, reads the file with the tifffile lib and 
    returns a np array

    final format is of the array dims: x y t - if color is True: x y t c
    """
    data = tifffile.imread(path)
    Data_cut = data[0,0,:,:,:] # empirical ... 
    Data_cut_rot = sp.swapaxes(Data_cut,0,2)
    
    if color: # Thorough testing if xy order is preserved is missing!
        Data_cut = data[0,:,:,:]
        Data_cut_rot = sp.swapaxes(Data_cut,2,0)
        Data_cut_rot = sp.swapaxes(Data_cut_rot,1,3)
       
    return Data_cut_rot
    
def read_mhd(mhd_path):
    """ reads the data from an mhd file and returns a np array. The data
    type to read is specified from the tifffile module by the tiff reading 
    capabilities. Based on code from the pirt library. 
        
    see: https://bitbucket.org/almarklein/pirt"""
    
    # Load description from mhd file
    mhd = open(mhd_path,'r').read()
    
    # Get data filename and load raw data
    raw_path = re.findall('ElementDataFile = (.+)',mhd)[0]
    
    # if the path in the mhd is not an absolute path, make it one
    if raw_path[0] != '/':
        raw_path = os.path.join(os.path.dirname(mhd_path),os.path.basename(raw_path))
        
    # get dimensions
    dimensions = sp.int16(re.findall('DimSize = (.+)',mhd)[0].split())
    
    # get correct datatype mapping    
    mhd_dtype = re.findall('ElementType = (.+)',mhd)[0]
    dtype = get_np_dtype(mhd_dtype)
    
    # read and reshape
    fh = open(raw_path, 'rb')
    data = sp.frombuffer(fh.read(),dtype = dtype)
    
    if len(dimensions) == 2:
        data_reshape = sp.reshape(data,(dimensions[1],dimensions[0]))
        data_reshape = data_reshape.T
    if len(dimensions) == 3: # FIXME
        sys.exit()
        data_reshape = sp.reshape(data,(dimensions[2],dimensions[1],dimensions[0]))
               
    return data_reshape
    
def read_pst(pst_path):
    """ read tillvision based .pst files as uint16. DEPRECATED! 
    USE THE VERSION IN gioIO! """

    inf_path = os.path.splitext(pst_path)[0] + '.inf'
    
    # reading stack size from inf
    meta = {}
    with open(inf_path,'r') as fh:
    #    fh.next()
        for line in fh.readlines():
            try:
                k,v = line.strip().split('=')
                meta[k] = v
            except:
                pass
    
    shape = sp.int32((meta['Width'],meta['Height'],meta['Frames']))
    
    
    raw = sp.fromfile(pst_path,dtype='int16')
    data = sp.reshape(raw,shape,order='F')
    return data.astype('uint16')
    
#==============================================================================
# writers    
#==============================================================================
### writers
    
def save_tstack(data,path):
    """ saves an ndarray to a tiff file with the z axes in the pages. There is 
    some confusion about the axes. read_lsm loads the correct x y z dims"""

    # tifffile.imsave gets z y x
    datac = data.copy()
    datac = datac.swapaxes(0,2) # 
        
    tifffile.imsave(path,datac)
    pass

def save_tiff(data,path):
    """ using the tifffile library to save a xy image array to a tiff, preserving
    correct xy order"""
    
    tifffile.imsave(path,data.T)
    pass

def save_mhd(data,path,dtype=None):
    """ writes np array to an mhd specified by path. the raw file is written
    with the same name.
    """

    # does the data have the right structure?
    # fixme for n dimensionality
    if len(data.shape) == 2:
        data = data.T
    if len(data.shape) == 3:
        sys.exit()
        # fixme this needs to be fixed empiricaly
        pass

    # converts to chosen dtype
    if dtype:
        data = data.astype(dtype)
        
    # left for possible future implementations
    resolution = sp.ones(len(data.shape))
    
    # path preparations        
    mhd_path = path
    raw_path = os.path.splitext(mhd_path)[0] + '.raw'    
    
    # metadata preparations
    lines = ["NDims = <ndims>",
             "DimSize = <dimsize>",
             "ElementSpacing = <resolution>",
             "Position = 0 0",
             "ElementByteOrderMSB = False",
             "ElementType = <mhd_dtype>",
             "ElementDataFile = <raw_path>"]
    text = '\n'.join(lines)

    # changing the fields
    text = text.replace('<ndims>', str(len(data.shape)))
    text = text.replace('<dimsize>', ' '.join([str(s) for s in data.shape[::-1]]))
    text = text.replace('<raw_path>', raw_path)
    text = text.replace('<resolution>', ' '.join([str(r) for r in resolution[::-1]]))
    text = text.replace('<mhd_dtype>', get_mhd_dtype(str(data.dtype)))

    # write raw
    f = open(raw_path, 'wb')
    try:
        f.write(data.data)
    finally:
        f.close()
        
    # write mhd file
    f = open(mhd_path, 'wb')
    try:
        f.write(text.encode('utf-8'))
    finally:
        f.close()
    pass

#==============================================================================
# convenience
#==============================================================================
### convenience
    
def lsm2tiff(path,outpath=None):
    """ convinence function for converting a .lsm to a .tiff """
    Stack = read_lsm(path)
    if not(outpath):
        outpath = os.path.splitext(path)[0] + '.tif'
    save_tstack(Stack,outpath)
    pass

def pst2tiff(path,outpath=None):
    """ convinence function for converting a .pst to a .tiff """
    Stack = read_pst(path)
    if not(outpath):
        outpath = os.path.splitext(path)[0] + '.tif'
    save_tstack(Stack,outpath)
    pass

def tiff2mhd(tiffpath,outpath=None,dtype=None):
    """ writes an mhd file from the tiff found at tiffpath to an mhd at the 
    location specified by outpath. If no outpath is given, the path of the tif
    is assumed.
    """
    
    # FIXME CALL SIGNATURE CHANGED!!!!    
    # should be fixed

    # path preparations
    if not(outpath):
        outpath = os.path.splitext(tiffpath)[0] + '.mhd'
        
    data = read_tiff(tiffpath)
    save_mhd(data,outpath,dtype=dtype)
    pass
    
def mhd2tiff(mhd_path,outpath=None):
    """ converts a mhd to a tif. if no outpath is specified, tif dirpath is 
    assumend """
    
    if not(outpath):
        outpath = os.path.splitext(mhd_path)[0] + '.tif'
    
    data = read_mhd(mhd_path)
    data = data.clip(0.0,2.0**16).astype('uint16') # looks like a "just to be safe"
    save_tiff(data,outpath)
    pass
    
def split_color_lsm(path,outpath=None):
    """ splits a lsm file with a color dimension into tiff files in the 
    same folder """
    
    if not(outpath):
        outpath = os.path.dirname(path)
    filename = os.path.basename(path)
    
    data = read_lsm(path,color=True)
    for i in range(data.shape[3]):
        out = os.path.join(outpath,os.path.splitext(filename)[0] + '_ch_' + str(i+1) + '.tif')
        save_tstack(data[:,:,:,i],out)

if __name__ == '__main__':
    import sys
    print "this is a library now"
    sys.exit()
    
    
#    import sys
    
## testing
#    path = '/home/georg/Dropbox/python/xyt_movement_correction/test_data/stack_trunc.tif'
#    os.chdir(os.path.dirname(path))
#    data = read_tiffstack(path)
#    page = data[:,:,0]
#    save_tiff(page,'stack_trunc_page.tif')
#    save_mhd(page,'stack_trunc_page.mhd')
#    mhd_data = read_mhd('stack_trunc_page.mhd')
#    tif_data = read_tiff('stack_trunc_page.tif')
#    mhd2tiff('stack_trunc_page.mhd','./stack_trunc_page_prev_mhd.tif')
#    

## nontesting
#    """ """
#    
#    paths = []
#        
#    if len(sys.argv) == 2:
#        paths.append(sys.argv[1])
#        
#    if len(sys.argv) == 3:
#        if sys.argv[2] == 'filelist':
#            filelist_path = sys.argv[1]
#            fH = open(filelist_path,'r')
#            for line in fH:
#                paths.append(line.strip())
#            fH.close()
#        else:
#            print "unknown mode ... "
#            print sys.argv
#            sys.exit()
#    
#    
#    for path in paths:
#        print "processing file: ",path
#        outpath = os.path.splitext(path)[0] + '.tif'
##        lsm2tiff(path,outpath)
#        split_color_lsm(path)
    
    
    