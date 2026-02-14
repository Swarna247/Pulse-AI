"""
Configuration Settings for Smart Patient Triage System
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_URL = f"http://localhost:{API_PORT}"

# Dashboard Configuration
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8501))

# Model Configuration
MODEL_DIR = BASE_DIR / "ml" / "models"
DATA_DIR = BASE_DIR / "data"

# Model Files
RISK_MODEL_PATH = MODEL_DIR / "risk_model.pkl"
DEPT_MODEL_PATH = MODEL_DIR / "dept_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
RISK_ENCODER_PATH = MODEL_DIR / "risk_encoder.pkl"
DEPT_ENCODER_PATH = MODEL_DIR / "dept_encoder.pkl"
METADATA_PATH = MODEL_DIR / "metadata.pkl"

# Training Data
TRAINING_DATA_PATH = DATA_DIR / "triage_golden_50.csv"

# Authentication
DEFAULT_ADMIN_EMAIL = "admin@gmail.com"
DEFAULT_ADMIN_PASSWORD = "admin@123"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Safety Thresholds (Rule-based overrides)
SAFETY_THRESHOLDS = {
    "spo2_critical": 90,
    "sbp_high": 180,
    "sbp_low": 90,
    "hr_high": 120,
    "hr_low": 50,
    "temp_high": 39.5,
    "infant_age": 2,
    "infant_temp": 38.0
}

# Model Performance Targets
TARGET_METRICS = {
    "risk_accuracy": 0.95,
    "dept_accuracy": 0.95,
    "high_risk_recall": 0.90
}

# EHR Integration
EHR_INTEGRATION_ENABLED = True
DEFAULT_EHR_FORMAT = "fhir"  # Options: "hl7", "fhir", "json"

# Supported Languages
SUPPORTED_LANGUAGES = ["English", "Tamil", "Hindi"]
DEFAULT_LANGUAGE = "English"
