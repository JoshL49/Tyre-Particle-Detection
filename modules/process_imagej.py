import imagej
import time
import os
import sys

# Start ImageJ in interactive mode
ij = imagej.init('sc.fiji:fiji', mode='interactive')

# Check if an image path was provided
if len(sys.argv) < 2:
    print("Error: No image path provided.")
    sys.exit(1)

# Get the image path from command-line arguments
image_path = sys.argv[1]

# Check if the file exists before attempting to open it
if not os.path.isfile(image_path):
    print("Error: File does not exist:", image_path)
    sys.exit(1)

print("File exists, proceeding to open:", image_path)
# Open the image in ImageJ
imp = ij.io().open(image_path)

# Show the image in the ImageJ window
ij.ui().show(imp)

# Wait to ensure the image is fully loaded
time.sleep(2)

# Get the absolute path of the current script (assumes this script is inside 'modules')
base_path = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path for the macro file in the 'modules' folder
macro_path = os.path.join(base_path, 'ParticleAnalysisMacro.ijm')

# Ensure that the macro file exists
if not os.path.exists(macro_path):
    print(f"Macro file not found: {macro_path}")
    sys.exit(1)

# Read and execute the macro
with open(macro_path, 'r') as macro_file:
    macro_script = macro_file.read()

# Run the macro using ImageJ's Python API
ij.py.run_macro(macro_script)

print("ImageJ is running and the image is ready.")
