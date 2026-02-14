"""
Example: Document Upload and Auto-Fill Triage Form
Demonstrates how to parse clinical notes and submit to triage API
"""

import requests
from utils.parser import parse_clinical_note

API_URL = "http://localhost:8000"

def demo_document_upload_workflow():
    """
    Demonstrate the complete workflow:
    1. Parse clinical note
    2. Auto-fill patient data
    3. Submit to triage API
    4. Get risk assessment
    """
    
    print("=" * 70)
    print("DOCUMENT UPLOAD & AUTO-FILL DEMO")
    print("=" * 70)
    
    # Example clinical notes (as if uploaded from EHR)
    clinical_notes = [
        {
            'name': 'Stroke Patient',
            'note': """
            72-year-old male presenting with sudden onset facial drooping and 
            slurred speech. Vitals: HR 82 bpm, BP 165/98 mmHg, SpO2 96%, 
            Temperature 37.1°C. Known history of hypertension and atrial fibrillation.
            Patient unable to lift right arm, symptoms started 30 minutes ago.
            """
        },
        {
            'name': 'Heart Attack Patient',
            'note': """
            65yo Male with crushing chest pain radiating to left arm. 
            Heart rate = 115, Blood pressure = 160/95, Temp = 38.5C, O2 sat = 92%.
            History of HTN and diabetes. Patient diaphoretic and anxious.
            Pain started 1 hour ago, not relieved by rest.
            """
        },
        {
            'name': 'Low Risk - Common Cold',
            'note': """
            28-year-old female with runny nose and sore throat for 2 days.
            Vitals: HR 72, BP 118/76, SpO2 99%, Temp 37.2°C.
            No significant medical history. Mild cough, no respiratory distress.
            """
        },
        {
            'name': 'Critical - Low SpO2',
            'note': """
            55yo Male with severe shortness of breath and wheezing.
            HR 105 bpm, BP 140/88 mmHg, SpO2 85%, Temp 37.8°C.
            History of COPD. Patient in respiratory distress.
            """
        }
    ]
    
    for i, case in enumerate(clinical_notes, 1):
        print(f"\n{'='*70}")
        print(f"CASE {i}: {case['name']}")
        print(f"{'='*70}")
        
        print(f"\n📄 Clinical Note:")
        print(f"{case['note'].strip()}")
        
        # Step 1: Parse the clinical note
        print(f"\n🔍 Step 1: Parsing clinical note...")
        parsed_data = parse_clinical_note(case['note'])
        
        print(f"\n✓ Extracted Data:")
        print(f"  Age: {parsed_data['age']}")
        print(f"  Gender: {parsed_data['gender']}")
        print(f"  Heart Rate: {parsed_data['vitals']['heart_rate']} bpm")
        print(f"  Blood Pressure: {parsed_data['vitals']['sbp']}/{parsed_data['vitals']['dbp']} mmHg")
        print(f"  Temperature: {parsed_data['vitals']['temp_c']}°C")
        print(f"  SpO2: {parsed_data['vitals']['spo2']}%")
        print(f"  Medical History: {parsed_data['medical_history']}")
        print(f"  Symptoms: {parsed_data['symptoms'][:80]}...")
        print(f"  Extraction Confidence: {parsed_data['extraction_confidence']:.1%}")
        
        if parsed_data['missing_fields']:
            print(f"  ⚠ Missing: {', '.join(parsed_data['missing_fields'])}")
            print(f"  → These fields would need manual entry")
        
        # Step 2: Check if we have minimum required data
        has_vitals = all([
            parsed_data['vitals']['heart_rate'] is not None,
            parsed_data['vitals']['sbp'] is not None,
            parsed_data['vitals']['dbp'] is not None,
            parsed_data['vitals']['temp_c'] is not None,
            parsed_data['vitals']['spo2'] is not None
        ])
        
        has_demographics = all([
            parsed_data['age'] is not None,
            parsed_data['gender'] is not None
        ])
        
        if not (has_vitals and has_demographics):
            print(f"\n⚠ Insufficient data extracted. Manual entry required for missing fields.")
            print(f"  Skipping API submission for this case.")
            continue
        
        # Step 3: Prepare API request
        print(f"\n📤 Step 2: Submitting to Triage API...")
        
        patient_data = {
            "age": parsed_data['age'],
            "gender": parsed_data['gender'],
            "vitals": {
                "heart_rate": parsed_data['vitals']['heart_rate'],
                "sbp": parsed_data['vitals']['sbp'],
                "dbp": parsed_data['vitals']['dbp'],
                "temp_c": parsed_data['vitals']['temp_c'],
                "spo2": parsed_data['vitals']['spo2']
            },
            "symptoms": parsed_data['symptoms'],
            "medical_history": parsed_data['medical_history']
        }
        
        try:
            response = requests.post(f"{API_URL}/api/triage", json=patient_data)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✓ Triage Assessment Complete!")
                print(f"\n🎯 RESULTS:")
                print(f"  Risk Level: {result['risk'].upper()}")
                print(f"  Recommended Department: {result['department']}")
                print(f"  Confidence: {result['confidence']:.1%}")
                
                if result['override_applied']:
                    print(f"  ⚠ SAFETY OVERRIDE: {result['override_reason']}")
                
                print(f"\n  Explanation: {result['explanation']}")
                
                if result['top_factors']:
                    print(f"\n  Top Contributing Factors:")
                    for factor in result['top_factors'][:3]:
                        print(f"    • {factor}")
                
                print(f"\n  Risk Probabilities:")
                for risk, prob in result['all_probabilities'].items():
                    bar = '█' * int(prob * 20)
                    print(f"    {risk:8s}: {bar:20s} {prob:.1%}")
            else:
                print(f"\n❌ API Error: {response.status_code}")
                print(f"   {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Cannot connect to API. Please start the server:")
            print(f"   python api/main.py")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print("DEMO COMPLETE")
    print(f"{'='*70}")
    print("\n💡 Key Takeaways:")
    print("  1. Parser extracts structured data from unstructured clinical notes")
    print("  2. Extraction confidence helps identify when manual review is needed")
    print("  3. Missing fields are flagged for manual entry")
    print("  4. Extracted data auto-fills the triage form")
    print("  5. API provides immediate risk assessment with explanations")
    print("  6. Safety overrides ensure critical cases are never missed")


if __name__ == "__main__":
    demo_document_upload_workflow()
