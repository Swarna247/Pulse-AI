"""
HL7 v2.x Integration Module
Handles HL7 message parsing and generation for hospital system integration
"""

from datetime import datetime
from typing import Dict, Optional, List
import re


class HL7Integration:
    """
    HL7 v2.x message handler for patient triage data
    Supports ADT (Admission/Discharge/Transfer) and ORU (Observation Result) messages
    """
    
    def __init__(self):
        self.field_separator = '|'
        self.component_separator = '^'
        self.repetition_separator = '~'
        self.escape_character = '\\'
        self.subcomponent_separator = '&'
        
    def parse_hl7_message(self, hl7_message: str) -> Dict:
        """
        Parse HL7 v2.x message and extract patient data
        
        Args:
            hl7_message: Raw HL7 message string
            
        Returns:
            Dictionary with parsed patient data
        """
        segments = hl7_message.strip().split('\n')
        patient_data = {
            'patient_id': None,
            'name': None,
            'age': None,
            'gender': None,
            'vitals': {},
            'symptoms': '',
            'medical_history': ''
        }
        
        for segment in segments:
            segment_type = segment[:3]
            
            if segment_type == 'PID':  # Patient Identification
                patient_data.update(self._parse_pid_segment(segment))
            elif segment_type == 'OBX':  # Observation/Result
                self._parse_obx_segment(segment, patient_data)
            elif segment_type == 'DG1':  # Diagnosis
                self._parse_dg1_segment(segment, patient_data)
                
        return patient_data
    
    def _parse_pid_segment(self, segment: str) -> Dict:
        """Parse PID (Patient Identification) segment"""
        fields = segment.split(self.field_separator)
        
        patient_data = {}
        
        # PID-3: Patient ID
        if len(fields) > 3:
            patient_data['patient_id'] = fields[3].split(self.component_separator)[0]
        
        # PID-5: Patient Name
        if len(fields) > 5:
            name_components = fields[5].split(self.component_separator)
            if len(name_components) >= 2:
                patient_data['name'] = f"{name_components[1]} {name_components[0]}"
        
        # PID-7: Date of Birth (calculate age)
        if len(fields) > 7:
            dob = fields[7]
            if dob:
                patient_data['age'] = self._calculate_age_from_dob(dob)
        
        # PID-8: Gender
        if len(fields) > 8:
            gender_code = fields[8]
            gender_map = {'M': 'Male', 'F': 'Female', 'O': 'Others', 'U': 'Others'}
            patient_data['gender'] = gender_map.get(gender_code, 'Others')
        
        return patient_data
    
    def _parse_obx_segment(self, segment: str, patient_data: Dict):
        """Parse OBX (Observation Result) segment for vital signs"""
        fields = segment.split(self.field_separator)
        
        if len(fields) < 6:
            return
        
        # OBX-3: Observation Identifier
        observation_id = fields[3].split(self.component_separator)[0]
        
        # OBX-5: Observation Value
        observation_value = fields[5]
        
        # Map LOINC codes to vital signs
        vital_mapping = {
            '8867-4': 'heart_rate',      # Heart rate
            '8480-6': 'sbp',              # Systolic BP
            '8462-4': 'dbp',              # Diastolic BP
            '8310-5': 'temp_c',           # Body temperature
            '2708-6': 'spo2',             # Oxygen saturation
        }
        
        if observation_id in vital_mapping:
            vital_name = vital_mapping[observation_id]
            try:
                patient_data['vitals'][vital_name] = float(observation_value)
            except ValueError:
                pass
    
    def _parse_dg1_segment(self, segment: str, patient_data: Dict):
        """Parse DG1 (Diagnosis) segment for medical history"""
        fields = segment.split(self.field_separator)
        
        if len(fields) > 3:
            diagnosis = fields[3].split(self.component_separator)
            if len(diagnosis) > 1:
                if patient_data['medical_history']:
                    patient_data['medical_history'] += f", {diagnosis[1]}"
                else:
                    patient_data['medical_history'] = diagnosis[1]
    
    def _calculate_age_from_dob(self, dob: str) -> int:
        """Calculate age from HL7 date format (YYYYMMDD)"""
        try:
            if len(dob) >= 8:
                year = int(dob[:4])
                current_year = datetime.now().year
                return current_year - year
        except ValueError:
            pass
        return None
    
    def generate_oru_message(self, triage_result: Dict, patient_data: Dict) -> str:
        """
        Generate HL7 ORU (Observation Result) message with triage results
        
        Args:
            triage_result: Triage prediction results
            patient_data: Patient information
            
        Returns:
            HL7 ORU message string
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_id = f"TRIAGE{timestamp}"
        
        # MSH - Message Header
        msh = self._create_msh_segment(message_id, timestamp)
        
        # PID - Patient Identification
        pid = self._create_pid_segment(patient_data)
        
        # OBR - Observation Request
        obr = self._create_obr_segment(message_id, timestamp)
        
        # OBX - Observation Results (Triage Results)
        obx_segments = self._create_triage_obx_segments(triage_result)
        
        # Combine all segments
        message = '\n'.join([msh, pid, obr] + obx_segments)
        
        return message
    
    def _create_msh_segment(self, message_id: str, timestamp: str) -> str:
        """Create MSH (Message Header) segment"""
        return (
            f"MSH|^~\\&|TRIAGE_SYSTEM|HOSPITAL|EHR_SYSTEM|HOSPITAL|"
            f"{timestamp}||ORU^R01|{message_id}|P|2.5"
        )
    
    def _create_pid_segment(self, patient_data: Dict) -> str:
        """Create PID (Patient Identification) segment"""
        patient_id = patient_data.get('patient_id', 'UNKNOWN')
        name = patient_data.get('name', 'UNKNOWN^PATIENT')
        dob = self._age_to_dob(patient_data.get('age', 0))
        gender = patient_data.get('gender', 'U')[0].upper()
        
        return f"PID|1||{patient_id}||{name}||{dob}|{gender}"
    
    def _create_obr_segment(self, message_id: str, timestamp: str) -> str:
        """Create OBR (Observation Request) segment"""
        return (
            f"OBR|1|{message_id}||TRIAGE^AI Triage Assessment^LOCAL||"
            f"{timestamp}|||||||||||||||||||F"
        )
    
    def _create_triage_obx_segments(self, triage_result: Dict) -> List[str]:
        """Create OBX segments for triage results"""
        obx_segments = []
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # OBX-1: Risk Level
        obx_segments.append(
            f"OBX|1|ST|RISK_LEVEL^Risk Level^LOCAL||"
            f"{triage_result['risk']}||||||F|||{timestamp}"
        )
        
        # OBX-2: Department
        obx_segments.append(
            f"OBX|2|ST|DEPARTMENT^Recommended Department^LOCAL||"
            f"{triage_result['department']}||||||F|||{timestamp}"
        )
        
        # OBX-3: Confidence
        confidence_pct = triage_result['confidence'] * 100
        obx_segments.append(
            f"OBX|3|NM|CONFIDENCE^Prediction Confidence^LOCAL||"
            f"{confidence_pct:.1f}|%|||||F|||{timestamp}"
        )
        
        # OBX-4: Explanation
        explanation = triage_result.get('explanation', '').replace('|', ' ')
        obx_segments.append(
            f"OBX|4|TX|REASONING^Clinical Reasoning^LOCAL||"
            f"{explanation}||||||F|||{timestamp}"
        )
        
        return obx_segments
    
    def _age_to_dob(self, age: int) -> str:
        """Convert age to approximate DOB in HL7 format"""
        if not age:
            return ''
        year = datetime.now().year - age
        return f"{year}0101"
    
    def validate_hl7_message(self, message: str) -> tuple[bool, str]:
        """
        Validate HL7 message structure
        
        Returns:
            (is_valid, error_message)
        """
        if not message:
            return False, "Empty message"
        
        segments = message.strip().split('\n')
        
        if not segments:
            return False, "No segments found"
        
        # Check for MSH segment
        if not segments[0].startswith('MSH'):
            return False, "Missing MSH segment"
        
        # Check field separator
        if len(segments[0]) < 4 or segments[0][3] != '|':
            return False, "Invalid field separator"
        
        return True, "Valid HL7 message"


# Example HL7 ADT^A01 message (Patient Admission)
EXAMPLE_HL7_ADT = """MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20240214120000||ADT^A01|MSG00001|P|2.5
EVN|A01|20240214120000
PID|1||PT-2024-001^^^HOSPITAL^MR||DOE^JOHN^A||19740515|M|||123 MAIN ST^^CITY^STATE^12345||555-1234|||S||PT-2024-001|123-45-6789
PV1|1|E|ER^101^01||||1234^SMITH^JOHN^A^^^MD|||||||||||1234567890|||||||||||||||||||||||||20240214120000
OBX|1|NM|8867-4^Heart Rate^LN||110|/min|||||F
OBX|2|NM|8480-6^Systolic BP^LN||165|mmHg|||||F
OBX|3|NM|8462-4^Diastolic BP^LN||95|mmHg|||||F
OBX|4|NM|8310-5^Body Temperature^LN||38.5|Cel|||||F
OBX|5|NM|2708-6^Oxygen Saturation^LN||92|%|||||F
DG1|1||I10^Hypertension^ICD10||20240214120000"""

# Example HL7 ORU^R01 message (Observation Result)
EXAMPLE_HL7_ORU = """MSH|^~\\&|LAB|HOSPITAL|EHR|HOSPITAL|20240214120000||ORU^R01|MSG00002|P|2.5
PID|1||PT-2024-001^^^HOSPITAL^MR||DOE^JOHN^A||19740515|M
OBR|1|ORDER123||TRIAGE^AI Triage Assessment^LOCAL||20240214120000|||||||||||||||||||F
OBX|1|ST|RISK_LEVEL^Risk Level^LOCAL||High||||||F|||20240214120000
OBX|2|ST|DEPARTMENT^Recommended Department^LOCAL||Cardiology||||||F|||20240214120000
OBX|3|NM|CONFIDENCE^Prediction Confidence^LOCAL||85.5|%|||||F|||20240214120000
OBX|4|TX|REASONING^Clinical Reasoning^LOCAL||Patient presents with elevated BP and tachycardia suggesting cardiac event||||||F|||20240214120000"""
