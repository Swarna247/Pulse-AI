"""
FHIR R4 Integration Module
Handles FHIR resource creation and parsing for modern EHR systems
"""

from datetime import datetime
from typing import Dict, Optional, List
import json


class FHIRIntegration:
    """
    FHIR R4 resource handler for patient triage data
    Supports Patient, Observation, and DiagnosticReport resources
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/fhir"):
        self.base_url = base_url
        self.fhir_version = "4.0.1"
    
    def parse_fhir_patient(self, patient_resource: Dict) -> Dict:
        """
        Parse FHIR Patient resource and extract data
        
        Args:
            patient_resource: FHIR Patient resource (JSON)
            
        Returns:
            Dictionary with parsed patient data
        """
        patient_data = {
            'patient_id': None,
            'name': None,
            'age': None,
            'gender': None,
            'vitals': {},
            'symptoms': '',
            'medical_history': ''
        }
        
        # Extract patient ID
        if 'id' in patient_resource:
            patient_data['patient_id'] = patient_resource['id']
        
        # Extract name
        if 'name' in patient_resource and len(patient_resource['name']) > 0:
            name_obj = patient_resource['name'][0]
            given = ' '.join(name_obj.get('given', []))
            family = name_obj.get('family', '')
            patient_data['name'] = f"{given} {family}".strip()
        
        # Extract birth date and calculate age
        if 'birthDate' in patient_resource:
            patient_data['age'] = self._calculate_age_from_birthdate(
                patient_resource['birthDate']
            )
        
        # Extract gender
        if 'gender' in patient_resource:
            gender_map = {
                'male': 'Male',
                'female': 'Female',
                'other': 'Others',
                'unknown': 'Others'
            }
            patient_data['gender'] = gender_map.get(
                patient_resource['gender'].lower(), 'Others'
            )
        
        return patient_data
    
    def parse_fhir_observations(self, observations: List[Dict], patient_data: Dict):
        """
        Parse FHIR Observation resources for vital signs
        
        Args:
            observations: List of FHIR Observation resources
            patient_data: Patient data dictionary to update
        """
        for obs in observations:
            if 'code' not in obs or 'valueQuantity' not in obs:
                continue
            
            # Get LOINC code
            loinc_code = None
            if 'coding' in obs['code']:
                for coding in obs['code']['coding']:
                    if coding.get('system') == 'http://loinc.org':
                        loinc_code = coding.get('code')
                        break
            
            if not loinc_code:
                continue
            
            # Map LOINC codes to vital signs
            vital_mapping = {
                '8867-4': 'heart_rate',
                '8480-6': 'sbp',
                '8462-4': 'dbp',
                '8310-5': 'temp_c',
                '2708-6': 'spo2',
            }
            
            if loinc_code in vital_mapping:
                vital_name = vital_mapping[loinc_code]
                value = obs['valueQuantity'].get('value')
                if value is not None:
                    patient_data['vitals'][vital_name] = float(value)
    
    def parse_fhir_conditions(self, conditions: List[Dict], patient_data: Dict):
        """
        Parse FHIR Condition resources for medical history
        
        Args:
            conditions: List of FHIR Condition resources
            patient_data: Patient data dictionary to update
        """
        history_items = []
        
        for condition in conditions:
            if 'code' not in condition:
                continue
            
            # Get condition text
            condition_text = condition['code'].get('text', '')
            
            if not condition_text and 'coding' in condition['code']:
                for coding in condition['code']['coding']:
                    if 'display' in coding:
                        condition_text = coding['display']
                        break
            
            if condition_text:
                history_items.append(condition_text)
        
        if history_items:
            patient_data['medical_history'] = ', '.join(history_items)
    
    def _calculate_age_from_birthdate(self, birthdate: str) -> int:
        """Calculate age from FHIR date format (YYYY-MM-DD)"""
        try:
            birth_year = int(birthdate[:4])
            current_year = datetime.now().year
            return current_year - birth_year
        except (ValueError, IndexError):
            return None
    
    def create_patient_resource(self, patient_data: Dict) -> Dict:
        """
        Create FHIR Patient resource
        
        Args:
            patient_data: Patient information dictionary
            
        Returns:
            FHIR Patient resource (JSON)
        """
        patient_id = patient_data.get('patient_id', f"PT-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Parse name
        name_parts = patient_data.get('name', 'Unknown Patient').split()
        given_names = name_parts[:-1] if len(name_parts) > 1 else name_parts
        family_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        # Calculate birth date from age
        birth_date = self._age_to_birthdate(patient_data.get('age', 0))
        
        # Map gender
        gender_map = {
            'Male': 'male',
            'Female': 'female',
            'Transgender': 'other',
            'Others': 'other'
        }
        gender = gender_map.get(patient_data.get('gender', 'Others'), 'unknown')
        
        resource = {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat() + "Z"
            },
            "identifier": [
                {
                    "system": "http://hospital.org/patients",
                    "value": patient_id
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "family": family_name,
                    "given": given_names
                }
            ],
            "gender": gender,
            "birthDate": birth_date
        }
        
        return resource
    
    def create_observation_resource(self, patient_id: str, vital_name: str, 
                                   value: float, unit: str) -> Dict:
        """
        Create FHIR Observation resource for vital sign
        
        Args:
            patient_id: Patient identifier
            vital_name: Name of vital sign
            value: Vital sign value
            unit: Unit of measurement
            
        Returns:
            FHIR Observation resource (JSON)
        """
        # LOINC codes for vital signs
        loinc_codes = {
            'heart_rate': ('8867-4', 'Heart rate', '/min'),
            'sbp': ('8480-6', 'Systolic blood pressure', 'mmHg'),
            'dbp': ('8462-4', 'Diastolic blood pressure', 'mmHg'),
            'temp_c': ('8310-5', 'Body temperature', 'Cel'),
            'spo2': ('2708-6', 'Oxygen saturation', '%'),
        }
        
        if vital_name not in loinc_codes:
            return None
        
        loinc_code, display, default_unit = loinc_codes[vital_name]
        unit = unit or default_unit
        
        obs_id = f"obs-{patient_id}-{vital_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        resource = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat() + "Z"
            },
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": loinc_code,
                        "display": display
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat() + "Z",
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit
            }
        }
        
        return resource
    
    def create_diagnostic_report(self, patient_id: str, triage_result: Dict) -> Dict:
        """
        Create FHIR DiagnosticReport resource for triage results
        
        Args:
            patient_id: Patient identifier
            triage_result: Triage prediction results
            
        Returns:
            FHIR DiagnosticReport resource (JSON)
        """
        report_id = f"triage-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create conclusion text
        conclusion = f"""
AI Triage Assessment Results:

Risk Level: {triage_result['risk'].upper()}
Recommended Department: {triage_result['department']}
Confidence: {triage_result['confidence']*100:.1f}%

Clinical Reasoning:
{triage_result.get('explanation', 'No explanation provided')}
"""
        
        if triage_result.get('override_applied'):
            conclusion += f"\n\nSafety Override Applied: {triage_result.get('override_reason', 'Critical vital signs detected')}"
        
        resource = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat() + "Z"
            },
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                            "code": "OTH",
                            "display": "Other"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://hospital.org/codes",
                        "code": "AI-TRIAGE",
                        "display": "AI-Powered Triage Assessment"
                    }
                ],
                "text": "AI Triage Assessment"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat() + "Z",
            "issued": datetime.now().isoformat() + "Z",
            "conclusion": conclusion.strip(),
            "conclusionCode": [
                {
                    "coding": [
                        {
                            "system": "http://hospital.org/triage-codes",
                            "code": triage_result['risk'].upper(),
                            "display": f"{triage_result['risk'].upper()} Risk"
                        }
                    ]
                }
            ]
        }
        
        return resource
    
    def create_bundle(self, resources: List[Dict], bundle_type: str = "transaction") -> Dict:
        """
        Create FHIR Bundle resource containing multiple resources
        
        Args:
            resources: List of FHIR resources
            bundle_type: Bundle type (transaction, batch, collection)
            
        Returns:
            FHIR Bundle resource (JSON)
        """
        bundle_id = f"bundle-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        entries = []
        for resource in resources:
            entry = {
                "resource": resource
            }
            
            if bundle_type == "transaction":
                entry["request"] = {
                    "method": "POST",
                    "url": resource['resourceType']
                }
            
            entries.append(entry)
        
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "lastUpdated": datetime.now().isoformat() + "Z"
            },
            "type": bundle_type,
            "entry": entries
        }
        
        return bundle
    
    def _age_to_birthdate(self, age: int) -> str:
        """Convert age to approximate birth date in FHIR format"""
        if not age:
            return datetime.now().strftime('%Y-%m-%d')
        year = datetime.now().year - age
        return f"{year}-01-01"
    
    def validate_fhir_resource(self, resource: Dict) -> tuple[bool, str]:
        """
        Validate FHIR resource structure
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(resource, dict):
            return False, "Resource must be a dictionary"
        
        if 'resourceType' not in resource:
            return False, "Missing resourceType"
        
        valid_types = ['Patient', 'Observation', 'Condition', 'DiagnosticReport', 'Bundle']
        if resource['resourceType'] not in valid_types:
            return False, f"Invalid resourceType: {resource['resourceType']}"
        
        return True, "Valid FHIR resource"


# Example FHIR Patient resource
EXAMPLE_FHIR_PATIENT = {
    "resourceType": "Patient",
    "id": "PT-2024-001",
    "identifier": [
        {
            "system": "http://hospital.org/patients",
            "value": "PT-2024-001"
        }
    ],
    "active": True,
    "name": [
        {
            "use": "official",
            "family": "Doe",
            "given": ["John", "A"]
        }
    ],
    "gender": "male",
    "birthDate": "1974-05-15"
}

# Example FHIR Observation (Heart Rate)
EXAMPLE_FHIR_OBSERVATION = {
    "resourceType": "Observation",
    "id": "obs-hr-001",
    "status": "final",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "8867-4",
                "display": "Heart rate"
            }
        ]
    },
    "subject": {
        "reference": "Patient/PT-2024-001"
    },
    "effectiveDateTime": "2024-02-14T12:00:00Z",
    "valueQuantity": {
        "value": 110,
        "unit": "/min",
        "system": "http://unitsofmeasure.org",
        "code": "/min"
    }
}
