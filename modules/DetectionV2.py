import subprocess
import sqlite3
import pandas as pd
from scipy.spatial import distance
import numpy as np
import os

# Step 2: Load the newly generated CSV file from ImageJ
# Make sure the new ImageJ CSV file is generated in the directory you expect
new_df = pd.read_csv("../Tyre Particle Data/WP40-1-4X-011.csv")

# Step 3: Continue with your original code to work with databases and identify particles
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
    'non_tyre': {
        'area_max': 1000, 'circularity_min': 0.8, 'feret_max': 50,
        'ar_max': 1.2, 'ar_min': 3, 'roundness_min': 0.6, 'solidity_min': 0.9
    }
}

threshold_score = 4  # Particles need a score of 4 or more to be classified as tyre

identified_tyre_particles = []
identified_non_tyre_particles = []


# Function to calculate a score based on matching conditions
def calculate_score(particle, conditions):
    score = 0
    area, perimeter, circularity, feret, minferet, ar, roundness, solidity = particle

    # Tyre conditions (points for each match)
    if conditions['tyre']['area_min'] < area < conditions['tyre']['area_max']:
        score += 1
    if conditions['tyre']['circularity_max'] > circularity:
        score += 1
    if conditions['tyre']['feret_min'] < feret:
        score += 1
    if conditions['tyre']['ar_min'] <= ar <= conditions['tyre']['ar_max']:
        score += 1
    if conditions['tyre']['roundness_max'] > roundness:
        score += 1
    if conditions['tyre']['solidity_max'] > solidity:
        score += 1

    return score


# Check each particle and calculate its score
for i, particle in enumerate(new_features):
    score = calculate_score(particle, conditions)

    if score >= threshold_score:
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

import os

# Define the CSV file name
csv_filename = "../Distributions/WP40-4X/WP40-4X-1.csv"

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
