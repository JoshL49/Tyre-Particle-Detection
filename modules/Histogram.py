# Read the filename from the text file
with open("../csv_filename.txt", "r") as f:
    csv_filename = f.read().strip()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv(csv_filename)

# Extract size data
size = df["Feret"]  # Change "Feret" to the actual column name you are using

# Define logarithmic bins (10^0 to 10^2.5 µm)
bin_edges = np.logspace(np.log10(0.1), np.log10(1000), num=15)  # Adjust num for resolution

# Create histogram with log bins
plt.figure(figsize=(8, 6))
plt.hist(size, bins=bin_edges, alpha=0.5, label="P40", color="blue", edgecolor="black")
any_graph_plotted = True

# If no graph is plotted, notify the user
if not any_graph_plotted:
    print("No graphs were selected. Exiting plot...")
    plt.close()
else:
    # Log scale for better visualisation
    plt.xscale("log")
    plt.yscale("log")

    # Labels
    plt.xlabel("Particle Size (µm)")
    plt.ylabel("Frequency")
    plt.title("W-1-4X Size Distribution")

    # Add legend if any graph is plotted
    plt.legend()

    # Customise grid lines
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.3)  # Adjust alpha for opacity

    # Save the figure
    plt.savefig("C:\\Users\\user\\OneDrive - University of Strathclyde\\Semester 2 Samples (2)\\Winter\\W-1-4x Size Distribution.png", dpi=300, bbox_inches='tight')
    plt.show()
