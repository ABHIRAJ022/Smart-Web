import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("Generating synthetic health data...")

# 1. Create some sample training data
# Columns match your fields: BodyTemp, Smoke, Alcohol, Distance, Humidity, RoomTemp
data = {
    'body_temp': [36.5, 39.5, 37.0, 40.1, 36.8, 38.9, 36.2, 39.2],
    'smoke':     [200, 750,  150, 800,  300, 650,  180, 274],
    'alcohol':   [150, 600,  100, 700,  200, 500,  120, 338],
    'distance':  [100, 15,   150, 10,   120, 20,   140, 25],
    'humidity':  [40,  70,   45,  80,   50,  75,   42,  58.1],
    'room_temp': [22,  30,   21,  35,   24,  32,   23,  33.7],
    'label':     ['Normal', 'High Risk', 'Normal', 'High Risk', 'Normal', 'High Risk', 'Normal', 'High Risk']
}

df = pd.DataFrame(data)

# Features (X) and Target (y)
X = df.drop('label', axis=1)
y = df['label']

print("Training the Random Forest AI Model...")
# 2. Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 3. Save the trained model to a file
model_filename = 'health_model.pkl'
joblib.dump(model, model_filename)

print(f"✅ Success! AI Model saved as '{model_filename}' in the current directory.")