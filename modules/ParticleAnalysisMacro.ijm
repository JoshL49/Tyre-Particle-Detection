// Wait until the image has been loaded with the channels
run("Make Composite");

// Extract the base image name
imageName = getTitle();
dotIndex = indexOf(imageName, ".");
if (dotIndex > 0) {
    imageName = substring(imageName, 0, dotIndex); // Remove file extension
}

// Construct the channel names based on the opened channels, keeping the .tiff extension
channel1 = "C1-" + imageName + ".tiff";
channel2 = "C2-" + imageName + ".tiff";
channel3 = "C3-" + imageName + ".tiff";
channel4 = "C4-" + imageName + ".tiff";

// Split the channels into separate grayscale images
run("Split Channels");

run("Make Composite", "display=Color");
run("Channels Tool...");
run("Merge Channels...", "c1=" + channel1 + " c2=" + channel2 + " c3=" + channel3 + " c4=" + channel4);

// Convert image to 8-bit
run("8-bit");

// Apply a threshold
run("Threshold...");  // Opens the threshold dialog
setAutoThreshold("Otsu dark");  // Uses Otsu's method with a dark background
setOption("BlackBackground", false);  // Ensure black foreground, white background
run("Convert to Mask");  // Convert to a binary mask

// Invert the image
run("Invert");

// Set scale
run("Set Scale...", "distance=0.732525 known=1 unit=um");

// Set measurements to include Mean Gray Value
run("Set Measurements...", "area mean perimeter shape feret's diameter");

// Analyze particles and save the results
run("Analyze Particles...", "size=0-Infinity show=Overlay add");

// Add labels (if you want to label the particles)
run("Labels...", "color=red font=36 show");

// Make sure the directory exists
outputDir = "C:\\Users\\user\\PycharmProjects\\Tyre Particle Detection\\Processed_Images\\Winter\\P150\\4X";
File.makeDirectory(outputDir);  // Create the directory if it doesn't exist

// The name of the image file to save
outputImagePath = outputDir + imageName + "_processed_with_overlays.jpg";

// Save the image as a JPEG
wait(1000); // Wait 1 second before saving
saveAs("Jpeg", outputImagePath);
print("Processed image with overlays saved to: " + outputImagePath);

// Save results (CSV for particle analysis)
newFileName = "C:\\Users\\user\\PycharmProjects\\Tyre Particle Detection\\Tyre Particle Data\\" + imageName + ".csv";
saveAs("Results", newFileName);
print("Saved particle analysis results to: " + newFileName);

// Save the filename to a .txt file for Python to read
filenamePath = "C:\\Users\\user\\PycharmProjects\\Tyre Particle Detection\\filename.txt";
File.saveString(newFileName, filenamePath);
