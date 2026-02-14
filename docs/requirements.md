# Requirements Document: AI-Powered Smart Patient Triage System

## 1. Project Overview

### 1.1 Purpose
Develop an intelligent patient triage system that automatically classifies patient risk levels (Low/Medium/High) and recommends appropriate departments based on clinical data, with full explainability for medical staff decision support.

### 1.2 Target Users
- Emergency Department (ED) nurses and triage staff
- Clinical administrators
- Healthcare providers requiring rapid patient prioritization

### 1.3 Hackathon Constraints
- Development timeframe: 32 hours
- Focus on MVP with core functionality
- Emphasis on safety and explainability over feature completeness

## 2. Functional Requirements

### 2.1 Data Ingestion (Phase 1)

#### FR-1.1: Manual Data Entry
- System SHALL provide a web form for manual entry of patient vitals and symptoms
- Form SHALL capture: Age, Gender, Heart Rate, Systolic BP, Diastolic BP, Temperature, SpO2, Pre-existing conditions, Symptoms (free text)
- System SHALL validate all numeric inputs against medically reasonable ranges
- System SHALL support real-time validation feedback

#### FR-1.2: Document Upload and Parsing
- System SHALL accept PDF and text-based EHR documents
- System SHALL extract structured data from unstructured medical documents using PyMuPDF
- System SHALL use LLM-based structuring to map extracted text to data schema
- System SHALL handle parsing failures gracefully with fallback to manual entry
- System SHALL display extracted data for clinical review before processing

#### FR-1.3: Data Validation and Cleaning
- System SHALL flag missing critical fields (vitals, age)
- System SHALL normalize text inputs (symptoms, conditions)
- System SHALL detect and flag physiologically impossible values
- System SHALL maintain audit trail of all data transformations

### 2.2 AI-Powered Risk Classification (Phase 2)

#### FR-2.1: Machine Learning Classification
- System SHALL use Random Forest classifier for risk prediction
- Model SHALL output three risk categories: Low, Medium, High
- Model SHALL provide confidence scores for each prediction
- System SHALL retrain capability with new validated cases

#### FR-2.2: Department Recommendation
- System SHALL recommend appropriate department based on symptoms and vitals
- Departments include: Emergency, Cardiology, Respiratory, General Medicine, Pediatrics, ICU
- System SHALL support multi-department recommendations when appropriate

#### FR-2.3: Rule-Based Safety Overrides
- System SHALL implement hard-coded rules for critical vital signs
- Critical thresholds SHALL override ML predictions to ensure patient safety
- Rules SHALL include:
  - SpO2 < 90% → High Risk, Respiratory/ICU
  - Systolic BP > 180 or < 90 → High Risk, Emergency
  - Heart Rate > 120 or < 50 → High Risk, Cardiology/Emergency
  - Temperature > 39.5°C → Medium/High Risk
- System SHALL log all override events for model improvement

### 2.3 Explainability Layer (Phase 3)

#### FR-3.1: SHAP-Based Feature Importance
- System SHALL generate SHAP values for each prediction
- System SHALL identify top 5 contributing features for each case
- System SHALL provide visual representation of feature impacts

#### FR-3.2: Clinical Reasoning Output
- System SHALL generate human-readable reasoning string explaining the decision
- Reasoning SHALL reference specific vitals and symptoms
- System SHALL display confidence score (0-100%) for the prediction
- System SHALL indicate if rule-based override was applied

### 2.4 Real-Time Dashboard (Phase 4)

#### FR-4.1: Patient Queue Visualization
- Dashboard SHALL display prioritized list of patients sorted by risk level
- Dashboard SHALL use color coding: Red (High), Yellow (Medium), Green (Low)
- Dashboard SHALL show key vitals and recommended department for each patient
- Dashboard SHALL auto-refresh with new patient submissions

#### FR-4.2: Patient Detail View
- Dashboard SHALL provide drill-down view for individual patients
- Detail view SHALL show complete vitals, SHAP visualization, and reasoning
- Detail view SHALL display confidence metrics and override indicators

#### FR-4.3: Queue Management
- Dashboard SHALL allow marking patients as "Seen" or "In Progress"
- Dashboard SHALL track wait times from submission to assessment
- Dashboard SHALL provide basic statistics (total patients, risk distribution)

## 3. Non-Functional Requirements

### 3.1 Safety and Reliability

#### NFR-1.1: High Recall for High-Risk Cases
- System SHALL prioritize sensitivity over specificity for High Risk classification
- Target: ≥95% recall for High Risk cases (minimize false negatives)
- Acceptable: Lower precision (more false positives acceptable for safety)

#### NFR-1.2: Fail-Safe Behavior
- System SHALL default to High Risk classification in case of model failure
- System SHALL never downgrade a rule-based High Risk classification
- System SHALL maintain operation even if AI engine fails (rule-based fallback)

### 3.2 Performance

#### NFR-2.1: Response Time
- Document parsing SHALL complete within 10 seconds for typical EHR documents
- Risk prediction SHALL return results within 2 seconds
- Dashboard SHALL refresh within 3 seconds

#### NFR-2.2: Scalability
- System SHALL handle at least 50 concurrent patient submissions
- System SHALL maintain performance with queue of 200+ patients

### 3.3 Usability

#### NFR-3.1: Clinical Interface
- Dashboard SHALL be intuitive for non-technical medical staff
- System SHALL use medical terminology familiar to ED staff
- Explainability outputs SHALL be clinically meaningful

#### NFR-3.2: Accessibility
- Interface SHALL be readable in high-stress clinical environments
- Color coding SHALL include text labels for color-blind users

### 3.4 Transparency and Auditability

#### NFR-4.1: Decision Transparency
- Every prediction SHALL include explainability output
- System SHALL log all inputs, predictions, and reasoning
- System SHALL provide version tracking for model and rules

#### NFR-4.2: Data Privacy
- System SHALL not persist identifiable patient data beyond session (hackathon scope)
- System SHALL comply with basic data handling best practices
- Production deployment SHALL require HIPAA compliance review

## 4. Data Requirements

### 4.1 Input Data Schema

#### Patient Metadata
- Age: Integer (0-120 years)
- Gender: Enum (Male, Female, Other, Unknown)

#### Vital Signs
- Heart Rate: Integer (30-200 bpm)
- Systolic BP: Integer (60-250 mmHg)
- Diastolic BP: Integer (40-150 mmHg)
- Temperature: Float (35.0-42.0°C)
- SpO2: Integer (70-100%)

#### Clinical Information
- Pre-existing Conditions: List of strings (e.g., "Diabetes", "Hypertension", "Asthma")
- Symptoms: Free text (max 1000 characters)
- Chief Complaint: String (optional, extracted from document)

### 4.2 Output Data Schema

#### Prediction Result
- Risk Level: Enum (Low, Medium, High)
- Confidence Score: Float (0.0-1.0)
- Recommended Department: String or List[String]
- Reasoning: String (human-readable explanation)
- Override Applied: Boolean
- SHAP Values: Dictionary of feature contributions
- Timestamp: DateTime

## 5. Technical Constraints

### 5.1 Technology Stack
- Backend Framework: FastAPI (Python 3.9+)
- Frontend: Streamlit
- ML Framework: Scikit-learn (Random Forest)
- Explainability: SHAP library
- Document Parsing: PyMuPDF (fitz)
- LLM Integration: OpenAI API or local model for text structuring
- Data Validation: Pydantic v2

### 5.2 Development Environment
- Version Control: Git
- Dependency Management: pip/poetry
- Testing: pytest (basic unit tests for critical functions)

## 6. Success Criteria

### 6.1 Minimum Viable Product (MVP)
- ✓ Manual data entry form functional
- ✓ Basic document parsing (at least PDF support)
- ✓ ML model trained and making predictions
- ✓ Rule-based overrides implemented
- ✓ SHAP explanations generated
- ✓ Dashboard displaying prioritized queue
- ✓ End-to-end flow from input to dashboard working

### 6.2 Hackathon Demo Requirements
- Live demonstration of complete patient flow
- Example of High Risk case with explanation
- Example of rule-based override
- Dashboard showing multiple patients with different risk levels
- Clear visualization of SHAP feature importance

### 6.3 Safety Validation
- Manual testing of critical vital thresholds
- Verification that no High Risk case is classified as Low
- Confirmation that rule overrides cannot be bypassed

## 7. Out of Scope (Post-Hackathon)

- Integration with real EHR systems (HL7, FHIR)
- User authentication and role-based access control
- Full HIPAA compliance implementation
- Mobile application
- Multi-language support
- Advanced ML models (deep learning, ensemble methods)
- Real-time vital sign monitoring integration
- Bed assignment and resource allocation
- Historical patient data analysis and trends

## 8. Assumptions and Dependencies

### 8.1 Assumptions
- Training data available or can be synthesized for hackathon
- LLM API access available for document structuring
- Single-user deployment sufficient for demo
- In-memory data storage acceptable (no database required)

### 8.2 Dependencies
- Python 3.9+ runtime environment
- Internet access for LLM API calls (if using cloud-based)
- Modern web browser for Streamlit dashboard
- Sufficient compute for Random Forest inference (<1 second)

## 9. Risk Assessment

### 9.1 Technical Risks
- **Document parsing accuracy**: Mitigation - Manual review step before processing
- **Model performance on limited training data**: Mitigation - Strong rule-based fallback
- **LLM API rate limits/costs**: Mitigation - Caching, local model fallback

### 9.2 Safety Risks
- **False negative High Risk cases**: Mitigation - High recall threshold, rule overrides
- **Over-reliance on AI by clinical staff**: Mitigation - Clear disclaimers, explainability
- **Data quality issues**: Mitigation - Strict validation, manual review options

## 10. Future Enhancements (Post-Hackathon)

- Integration with hospital bed management systems
- Predictive wait time estimation
- Automated patient outcome tracking for model improvement
- Multi-site deployment with centralized monitoring
- Advanced NLP for symptom extraction and standardization
- Integration with wearable devices for continuous monitoring
- Telemedicine triage support
