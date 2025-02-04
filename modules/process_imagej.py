import imagej
import time
import os

# Start ImageJ in interactive mode
ij = imagej.init('sc.fiji:fiji', mode='interactive')

# Get the absolute path of the current script
base_path = os.path.dirname(os.path.abspath(__file__))  # The 'modules' directory

# Now, go one level up and access 'Raw Microscope Images'
image_folder = os.path.join(base_path, '..', 'Raw Microscope Images')

# Construct the path to the image
image_path = os.path.join(image_folder, 'WP40-1-4X-012.tiff')

# Check if the file exists before attempting to open it
if not os.path.isfile(image_path):
    print("Error: File does not exist:", image_path)
else:
    print("File exists, proceeding to open:", image_path)
    # ImageJ code to open the image
    imp = ij.io().open(image_path)

# Show the image in the ImageJ window
ij.ui().show(imp)

# Wait for a moment to ensure the image is fully loaded
time.sleep(2)  # Adjust the time if needed to make sure the image is ready

# Define the absolute path for the macro file in the 'modules' folder
macro_path = os.path.join(base_path, 'ParticleAnalysisMacro.ijm')

# Ensure that the macro file exists
if not os.path.exists(macro_path):
    print(f"Macro file not found: {macro_path}")
else:
    # Read and execute the macro
    with open(macro_path, 'r') as macro_file:
        macro_script = macro_file.read()

    # Run the macro using ImageJ's Python API
    ij.py.run_macro(macro_script)

# At this point, ImageJ is still open and the user can interact with it
print("ImageJ is running and the image is ready.")
