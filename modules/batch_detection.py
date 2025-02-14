import subprocess
import sqlite3
import pandas as pd
from scipy.spatial import distance
import numpy as np
import os

output_txt = "C:\\Users\\user\\PycharmProjects\\Tyre Particle Detection\\filename.txt"

# Read the CSV filename from output.txt
with open(output_txt, "r") as file:
    csv_filename = file.read().strip()

# Display the CSV filename being opened
print(f"Opening CSV file: {csv_filename}")

# Ensure the file exists before reading
if not os.path.exists(csv_filename):
    raise FileNotFoundError(f"CSV file not found: {csv_filename}")

# Load the CSV
new_df = pd.read_csv(csv_filename)
print(new_df.head())  # Display first few rows for verification

# Define Solidity Threshold
solidity_threshold = 0.75

# Filter particles based on Solidity
filtered_particles = new_df[new_df["Solidity"] >= solidity_threshold]
non_tyre_particles = new_df[new_df["Solidity"] < solidity_threshold]

# Print summary
print(f"Filtered out {len(non_tyre_particles)} particles with solidity < {solidity_threshold}")

# Proceed only with filtered_particles
df = filtered_particles

# Create the TyreParticles table if it doesn't exist
conn = sqlite3.connect("../tyre_particles.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS TyreParticles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area REAL,
        perimeter REAL,
        circularity REAL,
        feret REAL,
        minferet REAL,
        ar REAL,
        round REAL,
        solidity REAL
    )
""")
conn.commit()  # Commit the changes after table creation
conn.close()

# Load tyre particle data from the database
conn = sqlite3.connect("../tyre_particles.db")
tyre_df = pd.read_sql_query("SELECT * FROM TyreParticles", conn)
conn.close()

# Convert to NumPy arrays for distance calculation
tyre_features = tyre_df.drop(columns=["id"]).values
new_features = new_df[["Area", "Perim.", "Circ.", "Feret", "MinFeret", "AR", "Round", "Solidity"]].values

# Define tyre and non-tyre conditions (based on feature ranges)
conditions = {
    'tyre': {
        'area_min': 1000, 'area_max': float('inf'),
        'circularity_max': 0.8, 'feret_min': 50,
        'ar_min': 1.2, 'ar_max': 3, 'roundness_max': 0.6, 'solidity_max': 0.9
    },
}

threshold_score = 4  # Particles need a score of 4 or more to be classified as tyre

similarity_threshold = 1.5  # Maximum distance for classification as tyre (smaller means stricter)

identified_tyre_particles = []

# Function to calculate a score based on matching conditions
def calculate_score(particle, conditions):
    score = 0
    if conditions['area_min'] <= particle[0] <= conditions['area_max']:
        score += 1
    if particle[2] <= conditions['circularity_max']:
        score += 1
    if particle[3] >= conditions['feret_min']:
        score += 1
    if conditions['ar_min'] <= particle[5] <= conditions['ar_max']:
        score += 1
    if particle[6] <= conditions['roundness_max']:
        score += 1
    if particle[7] <= conditions['solidity_max']:
        score += 1
    return score

# Function to classify based on similarity
def classify_by_similarity(particle, tyre_features, similarity_threshold):
    tyre_dist = np.mean([distance.euclidean(particle.flatten(), t.flatten()) for t in tyre_features])

    if tyre_dist < similarity_threshold:
        return 'Tyre'
    else:
        return 'Unknown'


# Check each particle
for i, particle in enumerate(new_features):
    score = calculate_score(particle, conditions['tyre'])

    if score >= threshold_score:
        identified_tyre_particles.append(i + 1)
    else:
        # Use similarity-based classification
        classification = classify_by_similarity(particle, tyre_features, similarity_threshold)
        if classification == "Tyre":
            identified_tyre_particles.append(i + 1)

# Print the identified particles
print(f"Identified tyre particles: {identified_tyre_particles}")

# Automatically save new tyre particles to the TyreParticles database
conn = sqlite3.connect("../tyre_particles.db")
cursor = conn.cursor()

# Insert identified tyre particles into the database
for particle_id in identified_tyre_particles:
    row = new_df.iloc[particle_id - 1]  # Get the corresponding row
    cursor.execute("""
    INSERT INTO TyreParticles (area, perimeter, circularity, feret, minferet, ar, round, solidity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (row["Area"], row["Perim."], row["Circ."], row["Feret"], row["MinFeret"], row["AR"], row["Round"], row["Solidity"]))
    conn.commit()
    print(f"Particle {particle_id} saved to the TyreParticles database.")

# Close the database connection
conn.close()

# Define a new CSV file to save the identified tyre particles
output_csv_filename = "WP40-4X-TEST.csv"

# Automatically save new tyre particles to the new CSV
save_to_csv = True  # Automatically set to True
if save_to_csv:
    # Filter new tyre particles from the dataset
    new_tyre_particles = new_df.iloc[[p - 1 for p in identified_tyre_particles]]

    # Check if the file exists to determine whether to write headers
    file_exists = os.path.isfile(output_csv_filename)

    # Save new tyre particles to the new CSV, appending if the file already exists
    new_tyre_particles.to_csv(output_csv_filename, mode='a', header=not file_exists, index=False)

    print(f"New tyre particles saved to {output_csv_filename}.")
