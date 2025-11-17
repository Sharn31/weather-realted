import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import logging
import joblib

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Files ---
MODEL_FILE = "model.pkl"
ENCODER_FILE = "label_encoder.pkl"

# Feature columns in EXACT order as training data (from CSV)
FEATURE_COLUMNS = [
    'Age', 'Gender', 'Temperature (C)', 'Humidity', 'Wind Speed (km/h)',
    'nausea', 'joint_pain', 'abdominal_pain', 'high_fever', 'chills',
    'fatigue', 'runny_nose', 'pain_behind_the_eyes', 'dizziness', 'headache',
    'chest_pain', 'vomiting', 'cough', 'shivering', 'asthma_history',
    'high_cholesterol', 'diabetes', 'obesity', 'hiv_aids', 'nasal_polyps',
    'asthma', 'high_blood_pressure', 'severe_headache', 'weakness',
    'trouble_seeing', 'fever', 'body_aches', 'sore_throat', 'sneezing',
    'diarrhea', 'rapid_breathing', 'rapid_heart_rate', 'pain_behind_eyes',
    'swollen_glands', 'rashes', 'sinus_headache', 'facial_pain',
    'shortness_of_breath', 'reduced_smell_and_taste', 'skin_irritation',
    'itchiness', 'throbbing_headache', 'confusion', 'back_pain', 'knee_ache'
]

# Symptom features for the form (excluding the duplicate pain_behind_eyes)
SYMPTOM_FEATURES = [
    'nausea', 'joint_pain', 'abdominal_pain', 'high_fever', 'chills',
    'fatigue', 'runny_nose', 'pain_behind_the_eyes', 'dizziness', 'headache',
    'chest_pain', 'vomiting', 'cough', 'shivering', 'asthma_history',
    'high_cholesterol', 'diabetes', 'obesity', 'hiv_aids', 'nasal_polyps',
    'asthma', 'high_blood_pressure', 'severe_headache', 'weakness',
    'trouble_seeing', 'fever', 'body_aches', 'sore_throat', 'sneezing',
    'diarrhea', 'rapid_breathing', 'rapid_heart_rate', 'pain_behind_eyes',
    'swollen_glands', 'rashes', 'sinus_headache', 'facial_pain',
    'shortness_of_breath', 'reduced_smell_and_taste', 'skin_irritation',
    'itchiness', 'throbbing_headache', 'confusion', 'back_pain', 'knee_ache'
]

# --- Load Model ---
model, label_encoder = None, None
try:
    model = joblib.load(MODEL_FILE)
    label_encoder = joblib.load(ENCODER_FILE)
    logger.info("ML artifacts loaded successfully.")
except FileNotFoundError as e:
    logger.error(f"Error loading ML files: {e}. Ensure {MODEL_FILE} and {ENCODER_FILE} are in the same directory.")

# --- Flask App Setup ---
app = Flask(__name__, static_folder='static')

@app.route('/')
def about():
    return render_template("about.html")

@app.route('/model')
def model_page():
    return render_template('model.html', symptom_list=SYMPTOM_FEATURES, prediction_text=None)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form
    prediction_text = None

    input_array = np.zeros(len(FEATURE_COLUMNS))
    input_df = pd.DataFrame([input_array], columns=FEATURE_COLUMNS)

    required_fields = ['age', 'temperature', 'humidity', 'wind_speed', 'gender']
    for field_name in required_fields:
        if not data.get(field_name):
            prediction_text = f"ERROR: The field '{field_name.title().replace('_', ' ')}' is required."
            return render_template('model.html', prediction_text=prediction_text, symptom_list=SYMPTOM_FEATURES)

    try:
        input_df['Age'] = float(data.get('age'))
        gender_map = {'male': 1.0, 'female': 0.0}
        input_df['Gender'] = gender_map.get(data.get('gender'), np.nan)
        input_df['Temperature (C)'] = float(data.get('temperature'))
        input_df['Humidity'] = float(data.get('humidity'))
        input_df['Wind Speed (km/h)'] = float(data.get('wind_speed'))
    except ValueError:
        prediction_text = "ERROR: Please ensure Age, Temperature, Humidity, and Wind Speed are valid numbers."
        return render_template('model.html', prediction_text=prediction_text, symptom_list=SYMPTOM_FEATURES)

    # Handle symptom input - map to correct columns
    for symptom in SYMPTOM_FEATURES:
        if symptom in FEATURE_COLUMNS:
            input_df[symptom] = 1.0 if data.get(symptom) == '1' else 0.0
    
    # Handle special case: if pain_behind_the_eyes is checked, also set pain_behind_eyes
    if data.get('pain_behind_the_eyes') == '1':
        input_df['pain_behind_eyes'] = 1.0
    elif 'pain_behind_eyes' in FEATURE_COLUMNS:
        input_df['pain_behind_eyes'] = 0.0

    # Ensure DataFrame has columns in the exact order expected by the model
    input_df = input_df[FEATURE_COLUMNS]
    
    # Ensure all columns are numeric (float64)
    for col in input_df.columns:
        input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0.0)
    
    logger.info(f"Input DataFrame shape: {input_df.shape}")
    logger.info(f"Input DataFrame columns: {list(input_df.columns)}")
    logger.info(f"Input DataFrame dtypes:\n{input_df.dtypes}")

    # --- Prediction ---
    prediction_data = None
    if model is not None and label_encoder is not None:
        try:
            # Get prediction - the Pipeline will handle scaling automatically
            logger.info("Calling model.predict()...")
            prediction_encoded = model.predict(input_df)
            logger.info(f"Prediction encoded: {prediction_encoded}")
            
            predicted_disease = label_encoder.inverse_transform(prediction_encoded)[0]
            logger.info(f"Predicted disease: {predicted_disease}")
            
            # Get prediction probabilities
            if hasattr(model, 'predict_proba'):
                logger.info("Getting prediction probabilities...")
                probabilities = model.predict_proba(input_df)[0]
                disease_names = label_encoder.classes_
                
                logger.info(f"Probabilities shape: {probabilities.shape}")
                logger.info(f"Number of diseases: {len(disease_names)}")
                
                # Create list of (disease, probability) tuples
                disease_probs = list(zip(disease_names, probabilities))
                # Sort by probability (descending)
                disease_probs.sort(key=lambda x: x[1], reverse=True)
                
                # Get top 3 predictions
                top_predictions = disease_probs[:3]
                
                # Get confidence for the predicted disease
                predicted_idx = prediction_encoded[0]
                confidence = float(probabilities[predicted_idx]) * 100
                
                prediction_data = {
                    'predicted_disease': predicted_disease
                }
                
                prediction_text = f"You may be facing {predicted_disease}"
            else:
                prediction_data = {
                    'predicted_disease': predicted_disease
                }
                prediction_text = f"You may be facing {predicted_disease}"
            
            logger.info(f"Prediction result: {prediction_text}")
        except Exception as e:
            logger.error(f"Error during prediction: {e}", exc_info=True)
            prediction_text = f"An unexpected error occurred during prediction: {str(e)}. Check server logs."
            prediction_data = None
    else:
        prediction_text = "ERROR: Machine Learning model files are not loaded correctly on the server."
        prediction_data = None

    return render_template('model.html', 
                         prediction_text=prediction_text, 
                         prediction_data=prediction_data,
                         symptom_list=SYMPTOM_FEATURES)

@app.route('/visualize')
def visualize():
    return render_template("visualize.html")

@app.route('/touch', methods=["GET", "POST"])
def touch():
    if request.method == "POST":
        # In this simplified version, just log data instead of sending to Supabase
        logger.info(f"Received form data: {dict(request.form)}")
        return redirect(url_for('thanks'))
    return render_template("contact.html")

@app.route('/contact')
def thanks():
    return render_template('contact.html')
if __name__ == '__main__':
    app.run(debug=True)
