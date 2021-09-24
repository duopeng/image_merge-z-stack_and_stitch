# Microscope picture preprocessing
## Full automation of merging z-stacks (focus-stacking) and then stitch different view of the same entity
### Example workflow:
![alt text](https://github.com/duopeng/image_merge-z-stack_and_stitch/blob/main/workflow.jpg?raw=true)

## Instructions:  
(1) Clone the repository.  
 
(2) Install ImageJ or Fiji (tested with ImageJ 1.53f51).  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Copy the two macro files "focusstack.ijm" and "stitch.ijm" to the "macro" folder in your ImageJ installation folder

(3) Prepare an excel file containing the metadata ( see metadata.xlsx for an example)  
This example have two mosquito midguts (entities), and each gut has two microscope views (regions),and each region has 2 z-stacks.  
![alt text](https://github.com/duopeng/image_merge-z-stack_and_stitch/blob/main/metadata.screenshot.jpg?raw=true)

(4) Prepare a folder containing images with names specificed by the metadata.  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The folder "example_images" has all the images specified in the example metadata

(5) Run the python script (need python >= 3.8 and pandas >=1.3.3)  
&nbsp;&nbsp;&nbsp;&nbsp; python merge-z-stack_and_stitch.py --dir [path to image folder] --excelfile [path to excel file] --IJpath [path to ImageJ excutable]  
&nbsp;&nbsp; to run the example:  
&nbsp;&nbsp;&nbsp;&nbsp; python merge-z-stack_and_stitch.py --dir example_images --excelfile metadata.xlsx --IJpath [path to ImageJ excutable]  
