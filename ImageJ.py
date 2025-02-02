import imagej
import time
import os

# Start ImageJ in interactive mode
ij = imagej.init('sc.fiji:fiji', mode='interactive')

# Load the image
image_path = 'Raw Microscope Images\\WP40-1-4X-011.tiff'  # Update with your image path
imp = ij.io().open(image_path)

# Show the image in the ImageJ window
ij.ui().show(imp)

# Wait for a moment to ensure the image is fully loaded
time.sleep(2)  # Adjust the time if needed to make sure the image is ready

# Define the macro file path
macro_path = 'ParticleAnalysisMacro.ijm'  # Update with the correct path to your macro file

# Ensure that the macro file exists
if not os.path.exists(macro_path):
    print(f"Macro file not found: {macro_path}")
else:
    # Read and execute the macro
    with open(macro_path, 'r') as macro_file:
        macro_script = macro_file.read()

    # Run the macro using ImageJ's Python API
    ij.py.run_macro(macro_script)

# Wait for user input to close ImageJ
input("Press Enter to close ImageJ...")
