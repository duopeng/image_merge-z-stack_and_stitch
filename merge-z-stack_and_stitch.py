import argparse
import sys
import linecache
import os
import shutil
import subprocess
import pandas as pd
import csv
from PIL import Image

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_args():
    parser= MyParser(description='This script does XXX')
    parser.add_argument('--dir', default="", type=str, help="path to a directory containing images")
    parser.add_argument('--excelfile', default="", type=str, help="excel file containing metadata, see github repo for details")
    parser.add_argument('--IJpath', default="", type=str, help="path to ImageJ executables")
    config = parser.parse_args()
    if len(sys.argv)==1: # print help message if arguments are not valid
        parser.print_help()
        sys.exit(1)
    return config

config = vars(parse_args())

#####################
##      main       ##
#####################    
def main():
    try: 
        dirname = config['dir']
        excelfile = config['excelfile']
        IJpath = config['IJpath']

        if not(excelfile.endswith("xlsx") or excelfile.endswith("xls")):
            sys.exit(f"Fatal error: {excelfile} is not an excel file")
        else:
            df = pd.read_excel(excelfile)

        #organize picture into folder stuctures
        for index, row in df.iterrows():
            filename = row['File_name']
            gutname = row['Entity']
            region = row['Region']
            #print(f"{dirname} {filename} {region}")

            #create subfolders
            filepath = os.path.join(dirname,filename)
            entity_dir_path = os.path.join(dirname,gutname)
            region_dir_path = os.path.join(dirname,gutname,region)
            if not os.path.isdir(entity_dir_path): # create subdir with gut name
                os.mkdir(entity_dir_path) 
            if not os.path.isdir(region_dir_path): #create subdir with region name
                os.mkdir(region_dir_path) 

            #check file existence and copyfiles to respective gut/region subfolders
            if os.path.isfile(filepath):
                #copy files in to gut/region subfolder
                dest_path = os.path.join(region_dir_path,filename)
                if not os.path.isfile(dest_path):
                    shutil.copy2(filepath, dest_path)
            else:
                sys.exit(f"Fatal error: {filename} could not be found in directory {dirname}")
                
        #start focus-stitching
        print("")
        entity_counter=0
        resize_records = []  # List to store resize information for CSV

        for entity_dir in os.listdir(dirname):
            entity_dir_path = os.path.join(dirname,entity_dir)
            if os.path.isdir(entity_dir_path):
                print(f"processing entity: {entity_dir}")
                for region_dir in os.listdir(entity_dir_path): #stack-focus all regions (subdirs)
                    print(f"focus-stacking region: {region_dir}")
                    region_dir_path = os.path.join(entity_dir_path,region_dir)
                    files = [ name for name in os.listdir(region_dir_path)]
                    file_list = " ".join(files)
                    focus_cmd = f"cd {region_dir_path} && {IJpath} -macro focusstack.ijm \"{file_list}\""
                    subprocess.call(focus_cmd, shell=True)
                    #move stacked img to the gut folder
                    shutil.copy2(os.path.join(region_dir_path,"stack.jpg"), os.path.join(entity_dir_path,f"{region_dir}_stack.jpg"))
                    #delete region folder
                    shutil.rmtree(region_dir_path)
                #stitch
                print(f"stiching all regions of {entity_dir}\n")
                ##check the number of images in the folder
                file_num = len([name for name in os.listdir(entity_dir_path) if os.path.isfile(os.path.join(entity_dir_path,name))])
                output_image_path = os.path.join(dirname, f"{entity_dir}_FocusStitch.jpg")

                if file_num == 1:
                    for thatonefile in os.listdir(entity_dir_path):
                        shutil.copy2(os.path.join(entity_dir_path,thatonefile), output_image_path)
                elif file_num == 0:
                    sys.exit(f"Fatal error during stitching: There is no focus-merged pictures in {entity_dir}")
                else:
                    stitch_cmd = f"cd {dirname} && {IJpath} -macro stitch.ijm \"{entity_dir}\""
                    subprocess.call(stitch_cmd, shell=True)
                    #move stitched img to the dir folder
                    shutil.copy2(os.path.join(entity_dir_path,f"{entity_dir}_FocusStitch.jpg"), output_image_path)

                # Smart resize: resize to width 2800 if original width > 3000
                print(f"Checking if resizing is needed for {entity_dir}_FocusStitch.jpg")
                resize_info = resize_image_if_needed(output_image_path, width_threshold=3000, target_width=2800)
                resize_records.append(resize_info)

                #delete gut folder
                shutil.rmtree(entity_dir_path)
                entity_counter+=1

        # Write resize information to CSV
        csv_path = os.path.join(dirname, "resize_info.csv")
        if resize_records:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['filename', 'original_width', 'original_height', 'resized_width', 'resized_height', 'scale', 'resized']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resize_records)
            print(f"\nResize information saved to: {csv_path}")

        print(f"All done!\nProcessed {entity_counter} entites.")

    except Exception  as e:
        print("Unexpected error:", str(sys.exc_info()))
        print("additional information:", e)
        PrintException()

##########################
## function definitions ##
##########################
def resize_image_if_needed(image_path, width_threshold=3000, target_width=2800):
    """
    Resize image to target_width if original width > width_threshold.
    Maintains aspect ratio and preserves quality.

    Args:
        image_path: Path to the image file
        width_threshold: Only resize if width > this value (default: 3000)
        target_width: Target width for resizing (default: 2800)

    Returns:
        dict: Dictionary with keys 'filename', 'original_width', 'original_height',
              'resized_width', 'resized_height', 'scale', 'resized' (bool)
    """
    result = {
        'filename': os.path.basename(image_path),
        'original_width': 0,
        'original_height': 0,
        'resized_width': 0,
        'resized_height': 0,
        'scale': 1.0,
        'resized': False
    }

    try:
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
            result['original_width'] = orig_w
            result['original_height'] = orig_h

            # Only resize if width exceeds threshold
            if orig_w > width_threshold:
                # Calculate new dimensions maintaining aspect ratio
                aspect_ratio = orig_h / orig_w
                new_w = target_width
                new_h = int(round(target_width * aspect_ratio))

                # Calculate scale (new/original)
                scale = new_w / float(orig_w)
                result['scale'] = scale
                result['resized_width'] = new_w
                result['resized_height'] = new_h
                result['resized'] = True

                print(f"  Resizing {os.path.basename(image_path)} from {orig_w}x{orig_h} to {new_w}x{new_h} (scale={scale:.6f})")

                # Resize using high-quality LANCZOS resampling
                resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Save with maximum quality, preserving DPI if available
                dpi = img.info.get("dpi")
                save_params = {
                    "format": "JPEG",
                    "quality": 100,
                    "subsampling": 0,
                    "optimize": True,
                }
                if dpi:
                    save_params["dpi"] = dpi

                resized_img.save(image_path, **save_params)
                print(f"  Resized and saved: {image_path}")
            else:
                # No resize needed, but keep original dimensions
                result['resized_width'] = orig_w
                result['resized_height'] = orig_h
                print(f"  Skipping resize for {os.path.basename(image_path)} (width {orig_w} <= {width_threshold})")

    except Exception as e:
        print(f"Warning: Could not resize {image_path}: {e}")

    return result

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

    
if __name__ == "__main__": main()    
