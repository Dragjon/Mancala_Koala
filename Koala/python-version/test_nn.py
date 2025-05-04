import tensorflow as tf
import numpy as np
from mancala import *

# Load the saved model
model_path = "./nn_data/nn_model.keras"
print(f"Loading model from {model_path}")
model = tf.keras.models.load_model(model_path)

def encode_pos(game):
    encoded = []
    encoded.append(game.turn)
    for i in range(12):
        encoded.append(game.board[i])
    encoded.append(game.houses[0])
    encoded.append(game.houses[1])
    return encoded

# Encode input
game = Mancala()
encoded_input = np.array([encode_pos(game)], dtype=np.float32)  # shape (1, 15)

# Make prediction
predicted_score = model.predict(encoded_input)
print(f"Predicted score: {predicted_score[0][0]}")
