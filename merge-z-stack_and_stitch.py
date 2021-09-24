import argparse
import sys
import linecache
import os
import shutil
import subprocess

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_args():
    parser= MyParser(description='This script does XXX')
    parser.add_argument('--dir', default="", type=str)
    parser.add_argument('--list', default="", type=str)
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
        filename = config['list']

        #organize picture into folder stuctures
        with open(filename, "r") as filehandle:
            next(filehandle) #skip header
            for line in filehandle:
                filename = line.split("\t")[0].rstrip()
                gutname = line.split("\t")[1].rstrip()
                region = line.split("\t")[2].rstrip()
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
                    focus_cmd = f"cd {region_dir_path} && D:/Fiji.app/ImageJ-win64.exe -macro focusstack.ijm \"{file_list}\""
                    subprocess.call(focus_cmd, shell=True)
                    #move stacked img to the gut folder
                    shutil.copy2(os.path.join(region_dir_path,"stack.jpg"), os.path.join(entity_dir_path,f"{region_dir}_stack.jpg"))
                    #delete region folder
                    shutil.rmtree(region_dir_path)
                #stitch 
                print(f"stiching all regions of {entity_dir}\n")
                stitch_cmd = f"cd {dirname} && D:/Fiji.app/ImageJ-win64.exe -macro stitch.ijm \"{entity_dir}\""
                subprocess.call(stitch_cmd, shell=True)
                #move stitched img to the dir folder
                shutil.copy2(os.path.join(entity_dir_path,f"{entity_dir}_FocusStitch.jpg"), os.path.join(dirname,f"{entity_dir}_FocusStitch.jpg"))
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
