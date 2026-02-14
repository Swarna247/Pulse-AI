"""
EHR Adapter - Unified interface for multiple EHR/EMR systems
Supports HL7, FHIR, and custom hospital formats
"""

from typing import Dict, Optional, List, Literal
from .hl7_integration import HL7Integration
from .fhir_integration import FHIRIntegration
import json


class EHRAdapter:
    """
    Unified adapter for EHR/EMR system integration
    Automatically detects format and routes to appropriate handler
    """
    
    def __init__(self, default_format: Literal['hl7', 'fhir', 'json'] = 'fhir'):
        self.hl7_handler = HL7Integration()
        self.fhir_handler = FHIRIntegration()
        self.default_format = default_format
        
    def import_patient_data(self, data: str, format: Optional[str] = None) -> Dict:
        """
        Import patient data from EHR system
        
        Args:
            data: Raw data string (HL7 message, FHIR JSON, or custom format)
            format: Data format ('hl7', 'fhir', 'json') - auto-detected if None
            
        Returns:
            Standardized patient data dictionary
        """
        if format is None:
            format = self._detect_format(data)
        
        if format == 'hl7':
            return self.hl7_handler.parse_hl7_message(data)
        elif format == 'fhir':
            fhir_data = json.loads(data) if isinstance(data, str) else data
            return self._parse_fhir_bundle(fhir_data)
        elif format == 'json':
            return json.loads(data) if isinstance(data, str) else data
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_triage_results(self, triage_result: Dict, patient_data: Dict, 
                             format: Optional[str] = None) -> str:
        """
        Export triage results to EHR system
        
        Args:
            triage_result: Triage prediction results
            patient_data: Patient information
            format: Export format ('hl7', 'fhir', 'json')
            
        Returns:
            Formatted data string ready for EHR system
        """
        format = format or self.default_format
        
        if format == 'hl7':
            return self.hl7_handler.generate_oru_message(triage_result, patient_data)
        elif format == 'fhir':
            return self._create_fhir_bundle(triage_result, patient_data)
        elif format == 'json':
            return json.dumps({
                'patient': patient_data,
                'triage': triage_result,
                'timestamp': self._get_timestamp()
            }, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _detect_format(self, data: str) -> str:
        """Auto-detect data format"""
        data_stripped = data.strip()
        
        # Check for HL7 (starts with MSH)
        if data_stripped.startswith('MSH|'):
            return 'hl7'
        
        # Check for FHIR JSON
        try:
            parsed = json.loads(data_stripped)
            if isinstance(parsed, dict) and 'resourceType' in parsed:
                return 'fhir'
            return 'json'
        except json.JSONDecodeError:
            pass
        
        # Default to HL7 if contains pipe separators
        if '|' in data_stripped:
            return 'hl7'
        
        return 'json'
    
    def _parse_fhir_bundle(self, fhir_data: Dict) -> Dict:
        """Parse FHIR Bundle or single resource"""
        patient_data = {
            'patient_id': None,
            'name': None,
            'age': None,
            'gender': None,
            'vitals': {},
            'symptoms': '',
            'medical_history': ''
        }
        
        # Handle Bundle
        if fhir_data.get('resourceType') == 'Bundle':
            entries = fhir_data.get('entry', [])
            
            observations = []
            conditions = []
            
            for entry in entries:
                resource = entry.get('resource', {})
                resource_type = resource.get('resourceType')
                
                if resource_type == 'Patient':
                    patient_data.update(self.fhir_handler.parse_fhir_patient(resource))
                elif resource_type == 'Observation':
                    observations.append(resource)
                elif resource_type == 'Condition':
                    conditions.append(resource)
            
            if observations:
                self.fhir_handler.parse_fhir_observations(observations, patient_data)
            if conditions:
                self.fhir_handler.parse_fhir_conditions(conditions, patient_data)
        
        # Handle single Patient resource
        elif fhir_data.get('resourceType') == 'Patient':
            patient_data.update(self.fhir_handler.parse_fhir_patient(fhir_data))
        
        return patient_data
    
    def _create_fhir_bundle(self, triage_result: Dict, patient_data: Dict) -> str:
        """Create FHIR Bundle with triage results"""
        patient_id = patient_data.get('patient_id', 'UNKNOWN')
        
        resources = []
        
        # Create Patient resource
        patient_resource = self.fhir_handler.create_patient_resource(patient_data)
        resources.append(patient_resource)
        
        # Create Observation resources for vitals
        vitals = patient_data.get('vitals', {})
        for vital_name, value in vitals.items():
            obs = self.fhir_handler.create_observation_resource(
                patient_id, vital_name, value, None
            )
            if obs:
                resources.append(obs)
        
        # Create DiagnosticReport for triage results
        report = self.fhir_handler.create_diagnostic_report(patient_id, triage_result)
        resources.append(report)
        
        # Create Bundle
        bundle = self.fhir_handler.create_bundle(resources, bundle_type="transaction")
        
        return json.dumps(bundle, indent=2)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat() + "Z"
    
    def validate_import(self, data: str, format: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate imported data
        
        Returns:
            (is_valid, error_message)
        """
        try:
            if format is None:
                format = self._detect_format(data)
            
            if format == 'hl7':
                return self.hl7_handler.validate_hl7_message(data)
            elif format == 'fhir':
                fhir_data = json.loads(data) if isinstance(data, str) else data
                return self.fhir_handler.validate_fhir_resource(fhir_data)
            elif format == 'json':
                json.loads(data) if isinstance(data, str) else data
                return True, "Valid JSON"
            else:
                return False, f"Unknown format: {format}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Integration Examples
class EHRIntegrationExamples:
    """Example usage patterns for EHR integration"""
    
    @staticmethod
    def example_hl7_import():
        """Example: Import patient from HL7 ADT message"""
        adapter = EHRAdapter()
        
        hl7_message = """MSH|^~\\&|SENDING_APP|HOSPITAL|TRIAGE|HOSPITAL|20240214120000||ADT^A01|MSG001|P|2.5
PID|1||PT-2024-001^^^HOSPITAL^MR||DOE^JOHN^A||19740515|M
OBX|1|NM|8867-4^Heart Rate^LN||110|/min|||||F
OBX|2|NM|8480-6^Systolic BP^LN||165|mmHg|||||F
OBX|3|NM|8462-4^Diastolic BP^LN||95|mmHg|||||F"""
        
        patient_data = adapter.import_patient_data(hl7_message, format='hl7')
        print("Imported patient:", patient_data)
        return patient_data
    
    @staticmethod
    def example_fhir_import():
        """Example: Import patient from FHIR Bundle"""
        adapter = EHRAdapter()
        
        fhir_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "PT-2024-001",
                        "name": [{"given": ["John"], "family": "Doe"}],
                        "gender": "male",
                        "birthDate": "1974-05-15"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "8867-4"
                            }]
                        },
                        "valueQuantity": {"value": 110}
                    }
                }
            ]
        }
        
        patient_data = adapter.import_patient_data(json.dumps(fhir_bundle), format='fhir')
        print("Imported patient:", patient_data)
        return patient_data
    
    @staticmethod
    def example_export_results():
        """Example: Export triage results to EHR"""
        adapter = EHRAdapter(default_format='fhir')
        
        patient_data = {
            'patient_id': 'PT-2024-001',
            'name': 'John Doe',
            'age': 50,
            'gender': 'Male',
            'vitals': {
                'heart_rate': 110,
                'sbp': 165,
                'dbp': 95,
                'temp_c': 38.5,
                'spo2': 92
            }
        }
        
        triage_result = {
            'risk': 'High',
            'department': 'Cardiology',
            'confidence': 0.85,
            'explanation': 'Patient presents with elevated BP and tachycardia',
            'override_applied': False
        }
        
        # Export as FHIR
        fhir_output = adapter.export_triage_results(triage_result, patient_data, format='fhir')
        print("FHIR Export:", fhir_output[:200], "...")
        
        # Export as HL7
        hl7_output = adapter.export_triage_results(triage_result, patient_data, format='hl7')
        print("HL7 Export:", hl7_output[:200], "...")
        
        return fhir_output, hl7_output
