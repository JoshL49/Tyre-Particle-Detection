import subprocess
import sys
import os

# Ensure the correct virtual environment Python is used
venv_python = os.path.join(os.getenv('VIRTUAL_ENV'), 'Scripts', 'python.exe')

# Define the path to the modules folder
modules_folder = os.path.join(os.getcwd(), 'modules')

try:
    # Start process_imagej.py in the background (non-blocking)
    print("Starting process_imagej.py in the background...")
    imagej_script = os.path.join(modules_folder, "process_imagej.py")
    imagej_process = subprocess.Popen([venv_python, imagej_script])

    # Wait for ImageJ to finish initialization (ImageJ is now open)
    print("Waiting for ImageJ to finish initializing...")
    imagej_process.wait()  # Waits until ImageJ is fully launched

    # After ImageJ is done, prompt the user to proceed
    proceed = input("ImageJ is open. Do you want to proceed with the detection? (yes/no): ").strip().lower()

    if proceed == "yes":
        # Run DetectionV3.py if the user agrees
        print("Running DetectionV3.py...")
        detection_script = os.path.join(modules_folder, "DetectionV3.py")
        subprocess.run([venv_python, detection_script], check=True)
        print("Detection script executed successfully.")
    else:
        print("Detection process aborted.")

except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    sys.exit(1)
