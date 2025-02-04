import sqlite3
import pandas as pd

# Load ImageJ CSV file
df = pd.read_csv("../Tyre Particle Data/WP40-1-4X-005.csv")

# Ask user for tyre particle IDs (e.g., manually determined from ImageJ)
tyre_particle_ids = [4, 3, 9, 5, 12, 16, 19, 24, 23, 22, 25, 31, 36]  # Example - replace with actual values

# Access the first column (no label) and filter based on the IDs
df.columns = ['ID'] + list(df.columns[1:])  # Rename the first column to 'ID'
tyre_particles = df[df['ID'].isin(tyre_particle_ids)]  # Filter based on the 'ID' column

# Identify non-tyre particles (i.e., those that are not in the tyre particle list)
non_tyre_particles = df[~df['ID'].isin(tyre_particle_ids)]  # Filter the particles that are not tyre particles

# --- Tyre Particles Database ---
# Connect to SQLite database for tyre particles (or create one)
conn = sqlite3.connect("../tyre_particles.db")
cursor = conn.cursor()

# Create table for tyre particles if it doesn't exist
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

# Insert selected tyre particles into the tyre particle database
for _, row in tyre_particles.iterrows():
    cursor.execute("""
    INSERT INTO TyreParticles (area, perimeter, circularity, feret, minferet, ar, round, solidity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (row["Area"], row["Perim."], row["Circ."], row["Feret"], row["MinFeret"], row["AR"], row["Round"], row["Solidity"]))

# Commit and close
conn.commit()
conn.close()
print("Tyre particle dimensions saved to tyre_particles.db!")

# --- Non-Tyre Particles Database ---
# Connect to SQLite database for non-tyre particles (or create one)
conn = sqlite3.connect("../non_tyre_particles.db")
cursor = conn.cursor()

# Create table for non-tyre particles if it doesn't exist
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

# Insert non-tyre particles into the non-tyre particle database
for _, row in non_tyre_particles.iterrows():
    cursor.execute("""
    INSERT INTO NonTyreParticles (area, perimeter, circularity, feret, minferet, ar, round, solidity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (row["Area"], row["Perim."], row["Circ."], row["Feret"], row["MinFeret"], row["AR"], row["Round"], row["Solidity"]))

# Commit and close
conn.commit()
conn.close()
print("Non-tyre particle dimensions saved to non_tyre_particles.db!")

# Optional: Check contents of both databases

# Connect to the tyre particles database
conn = sqlite3.connect('../tyre_particles.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM TyreParticles")
tyre_rows = cursor.fetchall()
print("Tyre Particles:")
for row in tyre_rows:
    print(row)
conn.close()

# Connect to the non-tyre particles database
conn = sqlite3.connect('../non_tyre_particles.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM NonTyreParticles")
non_tyre_rows = cursor.fetchall()
print("Non-Tyre Particles:")
for row in non_tyre_rows:
    print(row)
conn.close()
