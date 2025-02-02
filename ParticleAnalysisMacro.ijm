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
setThreshold(0, 150);
run("Convert to Mask");

// Set scale
run("Set Scale...", "distance=0.732525 known=1 unit=um");

// Analyze particles
run("Analyze Particles...", "size=0-Infinity show=Overlay");

run("Labels...", "color=pink font=36 show");

// Save results
newFileName = "C:\\Users\\user\\PycharmProjects\\Tyre Particle Detection\\Tyre Particle Data\\" + imageName + ".csv";
saveAs("Results", newFileName);
print("Saved to: " + newFileName);
