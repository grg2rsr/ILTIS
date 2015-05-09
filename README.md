# ILTIS
an _Interactive Labeled-Trial Image-stack Slicer_

## Description

this program was designed to interactively and flexibly slice datasets from functional imaging experiments along the time domain. A classical imaging experiment consists of high dimensional data sets: The individual imaging trials, e.g. the response of a certain area to a stimulus is ususally imaged as (x,y) images over time (t), resulting in 3d image stacks. Additionally, different stimuli (S) are given with a certain number of repetitons (R), resulting in 5 dimensional data (x,y,t,S,R)

This program is designed to extract time traces from these kind of data sets and sort them according to stimulus class S and repetiton R. While this is in principle possible with ImageJ/Fiji macros (because basically anything is in principle possible with their macros), this program offers great flexibility in terms of data display, scaling, color maps, overlays, data subselection and trace visualization.

## Usage
### loading data
The program is still in a very early developmental stage, but already useable. Load your data from the `load` menu, trial labels can be added with the `load labels` function. Label files are expected to consist of a label in each line, with the index of each line corresponding to the respective data set. For example, if you want to load the files

+ my_trial_1.tif
+ my_trial_2.tif
+ my_trial_3.tif
+ my_trial_4.tif

and in your experiment trial 1 and 3 were stimulus A, 2 and 4 were stimulus B, then the label file has to look like

> stimulus_A  
stimulus_B  
stimulus_A  
stimulus_B  

#### file support
Fully supported are only `.tif` files, `.lsm` files from Zeiss confocal are likely supported (at least the ones from the LSM 510 pre-Zen software). Imports for other formats are being developed, please leave a post and send me a example file.

### Frame visualization
To subset the currently displayed data set use the `Data Selector` on the top right. It supports intuitive `ctrl+click`, `shift+click`, `ctrl+a` etc. to select or deselect individual trials to display. The mode of display can be set with the centrally position icons, for example switch between $\frac{\Delta F}{F}$ / raw display, average over frames, or a _monochrome_ mode for individual trials with the raw data as the background optionally overlaid with the $\frac{\Delta F}{F}$ signal in a glow colormap.

### ROI functionality
ROIs are added by simply clicking on the image, the type of ROI (circular or polygonal) can be selected in the extra `Options` window, opened by clicking on the icon in the toolbar. The `ROI Manager` supports the same multiple selection of ROIs just as the `Data Selector`

### Traces visualization
Depending on the selected datasets and the activated ROIs, the displayed data is sliced along the time domain under the area covered by the ROIs, each frames values are averaged. The sliced traces are color coded and displayed in two seperated ways: All traces with a common time base, or sorted to stimulus identity. Both windows are tabbed below the frame display, but can also be detatched by clicking on the blue tab and dragging them (for example to a seperate screen). Traces are interactively updated upon any change to the ROIs or data selection.

## Installation
Installlation script coming soon. Until then, just run the `run.sh` if you are on Linux or just direcly `python Main.py`
### Dependencies
+ sicpy
+ PyQt4
+ pyqtgraph
