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

# Create the NonTyreParticles table if it doesn't exist
conn = sqlite3.connect("../non_tyre_particles.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS NonTyreParticles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area REAL,
        mean REAL,
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
        mean REAL,
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
new_features = new_df[["Area", "Mean", "Perim.", "Circ.", "Feret", "MinFeret", "AR", "Round", "Solidity"]].values

# Define feature columns in lowercase
feature_columns = ['area', 'mean', 'perimeter', 'circularity', 'feret', 'minferet', 'ar', 'round', 'solidity']

print(new_df.columns)  # This will show you the order of the columns

# Define tyre and non-tyre conditions (based on feature ranges)
conditions = {
    'tyre': {
        'area_min': 1000, 'area_max': float('inf'),
        'circularity_max': 0.8, 'feret_min': 50,
        'ar_min': 1.2, 'ar_max': 3, 'roundness_max': 0.6, 'solidity_max': 0.9
    },
}

threshold_score = 5  # Particles need a score of 4 or more to be classified as tyre

similarity_threshold = 1.5  # Maximum distance for classification as tyre (smaller means stricter)

# Define a minimum solidity threshold to ignore transparent particles
solidity_threshold = 0.8  # Adjust based on your data

# Define the Mean Gray Value threshold
mean_gray_threshold = 200  # Adjust as needed

identified_tyre_particles = []
identified_non_tyre_particles = []


# Function to calculate a score based on matching conditions
def calculate_score(particle, conditions):
    score = 0
    if conditions['area_min'] <= particle[0] <= conditions['area_max']:
        score += 1
    if particle[3] <= conditions['circularity_max']:
        score += 1
    if particle[5] >= conditions['feret_min']:
        score += 1
    if conditions['ar_min'] <= particle[6] <= conditions['ar_max']:
        score += 1
    if particle[7] <= conditions['roundness_max']:
        score += 1
    if particle[8] <= conditions['solidity_max']:
        score += 1
    return score


# Function to classify particles based on Solidity threshold
def classify_by_solidity(particle, solidity_threshold):
    print(f"Particle data: {particle}")  # Print the whole particle array for inspection
    solidity = particle[8]  # Index 8 is 'Solidity'
    print(f"Checking particle with solidity: {solidity}")  # Print the specific 'solidity' value
    if solidity < solidity_threshold:
        return "non_tyre"
    return "potential_tyre"

# Function to classify based on similarity to known tyre/non-tyre particles
def classify_by_similarity(particle, tyre_features, non_tyre_features, similarity_threshold):
    particle = np.array(particle).reshape(1, -1)

    # Calculate Euclidean distance to known tyre and non-tyre particles
    tyre_dist = np.mean([distance.euclidean(particle, t) for t in tyre_features]) if len(tyre_features) > 0 else float(
        'inf')
    non_tyre_dist = np.mean([distance.euclidean(particle, n) for n in non_tyre_features]) if len(
        non_tyre_features) > 0 else float('inf')

    # If the Euclidean distance to tyre features is smaller than non-tyre features and below the similarity threshold, classify as tyre
    if tyre_dist < non_tyre_dist and tyre_dist < similarity_threshold:
        return "tyre"
    return "non_tyre"

# Process each particle
for i, particle in enumerate(new_features):
    # First classify by Solidity
    classification = classify_by_solidity(particle, solidity_threshold)

    if classification == "non_tyre":
        identified_non_tyre_particles.append(i + 1)  # Mark as non-tyre if it failed the solidity threshold
    else:
        # If potential tyre, calculate the score using the other thresholds
        score = calculate_score(particle, conditions['tyre'])

        if score >= threshold_score:
            # Now apply similarity-based classification if the score passes
            similarity_classification = classify_by_similarity(particle, tyre_features, non_tyre_features,
                                                               similarity_threshold)
            if similarity_classification == "tyre":
                identified_tyre_particles.append(i + 1)  # Mark as tyre if it matches the similarity criteria
            else:
                identified_non_tyre_particles.append(i + 1)  # Otherwise, mark as non-tyre
        else:
            identified_non_tyre_particles.append(i + 1)  # Mark as non-tyre if the score is insufficient

# Output the results
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
        mean REAL,
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

with open