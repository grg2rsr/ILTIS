# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 12:19:07 2015

@author: georg
"""


""" 
#==============================================================================
# code style conventions:
#==============================================================================
General:
A mix of camelCase and under_score: all objects that are derived from a camelCase 
library are kept in camelCase style. All self definded objects, variables etc. are
in underscore.
https://whathecode.wordpress.com/2011/02/10/camelcase-vs-underscores-scientific-showdown/ 

Namings:
x,y = image
x,y,t = t_stack
x,y,t,T = multi_stack
t,ID,stim,rep = traces

'read/write' explicitly to/from a path on the dist
'load/save' implicitly knows where to get/put the data

#==============================================================================
# OO Structure
#==============================================================================

classes and their references to each other

program
-mainwindow
--menubar
--toolbar
--data display widget
---Image viewer
---traces viewer
--front panel control widget
---data selector
---roi manager
--status bar
-data object
--metadata object
-options (view options, analysis options)
-roi


#==============================================================================
# classes
#==============================================================================
mainwindow
-menu bar
-tool bar
-data display widget
-front panel control widget
-status bar

data display widget
-image view
-luts
-traces plot

front panel control widget
-view checkboxes
-ROI manager

data object
fields
-x y t T (xy = image, xyt = tstack, xytT = multi_stack)
-tvec after metadata association
-t id stim rep (traces)
-mask (tstack)
-metadata object
methods
-save
-load on or the other format (save format of dataset is always w the main pickled object that has references to the raw data that is stored as .npa in subfolders w same exp name)

metadata object
fields
-lst data dataframe
-dt
-stim labels
-coors (text file)
-stim start stop
methods

ROI class
-hack extras into per inheritance
-upon add, get from options dict how it should look like

ROI manager

Options class
-export format
-filter size
-jan soelter options
-


"""