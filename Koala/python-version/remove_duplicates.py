import pandas as pd

# Load the CSV file
df = pd.read_csv("./nn_data/datagen-50k.csv")

# Check if "pos" column exists
if "pos" not in df.columns:
    raise ValueError("The column 'pos' does not exist in the CSV.")

# Find duplicated "pos" values
duplicated_pos = df[df.duplicated(subset="pos", keep=False)]

# Show the duplicated rows
print("Duplicated 'pos' rows:")
print(duplicated_pos)

# Optionally, save to a new file
duplicated_pos.to_csv("./nn_data/cleaned_pos_rows.csv", index=False)
