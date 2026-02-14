# Project Structure

## Directory Layout

```
pulse-triage-ai/
│
├── api/                          # Backend API
│   ├── __pycache__/             # Python cache (auto-generated)
│   ├── main.py                  # FastAPI application
│   └── ehr_endpoints.py         # EHR integration endpoints
│
├── app/                          # Frontend Dashboard
│   ├── __pycache__/             # Python cache (auto-generated)
│   └── main.py                  # Streamlit dashboard (1122 lines)
│
├── config/                       # Configuration
│   ├── __init__.py              # Package init
│   └── settings.py              # Application settings
│
├── data/                         # Training Data
│   └── triage_golden_50.csv     # 50 synthetic patients
│
├── docs/                         # Documentation
│   ├── API_DOCUMENTATION.md     # API endpoint documentation
│   ├── DEPLOYMENT.md            # Production deployment guide
│   ├── design.md                # Technical design document
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── requirements.md          # Requirements specification
│   └── SETUP.md                 # Setup and installation guide
│
├── integrations/                 # EHR/EMR Integration
│   ├── __pycache__/             # Python cache (auto-generated)
│   ├── __init__.py              # Package init
│   ├── ehr_adapter.py           # Unified EHR adapter
│   ├── fhir_integration.py      # FHIR R4 handler
│   └── hl7_integration.py       # HL7 v2.x handler
│
├── ml/                           # Machine Learning
│   └── models/                  # Trained models (6 files)
│       ├── dept_encoder.pkl     # Department label encoder
│       ├── dept_model.pkl       # Department classifier
│       ├── metadata.pkl         # Feature names & symptom keywords
│       ├── risk_encoder.pkl     # Risk level label encoder
│       ├── risk_model.pkl       # Risk classifier
│       └── scaler.pkl           # Feature scaler
│
├── scripts/                      # Utility Scripts
│   ├── __init__.py              # Package init
│   ├── generate_golden_50.py   # Generate training data
│   ├── run_api.py               # Start API server
│   ├── run_dashboard.py         # Start dashboard
│   └── train_final.py           # Train ML models
│
├── tests/                        # Test Suite
│   ├── __init__.py              # Package init
│   ├── example_document_upload.py  # Document upload example
│   ├── test_api.py              # API endpoint tests
│   ├── test_ehr_integration.py  # EHR integration tests
│   └── test_parser_with_dataset.py  # Parser tests
│
├── utils/                        # Utilities
│   ├── __pycache__/             # Python cache (auto-generated)
│   ├── auth.py                  # Authentication module
│   └── parser.py                # Clinical note parser
│
├── .gitignore                    # Git ignore rules
├── README.md                     # Project overview
└── requirements.txt              # Python dependencies
```

## File Descriptions

### Core Application Files

#### `api/main.py` (Backend)
- FastAPI application with CORS middleware
- ML model manager with LOOCV training
- 7 rule-based safety overrides
- Feature engineering (39 features)
- Triage prediction endpoint
- Health check endpoint
- EHR integration router

#### `app/main.py` (Frontend)
- Streamlit dashboard (1122 lines)
- Authentication system
- Multilingual support (English/Tamil/Hindi)
- Voice assistant with AI analysis
- Clinical document parser integration
- Real-time disease suggestions
- Patient queue management
- Color-coded risk display
- Detailed clinical reasoning

### Configuration

#### `config/settings.py`
- API and dashboard configuration
- Model paths and data directories
- Safety thresholds for rule overrides
- Authentication settings
- EHR integration settings
- Supported languages

### Machine Learning

#### `scripts/generate_golden_50.py`
- Generates 50 synthetic patients
- 9 disease profiles (Stroke, MI, Sepsis, etc.)
- Realistic vital signs with variance
- Clinical notes for each patient
- Distribution: 10 HIGH, 15 MEDIUM, 25 LOW

#### `scripts/train_final.py`
- Random Forest classifier training
- Leave-One-Out Cross-Validation
- Feature engineering (39 features)
- Model evaluation and metrics
- Saves 6 model files to ml/models/

#### `ml/models/` (6 files)
- `risk_model.pkl`: Risk level classifier
- `dept_model.pkl`: Department classifier
- `scaler.pkl`: StandardScaler for features
- `risk_encoder.pkl`: Risk level label encoder
- `dept_encoder.pkl`: Department label encoder
- `metadata.pkl`: Feature names and symptom keywords

### Utilities

#### `utils/parser.py`
- Regex-based clinical note parser
- Extracts vitals, demographics, symptoms
- Medical history extraction
- Confidence scoring
- Temperature conversion (F→C)
- 85.7% extraction confidence

#### `utils/auth.py`
- Authentication manager
- SHA-256 password hashing
- Session management
- Login/logout functions
- User info storage

### EHR Integration

#### `integrations/ehr_adapter.py`
- Unified interface for multiple formats
- Auto-format detection
- Import/export patient data
- Validation functions

#### `integrations/hl7_integration.py`
- HL7 v2.x message handler
- ADT and ORU message support
- Parse PID, OBX, DG1 segments
- Generate ORU messages
- LOINC code mapping

#### `integrations/fhir_integration.py`
- FHIR R4 resource handler
- Patient, Observation, Condition resources
- DiagnosticReport creation
- Bundle generation
- LOINC code mapping

#### `api/ehr_endpoints.py`
- 8 EHR integration endpoints
- Import/export functionality
- HL7 parse/generate
- FHIR parse/generate
- Format listing
- Health check

### Tests

#### `tests/test_api.py`
- 6 comprehensive API tests
- Health check test
- Rule override tests (SpO2, BP)
- ML prediction tests (Stroke, MI, Low risk)
- All tests passing

#### `tests/test_ehr_integration.py`
- HL7 message parsing tests
- FHIR resource parsing tests
- Import/export tests
- Format detection tests

#### `tests/test_parser_with_dataset.py`
- Parser accuracy tests
- Extraction confidence tests
- Missing field detection tests

### Documentation

#### `docs/requirements.md`
- Functional requirements
- Non-functional requirements
- Safety requirements
- Performance targets

#### `docs/design.md`
- System architecture
- Pydantic models
- API endpoints
- Mermaid diagrams
- Database schema

#### `docs/SETUP.md`
- Installation instructions
- Running the system
- Troubleshooting guide
- Configuration options

#### `docs/API_DOCUMENTATION.md`
- Endpoint specifications
- Request/response examples
- Error handling
- Interactive docs link

#### `docs/DEPLOYMENT.md`
- Production checklist
- Docker deployment
- Cloud deployment (AWS/Azure/GCP)
- Scaling strategies
- Backup and disaster recovery

### Scripts

#### `scripts/run_api.py`
- Starts FastAPI server
- Configurable host and port
- Logging configuration

#### `scripts/run_dashboard.py`
- Starts Streamlit dashboard
- Configurable port
- Headless mode

## Data Flow

```
User Input (Dashboard)
    ↓
Streamlit UI (app/main.py)
    ↓
HTTP POST Request
    ↓
FastAPI Backend (api/main.py)
    ↓
Rule-Based Overrides Check
    ↓ (if no override)
Feature Engineering (39 features)
    ↓
ML Model Prediction
    ↓
Response with Explanation
    ↓
Display Results (Dashboard)
```

## Module Dependencies

```
app/main.py
├── utils/parser.py
├── utils/auth.py
└── api/main.py (HTTP)

api/main.py
├── integrations/ehr_adapter.py
├── api/ehr_endpoints.py
└── ml/models/*.pkl

integrations/ehr_adapter.py
├── integrations/hl7_integration.py
└── integrations/fhir_integration.py

scripts/train_final.py
├── data/triage_golden_50.csv
└── ml/models/*.pkl (output)
```

## Key Metrics

- **Total Lines of Code**: ~5,000+
- **Main Dashboard**: 1,122 lines
- **API Backend**: ~500 lines
- **EHR Integration**: ~1,200 lines
- **ML Training**: ~400 lines
- **Tests**: ~300 lines
- **Documentation**: ~2,000 lines

## Technology Stack

### Backend
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.0

### Machine Learning
- Scikit-learn 1.4.0
- NumPy 1.26.3
- Pandas 2.2.0
- Joblib 1.3.2

### Frontend
- Streamlit 1.30.0
- Plotly 5.18.0
- Requests 2.31.0

### Testing
- Pytest 7.4.4

## Version Control

Recommended `.gitignore` includes:
- Python cache (`__pycache__/`)
- Virtual environments (`venv/`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Logs (`*.log`)
- Environment variables (`.env`)

## Next Steps

1. Review [SETUP.md](SETUP.md) for installation
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
3. Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
4. See [requirements.md](requirements.md) for detailed requirements
5. Review [design.md](design.md) for technical architecture
