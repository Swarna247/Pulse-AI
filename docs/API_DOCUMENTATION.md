# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

**GET** `/health`

Check API server health and model status.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "risk_classes": ["High", "Medium", "Low"],
  "dept_classes": ["Cardiology", "Emergency", "Neurology", ...]
}
```

---

### Triage Patient

**POST** `/api/triage`

Submit patient data for triage assessment.

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "risk": "High",
  "department": "Cardiology",
  "confidence": 0.85,
  "explanation": "AI Classification: High risk with 85% confidence...",
  "override_applied": false,
  "override_reason": null,
  "top_factors": [
    "Abnormal blood pressure (BP: 160/95 mmHg)",
    "Abnormal heart rate (HR: 110 bpm)",
    "Chest pain reported",
    "Pre-existing conditions: Hypertension, Diabetes",
    "Advanced age (65 years)"
  ],
  "all_probabilities": {
    "High": 0.85,
    "Medium": 0.12,
    "Low": 0.03
  }
}
```

---

## EHR Integration Endpoints

### Import Patient Data

**POST** `/ehr/import`

Import patient data from EHR system (HL7, FHIR, or JSON).

**Request:**
```json
{
  "data": "{\"resourceType\": \"Patient\", ...}",
  "format": "fhir"
}
```

**Response:**
```json
{
  "success": true,
  "format_detected": "fhir",
  "patient_data": {...},
  "message": "Patient data imported successfully"
}
```

---

### Export Triage Results

**POST** `/ehr/export`

Export triage results to EHR system.

**Request:**
```json
{
  "triage_result": {...},
  "patient_data": {...},
  "format": "fhir"
}
```

---

### Parse HL7 Message

**POST** `/ehr/hl7/parse`

Parse HL7 v2.x message.

---

### Generate HL7 Message

**POST** `/ehr/hl7/generate`

Generate HL7 ORU message with triage results.

---

### Parse FHIR Resource

**POST** `/ehr/fhir/parse`

Parse FHIR R4 resource.

---

### Generate FHIR Bundle

**POST** `/ehr/fhir/generate`

Generate FHIR Bundle with triage results.

---

### Get Supported Formats

**GET** `/ehr/formats`

List supported EHR/EMR formats.

---

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request (validation error)
- `500`: Internal Server Error
