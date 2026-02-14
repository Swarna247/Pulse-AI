"""
FastAPI Backend for Smart Patient Triage System
Implements rule-based safety overrides + ML predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum
import joblib
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import EHR endpoints
try:
    from ehr_endpoints import router as ehr_router
    EHR_INTEGRATION_AVAILABLE = True
except ImportError:
    logger.warning("EHR integration module not available")
    EHR_INTEGRATION_AVAILABLE = False

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    TRANSGENDER = "Transgender"
    OTHERS = "Others"

class VitalSigns(BaseModel):
    heart_rate: float = Field(..., ge=30, le=200, description="Heart rate in bpm")
    sbp: float = Field(..., ge=60, le=250, description="Systolic BP in mmHg")
    dbp: float = Field(..., ge=40, le=150, description="Diastolic BP in mmHg")
    temp_c: float = Field(..., ge=35.0, le=42.0, description="Temperature in Celsius")
    spo2: float = Field(..., ge=70, le=100, description="Oxygen saturation %")
    
    @validator('dbp')
    def validate_bp_relationship(cls, v, values):
        if 'sbp' in values and v >= values['sbp']:
            raise ValueError('Diastolic BP must be less than Systolic BP')
        return v

class PatientInput(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: Gender
    vitals: VitalSigns
    symptoms: str = Field(..., max_length=1000, description="Patient symptoms")
    medical_history: str = Field(default="None", max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 65,
                "gender": "Male",
                "vitals": {
                    "heart_rate": 110,
                    "sbp": 160,
                    "dbp": 95,
                    "temp_c": 38.5,
                    "spo2": 92
                },
                "symptoms": "Chest pain, shortness of breath, sweating",
                "medical_history": "Hypertension, Diabetes"
            }
        }

class TriageResponse(BaseModel):
    risk: str
    department: str
    confidence: float
    explanation: str
    override_applied: bool
    override_reason: Optional[str] = None
    top_factors: List[str]
    all_probabilities: Dict[str, float]

# ============================================================================
# MODEL MANAGER
# ============================================================================

class TriageModelManager:
    """Manages ML models and makes predictions"""
    
    def __init__(self, model_dir='ml/models'):
        self.model_dir = Path(model_dir)
        self.risk_model = None
        self.dept_model = None
        self.scaler = None
        self.risk_encoder = None
        self.dept_encoder = None
        self.metadata = None
        self.symptom_keywords = []
        self.feature_names = []

    
    def load_models(self):
        """Load all models and transformers on startup"""
        try:
            logger.info(f"Loading models from {self.model_dir}...")
            
            self.risk_model = joblib.load(self.model_dir / 'risk_model.pkl')
            logger.info("✓ Loaded risk_model.pkl")
            
            self.dept_model = joblib.load(self.model_dir / 'dept_model.pkl')
            logger.info("✓ Loaded dept_model.pkl")
            
            self.scaler = joblib.load(self.model_dir / 'scaler.pkl')
            logger.info("✓ Loaded scaler.pkl")
            
            self.risk_encoder = joblib.load(self.model_dir / 'risk_encoder.pkl')
            logger.info("✓ Loaded risk_encoder.pkl")
            
            self.dept_encoder = joblib.load(self.model_dir / 'dept_encoder.pkl')
            logger.info("✓ Loaded dept_encoder.pkl")
            
            self.metadata = joblib.load(self.model_dir / 'metadata.pkl')
            self.symptom_keywords = self.metadata['symptom_keywords']
            self.feature_names = self.metadata['feature_names']
            logger.info("✓ Loaded metadata.pkl")
            
            logger.info(f"✓ All models loaded successfully!")
            logger.info(f"  Risk classes: {self.metadata['risk_classes']}")
            logger.info(f"  Dept classes: {self.metadata['dept_classes']}")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def check_rule_overrides(self, patient: PatientInput) -> Optional[Dict]:
        """
        Check critical vital thresholds for safety overrides
        Returns override dict if triggered, None otherwise
        """
        vitals = patient.vitals
        
        # Critical SpO2
        if vitals.spo2 < 90:
            return {
                'risk': 'High',
                'department': 'Emergency',
                'reason': f'Critical oxygen saturation: SpO2 {vitals.spo2:.0f}% < 90%',
                'confidence': 1.0
            }
        
        # Hypertensive Crisis
        if vitals.sbp > 180:
            return {
                'risk': 'High',
                'department': 'Emergency',
                'reason': f'Hypertensive crisis: Systolic BP {vitals.sbp:.0f} mmHg > 180',
                'confidence': 1.0
            }
        
        # Severe Hypotension
        if vitals.sbp < 90:
            return {
                'risk': 'High',
                'department': 'Emergency',
                'reason': f'Severe hypotension: Systolic BP {vitals.sbp:.0f} mmHg < 90',
                'confidence': 1.0
            }
        
        # Severe Tachycardia
        if vitals.heart_rate > 120:
            return {
                'risk': 'High',
                'department': 'Cardiology',
                'reason': f'Severe tachycardia: Heart rate {vitals.heart_rate:.0f} bpm > 120',
                'confidence': 1.0
            }
        
        # Severe Bradycardia
        if vitals.heart_rate < 50:
            return {
                'risk': 'High',
                'department': 'Cardiology',
                'reason': f'Severe bradycardia: Heart rate {vitals.heart_rate:.0f} bpm < 50',
                'confidence': 1.0
            }
        
        # High Fever
        if vitals.temp_c > 39.5:
            return {
                'risk': 'High',
                'department': 'Emergency',
                'reason': f'High fever: Temperature {vitals.temp_c:.1f}°C > 39.5°C',
                'confidence': 1.0
            }
        
        # Pediatric fever (infants)
        if patient.age < 2 and vitals.temp_c > 38.0:
            return {
                'risk': 'High',
                'department': 'Emergency',
                'reason': f'Infant with fever: Age {patient.age}, Temp {vitals.temp_c:.1f}°C',
                'confidence': 1.0
            }
        
        return None
    
    def extract_symptom_features(self, symptoms_text: str) -> List[int]:
        """Extract binary features from symptom text"""
        symptoms_lower = symptoms_text.lower()
        return [1 if keyword in symptoms_lower else 0 for keyword in self.symptom_keywords]
    
    def engineer_features(self, patient: PatientInput) -> np.ndarray:
        """Convert patient data to feature vector"""
        features = []
        
        # Demographics
        features.append(patient.age)
        features.append(1 if patient.gender == Gender.MALE else 0)
        
        # Vital signs
        vitals = patient.vitals
        features.append(vitals.heart_rate)
        features.append(vitals.sbp)
        features.append(vitals.dbp)
        features.append(vitals.temp_c)
        features.append(vitals.spo2)
        
        # Derived vitals
        pulse_pressure = vitals.sbp - vitals.dbp
        map_pressure = vitals.dbp + (pulse_pressure / 3)
        features.append(pulse_pressure)
        features.append(map_pressure)
        
        # Medical history flags
        history = patient.medical_history.lower()
        features.append(1 if 'hypertension' in history else 0)
        features.append(1 if 'diabetes' in history else 0)
        features.append(1 if any(word in history for word in ['cardiac', 'heart', 'mi']) else 0)
        features.append(1 if any(word in history for word in ['copd', 'asthma', 'respiratory']) else 0)
        
        # Symptom features
        symptom_features = self.extract_symptom_features(patient.symptoms)
        features.extend(symptom_features)
        
        return np.array(features).reshape(1, -1)
    
    def get_top_contributing_factors(self, patient: PatientInput, features_scaled: np.ndarray) -> List[str]:
        """Identify top contributing factors for explanation"""
        factors = []
        vitals = patient.vitals
        
        # Check critical vitals
        if vitals.spo2 < 94:
            factors.append(f"Low oxygen saturation (SpO2: {vitals.spo2:.0f}%)")
        
        if vitals.sbp > 140 or vitals.sbp < 100:
            factors.append(f"Abnormal blood pressure (BP: {vitals.sbp:.0f}/{vitals.dbp:.0f} mmHg)")
        
        if vitals.heart_rate > 100 or vitals.heart_rate < 60:
            factors.append(f"Abnormal heart rate (HR: {vitals.heart_rate:.0f} bpm)")
        
        if vitals.temp_c > 38.0:
            factors.append(f"Elevated temperature ({vitals.temp_c:.1f}°C)")
        
        # Check key symptoms
        symptoms_lower = patient.symptoms.lower()
        critical_symptoms = [
            ('chest pain', 'Chest pain reported'),
            ('shortness of breath', 'Shortness of breath'),
            ('confusion', 'Altered mental status'),
            ('drooping', 'Neurological symptoms (facial drooping)'),
            ('slurred speech', 'Speech difficulties'),
            ('severe pain', 'Severe pain reported')
        ]
        
        for keyword, description in critical_symptoms:
            if keyword in symptoms_lower:
                factors.append(description)
        
        # Check medical history
        history = patient.medical_history.lower()
        if 'hypertension' in history or 'diabetes' in history:
            factors.append(f"Pre-existing conditions: {patient.medical_history}")
        
        # Age factor
        if patient.age > 65:
            factors.append(f"Advanced age ({patient.age} years)")
        elif patient.age < 5:
            factors.append(f"Pediatric patient ({patient.age} years)")
        
        return factors[:5]  # Return top 5 factors
    
    def predict(self, patient: PatientInput) -> TriageResponse:
        """Make triage prediction with safety overrides"""
        
        # Step 1: Check rule-based overrides
        override = self.check_rule_overrides(patient)
        
        if override:
            logger.info(f"Rule override triggered: {override['reason']}")
            factors = self.get_top_contributing_factors(patient, None)
            
            return TriageResponse(
                risk=override['risk'],
                department=override['department'],
                confidence=override['confidence'],
                explanation=override['reason'],
                override_applied=True,
                override_reason=override['reason'],
                top_factors=factors,
                all_probabilities={'High': 1.0, 'Medium': 0.0, 'Low': 0.0}
            )
        
        # Step 2: AI Prediction
        try:
            # Engineer features
            features = self.engineer_features(patient)
            features_scaled = self.scaler.transform(features)
            
            # Predict risk
            risk_pred = self.risk_model.predict(features_scaled)[0]
            risk_proba = self.risk_model.predict_proba(features_scaled)[0]
            risk_label = self.risk_encoder.inverse_transform([risk_pred])[0]
            risk_confidence = float(max(risk_proba))
            
            # Predict department
            dept_pred = self.dept_model.predict(features_scaled)[0]
            dept_proba = self.dept_model.predict_proba(features_scaled)[0]
            dept_label = self.dept_encoder.inverse_transform([dept_pred])[0]
            
            # Get all risk probabilities
            risk_probs = {
                cls: float(prob) 
                for cls, prob in zip(self.risk_encoder.classes_, risk_proba)
            }
            
            # Get top contributing factors
            factors = self.get_top_contributing_factors(patient, features_scaled)
            
            # Generate explanation
            explanation = f"AI Classification: {risk_label} risk with {risk_confidence:.1%} confidence. "
            explanation += f"Recommended department: {dept_label}."
            
            logger.info(f"AI Prediction: Risk={risk_label} ({risk_confidence:.3f}), Dept={dept_label}")
            
            return TriageResponse(
                risk=risk_label,
                department=dept_label,
                confidence=round(risk_confidence, 3),
                explanation=explanation,
                override_applied=False,
                override_reason=None,
                top_factors=factors,
                all_probabilities=risk_probs
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Smart Patient Triage API",
    description="AI-powered patient triage system with safety-first rule overrides",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include EHR integration router if available
if EHR_INTEGRATION_AVAILABLE:
    app.include_router(ehr_router)
    logger.info("EHR integration endpoints enabled")

# Initialize model manager
model_manager = TriageModelManager()

@app.on_event("startup")
async def startup_event():
    """Load models on application startup"""
    logger.info("Starting Smart Patient Triage API...")
    model_manager.load_models()
    logger.info("API ready to accept requests!")
    if EHR_INTEGRATION_AVAILABLE:
        logger.info("EHR/EMR integration available at /ehr/*")

@app.get("/")
async def root():
    """Root endpoint"""
    endpoints = {
        "triage": "/api/triage",
        "health": "/health",
        "docs": "/docs"
    }
    
    if EHR_INTEGRATION_AVAILABLE:
        endpoints["ehr_integration"] = "/ehr/*"
    
    return {
        "message": "Smart Patient Triage API",
        "version": "1.0.0",
        "status": "operational",
        "ehr_integration": EHR_INTEGRATION_AVAILABLE,
        "endpoints": endpoints
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    models_loaded = all([
        model_manager.risk_model is not None,
        model_manager.dept_model is not None,
        model_manager.scaler is not None
    ])
    
    return {
        "status": "healthy" if models_loaded else "unhealthy",
        "models_loaded": models_loaded,
        "risk_classes": model_manager.metadata['risk_classes'] if model_manager.metadata else [],
        "dept_classes": model_manager.metadata['dept_classes'] if model_manager.metadata else []
    }

@app.post("/api/triage", response_model=TriageResponse)
async def triage_patient(patient: PatientInput):
    """
    Triage endpoint - Predicts risk level and recommended department
    
    Flow:
    1. Check rule-based safety overrides (critical vitals)
    2. If no override, use ML models for prediction
    3. Return structured response with explanation
    """
    logger.info(f"Triage request: Age={patient.age}, Gender={patient.gender}")
    logger.info(f"  Vitals: HR={patient.vitals.heart_rate}, BP={patient.vitals.sbp}/{patient.vitals.dbp}, "
                f"Temp={patient.vitals.temp_c}, SpO2={patient.vitals.spo2}")
    
    try:
        response = model_manager.predict(patient)
        logger.info(f"Response: Risk={response.risk}, Dept={response.department}, "
                   f"Confidence={response.confidence}, Override={response.override_applied}")
        return response
        
    except Exception as e:
        logger.error(f"Triage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
