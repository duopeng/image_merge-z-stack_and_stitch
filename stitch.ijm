in_folder = getArgument;

gut_name_array=split(in_folder,"/");
gut_name=gut_name_array[gut_name_array.length-1];
out_folder=in_folder

//stitch
GridStitch(in_folder, out_folder, gut_name);
run("Quit");


function GridStitch(input_folder, output_folder, output_filename) {
	run("Grid/Collection stitching", "type=[Unknown position] order=[All files in directory] directory=" + input_folder);
	run("Stack to RGB");
	//run("8-bit");
	run("Input/Output...", "jpeg="+100);
	saveAs("Jpeg", output_folder +"/" + output_filename + "_FocusStitch");
	close();
}



