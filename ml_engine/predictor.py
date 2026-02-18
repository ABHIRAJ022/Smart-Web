import pickle
import os
import pandas as pd
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier

# Path to your ML model
MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'disease_model.pkl')

def train_dummy_model():
    """Auto-trains a model if disease_model.pkl is missing."""
    print("Model not found. Training and saving a new disease_model.pkl...")
    
    # 1. Create the ml_models directory if it doesn't exist
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    # 2. Sample training data (0 = Normal, 1 = Critical Risk)
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
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    # 3. Train the Random Forest AI model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 4. Save the model using pickle
    with open(MODEL_PATH, 'wb') as file:
        pickle.dump(model, file)
    print(f"✅ Model saved successfully at {MODEL_PATH}")

def load_model():
    # If the model file is missing, train it right now!
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
    thingspeak_data is a dict containing field1 (bodyTemp), field2 (smoke), etc.
    """
    model = load_model()
    if not model:
        return "Model not found."

    try:
        # Convert ThingSpeak strings to floats
        features = {
            'bodyTemp': float(thingspeak_data.get('field1', 0)),
            'smoke': float(thingspeak_data.get('field2', 0)),
            'alcohol': float(thingspeak_data.get('field3', 0)),
            'distance': float(thingspeak_data.get('field4', 0)),
            'humidity': float(thingspeak_data.get('field5', 0)),
            'roomTemp': float(thingspeak_data.get('field6', 0)),
        }
        
        # Convert to DataFrame for scikit-learn
        df = pd.DataFrame([features])
        
        # Make prediction (assuming model expects these features in order)
        prediction = model.predict(df)[0] 
        
        # Example logic: 0 = Normal, 1 = Anomaly/Risk
        # Note: The template looks for the word 'Risk' to turn the box red!
        return "Critical Risk Detected" if prediction == 1 else "Vitals Normal"
        
    except Exception as e:
        return f"Prediction Error: {str(e)}"