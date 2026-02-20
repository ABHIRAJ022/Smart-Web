import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

print("Generating synthetic health data...")

# Added rows where ONLY ONE thing goes wrong at a time
data = {
    'body_temp': [36.5, 39.5, 37.0, 40.1, 36.8, 38.9, 36.2, 39.2,  36.5,  36.5,  36.5],
    'smoke':     [200,  750,  150,  800,  300,  650,  180,  274,  850,   150,   150],
    'alcohol':   [150,  600,  100,  700,  200,  500,  120,  338,  150,   750,   150],
    'distance':  [100,  15,   150,  10,   120,  20,   140,  25,   100,   100,   10],
    'humidity':  [40,   70,   45,   80,   50,   75,   42,   58.1, 40,    40,    40],
    'room_temp': [22,   30,   21,   35,   24,   32,   23,   33.7, 22,    22,    22],
    'label':     ['Normal', 'High Risk', 'Normal', 'High Risk', 'Normal', 'High Risk', 'Normal', 'High Risk', 'High Risk', 'High Risk', 'High Risk']
}
# Notice the last 3 rows: 
# Row 9: ONLY Smoke is high (850) -> High Risk
# Row 10: ONLY Alcohol is high (750) -> High Risk
# Row 11: ONLY Distance is low (10 - Fall) -> High Risk

df = pd.DataFrame(data)

X = df.drop('label', axis=1)
y = df['label']

print("Training the Random Forest AI Model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

model_filename = 'health_model.pkl'
joblib.dump(model, model_filename)

print(f"✅ Success! Smarter AI Model saved as '{model_filename}'.")