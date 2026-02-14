"""
Golden 50 Patient Dataset Generator
Creates 50 high-quality synthetic patients with clinically accurate disease presentations
"""

import csv
import random
import numpy as np
from datetime import datetime
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def add_realistic_variance(value, variance_pct=0.05):
    """Add slight variance to make vitals look realistic"""
    variance = value * variance_pct
    return round(value + np.random.uniform(-variance, variance), 1)

def generate_patient_id(index):
    """Generate patient ID"""
    return f"PT-2024-{index:03d}"

class ClinicalPatientGenerator:
    """Generate clinically accurate synthetic patients"""
    
    def __init__(self):
        self.patients = []
        self.patient_counter = 1
    
    def _base_patient(self, age, gender):
        """Create base patient with normal vitals"""
        return {
            'patient_id': generate_patient_id(self.patient_counter),
            'age': age,
            'gender': gender,
            'heart_rate': add_realistic_variance(75, 0.1),
            'sbp': add_realistic_variance(120, 0.08),
            'dbp': add_realistic_variance(80, 0.08),
            'temp_c': add_realistic_variance(37.0, 0.02),
            'spo2': add_realistic_variance(98, 0.01),
            'symptoms': '',
            'medical_history': 'None',
            'risk_level': 'Low',
            'target_dept': 'General Medicine',
            'clinical_note': ''
        }

    
    # ========== HIGH RISK CASES (10 total) ==========
    
    def generate_stroke(self):
        """Stroke - High BP, neurological symptoms"""
        age = random.randint(60, 85)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(85, 0.1)
        patient['sbp'] = add_realistic_variance(175, 0.08)  # Hypertensive
        patient['dbp'] = add_realistic_variance(100, 0.08)
        patient['temp_c'] = add_realistic_variance(37.1, 0.02)
        patient['spo2'] = add_realistic_variance(96, 0.02)
        patient['symptoms'] = 'Facial drooping, slurred speech, one-sided weakness, sudden confusion'
        patient['medical_history'] = 'Hypertension, Atrial Fibrillation'
        patient['risk_level'] = 'High'
        patient['target_dept'] = 'Neurology'
        patient['clinical_note'] = f"{age}yo {gender} presenting with sudden onset facial asymmetry and speech difficulties. Patient unable to lift right arm, BP significantly elevated at {int(patient['sbp'])}/{int(patient['dbp'])}."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_myocardial_infarction(self):
        """Heart Attack - Chest pain, elevated HR, abnormal BP"""
        age = random.randint(50, 75)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        # MI can present with high or low BP (cardiogenic shock)
        if random.random() > 0.5:
            patient['sbp'] = add_realistic_variance(155, 0.08)
            patient['dbp'] = add_realistic_variance(95, 0.08)
        else:
            patient['sbp'] = add_realistic_variance(85, 0.08)  # Shock
            patient['dbp'] = add_realistic_variance(55, 0.08)
        
        patient['heart_rate'] = add_realistic_variance(115, 0.1)
        patient['temp_c'] = add_realistic_variance(37.5, 0.02)
        patient['spo2'] = add_realistic_variance(93, 0.02)
        patient['symptoms'] = 'Crushing chest pain, radiating to left arm, profuse sweating, nausea'
        patient['medical_history'] = random.choice([
            'Hypertension, Diabetes',
            'Hyperlipidemia, Smoking history',
            'Previous MI, Hypertension'
        ])
        patient['risk_level'] = 'High'
        patient['target_dept'] = 'Cardiology'
        patient['clinical_note'] = f"{age}yo {gender} with acute onset substernal chest pressure 8/10, diaphoretic and anxious. Pain started 45 minutes ago, not relieved by rest."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_sepsis(self):
        """Sepsis - Extreme temp, tachycardia, hypotension"""
        age = random.randint(35, 80)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        # Sepsis can present with high or low temp
        if random.random() > 0.3:
            patient['temp_c'] = add_realistic_variance(39.8, 0.05)
        else:
            patient['temp_c'] = add_realistic_variance(35.5, 0.05)  # Hypothermia
        
        patient['heart_rate'] = add_realistic_variance(125, 0.1)
        patient['sbp'] = add_realistic_variance(88, 0.08)  # Hypotensive
        patient['dbp'] = add_realistic_variance(52, 0.08)
        patient['spo2'] = add_realistic_variance(91, 0.02)
        patient['symptoms'] = 'Confusion, severe shivering, extreme fatigue, mottled skin, rapid breathing'
        patient['medical_history'] = random.choice([
            'Recent UTI',
            'Diabetes, Immunocompromised',
            'Recent surgery'
        ])
        patient['risk_level'] = 'High'
        patient['target_dept'] = 'Emergency'
        patient['clinical_note'] = f"{age}yo {gender} appears acutely ill with altered mental status and signs of shock. Patient febrile with temp {patient['temp_c']:.1f}C, tachycardic, and hypotensive."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_anaphylaxis(self):
        """Anaphylaxis - Severe allergic reaction, low BP, low SpO2"""
        age = random.randint(18, 65)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(135, 0.1)
        patient['sbp'] = add_realistic_variance(82, 0.08)  # Severe drop
        patient['dbp'] = add_realistic_variance(48, 0.08)
        patient['temp_c'] = add_realistic_variance(37.2, 0.02)
        patient['spo2'] = add_realistic_variance(88, 0.02)  # Airway compromise
        patient['symptoms'] = 'Hives, swollen tongue, difficulty swallowing, wheezing, feeling of impending doom'
        patient['medical_history'] = random.choice([
            'Known peanut allergy',
            'Shellfish allergy',
            'Bee sting allergy'
        ])
        patient['risk_level'] = 'High'
        patient['target_dept'] = 'Emergency'
        patient['clinical_note'] = f"{age}yo {gender} with acute onset facial and tongue swelling after eating at restaurant. Patient in respiratory distress with audible stridor and diffuse urticaria."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_dka(self):
        """Diabetic Ketoacidosis - Diabetes complication"""
        age = random.randint(25, 55)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(118, 0.1)
        patient['sbp'] = add_realistic_variance(95, 0.08)  # Dehydration
        patient['dbp'] = add_realistic_variance(58, 0.08)
        patient['temp_c'] = add_realistic_variance(37.8, 0.02)
        patient['spo2'] = add_realistic_variance(96, 0.02)
        patient['symptoms'] = 'Fruity-smelling breath, extreme thirst, nausea, abdominal pain, rapid deep breathing'
        patient['medical_history'] = 'Type 1 Diabetes'
        patient['risk_level'] = 'High'
        patient['target_dept'] = 'Endocrinology'
        patient['clinical_note'] = f"{age}yo {gender} with known T1DM presenting with polyuria, polydipsia, and Kussmaul respirations. Patient reports missed insulin doses, breath has fruity odor."
        
        self.patients.append(patient)
        self.patient_counter += 1

    
    # ========== MEDIUM RISK CASES (15 total) ==========
    
    def generate_appendicitis(self):
        """Acute Appendicitis - Abdominal pain, mild fever"""
        age = random.randint(15, 45)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(98, 0.1)
        patient['sbp'] = add_realistic_variance(125, 0.08)
        patient['dbp'] = add_realistic_variance(78, 0.08)
        patient['temp_c'] = add_realistic_variance(38.3, 0.05)
        patient['spo2'] = add_realistic_variance(98, 0.01)
        patient['symptoms'] = 'Sharp lower right abdominal pain, loss of appetite, vomiting, pain worsens with movement'
        patient['medical_history'] = 'None'
        patient['risk_level'] = 'Medium'
        patient['target_dept'] = 'Surgery'
        patient['clinical_note'] = f"{age}yo {gender} with 12-hour history of periumbilical pain now localized to RLQ. Positive McBurney's point tenderness, guarding present."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_fracture(self):
        """Bone Fracture - Pain, deformity, normal vitals"""
        age = random.randint(20, 70)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(88, 0.1)
        patient['sbp'] = add_realistic_variance(135, 0.08)  # Pain response
        patient['dbp'] = add_realistic_variance(82, 0.08)
        patient['temp_c'] = add_realistic_variance(37.0, 0.02)
        patient['spo2'] = add_realistic_variance(99, 0.01)
        
        fracture_site = random.choice(['left wrist', 'right ankle', 'left clavicle', 'right radius'])
        patient['symptoms'] = f'Severe pain {fracture_site} 8/10, visible deformity, unable to bear weight, swelling'
        patient['medical_history'] = random.choice(['None', 'Osteoporosis', 'Previous fracture'])
        patient['risk_level'] = 'Medium'
        patient['target_dept'] = 'Orthopedics'
        patient['clinical_note'] = f"{age}yo {gender} fell from height with obvious deformity of {fracture_site}. Neurovascular status intact distally, significant swelling and ecchymosis."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_pneumonia(self):
        """Pneumonia - Respiratory symptoms, fever"""
        age = random.randint(40, 75)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(105, 0.1)
        patient['sbp'] = add_realistic_variance(118, 0.08)
        patient['dbp'] = add_realistic_variance(75, 0.08)
        patient['temp_c'] = add_realistic_variance(38.8, 0.05)
        patient['spo2'] = add_realistic_variance(92, 0.02)  # Mild hypoxia
        patient['symptoms'] = 'Productive cough with yellow sputum, shortness of breath, chest tightness, chills'
        patient['medical_history'] = random.choice(['COPD', 'Asthma', 'Smoking history', 'None'])
        patient['risk_level'] = 'Medium'
        patient['target_dept'] = 'Respiratory'
        patient['clinical_note'] = f"{age}yo {gender} with 4-day history of productive cough and fever. Decreased breath sounds right lower lobe, dullness to percussion."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_moderate_infection(self):
        """Moderate Infection - Fever, localized symptoms"""
        age = random.randint(25, 65)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(95, 0.1)
        patient['sbp'] = add_realistic_variance(122, 0.08)
        patient['dbp'] = add_realistic_variance(79, 0.08)
        patient['temp_c'] = add_realistic_variance(38.6, 0.05)
        patient['spo2'] = add_realistic_variance(97, 0.01)
        
        infection_type = random.choice([
            ('Cellulitis right leg, redness, warmth, swelling', 'Recent skin injury'),
            ('Urinary burning, frequency, urgency, lower back pain', 'Recurrent UTIs'),
            ('Severe sore throat, difficulty swallowing, white patches on tonsils', 'None')
        ])
        
        patient['symptoms'] = infection_type[0]
        patient['medical_history'] = infection_type[1]
        patient['risk_level'] = 'Medium'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} presenting with signs of localized infection. Febrile to {patient['temp_c']:.1f}C, area of concern shows classic inflammatory signs."
        
        self.patients.append(patient)
        self.patient_counter += 1

    
    # ========== LOW RISK CASES (25 total) ==========
    
    def generate_common_cold(self):
        """Common Cold - Mild symptoms, normal vitals"""
        age = random.randint(18, 60)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(72, 0.08)
        patient['sbp'] = add_realistic_variance(118, 0.08)
        patient['dbp'] = add_realistic_variance(76, 0.08)
        patient['temp_c'] = add_realistic_variance(37.2, 0.02)
        patient['spo2'] = add_realistic_variance(99, 0.01)
        patient['symptoms'] = 'Runny nose, sore throat, mild cough, sneezing, fatigue'
        patient['medical_history'] = 'None'
        patient['risk_level'] = 'Low'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} with 2-day history of upper respiratory symptoms. Afebrile, lungs clear, no respiratory distress."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_migraine(self):
        """Migraine - Headache, normal vitals"""
        age = random.randint(20, 55)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(78, 0.08)
        patient['sbp'] = add_realistic_variance(125, 0.08)
        patient['dbp'] = add_realistic_variance(80, 0.08)
        patient['temp_c'] = add_realistic_variance(36.9, 0.02)
        patient['spo2'] = add_realistic_variance(99, 0.01)
        patient['symptoms'] = 'Severe throbbing headache, photophobia, nausea, visual aura'
        patient['medical_history'] = random.choice(['History of migraines', 'None'])
        patient['risk_level'] = 'Low'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} with recurrent unilateral headache, typical of previous episodes. Neurological exam normal, no focal deficits."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_minor_allergy(self):
        """Minor Allergic Reaction - Rash, normal vitals"""
        age = random.randint(15, 50)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(74, 0.08)
        patient['sbp'] = add_realistic_variance(120, 0.08)
        patient['dbp'] = add_realistic_variance(78, 0.08)
        patient['temp_c'] = add_realistic_variance(37.0, 0.02)
        patient['spo2'] = add_realistic_variance(99, 0.01)
        patient['symptoms'] = 'Itchy rash on arms, mild hives, no breathing difficulty'
        patient['medical_history'] = random.choice(['Seasonal allergies', 'Eczema', 'None'])
        patient['risk_level'] = 'Low'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} with localized urticarial rash after new detergent exposure. No angioedema, airway patent, no respiratory compromise."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_minor_injury(self):
        """Minor Injury - Sprain, laceration, normal vitals"""
        age = random.randint(18, 65)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(76, 0.08)
        patient['sbp'] = add_realistic_variance(122, 0.08)
        patient['dbp'] = add_realistic_variance(79, 0.08)
        patient['temp_c'] = add_realistic_variance(37.1, 0.02)
        patient['spo2'] = add_realistic_variance(99, 0.01)
        
        injury_type = random.choice([
            'Ankle sprain, mild swelling, able to bear weight with discomfort',
            'Small laceration on hand 2cm, bleeding controlled, no tendon involvement',
            'Bruised knee from fall, full range of motion, no deformity'
        ])
        
        patient['symptoms'] = injury_type
        patient['medical_history'] = 'None'
        patient['risk_level'] = 'Low'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} with minor traumatic injury. Stable vitals, neurovascular exam intact, no signs of serious injury."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_gastroenteritis(self):
        """Mild Gastroenteritis - GI symptoms, stable"""
        age = random.randint(20, 60)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(82, 0.08)
        patient['sbp'] = add_realistic_variance(115, 0.08)
        patient['dbp'] = add_realistic_variance(74, 0.08)
        patient['temp_c'] = add_realistic_variance(37.6, 0.02)
        patient['spo2'] = add_realistic_variance(98, 0.01)
        patient['symptoms'] = 'Nausea, vomiting, mild diarrhea, cramping, able to tolerate fluids'
        patient['medical_history'] = 'None'
        patient['risk_level'] = 'Low'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} with 24-hour history of gastroenteritis symptoms. Adequate hydration, no signs of severe dehydration or peritonitis."
        
        self.patients.append(patient)
        self.patient_counter += 1
    
    def generate_anxiety(self):
        """Anxiety/Panic Attack - Psychological, normal vitals"""
        age = random.randint(22, 50)
        gender = random.choice(['Male', 'Female'])
        patient = self._base_patient(age, gender)
        
        patient['heart_rate'] = add_realistic_variance(95, 0.1)  # Slightly elevated
        patient['sbp'] = add_realistic_variance(128, 0.08)
        patient['dbp'] = add_realistic_variance(82, 0.08)
        patient['temp_c'] = add_realistic_variance(37.0, 0.02)
        patient['spo2'] = add_realistic_variance(99, 0.01)
        patient['symptoms'] = 'Palpitations, shortness of breath, chest tightness, feeling of panic, tingling hands'
        patient['medical_history'] = random.choice(['Anxiety disorder', 'Depression', 'None'])
        patient['risk_level'] = 'Low'
        patient['target_dept'] = 'General Medicine'
        patient['clinical_note'] = f"{age}yo {gender} with acute anxiety symptoms. Cardiac exam normal, ECG unremarkable, symptoms improving with reassurance."
        
        self.patients.append(patient)
        self.patient_counter += 1

    
    def generate_dataset(self):
        """Generate complete dataset of 50 patients"""
        
        print("Generating Golden 50 Patient Dataset...")
        print("=" * 60)
        
        # HIGH RISK: 10 patients
        print("\n[HIGH RISK] Generating 10 critical cases...")
        for _ in range(2):
            self.generate_stroke()
        for _ in range(3):
            self.generate_myocardial_infarction()
        for _ in range(2):
            self.generate_sepsis()
        for _ in range(2):
            self.generate_anaphylaxis()
        self.generate_dka()
        
        # MEDIUM RISK: 15 patients
        print("[MEDIUM RISK] Generating 15 moderate cases...")
        for _ in range(5):
            self.generate_appendicitis()
        for _ in range(5):
            self.generate_fracture()
        for _ in range(3):
            self.generate_pneumonia()
        for _ in range(2):
            self.generate_moderate_infection()
        
        # LOW RISK: 25 patients
        print("[LOW RISK] Generating 25 minor cases...")
        for _ in range(8):
            self.generate_common_cold()
        for _ in range(5):
            self.generate_migraine()
        for _ in range(4):
            self.generate_minor_allergy()
        for _ in range(4):
            self.generate_minor_injury()
        for _ in range(3):
            self.generate_gastroenteritis()
        self.generate_anxiety()
        
        return self.patients
    
    def save_to_csv(self, filename='data/triage_golden_50.csv'):
        """Save dataset to CSV file"""
        
        # Create data directory if it doesn't exist
        Path('data').mkdir(exist_ok=True)
        
        fieldnames = [
            'patient_id', 'age', 'gender', 'heart_rate', 'sbp', 'dbp',
            'temp_c', 'spo2', 'symptoms', 'medical_history', 
            'risk_level', 'target_dept', 'clinical_note'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.patients)
        
        print(f"\n✓ Dataset saved to: {filename}")
    
    def print_summary(self):
        """Print dataset summary statistics"""
        
        high_risk = sum(1 for p in self.patients if p['risk_level'] == 'High')
        medium_risk = sum(1 for p in self.patients if p['risk_level'] == 'Medium')
        low_risk = sum(1 for p in self.patients if p['risk_level'] == 'Low')
        
        print("\n" + "=" * 60)
        print("DATASET SUMMARY")
        print("=" * 60)
        print(f"Total Patients:    {len(self.patients)}")
        print(f"  🔴 High Risk:    {high_risk} ({high_risk/len(self.patients)*100:.1f}%)")
        print(f"  🟡 Medium Risk:  {medium_risk} ({medium_risk/len(self.patients)*100:.1f}%)")
        print(f"  🟢 Low Risk:     {low_risk} ({low_risk/len(self.patients)*100:.1f}%)")
        
        # Department distribution
        dept_counts = {}
        for p in self.patients:
            dept = p['target_dept']
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        print("\nDepartment Distribution:")
        for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {dept:20s}: {count:2d} patients")
        
        # Vital signs ranges
        print("\nVital Signs Ranges:")
        hr_values = [p['heart_rate'] for p in self.patients]
        sbp_values = [p['sbp'] for p in self.patients]
        temp_values = [p['temp_c'] for p in self.patients]
        spo2_values = [p['spo2'] for p in self.patients]
        
        print(f"  Heart Rate:  {min(hr_values):.0f} - {max(hr_values):.0f} bpm")
        print(f"  Systolic BP: {min(sbp_values):.0f} - {max(sbp_values):.0f} mmHg")
        print(f"  Temperature: {min(temp_values):.1f} - {max(temp_values):.1f} °C")
        print(f"  SpO2:        {min(spo2_values):.0f} - {max(spo2_values):.0f} %")
        
        print("\n" + "=" * 60)
        print("✓ Dataset generation complete!")
        print("=" * 60)
        
        # Show sample patients
        print("\nSample Patients:")
        print("-" * 60)
        for risk in ['High', 'Medium', 'Low']:
            sample = next(p for p in self.patients if p['risk_level'] == risk)
            print(f"\n{risk.upper()} RISK Example: {sample['patient_id']}")
            print(f"  Age: {sample['age']}, Gender: {sample['gender']}")
            print(f"  Vitals: HR={sample['heart_rate']:.0f}, BP={sample['sbp']:.0f}/{sample['dbp']:.0f}, "
                  f"Temp={sample['temp_c']:.1f}°C, SpO2={sample['spo2']:.0f}%")
            print(f"  Symptoms: {sample['symptoms'][:80]}...")
            print(f"  Department: {sample['target_dept']}")


def main():
    """Main execution function"""
    
    generator = ClinicalPatientGenerator()
    
    # Generate dataset
    patients = generator.generate_dataset()
    
    # Save to CSV
    generator.save_to_csv('data/triage_golden_50.csv')
    
    # Print summary
    generator.print_summary()
    
    print("\n💡 Next Steps:")
    print("  1. Review data/triage_golden_50.csv")
    print("  2. Use this dataset to train your Random Forest model")
    print("  3. Test document parsing with the 'clinical_note' field")
    print("  4. Validate that rule-based overrides catch all High Risk cases")


if __name__ == "__main__":
    main()
