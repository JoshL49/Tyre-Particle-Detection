import subprocess
import sys
import os

# Make sure to set correct image paths before running
# DetectionV3.py - 241
# ParticleAnalysisMacro.ijm - 43
# Main.py - 21

# Ensure the correct virtual environment Python is used
venv_python = os.path.join(os.getenv('VIRTUAL_ENV'), 'Scripts', 'python.exe')

# Define the path to the modules folder
modules_folder = os.path.join(os.getcwd(), 'modules')

def run_imagej_and_detection():
    # Prompt user for the image filename
    image_filename = input("Enter the image filename (e.g., 013.tiff): ").strip()

    # Define the full image path (modify the folder structure as needed)
    image_folder = os.path.join(os.getcwd(), 'Semester 2 Samples (2)', 'Winter', 'P150', '4X')
    image_path = os.path.join(image_folder, image_filename)

    try:
        # Start process_imagej.py in the background with the image path as an argument
        print(f"Starting process_imagej.py with image: {image_path}")
        imagej_script = os.path.join(modules_folder, "process_imagej.py")
        imagej_process = subprocess.Popen([venv_python, imagej_script, image_path])

        # Wait for ImageJ to finish initialization
        print("Waiting for ImageJ to finish initializing...")
        imagej_process.wait()  # Waits until ImageJ is fully launched

        # After ImageJ is done, prompt the user to proceed
        proceed = input("ImageJ is open. Do you want to proceed with the detection? (yes/no): ").strip().lower()

        if proceed == "yes":
            # Run DetectionV3.py if the user agrees
            print("Running DetectionV4.py...")
            detection_script = os.path.join(modules_folder, "DetectionV3.py")
            subprocess.run([venv_python, detection_script], check=True)
            print("Detection script executed successfully.")
        else:
            print("Detection process aborted.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    while True:
        run_imagej_and_detection()
        # Ask if the user wants to run the process again
        run_again = input("Do you want to run the process again with a different image? (yes/no): ").strip().lower()
        if run_again != "yes":
            print("Exiting the program.")
            break

if __name__ == "__main__":
    main()
