import sqlite3
import pandas as pd
from scipy.spatial import distance
import numpy as np

# Load new ImageJ CSV file (new particles)
new_df = pd.read_csv("Tyre Particle Data\\WP40-1-4X-006.csv")

# Load non-tyre particle data from the database
conn = sqlite3.connect("non_tyre_particles.db")
non_tyre_df = pd.read_sql_query("SELECT * FROM NonTyreParticles", conn)
conn.close()

# Load tyre particle data from the database
conn = sqlite3.connect("tyre_particles.db")
tyre_df = pd.read_sql_query("SELECT * FROM TyreParticles", conn)
conn.close()

# Convert to NumPy arrays for distance calculation
non_tyre_features = non_tyre_df.drop(columns=["id"]).values
tyre_features = tyre_df.drop(columns=["id"]).values
new_features = new_df[["Area", "Perim.", "Circ.", "Feret", "MinFeret", "AR", "Round", "Solidity"]].values

# Define feature columns in lowercase
feature_columns = ['area', 'perimeter', 'circularity', 'feret', 'minferet', 'ar', 'round', 'solidity']

threshold = 10  # Similarity threshold for matching

identified_tyre_particles = []
identified_non_tyre_particles = []

# Apply thresholds before distance calculation
filtered_particles = []
filtered_indices = []

for i, particle in enumerate(new_features):
    if len(particle) != len(feature_columns):
        print(f"Skipping particle {i + 1} due to missing features")
        continue

    area, perimeter, circularity, feret, minferet, ar, roundness, solidity = particle

    # Tyre particle conditions
    is_tyre = (
            area > 1000 and
            circularity < 0.8 and
            feret > 50 and
            1.2 <= ar <= 3 and
            roundness < 0.6 and
            solidity < 0.9
    )

    # Non-tyre particle conditions
    is_non_tyre = (
            area < 1000 or
            circularity > 0.8 or
            feret < 50 or
            ar < 1.2 or ar > 3 or
            roundness > 0.6 or
            solidity > 0.9
    )

    # If it meets tyre criteria, add to potential tyre list
    if is_tyre:
        filtered_particles.append(particle)
        filtered_indices.append(i + 1)  # Store particle number

    # If it meets non-tyre criteria, classify immediately
    if is_non_tyre:
        identified_non_tyre_particles.append(i + 1)

filtered_particles = np.array(filtered_particles)

# First, check for non-tyre particles
for i, new_particle in enumerate(new_features):
    distances = [distance.euclidean(new_particle, non_tyre) for non_tyre in non_tyre_features]
    if min(distances) < threshold:  # If a close match is found in non-tyre particles
        identified_non_tyre_particles.append(i + 1)  # Store particle number as non-tyre
        continue  # Skip this particle, as it's already identified as non-tyre

# Now, check for tyre particles (only particles not identified as non-tyre)
for i, new_particle in enumerate(new_features):
    if i + 1 not in identified_non_tyre_particles:  # Only check for particles not identified as non-tyre
        distances = [distance.euclidean(new_particle, tyre) for tyre in tyre_features]
        if min(distances) < threshold:  # If a close match is found in tyre particles
            identified_tyre_particles.append(i + 1)  # Store particle number as tyre

# Flag misidentified particles
misidentified_tyre_particles = [i for i in identified_tyre_particles if i not in identified_non_tyre_particles]
misidentified_non_tyre_particles = [i for i in identified_non_tyre_particles if i not in identified_tyre_particles]

# Print results
print(f"Identified tyre particles: {identified_tyre_particles}")
print(f"Identified non-tyre particles: {identified_non_tyre_particles}")
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
def transfer_particles(particle_ids, target_db_name, target_table):
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
        print(f"\nTransferring Particle ID: {particle_id}")
        print(row)

        # Ask if the particle should be transferred
        transfer = input(
            f"Should Particle {particle_id} be transferred to the {target_db_name} database? (yes/no): ").strip().lower()
        if transfer == "yes":
            cursor_target.execute(f"""
            INSERT INTO {target_table} (area, perimeter, circularity, feret, minferet, ar, round, solidity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (row["Area"], row["Perim."], row["Circ."], row["Feret"], row["MinFeret"], row["AR"], row["Round"],
                  row["Solidity"]))
            conn_target.commit()
            print(f"Particle {particle_id} transferred to the {target_db_name} database.")
        else:
            print(f"Particle {particle_id} not transferred.")

    # Close the database connection
    conn_target.close()


# Transfer the misidentified particles
if misidentified_particles:
    # Separate tyre and non-tyre particles for transfer
    non_tyre_particles_to_transfer = [p for p in misidentified_particles if p in misidentified_tyre_particles]
    tyre_particles_to_transfer = [p for p in misidentified_particles if p in misidentified_non_tyre_particles]

    # Transfer misidentified tyre particles to the non-tyre database
    if non_tyre_particles_to_transfer:
        transfer_particles(non_tyre_particles_to_transfer, "non_tyre", "NonTyreParticles")

    # Transfer misidentified non-tyre particles to the tyre database
    if tyre_particles_to_transfer:
        transfer_particles(tyre_particles_to_transfer, "tyre", "TyreParticles")

print("Identification and transfer complete!")
