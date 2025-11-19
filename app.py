import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import logging
import joblib
import os
import re
import google.generativeai as genai
from typing import Optional, Dict
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Files ---
MODEL_FILE = "model.pkl"
ENCODER_FILE = "label_encoder.pkl"

# --- Gemini API Configuration ---
# Try to get API key from environment variable, or use default
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyD-kyo84xEDpyV08VJGrHHJ6Kn99lQlfS8')

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Gemini API configured successfully.")
    except Exception as e:
        logger.warning(f"Failed to configure Gemini API: {e}")
else:
    logger.warning("GEMINI_API_KEY not found. AI information feature will be disabled.")

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"Supabase client configured successfully. URL: {SUPABASE_URL[:30]}...")
    except Exception as e:
        logger.error(f"Failed to configure Supabase client: {e}", exc_info=True)
        supabase = None
else:
    logger.warning("SUPABASE_URL or SUPABASE_KEY not found. Contact form data will not be saved to Supabase.")
    logger.warning(f"SUPABASE_URL: {SUPABASE_URL if SUPABASE_URL else 'NOT SET'}")
    logger.warning(f"SUPABASE_KEY: {'SET' if SUPABASE_KEY else 'NOT SET'}")

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

# --- Gemini AI Helper Function ---
def get_disease_info(disease_name: str) -> Optional[Dict[str, str]]:
    """
    Get AI-generated information about the disease using Gemini API.
    Returns information about tests, emergency status, and symptom ranges.
    """
    if not GEMINI_API_KEY:
        return None
    
    try:
        # Use available Gemini models (try latest versions first)
        model = None
        model_names = [
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-flash-latest',
            'gemini-pro-latest',
            'gemini-2.0-flash'
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test if model works
                test_response = model.generate_content("test")
                logger.info(f"Using model: {model_name}")
                break
            except Exception as e:
                logger.debug(f"Model {model_name} failed: {e}")
                continue
        
        if model is None:
            raise Exception("No available Gemini model found")
        
        prompt = f"""Provide concise medical information about {disease_name}. Format your response EXACTLY as follows:

**Recommended Tests:**
[List 2-3 key diagnostic tests like blood tests, imaging, etc. Keep it simple and brief - 2-3 sentences max]

**Medical Emergency:**
[State clearly Yes or No, and briefly explain why - 2-3 sentences max]

**Common Symptoms:**
[List 3-4 most common symptoms with brief descriptions - keep it simple and easy to understand - 3-4 sentences max]

Keep each section brief and clear."""
        
        response = model.generate_content(prompt)
        ai_info = response.text
        
        # Parse the response into structured format
        info_dict = {
            'full_response': ai_info,
            'tests': '',
            'emergency': '',
            'symptoms': ''
        }
        
        # Improved parsing - look for section headers
        text = ai_info
        
        # Extract Recommended Tests
        if '**Recommended Tests:**' in text or 'Recommended Tests:' in text:
            start_markers = ['**Recommended Tests:**', 'Recommended Tests:']
            end_markers = ['**Medical Emergency:**', 'Medical Emergency:', '**Common Symptoms:**', 'Common Symptoms:']
            
            for start in start_markers:
                if start in text:
                    start_idx = text.find(start) + len(start)
                    end_idx = len(text)
                    for end in end_markers:
                        if end in text and text.find(end) > start_idx:
                            end_idx = min(end_idx, text.find(end))
                    info_dict['tests'] = text[start_idx:end_idx].strip()
                    break
        
        # Extract Medical Emergency
        if '**Medical Emergency:**' in text or 'Medical Emergency:' in text:
            start_markers = ['**Medical Emergency:**', 'Medical Emergency:']
            end_markers = ['**Common Symptoms:**', 'Common Symptoms:', '**Recommended Tests:**', 'Recommended Tests:']
            
            for start in start_markers:
                if start in text:
                    start_idx = text.find(start) + len(start)
                    end_idx = len(text)
                    for end in end_markers:
                        if end in text and text.find(end) > start_idx:
                            end_idx = min(end_idx, text.find(end))
                    info_dict['emergency'] = text[start_idx:end_idx].strip()
                    break
        
        # Extract Common Symptoms
        if '**Common Symptoms:**' in text or 'Common Symptoms:' in text:
            start_markers = ['**Common Symptoms:**', 'Common Symptoms:']
            start_idx = 0
            for start in start_markers:
                if start in text:
                    start_idx = text.find(start) + len(start)
                    break
            info_dict['symptoms'] = text[start_idx:].strip()
        
        # Clean up extracted text (remove markdown, extra whitespace)
        for key in ['tests', 'emergency', 'symptoms']:
            if info_dict[key]:
                # Remove markdown formatting
                info_dict[key] = info_dict[key].replace('**', '').replace('*', '').strip()
                # Remove extra newlines
                info_dict[key] = ' '.join(info_dict[key].split())
        
        return info_dict
        
    except Exception as e:
        logger.error(f"Error getting AI information: {e}")
        return None

# --- Flask App Setup ---
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)  # Required for session

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
                
                # Get AI information about the disease
                ai_info = get_disease_info(predicted_disease)
                
                prediction_data = {
                    'predicted_disease': predicted_disease,
                    'ai_info': ai_info
                }
                
                prediction_text = f"You may be facing {predicted_disease}"
            else:
                # Get AI information about the disease
                ai_info = get_disease_info(predicted_disease)
                
                prediction_data = {
                    'predicted_disease': predicted_disease,
                    'ai_info': ai_info
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

    # Store prediction data in session for PDF generation
    from flask import session
    session['prediction_data'] = prediction_data
    session['input_data'] = {
        'age': data.get('age'),
        'gender': data.get('gender'),
        'temperature': data.get('temperature'),
        'humidity': data.get('humidity'),
        'wind_speed': data.get('wind_speed'),
        'symptoms': [s for s in SYMPTOM_FEATURES if data.get(s) == '1']
    }

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
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message_type = request.form.get('message_type', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation errors list
        errors = []
        
        # Validate name
        if not name:
            errors.append("Name is required.")
        elif len(name) < 2 or len(name) > 100:
            errors.append("Name must be between 2 and 100 characters.")
        elif not name.replace(' ', '').isalpha():
            errors.append("Name should only contain letters and spaces.")
        
        # Validate email
        if not email:
            errors.append("Email is required.")
        elif len(email) > 255:
            errors.append("Email is too long.")
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Please enter a valid email address.")
        
        # Validate message type
        valid_message_types = ['query', 'suggestion', 'complaint', 'compliment']
        if not message_type:
            errors.append("Message type is required.")
        elif message_type not in valid_message_types:
            errors.append("Invalid message type selected.")
        
        # Validate message
        if not message:
            errors.append("Message is required.")
        elif len(message) < 10 or len(message) > 1000:
            errors.append("Message must be between 10 and 1000 characters.")
        
        if errors:
            return render_template("contact.html", errors=errors, 
                                 name=name, email=email, message_type=message_type, message=message)
        
        form_data = {
            'name': name,
            'email': email,
            'message_type': message_type,
            'message': message
        }
        logger.info(f"Received valid form data: {form_data}")
        
        # Save to Supabase if configured
        if supabase:
            try:
                # Insert data into Supabase table (table name: 'contact_submissions')
                data_to_insert = {
                    'name': name,
                    'email': email,
                    'message_type': message_type,
                    'message': message,
                    'submitted_at': datetime.utcnow().isoformat()
                }
                logger.info(f"Attempting to save to Supabase: {data_to_insert}")
                
                response = supabase.table('contact_submissions').insert(data_to_insert).execute()
                
                if response.data:
                    logger.info(f"Successfully saved contact form data to Supabase. Response: {response.data}")
                else:
                    logger.warning(f"Supabase insert completed but no data returned. Response: {response}")
            except Exception as e:
                logger.error(f"Failed to save contact form data to Supabase: {e}", exc_info=True)
                # Continue even if Supabase save fails - don't break the user experience
        else:
            logger.warning("Supabase not configured. Contact form data not saved to database.")
            logger.warning(f"SUPABASE_URL: {'Set' if SUPABASE_URL else 'Not set'}, SUPABASE_KEY: {'Set' if SUPABASE_KEY else 'Not set'}")
        
        return redirect(url_for('touch', success='true'))
    
    return render_template("contact.html")

@app.route('/contact')
def thanks():
    return render_template('contact.html')

@app.route('/test-supabase')
def test_supabase():
    """Test route to verify Supabase connection"""
    result = {
        'supabase_configured': supabase is not None,
        'supabase_url_set': bool(SUPABASE_URL),
        'supabase_key_set': bool(SUPABASE_KEY),
        'connection_status': 'unknown'
    }
    
    if supabase:
        try:
            # Try a simple query to test connection
            test_response = supabase.table('contact_submissions').select('id').limit(1).execute()
            result['connection_status'] = 'success'
            result['message'] = 'Supabase connection is working!'
            result['test_response'] = str(test_response.data) if hasattr(test_response, 'data') else 'No data'
        except Exception as e:
            result['connection_status'] = 'error'
            result['error'] = str(e)
            result['message'] = f'Supabase connection failed: {e}'
    else:
        result['message'] = 'Supabase is not configured. Check environment variables.'
    
    return f"""
    <h2>Supabase Connection Test</h2>
    <pre>{result}</pre>
    <p><a href="/touch">Back to Contact Form</a></p>
    """

@app.route('/generate_pdf')
def generate_pdf():
    """Generate PDF report with prediction details"""
    from flask import session
    
    prediction_data = session.get('prediction_data')
    input_data = session.get('input_data')
    
    if not prediction_data or not input_data:
        return redirect(url_for('model_page'))
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=60, bottomMargin=50)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style with gradient effect
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#00d9ff'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#8b5cf6'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#4ecdc4'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Info text style
    info_style = ParagraphStyle(
        'InfoText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        leading=16
    )
    
    # Title
    elements.append(Paragraph("Disease Prediction Report", title_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Date
    date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    date_para = Paragraph(f"<b>Generated on:</b> {date_str}", 
                         ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.HexColor('#666666'), alignment=TA_CENTER))
    elements.append(date_para)
    elements.append(Spacer(1, 0.4*inch))
    
    # Prediction Result - Highlighted Box
    disease_name = prediction_data.get('predicted_disease', 'N/A')
    if disease_name and disease_name != 'N/A':
        prediction_box_data = [
            [Paragraph('<b>Predicted Disease</b>', ParagraphStyle('PredLabel', parent=styles['Normal'], 
                                                                    fontSize=12, textColor=colors.whitesmoke, 
                                                                    fontName='Helvetica-Bold', alignment=TA_CENTER)),
             Paragraph(f'<b>{disease_name}</b>', ParagraphStyle('PredValue', parent=styles['Normal'], 
                                                                 fontSize=16, textColor=colors.whitesmoke, 
                                                                 fontName='Helvetica-Bold', alignment=TA_CENTER))]
        ]
        prediction_table = Table(prediction_box_data, colWidths=[2.5*inch, 3.5*inch])
        prediction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#8b5cf6')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#00d9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#00d9ff')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(prediction_table)
        elements.append(Spacer(1, 0.4*inch))
    
    # Input Variables - Improved Table
    elements.append(Paragraph("Input Variables", heading_style))
    
    # Ensure age is properly retrieved - handle all cases
    age_value = input_data.get('age')
    if age_value is None or age_value == '' or str(age_value).strip() == '':
        age_value = 'N/A'
    else:
        age_value = str(age_value).strip()
    
    # Ensure all values are properly formatted
    gender_value = str(input_data.get('gender', 'N/A')).strip()
    if gender_value == '':
        gender_value = 'N/A'
    else:
        gender_value = gender_value.title()
    
    temp_value = str(input_data.get('temperature', 'N/A')).strip()
    if temp_value == '':
        temp_value = 'N/A'
    
    humidity_value = str(input_data.get('humidity', 'N/A')).strip()
    if humidity_value == '':
        humidity_value = 'N/A'
    
    wind_value = str(input_data.get('wind_speed', 'N/A')).strip()
    if wind_value == '':
        wind_value = 'N/A'
    
    input_table_data = [
        ['Variable', 'Value'],
        ['Age', age_value],
        ['Gender', gender_value],
        ['Temperature (°C)', temp_value],
        ['Humidity (%)', humidity_value],
        ['Wind Speed (km/h)', wind_value],
    ]
    
    input_table = Table(input_table_data, colWidths=[2.8*inch, 3.2*inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d9ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Symptoms - Table Format
    symptoms = input_data.get('symptoms', [])
    if symptoms:
        elements.append(Paragraph("Selected Symptoms", heading_style))
        symptom_list = [s.replace('_', ' ').title() for s in symptoms]
        # Create a table for symptoms
        symptom_table_data = [['Symptom']]
        for symptom in symptom_list:
            symptom_table_data.append([symptom])
        
        symptom_table = Table(symptom_table_data, colWidths=[6*inch])
        symptom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))
        elements.append(symptom_table)
        elements.append(Spacer(1, 0.4*inch))
    
    # AI Information - Table Format with Proper Text Wrapping
    ai_info = prediction_data.get('ai_info')
    if ai_info:
        elements.append(Paragraph("AI-Generated Information", heading_style))
        
        ai_table_data = []
        
        # Create text style for wrapping
        ai_text_style = ParagraphStyle(
            'AIText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leading=14,
            alignment=TA_LEFT
        )
        
        category_style = ParagraphStyle(
            'AICategory',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2e7d32'),
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        
        if ai_info.get('tests'):
            ai_table_data.append([
                Paragraph('🔬 <b>Recommended Tests</b>', category_style),
                Paragraph(ai_info['tests'], ai_text_style)
            ])
        
        if ai_info.get('emergency'):
            ai_table_data.append([
                Paragraph('🚨 <b>Medical Emergency Status</b>', category_style),
                Paragraph(ai_info['emergency'], ai_text_style)
            ])
        
        if ai_info.get('symptoms'):
            ai_table_data.append([
                Paragraph('📊 <b>Common Symptoms</b>', category_style),
                Paragraph(ai_info['symptoms'], ai_text_style)
            ])
        
        if ai_info.get('full_response') and not any([ai_info.get('tests'), ai_info.get('emergency'), ai_info.get('symptoms')]):
            ai_table_data.append([
                Paragraph('📋 <b>Additional Information</b>', category_style),
                Paragraph(ai_info['full_response'], ai_text_style)
            ])
        
        if ai_table_data:
            # Add header
            header_style = ParagraphStyle(
                'AIHeader',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.whitesmoke,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER
            )
            ai_table_data.insert(0, [
                Paragraph('<b>Category</b>', header_style),
                Paragraph('<b>Information</b>', header_style)
            ])
            
            ai_table = Table(ai_table_data, colWidths=[2.2*inch, 3.8*inch])
            ai_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ecdc4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e8f5e9')),
                ('BACKGROUND', (1, 1), (1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 15),
            ]))
            elements.append(ai_table)
            elements.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    buffer.seek(0)
    
    # Generate filename
    filename = f"disease_prediction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
