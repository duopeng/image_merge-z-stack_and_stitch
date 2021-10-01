import argparse
import sys
import linecache
import os
import shutil
import subprocess
import pandas as pd

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
                if file_num == 1:
                    for thatonefile in os.listdir(entity_dir_path):
                        shutil.copy2(os.path.join(entity_dir_path,thatonefile), os.path.join(f"{entity_dir}_FocusStitch.jpg"))
                elif file_num == 0:
                    sys.exit(f"Fatal error during stitching: There is no focus-merged pictures in {entity_dir}")
                else:
                    stitch_cmd = f"cd {dirname} && {IJpath} -macro stitch.ijm \"{entity_dir}\""
                    subprocess.call(stitch_cmd, shell=True)
                    #move stitched img to the dir folder
                    shutil.copy2(os.path.join(entity_dir_path,f"{entity_dir}_FocusStitch.jpg"), os.path.join(f"{entity_dir}_FocusStitch.jpg"))
                #delete gut folder    
                shutil.rmtree(entity_dir_path)
                entity_counter+=1

        print(f"All done!\nProcessed {entity_counter} entites.")

    except Exception  as e:
        print("Unexpected error:", str(sys.exc_info()))
        print("additional information:", e)
        PrintException()

##########################
## function definitions ##
##########################
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

    
if __name__ == "__main__": main()    
