"""
Test script for the Triage API
Tests both rule-based overrides and ML predictions
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 70)
    print("TEST 1: Health Check")
    print("=" * 70)
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_rule_override_low_spo2():
    """Test rule override for critical SpO2"""
    print("=" * 70)
    print("TEST 2: Rule Override - Critical SpO2 < 90")
    print("=" * 70)
    
    patient = {
        "age": 65,
        "gender": "Male",
        "vitals": {
            "heart_rate": 95,
            "sbp": 130,
            "dbp": 85,
            "temp_c": 37.5,
            "spo2": 85  # Critical!
        },
        "symptoms": "Shortness of breath, wheezing",
        "medical_history": "COPD"
    }
    
    response = requests.post(f"{API_URL}/api/triage", json=patient)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    assert result['override_applied'] == True, "Override should be applied"
    assert result['risk'] == 'High', "Risk should be High"
    print("\n✓ Test passed: Rule override correctly triggered for low SpO2")
    print()

def test_rule_override_high_bp():
    """Test rule override for hypertensive crisis"""
    print("=" * 70)
    print("TEST 3: Rule Override - Hypertensive Crisis (SBP > 180)")
    print("=" * 70)
    
    patient = {
        "age": 58,
        "gender": "Female",
        "vitals": {
            "heart_rate": 88,
            "sbp": 195,  # Critical!
            "dbp": 110,
            "temp_c": 37.2,
            "spo2": 97
        },
        "symptoms": "Severe headache, blurred vision",
        "medical_history": "Hypertension"
    }
    
    response = requests.post(f"{API_URL}/api/triage", json=patient)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    assert result['override_applied'] == True, "Override should be applied"
    assert result['risk'] == 'High', "Risk should be High"
    print("\n✓ Test passed: Rule override correctly triggered for high BP")
    print()

def test_ml_prediction_stroke():
    """Test ML prediction for stroke case"""
    print("=" * 70)
    print("TEST 4: ML Prediction - Stroke Case")
    print("=" * 70)
    
    patient = {
        "age": 72,
        "gender": "Male",
        "vitals": {
            "heart_rate": 82,
            "sbp": 165,
            "dbp": 98,
            "temp_c": 37.1,
            "spo2": 96
        },
        "symptoms": "Facial drooping, slurred speech, one-sided weakness",
        "medical_history": "Hypertension, Atrial Fibrillation"
    }
    
    response = requests.post(f"{API_URL}/api/triage", json=patient)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    print(f"\n✓ Prediction: {result['risk']} risk, {result['department']}")
    print(f"✓ Confidence: {result['confidence']:.1%}")
    print(f"✓ Top factors: {', '.join(result['top_factors'][:3])}")
    print()

def test_ml_prediction_low_risk():
    """Test ML prediction for low risk case"""
    print("=" * 70)
    print("TEST 5: ML Prediction - Low Risk (Common Cold)")
    print("=" * 70)
    
    patient = {
        "age": 28,
        "gender": "Female",
        "vitals": {
            "heart_rate": 72,
            "sbp": 118,
            "dbp": 76,
            "temp_c": 37.2,
            "spo2": 99
        },
        "symptoms": "Runny nose, sore throat, mild cough",
        "medical_history": "None"
    }
    
    response = requests.post(f"{API_URL}/api/triage", json=patient)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    print(f"\n✓ Prediction: {result['risk']} risk, {result['department']}")
    print(f"✓ Confidence: {result['confidence']:.1%}")
    print()

def test_ml_prediction_heart_attack():
    """Test ML prediction for heart attack"""
    print("=" * 70)
    print("TEST 6: ML Prediction - Myocardial Infarction")
    print("=" * 70)
    
    patient = {
        "age": 62,
        "gender": "Male",
        "vitals": {
            "heart_rate": 115,
            "sbp": 145,
            "dbp": 92,
            "temp_c": 37.6,
            "spo2": 93
        },
        "symptoms": "Crushing chest pain, radiating to left arm, sweating, nausea",
        "medical_history": "Hypertension, Diabetes"
    }
    
    response = requests.post(f"{API_URL}/api/triage", json=patient)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    print(f"\n✓ Prediction: {result['risk']} risk, {result['department']}")
    print(f"✓ Confidence: {result['confidence']:.1%}")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SMART PATIENT TRIAGE API - TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        # Test health
        test_health()
        
        # Test rule overrides
        test_rule_override_low_spo2()
        test_rule_override_high_bp()
        
        # Test ML predictions
        test_ml_prediction_stroke()
        test_ml_prediction_low_risk()
        test_ml_prediction_heart_attack()
        
        print("=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Please start the API server first:")
        print("  python api/main.py")
        print("  or")
        print("  uvicorn api.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")

if __name__ == "__main__":
    main()
