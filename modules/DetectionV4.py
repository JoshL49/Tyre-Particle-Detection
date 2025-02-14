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

#Define Solidity Threshold
solidity_threshold = 0.75

# Filter particles based on Solidity
filtered_particles = new_df[new_df["Solidity"] >= solidity_threshold]
non_tyre_particles = new_df[new_df["Solidity"] < solidity_threshold]

# Print summary
print(f"Filtered out {len(non_tyre_particles)} particles with solidity < {solidity_threshold}")

# Proceed only with filtered_particles
df = filtered_particles

# Create the NonTyreParticles table if it doesn't exist
conn = sqlite3.connect("../non_tyre_particles.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS NonTyreParticles (
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

# Load non-tyre particle data from the database
conn = sqlite3.connect("../non_tyre_particles.db")
non_tyre_df = pd.read_sql_query("SELECT * FROM NonTyreParticles", conn)
conn.close()

# Load tyre particle data from the database
conn = sqlite3.connect("../tyre_particles.db")
tyre_df = pd.read_sql_query("SELECT * FROM TyreParticles", conn)
conn.close()

# Convert to NumPy arrays for distance calculation
non_tyre_features = non_tyre_df.drop(columns=["id"]).values
tyre_features = tyre_df.drop(columns=["id"]).values
new_features = new_df[["Area", "Perim.", "Circ.", "Feret", "MinFeret", "AR", "Round", "Solidity"]].values

# Define feature columns in lowercase
feature_columns = ['area', 'perimeter', 'circularity', 'feret', 'minferet', 'ar', 'round', 'solidity']

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
identified_non_tyre_particles = []

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
def classify_by_similarity(particle, tyre_features, non_tyre_features, similarity_threshold):
    # Ensure both are flattened to 1D vectors
    tyre_dist = np.mean([distance.euclidean(particle.flatten(), t.flatten()) for t in tyre_features])
    non_tyre_dist = np.mean([distance.euclidean(particle.flatten(), nt.flatten()) for nt in non_tyre_features])

    if tyre_dist < similarity_threshold:
        return 'Tyre'
    elif non_tyre_dist < similarity_threshold:
        return 'Non-Tyre'
    else:
        return 'Unknown'


# Check each particle
for i, particle in enumerate(new_features):
    score = calculate_score(particle, conditions['tyre'])

    if score >= threshold_score:
        identified_tyre_particles.append(i + 1)
    else:
        # Use similarity-based classification
        classification = classify_by_similarity(particle, tyre_features, non_tyre_features, similarity_threshold)
        if classification == "tyre":
            identified_tyre_particles.append(i + 1)
        else:
            identified_non_tyre_particles.append(i + 1)

# Print the identified particles
print(f"Identified tyre particles: {identified_tyre_particles}")
print(f"Identified non-tyre particles: {identified_non_tyre_particles}")

# Flag misidentified particles
misidentified_tyre_particles = [i for i in identified_tyre_particles if i not in identified_non_tyre_particles]
misidentified_non_tyre_particles = [i for i in identified_non_tyre_particles if i not in identified_tyre_particles]

print(f"Misidentified tyre particles: {misidentified_tyre_particles}")
print(f"Misidentified non-tyre particles: {misidentified_non_tyre_particles}")

# Ask if there are any misidentified particles and get the particle IDs
misidentified_particles = []
if misidentified_tyre_particles or misidentified_non_tyre_particles:
    response = input("Are there any misidentified particles? (yes/no): ").strip().lower()
    if response == "yes":
        # Ask for particle numbers to transfer
        misidentified_str = input("Enter the misidentified particle numbers, separated by commas: ").strip()
        misidentified_particles = list(map(int, misidentified_str.split(',')))

# Function to transfer particles to the correct database
def transfer_particles(particle_ids, target_db_name, target_table, auto_transfer=False):
    # Connect to the target database
    conn_target = sqlite3.connect(f"{target_db_name}.db")
    cursor_target = conn_target.cursor()

    # Ensure the table exists
    cursor_target.execute(f"""
    CREATE TABLE IF NOT EXISTS {target_table} (
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

    # Transfer particles to the target table
    for particle_id in particle_ids:
        row = new_df.iloc[particle_id - 1]  # Get the corresponding row

        if auto_transfer:
            transfer = "yes"
        else:
            print(f"\nTransferring Particle ID: {particle_id}")
            print(row)
            transfer = input(f"Should Particle {particle_id} be transferred to the {target_db_name} database? (yes/no): ").strip().lower()

        if transfer == "yes":
            cursor_target.execute(f"""
            INSERT INTO {target_table} (area, perimeter, circularity, feret, minferet, ar, round, solidity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (row["Area"], row["Perim."], row["Circ."], row["Feret"], row["MinFeret"], row["AR"], row["Round"], row["Solidity"]))
            conn_target.commit()
            print(f"Particle {particle_id} transferred to the {target_db_name} database.")
        else:
            print(f"Particle {particle_id} not transferred.")

    # Close the database connection
    conn_target.close()

# Ask if the user wants to transfer all misidentified particles at once
auto_transfer_all = False
if misidentified_particles:
    auto_response = input("Do you want to transfer all misidentified particles automatically? (yes/no): ").strip().lower()
    if auto_response == "yes":
        auto_transfer_all = True

# Transfer the misidentified particles
if misidentified_particles:
    # Separate tyre and non-tyre particles for transfer
    non_tyre_particles_to_transfer = [p for p in misidentified_particles if p in misidentified_tyre_particles]
    tyre_particles_to_transfer = [p for p in misidentified_particles if p in misidentified_non_tyre_particles]

    # Transfer misidentified tyre particles to the non-tyre database
    if non_tyre_particles_to_transfer:
        transfer_particles(non_tyre_particles_to_transfer, "non_tyre", "NonTyreParticles", auto_transfer_all)

    # Transfer misidentified non-tyre particles to the tyre database
    if tyre_particles_to_transfer:
        transfer_particles(tyre_particles_to_transfer, "tyre", "TyreParticles", auto_transfer_all)

print("Identification and transfer complete!")

# Define the CSV file name
csv_filename = "../Distributions/WP150-4X/WP150-4X-1.csv"

with open("../csv_filename.txt", "w") as f:
    f.write(csv_filename)

# Ask if the user wants to save new tyre particles to a CSV
save_to_csv = input("Do you want to save the new tyre particles to a CSV? (yes/no): ").strip().lower()

if save_to_csv == "yes":
    # Filter new tyre particles from the dataset
    new_tyre_particles = new_df.iloc[[p - 1 for p in identified_tyre_particles]]

    # Check if the file exists to determine whether to write headers
    file_exists = os.path.isfile(csv_filename)

    # Save new tyre particles to the CSV, appending if the file already exists
    new_tyre_particles.to_csv(csv_filename, mode='a', header=not file_exists, index=False)

    print(f"New tyre particles saved to {csv_filename}.")
else:
    print("Tyre particles were not saved to a CSV.")

# Define the CSV file name
tyre_particles_csv = "tyre_particles.csv"

# Extract the identified tyre particles based on their indices (adjust as needed)
identified_tyre_particles = new_df.iloc[identified_tyre_particles]

# Append the identified particles to the CSV, creating a new file if it doesn't exist
identified_tyre_particles.to_csv(tyre_particles_csv, mode='a', header=not os.path.exists(tyre_particles_csv), index=False)

print(f"Identified tyre particles saved to {tyre_particles_csv}.")
