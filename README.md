## Convert multiple z-stacks of different view into a single panoramic view with extended focus
### Example workflow:
![alt text](https://github.com/duopeng/image_merge-z-stack_and_stitch/blob/main/workflow.jpg?raw=true)

## Instructions:  
### (1) Clone the repository  
`git clone https://github.com/duopeng/image_merge-z-stack_and_stitch`
 
### (2) Install dependencies
- Install ImageJ (tested with v1.53f51) *or* Fiji.  
Copy the two macro files `focusstack.ijm` and `stitch.ijm` to the `macro` folder in your ImageJ/Fiji installation folder
- pandas (tested with v1.3.3) and openpyxl

### (3) Prepare an excel file containing the metadata
see `metadata.xlsx` for an example  
The following picture shows an example that has two mosquito midguts (entities), and each gut has two microscope views (regions),and each region has 2 z-stacks.  
![alt text](https://github.com/duopeng/image_merge-z-stack_and_stitch/blob/main/metadata.screenshot.jpg?raw=true)

### (4) Prepare a folder containing images with names specified by the metadata.  
The existing folder `example_images` contains the images for the example metadata

### (5) Run the python script  
`python merge-z-stack_and_stitch.py --dir [path to image folder] --excelfile [path to excel file] --IJpath [path to ImageJ excutable]`  
To run the example:  
`python merge-z-stack_and_stitch.py --dir example_images --excelfile metadata.xlsx --IJpath [path to ImageJ excutable]`  

Result files will be named :  `[Entity prefix]_FocusStitch.jpg`
