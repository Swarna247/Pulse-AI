"""
Test EHR/EMR Integration
Demonstrates HL7 and FHIR integration capabilities
"""

import requests
import json
from integrations.ehr_adapter import EHRAdapter, EHRIntegrationExamples


def test_hl7_integration():
    """Test HL7 v2.x integration"""
    print("\n" + "="*60)
    print("TEST 1: HL7 v2.x Integration")
    print("="*60)
    
    adapter = EHRAdapter()
    
    # Sample HL7 ADT message
    hl7_message = """MSH|^~\\&|SENDING_APP|HOSPITAL|TRIAGE|HOSPITAL|20240214120000||ADT^A01|MSG001|P|2.5
PID|1||PT-2024-001^^^HOSPITAL^MR||DOE^JOHN^A||19740515|M|||123 MAIN ST^^CITY^STATE^12345||555-1234
OBX|1|NM|8867-4^Heart Rate^LN||110|/min|||||F
OBX|2|NM|8480-6^Systolic BP^LN||165|mmHg|||||F
OBX|3|NM|8462-4^Diastolic BP^LN||95|mmHg|||||F
OBX|4|NM|8310-5^Body Temperature^LN||38.5|Cel|||||F
OBX|5|NM|2708-6^Oxygen Saturation^LN||92|%|||||F
DG1|1||I10^Hypertension^ICD10||20240214120000"""
    
    print("\n1. Parsing HL7 ADT Message...")
    patient_data = adapter.import_patient_data(hl7_message, format='hl7')
    
    print("\nExtracted Patient Data:")
    print(f"  Patient ID: {patient_data['patient_id']}")
    print(f"  Name: {patient_data['name']}")
    print(f"  Age: {patient_data['age']}")
    print(f"  Gender: {patient_data['gender']}")
    print(f"  Vitals: {patient_data['vitals']}")
    print(f"  Medical History: {patient_data['medical_history']}")
    
    # Simulate triage result
    triage_result = {
        'risk': 'High',
        'department': 'Cardiology',
        'confidence': 0.85,
        'explanation': 'Patient presents with elevated BP (165/95) and tachycardia (HR 110). Fever present (38.5°C). Hypertension in medical history.',
        'override_applied': True,
        'override_reason': 'Systolic BP > 160 mmHg (Hypertensive Crisis)'
    }
    
    print("\n2. Generating HL7 ORU Message with Triage Results...")
    hl7_output = adapter.export_triage_results(triage_result, patient_data, format='hl7')
    
    print("\nGenerated HL7 ORU Message:")
    print(hl7_output)
    
    print("\n✓ HL7 Integration Test Complete")


def test_fhir_integration():
    """Test FHIR R4 integration"""
    print("\n" + "="*60)
    print("TEST 2: FHIR R4 Integration")
    print("="*60)
    
    adapter = EHRAdapter()
    
    # Sample FHIR Bundle
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "PT-2024-001",
                    "identifier": [
                        {
                            "system": "http://hospital.org/patients",
                            "value": "PT-2024-001"
                        }
                    ],
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
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8867-4",
                                "display": "Heart rate"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 110,
                        "unit": "/min"
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 165,
                        "unit": "mmHg"
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {
                        "text": "Hypertension"
                    }
                }
            }
        ]
    }
    
    print("\n1. Parsing FHIR Bundle...")
    patient_data = adapter.import_patient_data(json.dumps(fhir_bundle), format='fhir')
    
    print("\nExtracted Patient Data:")
    print(f"  Patient ID: {patient_data['patient_id']}")
    print(f"  Name: {patient_data['name']}")
    print(f"  Age: {patient_data['age']}")
    print(f"  Gender: {patient_data['gender']}")
    print(f"  Vitals: {patient_data['vitals']}")
    print(f"  Medical History: {patient_data['medical_history']}")
    
    # Simulate triage result
    triage_result = {
        'risk': 'High',
        'department': 'Cardiology',
        'confidence': 0.85,
        'explanation': 'Patient presents with elevated BP and tachycardia',
        'override_applied': True,
        'override_reason': 'Systolic BP > 160 mmHg'
    }
    
    print("\n2. Generating FHIR Bundle with Triage Results...")
    fhir_output = adapter.export_triage_results(triage_result, patient_data, format='fhir')
    
    print("\nGenerated FHIR Bundle (first 500 chars):")
    print(fhir_output[:500] + "...")
    
    # Parse and display key resources
    bundle = json.loads(fhir_output)
    print(f"\nBundle contains {len(bundle['entry'])} resources:")
    for entry in bundle['entry']:
        resource_type = entry['resource']['resourceType']
        print(f"  - {resource_type}")
    
    print("\n✓ FHIR Integration Test Complete")


def test_api_endpoints():
    """Test EHR API endpoints (requires running API server)"""
    print("\n" + "="*60)
    print("TEST 3: API Endpoints")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    # Check if API is running
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code != 200:
            print("\n⚠️  API server not running. Start with: python api/main.py")
            return
    except requests.exceptions.ConnectionError:
        print("\n⚠️  API server not running. Start with: python api/main.py")
        return
    
    print("\n1. Testing /ehr/formats endpoint...")
    response = requests.get(f"{base_url}/ehr/formats")
    if response.status_code == 200:
        formats = response.json()
        print(f"✓ Supported formats: {len(formats['formats'])}")
        for fmt in formats['formats']:
            print(f"  - {fmt['name']} ({fmt['code']})")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    print("\n2. Testing /ehr/health endpoint...")
    response = requests.get(f"{base_url}/ehr/health")
    if response.status_code == 200:
        health = response.json()
        print(f"✓ Status: {health['status']}")
        print(f"  HL7 Handler: {health['hl7_handler']}")
        print(f"  FHIR Handler: {health['fhir_handler']}")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    print("\n3. Testing /ehr/import endpoint (HL7)...")
    hl7_data = {
        "data": "MSH|^~\\&|APP|HOSPITAL|TRIAGE|HOSPITAL|20240214120000||ADT^A01|MSG001|P|2.5\nPID|1||PT-001||DOE^JOHN||19740515|M\nOBX|1|NM|8867-4^Heart Rate^LN||110|/min|||||F",
        "format": "hl7"
    }
    response = requests.post(f"{base_url}/ehr/import", json=hl7_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Import successful")
        print(f"  Patient ID: {result['patient_data']['patient_id']}")
        print(f"  Format: {result['format_detected']}")
    else:
        print(f"✗ Failed: {response.status_code}")
    
    print("\n✓ API Endpoints Test Complete")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("EHR/EMR INTEGRATION TEST SUITE")
    print("="*60)
    
    # Test 1: HL7 Integration
    test_hl7_integration()
    
    # Test 2: FHIR Integration
    test_fhir_integration()
    
    # Test 3: API Endpoints (if server is running)
    test_api_endpoints()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)
    print("\nNext Steps:")
    print("1. Start API server: python api/main.py")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Test EHR endpoints: http://localhost:8000/ehr/*")
    print("4. Read integration guide: EHR_INTEGRATION_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
