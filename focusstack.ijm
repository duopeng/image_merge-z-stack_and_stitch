cwd = call("java.lang.System.getProperty", "user.dir");
args = getArgument;
file_array=split(args," ");
//print(unique_prefix);

//open all images
num_open_img=0

for (i=0; i<file_array.length; i++) {
	print("opening: " + file_array[i]);
	run("Bio-Formats Importer", "open=" + file_array[i] + " color_mode=Default");
	wait(1000);
	run("Stack to RGB");
	wait(400);
	//open(file_array[i]);
	num_open_img++;
}

if (num_open_img>1) //focus stack if more than 1 images are open
{
	//z-project
	 wait(200);
	 print("opened: " + num_open_img + " images");
	 run("Images to Stack", "name=Stack title=[] use"); 
	 wait(500);
	 run("Z Project...", "start=1 stop="+num_open_img+" projection=[Min Intensity]");
	 
	 
	//save image
	run("Input/Output...", "jpeg="+100);
	saveAs("Jpeg", "stack"); // This will save into same subdirectory of midgut file 
	run("Close All"); // Take care that all images are closed 
}
else{
	//save image
	run("Input/Output...", "jpeg="+100);
	saveAs("Jpeg", "stack"); // This will save into same subdirectory of midgut file 
	run("Close All"); // Take care that all images are closed 
}

run("Quit")