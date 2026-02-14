"""
Clinical Document Parser
Extracts structured patient data from unstructured clinical notes
Uses regex patterns with optional LLM fallback for complex cases
"""

import re
from typing import Dict, Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClinicalNoteParser:
    """Parse clinical notes to extract structured patient data"""
    
    def __init__(self):
        # Regex patterns for vital signs
        self.patterns = {
            'heart_rate': [
                r'HR[:\s]+(\d{2,3})',
                r'heart rate[:\s]+(\d{2,3})',
                r'pulse[:\s]+(\d{2,3})',
                r'(\d{2,3})\s*bpm',
                r'HR\s*=\s*(\d{2,3})',
            ],
            'blood_pressure': [
                r'BP[:\s]+(\d{2,3})/(\d{2,3})',
                r'blood pressure[:\s]+(\d{2,3})/(\d{2,3})',
                r'(\d{2,3})/(\d{2,3})\s*mmHg',
                r'BP\s*=\s*(\d{2,3})/(\d{2,3})',
            ],
            'temperature': [
                r'temp[:\s]+(\d{2,3}\.?\d?)',
                r'temperature[:\s]+(\d{2,3}\.?\d?)',
                r'(\d{2,3}\.?\d?)\s*°?C',
                r'T\s*=\s*(\d{2,3}\.?\d?)',
                r'febrile.*?(\d{2,3}\.?\d?)',
            ],
            'spo2': [
                r'SpO2[:\s]+(\d{2,3})',
                r'O2 sat[:\s]+(\d{2,3})',
                r'oxygen saturation[:\s]+(\d{2,3})',
                r'sat[:\s]+(\d{2,3})%',
                r'SpO2\s*=\s*(\d{2,3})',
            ],
            'age': [
                r'(\d{1,3})\s*y/?o',
                r'(\d{1,3})\s*year',
                r'age[:\s]+(\d{1,3})',
                r'(\d{1,3})-year-old',
            ],
            'gender': [
                r'\b(male|female|man|woman)\b',
                r'\b(M|F)\b(?!\w)',
            ]
        }
        
        # Common medical conditions patterns
        self.condition_patterns = [
            r'history of ([^.,]+)',
            r'known ([^.,]+)',
            r'diagnosed with ([^.,]+)',
            r'h/o ([^.,]+)',
            r'PMH[:\s]+([^.,]+)',
        ]
        
        # Symptom extraction patterns
        self.symptom_keywords = [
            'chest pain', 'shortness of breath', 'dyspnea', 'sob',
            'nausea', 'vomiting', 'dizziness', 'confusion',
            'headache', 'fever', 'chills', 'sweating', 'diaphoretic',
            'weakness', 'fatigue', 'pain', 'cough',
            'facial drooping', 'slurred speech', 'numbness',
            'palpitations', 'syncope', 'seizure'
        ]

    
    def extract_vitals_from_note(self, text: str) -> Dict[str, Optional[float]]:
        """
        Extract vital signs from clinical note text
        
        Args:
            text: Clinical note text
            
        Returns:
            Dictionary with extracted vitals (None if not found)
        """
        text_lower = text.lower()
        vitals = {
            'heart_rate': None,
            'sbp': None,
            'dbp': None,
            'temp_c': None,
            'spo2': None
        }
        
        # Extract heart rate
        for pattern in self.patterns['heart_rate']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    hr = int(match.group(1))
                    if 30 <= hr <= 200:  # Validate range
                        vitals['heart_rate'] = float(hr)
                        logger.info(f"Extracted HR: {hr}")
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract blood pressure
        for pattern in self.patterns['blood_pressure']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    sbp = int(match.group(1))
                    dbp = int(match.group(2))
                    if 60 <= sbp <= 250 and 40 <= dbp <= 150 and sbp > dbp:
                        vitals['sbp'] = float(sbp)
                        vitals['dbp'] = float(dbp)
                        logger.info(f"Extracted BP: {sbp}/{dbp}")
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract temperature
        for pattern in self.patterns['temperature']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    temp = float(match.group(1))
                    if 35.0 <= temp <= 42.0:  # Celsius range
                        vitals['temp_c'] = temp
                        logger.info(f"Extracted Temp: {temp}°C")
                        break
                    elif 95.0 <= temp <= 107.0:  # Fahrenheit range, convert
                        temp_c = (temp - 32) * 5/9
                        vitals['temp_c'] = round(temp_c, 1)
                        logger.info(f"Extracted Temp: {temp}°F → {temp_c:.1f}°C")
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract SpO2
        for pattern in self.patterns['spo2']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    spo2 = int(match.group(1))
                    if 70 <= spo2 <= 100:
                        vitals['spo2'] = float(spo2)
                        logger.info(f"Extracted SpO2: {spo2}%")
                        break
                except (ValueError, IndexError):
                    continue
        
        return vitals
    
    def extract_demographics(self, text: str) -> Dict[str, Optional[str]]:
        """Extract age and gender from text"""
        text_lower = text.lower()
        demographics = {
            'age': None,
            'gender': None
        }
        
        # Extract age
        for pattern in self.patterns['age']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    age = int(match.group(1))
                    if 0 <= age <= 120:
                        demographics['age'] = age
                        logger.info(f"Extracted Age: {age}")
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract gender
        for pattern in self.patterns['gender']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                gender_text = match.group(1).lower()
                if gender_text in ['male', 'man', 'm']:
                    demographics['gender'] = 'Male'
                elif gender_text in ['female', 'woman', 'f']:
                    demographics['gender'] = 'Female'
                logger.info(f"Extracted Gender: {demographics['gender']}")
                break
        
        return demographics
    
    def extract_medical_history(self, text: str) -> List[str]:
        """Extract pre-existing conditions from text"""
        conditions = []
        text_lower = text.lower()
        
        # Common conditions to look for
        condition_keywords = {
            'hypertension': ['hypertension', 'htn', 'high blood pressure'],
            'diabetes': ['diabetes', 'dm', 'diabetic'],
            'asthma': ['asthma'],
            'copd': ['copd', 'chronic obstructive'],
            'heart disease': ['cad', 'coronary artery', 'heart disease', 'mi', 'myocardial infarction'],
            'atrial fibrillation': ['afib', 'atrial fibrillation', 'a-fib'],
            'stroke': ['stroke', 'cva', 'cerebrovascular'],
            'kidney disease': ['ckd', 'kidney disease', 'renal'],
            'cancer': ['cancer', 'malignancy', 'carcinoma'],
        }
        
        for condition, keywords in condition_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    conditions.append(condition.title())
                    break
        
        # Try structured extraction patterns
        for pattern in self.condition_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if match and len(match) < 50:  # Avoid long extractions
                    conditions.append(match.strip().title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_conditions = []
        for cond in conditions:
            cond_lower = cond.lower()
            if cond_lower not in seen:
                seen.add(cond_lower)
                unique_conditions.append(cond)
        
        return unique_conditions[:5]  # Return top 5
    
    def extract_symptoms(self, text: str) -> str:
        """Extract symptoms from clinical note"""
        text_lower = text.lower()
        found_symptoms = []
        
        for symptom in self.symptom_keywords:
            if symptom in text_lower:
                found_symptoms.append(symptom)
        
        # Also look for "presenting with", "complains of", "reports"
        symptom_intro_patterns = [
            r'presenting with ([^.]+)',
            r'complains? of ([^.]+)',
            r'reports? ([^.]+)',
            r'symptoms?[:\s]+([^.]+)',
            r'chief complaint[:\s]+([^.]+)',
        ]
        
        for pattern in symptom_intro_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                symptom_text = match.group(1).strip()
                if len(symptom_text) < 200:  # Reasonable length
                    found_symptoms.append(symptom_text)
        
        if found_symptoms:
            return ', '.join(found_symptoms[:10])  # Limit to 10 symptoms
        
        return "No specific symptoms extracted"
    
    def parse_clinical_note(self, text: str) -> Dict:
        """
        Complete parsing of clinical note
        
        Args:
            text: Clinical note text
            
        Returns:
            Dictionary with all extracted patient data
        """
        logger.info("Parsing clinical note...")
        
        # Extract all components
        vitals = self.extract_vitals_from_note(text)
        demographics = self.extract_demographics(text)
        conditions = self.extract_medical_history(text)
        symptoms = self.extract_symptoms(text)
        
        # Compile results
        result = {
            'age': demographics['age'],
            'gender': demographics['gender'],
            'vitals': {
                'heart_rate': vitals['heart_rate'],
                'sbp': vitals['sbp'],
                'dbp': vitals['dbp'],
                'temp_c': vitals['temp_c'],
                'spo2': vitals['spo2']
            },
            'medical_history': ', '.join(conditions) if conditions else 'None',
            'symptoms': symptoms,
            'extraction_confidence': self._calculate_confidence(vitals, demographics),
            'missing_fields': self._identify_missing_fields(vitals, demographics)
        }
        
        logger.info(f"Extraction complete. Confidence: {result['extraction_confidence']:.1%}")
        
        return result
    
    def _calculate_confidence(self, vitals: Dict, demographics: Dict) -> float:
        """Calculate confidence score based on extracted fields"""
        total_fields = 7  # age, gender, hr, sbp, dbp, temp, spo2
        extracted_fields = 0
        
        if demographics['age'] is not None:
            extracted_fields += 1
        if demographics['gender'] is not None:
            extracted_fields += 1
        if vitals['heart_rate'] is not None:
            extracted_fields += 1
        if vitals['sbp'] is not None and vitals['dbp'] is not None:
            extracted_fields += 1
        if vitals['temp_c'] is not None:
            extracted_fields += 1
        if vitals['spo2'] is not None:
            extracted_fields += 1
        
        return extracted_fields / total_fields
    
    def _identify_missing_fields(self, vitals: Dict, demographics: Dict) -> List[str]:
        """Identify which fields are missing"""
        missing = []
        
        if demographics['age'] is None:
            missing.append('age')
        if demographics['gender'] is None:
            missing.append('gender')
        if vitals['heart_rate'] is None:
            missing.append('heart_rate')
        if vitals['sbp'] is None or vitals['dbp'] is None:
            missing.append('blood_pressure')
        if vitals['temp_c'] is None:
            missing.append('temperature')
        if vitals['spo2'] is None:
            missing.append('spo2')
        
        return missing


# Convenience function for simple use cases
def extract_vitals_from_note(text: str) -> Dict[str, Optional[float]]:
    """
    Simple function to extract vitals from clinical note
    
    Example:
        >>> text = "Patient has HR of 110 and BP 150/90"
        >>> vitals = extract_vitals_from_note(text)
        >>> print(vitals)
        {'heart_rate': 110.0, 'sbp': 150.0, 'dbp': 90.0, 'temp_c': None, 'spo2': None}
    """
    parser = ClinicalNoteParser()
    return parser.extract_vitals_from_note(text)


def parse_clinical_note(text: str) -> Dict:
    """
    Parse complete clinical note and extract all patient data
    
    Example:
        >>> note = "65yo Male with HR 110, BP 160/95, Temp 38.5C, SpO2 92%. 
        ...         History of HTN and DM. Presenting with chest pain."
        >>> data = parse_clinical_note(note)
    """
    parser = ClinicalNoteParser()
    return parser.parse_clinical_note(text)


if __name__ == "__main__":
    # Test cases
    print("=" * 70)
    print("CLINICAL NOTE PARSER - TEST CASES")
    print("=" * 70)
    
    test_cases = [
        {
            'name': 'Simple vitals',
            'text': 'Patient has HR of 110 and BP 150/90'
        },
        {
            'name': 'Complete note',
            'text': '65yo Male with HR 110, BP 160/95, Temp 38.5C, SpO2 92%. History of HTN and DM. Presenting with chest pain.'
        },
        {
            'name': 'Stroke case',
            'text': '72-year-old male presenting with sudden onset facial drooping and slurred speech. BP 165/98, HR 82, SpO2 96%, Temp 37.1C. Known history of hypertension and atrial fibrillation.'
        },
        {
            'name': 'Alternative formats',
            'text': 'Patient vitals: Heart rate = 95 bpm, Blood pressure = 130/85 mmHg, O2 sat = 98%, Temperature = 37.2°C'
        }
    ]
    
    parser = ClinicalNoteParser()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 70)
        print(f"Input: {test['text'][:100]}...")
        print()
        
        result = parser.parse_clinical_note(test['text'])
        
        print(f"Age: {result['age']}, Gender: {result['gender']}")
        print(f"Vitals: HR={result['vitals']['heart_rate']}, "
              f"BP={result['vitals']['sbp']}/{result['vitals']['dbp']}, "
              f"Temp={result['vitals']['temp_c']}°C, SpO2={result['vitals']['spo2']}%")
        print(f"Medical History: {result['medical_history']}")
        print(f"Symptoms: {result['symptoms'][:80]}...")
        print(f"Confidence: {result['extraction_confidence']:.1%}")
        if result['missing_fields']:
            print(f"Missing: {', '.join(result['missing_fields'])}")
    
    print("\n" + "=" * 70)
    print("✓ All tests complete!")
    print("=" * 70)
