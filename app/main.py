"""
Smart Patient Triage System - Main Application
Professional Clinical UI with Patient Queue and Explainability
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import sys
import os
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parser import parse_clinical_note
from utils.auth import AuthManager, show_login_page, show_logout_button

# Configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Smart Patient Triage System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication
auth_manager = AuthManager()
# Custom CSS for professional clinical styling
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Risk status boxes */
    .status-box-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3);
        margin: 1.5rem 0;
    }
    
    .status-box-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3);
        margin: 1.5rem 0;
    }
    
    .status-box-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        margin: 1.5rem 0;
    }
    
    .status-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .status-subtitle {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.95;
    }
    
    /* Department badge */
    .dept-badge {
        background-color: rgba(255,255,255,0.2);
        padding: 0.75rem 1.5rem;
        border-radius: 2rem;
        display: inline-block;
        margin-top: 1rem;
        font-size: 1.3rem;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    /* Factor items */
    .factor-item {
        background: linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%);
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
        border-radius: 0.5rem;
        font-size: 1rem;
    }
    
    /* Override warning */
    .override-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 6px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(245, 158, 11, 0.2);
    }
    
    /* Queue table styling */
    .queue-header {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem 0.5rem 0 0;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f1f5f9;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'patient_queue' not in st.session_state:
    st.session_state.patient_queue = []

if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None

if 'voice_extracted_data' not in st.session_state:
    st.session_state.voice_extracted_data = None

if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Translation dictionary
TRANSLATIONS = {
    'English': {
        'title': 'Smart Patient Triage System',
        'subtitle': 'AI-Powered Clinical Decision Support with Safety-First Design',
        'language_selector': '🌐 Language / மொழி / भाषा',
        'patient_queue': 'Recent Patient Queue',
        'no_patients': 'No patients in queue yet. Triage your first patient to see the queue.',
        'clinical_info': 'Clinical Information & Triage',
        'input_method': 'Input Method:',
        'manual_entry': 'Manual Entry',
        'clinical_note': 'Clinical Note Upload',
        'demographics': 'Demographics',
        'patient_name': 'Patient Name',
        'patient_id': 'Patient ID',
        'age': 'Age',
        'gender': 'Gender',
        'male': 'Male',
        'female': 'Female',
        'transgender': 'Transgender',
        'others': 'Others',
        'vital_signs': 'Vital Signs',
        'heart_rate': 'Heart Rate (bpm)',
        'systolic_bp': 'Systolic BP (mmHg)',
        'diastolic_bp': 'Diastolic BP (mmHg)',
        'temperature': 'Temperature (°C)',
        'spo2': 'SpO2 (%)',
        'clinical_information': 'Clinical Information',
        'symptoms': 'Symptoms',
        'medical_history': 'Medical History',
        'voice_assistant': 'Voice Assistant - Quick Symptom Input',
        'voice_caption': 'Speak or type your symptoms naturally, then click Analyze to auto-fill the form above',
        'analyze': 'Analyze',
        'clear_voice': 'Clear Voice Data',
        'run_triage': 'RUN AI TRIAGE',
        'risk_level': 'Risk Level',
        'department': 'Department',
        'confidence': 'Confidence',
        'high_risk': 'HIGH RISK',
        'medium_risk': 'MEDIUM RISK',
        'low_risk': 'LOW RISK',
        'immediate_attention': 'Immediate Attention Required',
        'priority_assessment': 'Priority Assessment Needed',
        'standard_care': 'Standard Care Pathway',
        'clinical_assessment': 'Clinical Assessment & Recommendations',
        'ai_analysis': 'AI Analysis:',
        'top_factors': 'Top Contributing Factors',
    },
    'Tamil': {
        'title': 'ஸ்மார்ட் நோயாளி முன்னுரிமை அமைப்பு',
        'subtitle': 'AI-இயங்கும் மருத்துவ முடிவு ஆதரவு - பாதுகாப்பு முதல் வடிவமைப்பு',
        'language_selector': '🌐 Language / மொழி / भाषा',
        'patient_queue': 'சமீபத்திய நோயாளி வரிசை',
        'no_patients': 'இன்னும் வரிசையில் நோயாளிகள் இல்லை. வரிசையைப் பார்க்க உங்கள் முதல் நோயாளியை பரிசோதிக்கவும்.',
        'clinical_info': 'மருத்துவ தகவல் & முன்னுரிமை',
        'input_method': 'உள்ளீட்டு முறை:',
        'manual_entry': 'கைமுறை உள்ளீடு',
        'clinical_note': 'மருத்துவ குறிப்பு பதிவேற்றம்',
        'demographics': 'மக்கள்தொகை விவரங்கள்',
        'patient_name': 'நோயாளியின் பெயர்',
        'patient_id': 'நோயாளி அடையாள எண்',
        'age': 'வயது',
        'gender': 'பாலினம்',
        'male': 'ஆண்',
        'female': 'பெண்',
        'transgender': 'திருநங்கை',
        'others': 'மற்றவை',
        'vital_signs': 'முக்கிய அறிகுறிகள்',
        'heart_rate': 'இதய துடிப்பு (bpm)',
        'systolic_bp': 'சிஸ்டாலிக் BP (mmHg)',
        'diastolic_bp': 'டயஸ்டாலிக் BP (mmHg)',
        'temperature': 'வெப்பநிலை (°C)',
        'spo2': 'SpO2 (%)',
        'clinical_information': 'மருத்துவ தகவல்',
        'symptoms': 'அறிகுறிகள்',
        'medical_history': 'மருத்துவ வரலாறு',
        'voice_assistant': 'குரல் உதவியாளர் - விரைவு அறிகுறி உள்ளீடு',
        'voice_caption': 'உங்கள் அறிகுறிகளை இயல்பாகப் பேசவும் அல்லது தட்டச்சு செய்யவும், பின்னர் மேலே உள்ள படிவத்தை தானாக நிரப்ப பகுப்பாய்வு என்பதைக் கிளிக் செய்யவும்',
        'analyze': 'பகுப்பாய்வு',
        'clear_voice': 'குரல் தரவை அழி',
        'run_triage': 'AI முன்னுரிமை இயக்கு',
        'risk_level': 'ஆபத்து நிலை',
        'department': 'துறை',
        'confidence': 'நம்பிக்கை',
        'high_risk': 'அதிக ஆபத்து',
        'medium_risk': 'நடுத்தர ஆபத்து',
        'low_risk': 'குறைந்த ஆபத்து',
        'immediate_attention': 'உடனடி கவனம் தேவை',
        'priority_assessment': 'முன்னுரிமை மதிப்பீடு தேவை',
        'standard_care': 'நிலையான பராமரிப்பு பாதை',
        'clinical_assessment': 'மருத்துவ மதிப்பீடு & பரிந்துரைகள்',
        'ai_analysis': 'AI பகுப்பாய்வு:',
        'top_factors': 'முக்கிய பங்களிப்பு காரணிகள்',
    },
    'Hindi': {
        'title': 'स्मार्ट रोगी ट्राइएज सिस्टम',
        'subtitle': 'AI-संचालित नैदानिक निर्णय समर्थन - सुरक्षा-प्रथम डिज़ाइन',
        'language_selector': '🌐 Language / மொழி / भाषा',
        'patient_queue': 'हाल के रोगी कतार',
        'no_patients': 'अभी तक कतार में कोई मरीज नहीं है। कतार देखने के लिए अपने पहले रोगी का परीक्षण करें।',
        'clinical_info': 'नैदानिक जानकारी और ट्राइएज',
        'input_method': 'इनपुट विधि:',
        'manual_entry': 'मैनुअल एंट्री',
        'clinical_note': 'क्लिनिकल नोट अपलोड',
        'demographics': 'जनसांख्यिकी',
        'patient_name': 'रोगी का नाम',
        'patient_id': 'रोगी आईडी',
        'age': 'आयु',
        'gender': 'लिंग',
        'male': 'पुरुष',
        'female': 'महिला',
        'transgender': 'ट्रांसजेंडर',
        'others': 'अन्य',
        'vital_signs': 'महत्वपूर्ण संकेत',
        'heart_rate': 'हृदय गति (bpm)',
        'systolic_bp': 'सिस्टोलिक BP (mmHg)',
        'diastolic_bp': 'डायस्टोलिक BP (mmHg)',
        'temperature': 'तापमान (°C)',
        'spo2': 'SpO2 (%)',
        'clinical_information': 'नैदानिक जानकारी',
        'symptoms': 'लक्षण',
        'medical_history': 'चिकित्सा इतिहास',
        'voice_assistant': 'वॉयस असिस्टेंट - त्वरित लक्षण इनपुट',
        'voice_caption': 'अपने लक्षणों को स्वाभाविक रूप से बोलें या टाइप करें, फिर ऊपर फॉर्म को ऑटो-फिल करने के लिए विश्लेषण पर क्लिक करें',
        'analyze': 'विश्लेषण करें',
        'clear_voice': 'वॉयस डेटा साफ़ करें',
        'run_triage': 'AI ट्राइएज चलाएं',
        'risk_level': 'जोखिम स्तर',
        'department': 'विभाग',
        'confidence': 'विश्वास',
        'high_risk': 'उच्च जोखिम',
        'medium_risk': 'मध्यम जोखिम',
        'low_risk': 'कम जोखिम',
        'immediate_attention': 'तत्काल ध्यान आवश्यक',
        'priority_assessment': 'प्राथमिकता मूल्यांकन आवश्यक',
        'standard_care': 'मानक देखभाल मार्ग',
        'clinical_assessment': 'नैदानिक मूल्यांकन और सिफारिशें',
        'ai_analysis': 'AI विश्लेषण:',
        'top_factors': 'शीर्ष योगदान कारक',
    }
}

def t(key):
    """Translation helper function"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

# Symptom options (matching dataset)
SYMPTOM_OPTIONS = [
    "Chest pain",
    "Shortness of breath",
    "Facial drooping",
    "Slurred speech",
    "One-sided weakness",
    "Confusion",
    "Headache",
    "Nausea",
    "Vomiting",
    "Fever",
    "Chills",
    "Sweating",
    "Cough",
    "Wheezing",
    "Abdominal pain",
    "Dizziness",
    "Palpitations",
    "Fatigue",
    "Pain",
    "Swelling",
    "Rash",
    "Difficulty swallowing"
]

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def submit_triage(patient_data):
    """Submit patient data to triage API"""
    try:
        response = requests.post(
            f"{API_URL}/api/triage",
            json=patient_data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Please ensure the server is running."
    except Exception as e:
        return None, f"Error: {str(e)}"

def display_risk_status(result):
    """Display large color-coded status box"""
    risk = result['risk'].upper()
    
    if risk == "HIGH":
        st.markdown(f"""
        <div class="status-box-high">
            <div class="status-title">🔴 HIGH RISK</div>
            <div class="status-subtitle">Immediate Attention Required</div>
            <div class="dept-badge">🏥 {result['department']}</div>
        </div>
        """, unsafe_allow_html=True)
    elif risk == "MEDIUM":
        st.markdown(f"""
        <div class="status-box-medium">
            <div class="status-title">🟡 MEDIUM RISK</div>
            <div class="status-subtitle">Priority Assessment Needed</div>
            <div class="dept-badge">🏥 {result['department']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-box-low">
            <div class="status-title">🟢 LOW RISK</div>
            <div class="status-subtitle">Standard Care Pathway</div>
            <div class="dept-badge">🏥 {result['department']}</div>
        </div>
        """, unsafe_allow_html=True)

def display_confidence_bar(confidence):
    """Display confidence score as progress bar"""
    confidence_pct = confidence * 100
    
    # Create Plotly gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence_pct,
        title={'text': "Confidence Score", 'font': {'size': 20}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e7eb",
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},
                {'range': [50, 75], 'color': '#fef3c7'},
                {'range': [75, 100], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': "Arial"}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_feature_importance(factors):
    """Display top contributing features as horizontal bar chart"""
    if not factors:
        return
    
    st.markdown("### 🔍 Top Contributing Factors")
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Reverse order for better visualization (top factor at top)
    factors_display = factors[:5][::-1]
    
    fig.add_trace(go.Bar(
        y=[f"Factor {i+1}" for i in range(len(factors_display))][::-1],
        x=[1] * len(factors_display),  # Equal weights for visualization
        orientation='h',
        text=factors_display,
        textposition='inside',
        textfont=dict(size=12, color='white'),
        marker=dict(
            color=['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe'][:len(factors_display)],
            line=dict(color='#1e40af', width=2)
        ),
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))
    
    fig.update_layout(
        height=max(200, len(factors_display) * 60),
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Also display as list
    for i, factor in enumerate(factors[:5], 1):
        st.markdown(f'<div class="factor-item">{i}. {factor}</div>', unsafe_allow_html=True)

def add_to_queue(patient_data, result, patient_name="", patient_id=""):
    """Add patient to queue history"""
    queue_entry = {
        'Time': datetime.now().strftime("%H:%M:%S"),
        'Patient ID': patient_id if patient_id else "N/A",
        'Name': patient_name if patient_name else "Anonymous",
        'Age': patient_data['age'],
        'Gender': patient_data['gender'],
        'Risk': result['risk'].upper(),
        'Department': result['department'],
        'Confidence': f"{result['confidence']*100:.0f}%"
    }
    
    st.session_state.patient_queue.insert(0, queue_entry)
    
    # Keep only last 5 patients
    if len(st.session_state.patient_queue) > 5:
        st.session_state.patient_queue = st.session_state.patient_queue[:5]

def display_patient_queue():
    """Display patient queue as dataframe"""
    st.markdown(f"### 👥 {t('patient_queue')}")
    
    if st.session_state.patient_queue:
        df = pd.DataFrame(st.session_state.patient_queue)
        
        # Style the dataframe
        def color_risk(val):
            if val == 'HIGH':
                return 'background-color: #fee2e2; color: #991b1b; font-weight: bold'
            elif val == 'MEDIUM':
                return 'background-color: #fef3c7; color: #92400e; font-weight: bold'
            else:
                return 'background-color: #d1fae5; color: #065f46; font-weight: bold'
        
        styled_df = df.style.applymap(color_risk, subset=['Risk'])
        st.dataframe(styled_df, use_container_width=True, height=250)
    else:
        st.info(t('no_patients'))

def get_detailed_clinical_reasoning(department, risk_level, symptoms, vitals):
    """Generate detailed disease and department information"""
    
    # Department descriptions
    dept_info = {
        "Cardiology": {
            "description": "Cardiology specializes in diagnosing and treating conditions of the heart and blood vessels. This includes coronary artery disease, heart attacks, arrhythmias, heart failure, and hypertension.",
            "common_conditions": ["Myocardial Infarction (Heart Attack)", "Angina", "Arrhythmias", "Heart Failure", "Hypertensive Crisis"],
            "urgency": "Cardiac conditions often require immediate intervention to prevent permanent heart damage or death. Time is critical - 'Time is Muscle'."
        },
        "Emergency": {
            "description": "Emergency Medicine provides immediate evaluation and treatment for acute illnesses and injuries that require urgent medical attention. This department handles life-threatening conditions requiring rapid stabilization.",
            "common_conditions": ["Trauma", "Severe Infections", "Acute Respiratory Distress", "Anaphylaxis", "Severe Bleeding"],
            "urgency": "Emergency conditions require immediate medical intervention to prevent death or serious disability. Rapid assessment and treatment are critical."
        },
        "Neurology": {
            "description": "Neurology focuses on disorders of the nervous system, including the brain, spinal cord, and peripheral nerves. Neurological emergencies can result in permanent disability if not treated promptly.",
            "common_conditions": ["Stroke", "Seizures", "Meningitis", "Encephalitis", "Severe Headaches"],
            "urgency": "Neurological emergencies like stroke require immediate treatment within the 'golden hour' to minimize brain damage and improve outcomes."
        },
        "Respiratory": {
            "description": "Respiratory Medicine (Pulmonology) treats diseases of the lungs and airways, including infections, chronic conditions, and acute breathing difficulties that affect oxygen delivery to the body.",
            "common_conditions": ["Pneumonia", "COPD Exacerbation", "Asthma Attack", "Pulmonary Embolism", "Respiratory Failure"],
            "urgency": "Respiratory emergencies can rapidly lead to oxygen deprivation and organ damage. Immediate oxygen support and treatment are often necessary."
        },
        "Surgery": {
            "description": "General Surgery handles conditions requiring operative intervention, including acute abdominal emergencies, trauma, and infections that may need surgical drainage or repair.",
            "common_conditions": ["Acute Appendicitis", "Bowel Obstruction", "Perforated Ulcer", "Trauma", "Abscesses"],
            "urgency": "Surgical emergencies like appendicitis can lead to life-threatening complications (perforation, sepsis) if not treated promptly."
        },
        "Endocrinology": {
            "description": "Endocrinology treats disorders of the endocrine system and hormones, including diabetes complications, thyroid disorders, and metabolic emergencies that can be life-threatening.",
            "common_conditions": ["Diabetic Ketoacidosis (DKA)", "Hypoglycemia", "Thyroid Storm", "Adrenal Crisis"],
            "urgency": "Endocrine emergencies like DKA can rapidly progress to coma and death without immediate insulin therapy and fluid resuscitation."
        },
        "Orthopedics": {
            "description": "Orthopedics specializes in the musculoskeletal system, treating bone fractures, joint injuries, and soft tissue trauma. While often not immediately life-threatening, prompt treatment prevents complications.",
            "common_conditions": ["Fractures", "Dislocations", "Ligament Tears", "Compartment Syndrome"],
            "urgency": "While most orthopedic injuries are not immediately life-threatening, certain conditions like compartment syndrome require urgent surgical intervention."
        },
        "General Medicine": {
            "description": "General Medicine (Internal Medicine) provides comprehensive care for adult patients with a wide range of medical conditions, from minor illnesses to chronic disease management.",
            "common_conditions": ["Upper Respiratory Infections", "Gastroenteritis", "Urinary Tract Infections", "Minor Infections"],
            "urgency": "General medicine conditions are typically less urgent but still require proper medical evaluation and treatment to prevent complications."
        }
    }
    
    # Get department info
    dept_data = dept_info.get(department, {
        "description": f"{department} provides specialized medical care for this condition.",
        "common_conditions": ["Various conditions"],
        "urgency": "Medical evaluation and treatment recommended."
    })
    
    # Build detailed reasoning
    reasoning = f"""
**Department: {department}**

{dept_data['description']}

**Common Conditions Treated:**
{', '.join(dept_data['common_conditions'])}

**Why This Department:**
Based on the patient's symptoms and vital signs, this condition falls under the expertise of {department}. {dept_data['urgency']}

**Risk Level: {risk_level.upper()}**
"""
    
    if risk_level.upper() == "HIGH":
        reasoning += """
This patient requires IMMEDIATE medical attention. High-risk conditions can rapidly deteriorate and may be life-threatening. Prompt evaluation and treatment are critical to prevent serious complications or death.

**Immediate Actions:**
- Rapid triage and assessment
- Continuous vital sign monitoring
- Immediate physician evaluation
- Prepare for emergency interventions if needed
"""
    elif risk_level.upper() == "MEDIUM":
        reasoning += """
This patient requires PRIORITY medical attention. Medium-risk conditions need timely evaluation to prevent progression to more serious states. While not immediately life-threatening, delays in treatment could lead to complications.

**Recommended Actions:**
- Priority triage placement
- Regular vital sign monitoring
- Physician evaluation within 30-60 minutes
- Prepare for potential admission or further testing
"""
    else:
        reasoning += """
This patient can be seen through standard care pathways. Low-risk conditions are typically not immediately threatening but still require proper medical evaluation and treatment.

**Recommended Actions:**
- Standard triage process
- Routine vital sign monitoring
- Physician evaluation as per normal queue
- Outpatient management likely appropriate
"""
    
    return reasoning

def main():
    """Main application"""
    
    # Check authentication first
    if not auth_manager.is_authenticated():
        show_login_page()
        return
    
    # Header
    st.markdown(f'<div class="main-header">🏥 {t("title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{t("subtitle")}</div>', unsafe_allow_html=True)
    
    # Check API health
    api_healthy = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ **API Server Not Running**")
        st.warning("Please start the FastAPI server: `python api/main.py`")
        st.stop()
    
    # Sidebar for language selection and queue
    with st.sidebar:
        st.title(t('language_selector'))
        
        # Language selector
        selected_language = st.selectbox(
            "Select Language:",
            ["English", "Tamil", "Hindi"],
            index=["English", "Tamil", "Hindi"].index(st.session_state.language),
            help="Choose your preferred language",
            label_visibility="collapsed"
        )
        
        # Update language if changed
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()
        
        st.markdown("---")
        
        # Patient Queue
        display_patient_queue()
        
        # Logout button at bottom of sidebar
        show_logout_button()
    
    # Main content area - Clinical Information Input
    st.markdown(f"### 📋 {t('clinical_info')}")
    
    # Input method selection
    input_method = st.radio(
        f"{t('input_method')}",
        [t('manual_entry'), t('clinical_note')],
        help="Choose how to enter patient data",
        horizontal=True
    )
    
    st.markdown("---")
    
    if input_method == "Clinical Note Upload":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Upload Clinical Note")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload text file",
                type=['txt'],
                help="Upload a clinical note in text format"
            )
        
        with col2:
            st.subheader("📝 Or Paste Note")
            # Text area for pasting
            clinical_note = st.text_area(
                "Paste clinical note here:",
                height=150,
                placeholder="Example: 65yo Male with HR 110, BP 160/95, Temp 38.5C, SpO2 92%...",
                label_visibility="collapsed"
            )
        
        # Read uploaded file
        if uploaded_file is not None:
            clinical_note = uploaded_file.read().decode('utf-8')
            st.success(f"✓ File loaded: {uploaded_file.name}")
        
        # Parse button
        col_parse1, col_parse2, col_parse3 = st.columns([1, 1, 1])
        with col_parse2:
            if st.button("🔍 Parse Document", type="primary", use_container_width=True):
                if clinical_note:
                    with st.spinner("Parsing clinical note..."):
                        parsed = parse_clinical_note(clinical_note)
                        st.session_state.parsed_data = parsed
                        st.success(f"✓ Extraction complete! Confidence: {parsed['extraction_confidence']:.1%}")
                        
                        if parsed['missing_fields']:
                            st.warning(f"⚠️ Missing: {', '.join(parsed['missing_fields'])}")
                else:
                    st.error("Please upload a file or paste clinical note text")
        
        st.markdown("---")
        
        # Show parsed data or use defaults
        if st.session_state.parsed_data:
            parsed = st.session_state.parsed_data
            st.info("✓ Data extracted! Review and adjust below if needed:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 Demographics")
                patient_name = st.text_input("Patient Name", placeholder="e.g., John Doe", key="parsed_name")
                patient_id = st.text_input("Patient ID", placeholder="e.g., PT-2024-001", key="parsed_id")
                age = st.slider("Age", 0, 120, parsed['age'] if parsed['age'] else 65)
                gender = st.selectbox("Gender", ["Male", "Female", "Transgender", "Others"], 
                                     index=0 if parsed['gender'] == "Male" else (1 if parsed['gender'] == "Female" else 3))
            
            with col2:
                st.subheader("🩺 Vital Signs")
                hr = st.slider("Heart Rate (bpm)", 30, 200, 
                              int(parsed['vitals']['heart_rate']) if parsed['vitals']['heart_rate'] else 75)
                sbp = st.slider("Systolic BP (mmHg)", 60, 250,
                               int(parsed['vitals']['sbp']) if parsed['vitals']['sbp'] else 120)
                dbp = st.slider("Diastolic BP (mmHg)", 40, 150,
                               int(parsed['vitals']['dbp']) if parsed['vitals']['dbp'] else 80)
                temp = st.slider("Temperature (°C)", 35.0, 42.0,
                                float(parsed['vitals']['temp_c']) if parsed['vitals']['temp_c'] else 37.0, 0.1)
                spo2 = st.slider("SpO2 (%)", 70, 100,
                                int(parsed['vitals']['spo2']) if parsed['vitals']['spo2'] else 98)
            
            st.subheader("🔍 Clinical Details")
            symptoms_text = st.text_area("Symptoms", parsed['symptoms'], height=80)
            medical_history = st.text_input("Medical History", parsed['medical_history'])
        else:
            st.info("👆 Parse a document first or switch to Manual Entry")
            patient_name = ""
            patient_id = ""
            age = 65
            gender = "Male"
            hr = 75
            sbp = 120
            dbp = 80
            temp = 37.0
            spo2 = 98
            symptoms_text = ""
            medical_history = "None"
    
    else:  # Manual Entry
        # Get defaults from voice data if available
        voice_data = st.session_state.voice_extracted_data
        
        default_age = voice_data['age'] if voice_data and voice_data['age'] else 65
        default_gender_idx = 0
        if voice_data and voice_data['gender']:
            if voice_data['gender'] == "Female":
                default_gender_idx = 1
            elif voice_data['gender'] == "Transgender":
                default_gender_idx = 2
            elif voice_data['gender'] == "Others":
                default_gender_idx = 3
        
        default_hr = int(voice_data['vitals']['heart_rate']) if voice_data and voice_data['vitals']['heart_rate'] else 75
        default_sbp = int(voice_data['vitals']['sbp']) if voice_data and voice_data['vitals']['sbp'] else 120
        default_dbp = int(voice_data['vitals']['dbp']) if voice_data and voice_data['vitals']['dbp'] else 80
        default_temp = float(voice_data['vitals']['temp_c']) if voice_data and voice_data['vitals']['temp_c'] else 37.0
        default_spo2 = int(voice_data['vitals']['spo2']) if voice_data and voice_data['vitals']['spo2'] else 98
        default_symptoms = voice_data['symptoms'] if voice_data and voice_data['symptoms'] else ""
        default_history = voice_data['medical_history'] if voice_data and voice_data['medical_history'] and voice_data['medical_history'] != "None" else ""
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"👤 {t('demographics')}")
            patient_name = st.text_input(t('patient_name'), placeholder="e.g., John Doe", help="Enter patient's full name")
            patient_id = st.text_input(t('patient_id'), placeholder="e.g., PT-2024-001", help="Enter patient identification number")
            age = st.slider(t('age'), 0, 120, default_age, help="Patient age in years")
            gender = st.selectbox(t('gender'), [t('male'), t('female'), t('transgender'), t('others')], index=default_gender_idx)
            
            st.subheader(f"🔍 {t('clinical_information')}")
            
            # If voice data has symptoms, show them in text area, otherwise use multiselect
            if default_symptoms:
                st.info("✓ Symptoms from voice input (edit if needed):")
                symptoms_text = st.text_area(
                    t('symptoms'),
                    value=default_symptoms,
                    height=100,
                    help="Edit symptoms extracted from voice"
                )
            else:
                symptoms = st.multiselect(
                    t('symptoms'),
                    SYMPTOM_OPTIONS + ["Other (specify below)"],
                    help="Select all applicable symptoms"
                )
                
                # Show text input if "Other" is selected
                other_symptoms = ""
                if "Other (specify below)" in symptoms:
                    other_symptoms = st.text_input(
                        "Specify other symptoms:",
                        placeholder="e.g., Tingling sensation, Blurred vision",
                        help="Enter any symptoms not listed above"
                    )
                    # Remove "Other" from the list and add custom symptoms
                    symptoms = [s for s in symptoms if s != "Other (specify below)"]
                    if other_symptoms:
                        symptoms.append(other_symptoms)
                
                symptoms_text = ", ".join(symptoms) if symptoms else "No specific symptoms"
            
            medical_history = st.text_input(
                t('medical_history'),
                value=default_history,
                placeholder="e.g., Hypertension, Diabetes",
                help="Enter pre-existing conditions"
            )
        
        with col2:
            st.subheader(f"🩺 {t('vital_signs')}")
            hr = st.slider(t('heart_rate'), 30, 200, default_hr)
            sbp = st.slider(t('systolic_bp'), 60, 250, default_sbp)
            dbp = st.slider(t('diastolic_bp'), 40, 150, default_dbp)
            temp = st.slider(t('temperature'), 35.0, 42.0, default_temp, 0.1)
            spo2 = st.slider(t('spo2'), 70, 100, default_spo2)
    
    st.markdown("---")
    
    # Voice Assistant Section
    st.markdown(f"### 🎤 {t('voice_assistant')}")
    st.caption(t('voice_caption'))
    
    voice_col1, voice_col2 = st.columns([5, 1])
    
    with voice_col1:
        voice_input = st.text_area(
            "Voice/Text Input",
            height=100,
            placeholder="Example: 'I'm a 45 year old male with severe chest pain and shortness of breath, my heart is racing'",
            key="voice_input_area",
            help="Use device voice-to-text: Windows (Win+H), Mac (Fn twice), Mobile (mic icon on keyboard)",
            label_visibility="collapsed"
        )
    
    with voice_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Voice guide button
        with st.popover("🎙️ Help"):
            st.markdown("""
            **How to use voice:**
            - **Windows**: Win + H
            - **Mac**: Fn twice  
            - **Mobile**: Mic icon
            
            Speak naturally about:
            - Age and gender
            - Symptoms
            - Vital signs if known
            - Medical history
            """)
        
        # Analyze button
        if voice_input and voice_input.strip():
            if st.button(f"🔍 {t('analyze')}", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    parsed_voice = parse_clinical_note(voice_input)
                    st.session_state.voice_extracted_data = parsed_voice
                    st.rerun()
    
    # Display extracted voice data if available
    if st.session_state.voice_extracted_data:
        parsed_voice = st.session_state.voice_extracted_data
        
        st.success(f"✅ Data extracted! Confidence: {parsed_voice['extraction_confidence']:.0%} - Form fields updated above")
        
        # Show quick summary in columns
        sum_cols = st.columns(5)
        
        with sum_cols[0]:
            if parsed_voice['age']:
                st.metric("Age", f"{parsed_voice['age']}")
        with sum_cols[1]:
            if parsed_voice['vitals']['heart_rate']:
                st.metric("HR", f"{parsed_voice['vitals']['heart_rate']:.0f}")
        with sum_cols[2]:
            if parsed_voice['vitals']['sbp'] and parsed_voice['vitals']['dbp']:
                st.metric("BP", f"{parsed_voice['vitals']['sbp']:.0f}/{parsed_voice['vitals']['dbp']:.0f}")
        with sum_cols[3]:
            if parsed_voice['vitals']['temp_c']:
                st.metric("Temp", f"{parsed_voice['vitals']['temp_c']:.1f}°C")
        with sum_cols[4]:
            if parsed_voice['vitals']['spo2']:
                st.metric("SpO2", f"{parsed_voice['vitals']['spo2']:.0f}%")
        
        if parsed_voice['symptoms']:
            st.info(f"**Symptoms:** {parsed_voice['symptoms']}")
        
        if parsed_voice['missing_fields']:
            st.warning(f"⚠️ Missing: {', '.join(parsed_voice['missing_fields'])} - Please fill manually above")
        
        # Clear button
        clear_col1, clear_col2, clear_col3 = st.columns([2, 1, 2])
        with clear_col2:
            if st.button(f"🗑️ {t('clear_voice')}", use_container_width=True):
                st.session_state.voice_extracted_data = None
                st.rerun()
    
    st.markdown("---")
    
    # Run Triage Button - Centered and prominent
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        run_triage = st.button(f"🎯 {t('run_triage')}", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # Results area
    if run_triage:
        # Prepare patient data
        patient_data = {
            "age": age,
            "gender": gender,
            "vitals": {
                "heart_rate": float(hr),
                "sbp": float(sbp),
                "dbp": float(dbp),
                "temp_c": float(temp),
                "spo2": float(spo2)
            },
            "symptoms": symptoms_text,
            "medical_history": medical_history if medical_history else "None"
        }
        
        with st.spinner("🔄 Analyzing patient data..."):
            result, error = submit_triage(patient_data)
            
            if error:
                st.error(f"❌ {error}")
            else:
                # Display risk status
                display_risk_status(result)
                
                # Override warning
                if result.get('override_applied'):
                    st.markdown(f"""
                    <div class="override-warning">
                        <h3 style="margin-top:0;">⚠️ SAFETY OVERRIDE APPLIED</h3>
                        <p style="font-size:1.1rem; margin-bottom:0;"><strong>Reason:</strong> {result.get('override_reason', 'Critical vital signs detected')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Metrics row
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric(t('risk_level'), result['risk'].upper())
                
                with metric_col2:
                    st.metric(t('department'), result['department'])
                
                with metric_col3:
                    st.metric(t('confidence'), f"{result['confidence']*100:.1f}%")
                
                st.markdown("---")
                
                # Clinical reasoning with detailed disease and department info
                st.markdown(f"### 💭 {t('clinical_assessment')}")
                
                detailed_reasoning = get_detailed_clinical_reasoning(
                    result['department'],
                    result['risk'],
                    symptoms_text,
                    patient_data['vitals']
                )
                
                st.markdown(detailed_reasoning)
                
                # Original AI explanation
                st.markdown(f"**{t('ai_analysis')}**")
                st.info(result['explanation'])
                
                # Feature importance
                if result.get('top_factors'):
                    st.markdown("---")
                    display_feature_importance(result['top_factors'])
                
                # Add to queue
                add_to_queue(patient_data, result, patient_name, patient_id)
    else:
        # Welcome message with instructions
        st.info("👆 Enter patient information above and click 'RUN AI TRIAGE' to begin assessment")
        
        # Show possible diseases based on current inputs (if any symptoms or abnormal vitals)
        if input_method == "Manual Entry":
            # Check if user has entered any data
            has_symptoms = symptoms_text and symptoms_text != "No specific symptoms"
            has_abnormal_vitals = (hr > 100 or hr < 60 or sbp > 140 or sbp < 90 or 
                                  temp > 38.0 or spo2 < 95)
            
            if has_symptoms or has_abnormal_vitals:
                st.markdown("---")
                st.markdown("### 🔍 Preliminary Assessment")
                st.caption("Based on entered data. Click 'RUN AI TRIAGE' for complete analysis.")
                
                possible_conditions = []
                
                # Check for cardiac conditions
                if ("chest pain" in symptoms_text.lower() or hr > 100 or sbp > 140):
                    possible_conditions.append({
                        "name": "Acute Coronary Syndrome / Myocardial Infarction",
                        "description": "Heart attack caused by blocked blood flow to the heart muscle. Symptoms include chest pain, shortness of breath, sweating, and nausea.",
                        "department": "Cardiology / Emergency",
                        "urgency": "🔴 HIGH"
                    })
                
                # Check for stroke
                if ("facial drooping" in symptoms_text.lower() or "slurred speech" in symptoms_text.lower() or 
                    "weakness" in symptoms_text.lower() or sbp > 160):
                    possible_conditions.append({
                        "name": "Cerebrovascular Accident (Stroke)",
                        "description": "Interruption of blood supply to the brain causing neurological symptoms. Symptoms include facial drooping, slurred speech, one-sided weakness, and confusion.",
                        "department": "Neurology / Emergency",
                        "urgency": "🔴 HIGH"
                    })
                
                # Check for respiratory conditions
                if ("shortness of breath" in symptoms_text.lower() or "wheezing" in symptoms_text.lower() or 
                    "cough" in symptoms_text.lower() or spo2 < 92):
                    possible_conditions.append({
                        "name": "Respiratory Distress / Pneumonia",
                        "description": "Lung infection or breathing difficulty causing reduced oxygen levels. Symptoms include shortness of breath, cough, fever, and low oxygen saturation.",
                        "department": "Respiratory / Emergency",
                        "urgency": "🔴 HIGH" if spo2 < 90 else "🟡 MEDIUM"
                    })
                
                # Check for sepsis
                if (temp > 39.0 or temp < 36.0) and (hr > 110 or sbp < 100):
                    possible_conditions.append({
                        "name": "Sepsis / Severe Infection",
                        "description": "Life-threatening response to infection causing organ dysfunction. Symptoms include extreme temperature, rapid heart rate, low blood pressure, and confusion.",
                        "department": "Emergency / Intensive Care",
                        "urgency": "🔴 HIGH"
                    })
                
                # Check for hypertensive crisis
                if sbp > 180:
                    possible_conditions.append({
                        "name": "Hypertensive Crisis",
                        "description": "Severely elevated blood pressure that can damage organs. Requires immediate treatment to prevent complications.",
                        "department": "Emergency / Cardiology",
                        "urgency": "🔴 HIGH"
                    })
                
                # Check for appendicitis
                if "abdominal pain" in symptoms_text.lower() and temp > 37.5:
                    possible_conditions.append({
                        "name": "Acute Appendicitis",
                        "description": "Inflammation of the appendix causing abdominal pain, typically in the lower right quadrant. May require surgical intervention.",
                        "department": "Surgery / Emergency",
                        "urgency": "🟡 MEDIUM"
                    })
                
                # Display possible conditions
                if possible_conditions:
                    for condition in possible_conditions[:3]:  # Show top 3 matches
                        with st.expander(f"{condition['urgency']} {condition['name']}", expanded=False):
                            st.markdown(f"**Description:** {condition['description']}")
                            st.markdown(f"**Recommended Department:** 🏥 {condition['department']}")
                            st.markdown(f"**Urgency Level:** {condition['urgency']}")
                else:
                    st.info("No specific conditions identified based on current inputs.")

if __name__ == "__main__":
    main()
