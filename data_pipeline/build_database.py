import pandas as pd
import sqlite3
import os

print("Downloading Global Space Launch Dataset...")
csv_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2019/2019-01-15/launches.csv"

# 1. Extract: Read directly from the URL into a Pandas DataFrame
df = pd.read_csv(csv_url)

print(f"Downloaded {len(df)} total global launches. Cleaning data...")

# 2. Feature Engineering: Create a cleaner "Agency/Company" column
def assign_agency(row):
    # 'state_code' IN = India, US = United States
    if row['state_code'] == 'IN':
        return 'ISRO'
    # Check if SpaceX is mentioned in the agency type or vehicle type
    elif 'SpaceX' in str(row['agency_type']) or 'SpaceX' in str(row['type']):
        return 'SpaceX'
    elif row['state_code'] == 'US':
        return 'NASA'
    # Everything else (Russia, ESA, China, etc.)
    return 'Other'

# Apply the logic to every row
df['dashboard_agency'] = df.apply(assign_agency, axis=1)

# Keep only the columns we need for our dashboard
final_df = df[['dashboard_agency', 'launch_year', 'type', 'category']].copy()

# Rename columns to be database-friendly
final_df.columns = ['agency', 'year', 'rocket_type', 'success_status']

# Standardize the success column (category O = Orbit/Success, F = Failure)
final_df['is_success'] = final_df['success_status'] == 'O'

print("Saving cleaned data to SQLite database...")

# 3. Load: Connect to SQLite Database
# Make sure it points to the backend folder
db_dir = os.path.join("..", "backend")
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

db_path = os.path.join(db_dir, "space_data.db")
conn = sqlite3.connect(db_path)

# Export Pandas DataFrame to SQL table named 'launches'
final_df.to_sql("launches", conn, if_exists="replace", index=False)
conn.close()

print(f"Success! Processed {len(final_df)} global records.")
print("Database saved to backend/space_data.db")