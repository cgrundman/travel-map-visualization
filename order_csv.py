import pandas as pd


OLD_CSV = "Sehenswuerdigkeiten/sehenswuerdigkeiten.csv"
NEW_CSV = OLD_CSV.replace(".csv", "_new.csv")

df = pd.read_table(OLD_CSV, delimiter =",")

df = df.sort_values('latitude', ascending=False)

df = df.drop(columns='number')

df = df.reset_index(drop=True)

df.to_csv(NEW_CSV, sep=",")
