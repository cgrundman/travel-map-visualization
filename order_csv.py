import pandas as pd

# Paths for CSV files
OLD_CSV = "Europe/europe_sites.csv" # old path
NEW_CSV = OLD_CSV.replace(".csv", "_new.csv") # new path

# Read the CSV file using pandas
df = pd.read_table(OLD_CSV, delimiter=",")

# Sort the DataFrame by the 'latitude' column in descending order
df = df.sort_values('latitude', ascending=False)

# Remove the 'number' column from the DataFrame
df = df.drop(columns='number')

# Reset the DataFrame index and drop the old index column
df = df.reset_index(drop=True)

# Write the cleaned and sorted DataFrame to a new CSV file
df.to_csv(NEW_CSV, sep=",", index=False)
