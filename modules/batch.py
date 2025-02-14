import os
import subprocess

# Ensure correct virtual environment Python
venv_python = os.path.join(os.getenv('VIRTUAL_ENV'), 'Scripts', 'python.exe')

# Define the absolute path to the image folder
image_folder = r"C:\Users\user\PycharmProjects\Tyre Particle Detection\Semester 2 Samples (2)\Winter\P150\4X"

# Correct path to the modules directory (explicitly define it)
modules_folder = r"C:\Users\user\PycharmProjects\Tyre Particle Detection\modules"


def process_image(image_filename):
    """Runs ImageJ and detection script on a single image."""
    image_path = os.path.join(image_folder, image_filename)

    # Check if the file exists
    if not os.path.isfile(image_path):
        print(f"[⚠️] Skipping {image_filename} (file not found at {image_path})")
        return

    print(f"[✅] Processing {image_filename}...")

    try:
        # Run ImageJ macro
        imagej_script = os.path.join(modules_folder, "process_imagej.py")
        subprocess.run([venv_python, imagej_script, image_path], check=True)

        # Run detection script
        detection_script = os.path.join(modules_folder, "batch_detection.py")
        subprocess.run([venv_python, detection_script], check=True)

        print(f"[✔] {image_filename} processed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"[❌] Error processing {image_filename}: {e}")


def main():
    """Batch process multiple images."""
    image_range = input("Enter the image range (e.g., 001-050): ").strip()

    # Parse user input for range
    try:
        start, end = map(int, image_range.split('-'))
    except ValueError:
        print("[❌] Invalid input. Use the format 001-050.")
        return

    print(f"[⏳] Processing images {start:03d} to {end:03d}...")

    for i in range(start, end + 1):
        image_filename = f"{i:03d}.tiff"
        image_path = os.path.join(image_folder, image_filename)

        # Log full path for debugging
        print(f"Checking for file: {image_path}")

        if os.path.isfile(image_path):
            process_image(image_filename)
        else:
            print(f"[⚠️] File not found: {image_path}")

    print("[✅] Batch processing completed!")


if __name__ == "__main__":
    main()
