import pandas as pd

# Paths for CSV files
OLD_CSV = "de/locations.csv" # old path
NEW_CSV = OLD_CSV.replace(".csv", "_new.csv") # new path

# Read the CSV file using pandas
df = pd.read_table(OLD_CSV, delimiter=",")

# Sort the DataFrame by the 'latitude' column in descending order
df = df.sort_values('latitude', ascending=False)

# Resort the columns
df = df[['submap','latitude','longitude','date','name']]

# Reset the DataFrame index and drop the old index column
df = df.reset_index(drop=True)

# Write the cleaned and sorted DataFrame to a new CSV file
df.to_csv(NEW_CSV, sep=",", index=False)
