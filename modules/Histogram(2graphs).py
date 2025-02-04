import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load data
df1 = pd.read_csv("C:\\Users\\user\\OneDrive - University of Strathclyde\\Semester 2 Samples (2)\\Summer\\P150\\4X\\SP150-1-4X Results.csv")
df2 = pd.read_csv("C:\\Users\\user\\OneDrive - University of Strathclyde\\Semester 2 Samples (2)\\Winter\\P150\\4X\\P150-1-4X Results.csv")


# Extract size data
size1 = df1["Feret"]  # Change "Feret" to the actual column name you are using
size2 = df2["Feret"]

# Define logarithmic bins (10^0 to 10^2.5 µm)
bin_edges = np.logspace(np.log10(0.1), np.log10(1000), num=15)  # Adjust num for resolution

# Ask user which graphs to plot
print("Select the graphs to display:")
print("1. SP150")
print("2. WP150")
print("3. All")

# Get user input
graph_choice = input("Enter the number of the graph(s) you want to see (comma separated for multiple): ")

# Convert input to a list of integers
selected_graphs = [int(choice.strip()) for choice in graph_choice.split(',')]

# Create histogram with log bins
plt.figure(figsize=(8, 6))

# Flag to check if any graphs are plotted
any_graph_plotted = False

# Plot selected graphs based on user input
if 1 in selected_graphs:
    plt.hist(size1, bins=bin_edges, alpha=0.5, label="SP150", color="blue", edgecolor="black")
    any_graph_plotted = True
if 2 in selected_graphs:
    plt.hist(size2, bins=bin_edges, alpha=0.5, label="WP150", color="red", edgecolor="black")
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
    plt.title("SWP150-1-4X Size Distribution")

    # Add legend if any graph is plotted
    plt.legend()

    # Customise grid lines
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.3)  # Adjust alpha for opacity

    # Save the figure
    plt.savefig("C:\\Users\\user\\OneDrive - University of Strathclyde\\Semester 2 Samples (2)\\SWP150-1-4x Size Distribution.png", dpi=300, bbox_inches='tight')
    plt.show()
