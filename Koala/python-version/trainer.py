def parseStr(opstr):
    encoded = []
    parts = opstr.split()
    encoded.append(int(parts[0]))
    for x in parts[1].split("-"):
        encoded.append(int(x))
    for x in parts[2].split("+"):
        encoded.append(int(x))
    return encoded

import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np

# Load the CSV file
df = pd.read_csv("./nn_data/cleaned_pos_rows.csv")

# Ensure required columns exist
if "pos" not in df.columns or "score" not in df.columns:
    raise ValueError("CSV must contain 'pos' and 'score' columns.")

# Convert 'pos' column to list of strings
pos_list__str = df["pos"].astype(str).tolist()

# Convert 'score' column to list of numbers (floats)
score_list = pd.to_numeric(df["score"], errors='coerce').dropna().tolist()

print("Loaded", len(pos_list__str), "positions and", len(score_list), "scores.")

# Ensure lengths match
assert len(pos_list__str) == len(score_list), "Mismatch in data lengths."

# Encode positions
encoded = []
print("Encoding strings...")
for s in pos_list__str:
    encoded.append(parseStr(s))

# Combine and shuffle data
print("Shuffling data...")
combined = list(zip(encoded, score_list))
np.random.shuffle(combined)
encoded_shuffled, score_shuffled = zip(*combined)

# Convert to NumPy arrays
X = np.array(encoded_shuffled, dtype=np.float32)
y = np.array(score_shuffled, dtype=np.float32).reshape(-1, 1)

# Define model with tanh in output layer
model = Sequential([
    Dense(8, input_shape=(15,), activation='relu'),
    Dense(1, activation='tanh')  # Output now constrained to [-1, 1]
])

print("Compiling model")
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

print("Training")
model.fit(X, y, epochs=120, batch_size=16384, verbose=1)

# Save model
save_path = "./nn_data/nn_model.keras"
print(f"Saving model to {save_path}")
model.save(save_path)
