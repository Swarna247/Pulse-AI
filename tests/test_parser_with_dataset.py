"""
Test the parser with actual clinical notes from our dataset
"""

import pandas as pd
from utils.parser import ClinicalNoteParser

def test_parser_with_real_data():
    """Test parser with clinical notes from the golden 50 dataset"""
    
    print("=" * 70)
    print("TESTING PARSER WITH REAL CLINICAL NOTES")
    print("=" * 70)
    
    # Load dataset
    df = pd.read_csv('data/triage_golden_50.csv')
    parser = ClinicalNoteParser()
    
    # Test with first 5 patients
    print(f"\nTesting with {min(5, len(df))} clinical notes from dataset...\n")
    
    for idx in range(min(5, len(df))):
        row = df.iloc[idx]
        
        print(f"\n{'='*70}")
        print(f"Patient {idx + 1}: {row['patient_id']} - {row['risk_level']} Risk")
        print(f"{'='*70}")
        
        print(f"\nOriginal Data:")
        print(f"  Age: {row['age']}, Gender: {row['gender']}")
        print(f"  Vitals: HR={row['heart_rate']:.0f}, BP={row['sbp']:.0f}/{row['dbp']:.0f}, "
              f"Temp={row['temp_c']:.1f}°C, SpO2={row['spo2']:.0f}%")
        print(f"  Dept: {row['target_dept']}")
        
        print(f"\nClinical Note:")
        print(f"  \"{row['clinical_note']}\"")
        
        # Parse the clinical note
        parsed = parser.parse_clinical_note(row['clinical_note'])
        
        print(f"\nExtracted Data:")
        print(f"  Age: {parsed['age']}, Gender: {parsed['gender']}")
        print(f"  Vitals: HR={parsed['vitals']['heart_rate']}, "
              f"BP={parsed['vitals']['sbp']}/{parsed['vitals']['dbp']}, "
              f"Temp={parsed['vitals']['temp_c']}°C, SpO2={parsed['vitals']['spo2']}%")
        print(f"  Confidence: {parsed['extraction_confidence']:.1%}")
        
        # Compare accuracy
        matches = []
        if parsed['age'] == row['age']:
            matches.append('age')
        if parsed['gender'] == row['gender']:
            matches.append('gender')
        if parsed['vitals']['heart_rate'] and abs(parsed['vitals']['heart_rate'] - row['heart_rate']) < 2:
            matches.append('HR')
        if parsed['vitals']['sbp'] and abs(parsed['vitals']['sbp'] - row['sbp']) < 2:
            matches.append('SBP')
        if parsed['vitals']['dbp'] and abs(parsed['vitals']['dbp'] - row['dbp']) < 2:
            matches.append('DBP')
        if parsed['vitals']['temp_c'] and abs(parsed['vitals']['temp_c'] - row['temp_c']) < 0.5:
            matches.append('Temp')
        if parsed['vitals']['spo2'] and abs(parsed['vitals']['spo2'] - row['spo2']) < 2:
            matches.append('SpO2')
        
        print(f"\n✓ Matched fields: {', '.join(matches) if matches else 'None'}")
        
        if parsed['missing_fields']:
            print(f"⚠ Missing fields: {', '.join(parsed['missing_fields'])}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Test all notes and calculate overall accuracy
    total_fields = 0
    correct_fields = 0
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        parsed = parser.parse_clinical_note(row['clinical_note'])
        
        # Check each field
        if parsed['age'] == row['age']:
            correct_fields += 1
        total_fields += 1
        
        if parsed['gender'] == row['gender']:
            correct_fields += 1
        total_fields += 1
        
        if parsed['vitals']['heart_rate'] and abs(parsed['vitals']['heart_rate'] - row['heart_rate']) < 2:
            correct_fields += 1
        total_fields += 1
        
        if parsed['vitals']['sbp'] and abs(parsed['vitals']['sbp'] - row['sbp']) < 2:
            correct_fields += 1
        total_fields += 1
        
        if parsed['vitals']['dbp'] and abs(parsed['vitals']['dbp'] - row['dbp']) < 2:
            correct_fields += 1
        total_fields += 1
    
    accuracy = correct_fields / total_fields
    print(f"\nOverall Extraction Accuracy: {accuracy:.1%}")
    print(f"Correct fields: {correct_fields}/{total_fields}")
    print("\n✓ Parser testing complete!")


if __name__ == "__main__":
    test_parser_with_real_data()
