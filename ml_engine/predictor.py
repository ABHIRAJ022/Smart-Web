import pickle
import os
import pandas as pd
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier

# Path configuration
MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'disease_model.pkl')

# Define feature names globally to ensure order consistency
FEATURE_NAMES = ['bodyTemp', 'smoke', 'alcohol', 'distance', 'humidity', 'roomTemp']

def train_dummy_model():
    """Auto-trains a model if disease_model.pkl is missing."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    # Sample training data (Increased samples for slightly better stability)
    data = {
        'bodyTemp': [36.5, 39.5, 37.0, 40.1, 36.8, 38.9, 36.2, 39.2],
        'smoke':    [200,  750,  150,  800,  300,  650,  180,  274],
        'alcohol':  [150,  600,  100,  700,  200,  500,  120,  338],
        'distance': [100,  15,   150,  10,   120,  20,   140,  25],
        'humidity': [40,   70,   45,   80,   50,   75,   42,   58.1],
        'roomTemp': [22,   30,   21,   35,   24,   32,   23,   33.7],
        'label':    [0,    1,    0,    1,    0,    1,    0,    1]
    }
    df = pd.DataFrame(data)
    
    # Explicitly define X using FEATURE_NAMES to lock order
    X = df[FEATURE_NAMES]
    y = df['label']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    with open(MODEL_PATH, 'wb') as file:
        pickle.dump(model, file)
    print(f"✅ Model trained and saved at {MODEL_PATH}")

def load_model():
    if not os.path.exists(MODEL_PATH):
        train_dummy_model()
        
    try:
        with open(MODEL_PATH, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def predict_health_status(thingspeak_data):
    """
    Predicts health status based on IoT fields.
    Returns: String status for the Dashboard.
    """
    model = load_model()
    if not model:
        return "Model Error"

    try:
        # 1. Extract and convert with strict feature ordering
        # Using a list of values ensures scikit-learn gets the data in the right 'columns'
        current_features = [
            float(thingspeak_data.get('field1', 0)), # bodyTemp
            float(thingspeak_data.get('field2', 0)), # smoke
            float(thingspeak_data.get('field3', 0)), # alcohol
            float(thingspeak_data.get('field4', 0)), # distance
            float(thingspeak_data.get('field5', 0)), # humidity
            float(thingspeak_data.get('field6', 0))  # roomTemp
        ]
        
        # 2. Create DataFrame with explicit columns
        df = pd.DataFrame([current_features], columns=FEATURE_NAMES)
        
        # 3. Get Prediction and Probability
        prediction = model.predict(df)[0]
        # Optional: Get probability to see 'how sure' the AI is
        # probs = model.predict_proba(df)[0] 

        if prediction == 1:
            return "Critical Risk Detected"
        
        # Secondary logic: Even if the AI says 0, double-check extreme thresholds
        if float(thingspeak_data.get('field4', 100)) < 30:
            return "Risk: Fall Detected"

        return "Vitals Normal"
        
    except Exception as e:
        return f"Prediction Error: {str(e)}"