"""
Final Model Training Script
Trains Random Forest models for Risk Level and Department prediction
Uses Leave-One-Out Cross-Validation for robust evaluation on small dataset
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import re
import warnings
warnings.filterwarnings('ignore')

class TriageModelTrainer:
    """Train and evaluate triage prediction models"""
    
    def __init__(self, data_path='data/triage_golden_50.csv'):
        self.data_path = data_path
        self.df = None
        self.X = None
        self.y_risk = None
        self.y_dept = None
        
        # Models and transformers
        self.scaler = StandardScaler()
        self.risk_encoder = LabelEncoder()
        self.dept_encoder = LabelEncoder()
        self.risk_model = None
        self.dept_model = None
        
        # Feature names for reference
        self.feature_names = []
        
        # Symptom keywords for feature extraction
        self.symptom_keywords = [
            'chest pain', 'shortness of breath', 'sweating', 'nausea',
            'confusion', 'weakness', 'drooping', 'slurred speech',
            'fever', 'cough', 'wheezing', 'difficulty breathing',
            'abdominal pain', 'vomiting', 'diarrhea',
            'headache', 'dizziness', 'vision',
            'swelling', 'hives', 'rash', 'itching',
            'pain', 'bleeding', 'fracture', 'deformity'
        ]
    
    def load_data(self):
        """Load and inspect the dataset"""
        print("=" * 70)
        print("LOADING DATASET")
        print("=" * 70)
        
        self.df = pd.read_csv(self.data_path)
        print(f"✓ Loaded {len(self.df)} patients from {self.data_path}")
        print(f"\nColumns: {list(self.df.columns)}")
        print(f"\nRisk Level Distribution:")
        print(self.df['risk_level'].value_counts())
        print(f"\nDepartment Distribution:")
        print(self.df['target_dept'].value_counts())
        
        return self.df
    
    def extract_symptom_features(self, symptoms_text):
        """Extract binary features from symptom text using keyword matching"""
        symptoms_lower = symptoms_text.lower()
        features = []
        
        for keyword in self.symptom_keywords:
            features.append(1 if keyword in symptoms_lower else 0)
        
        return features
    
    def engineer_features(self):
        """Create feature matrix from raw data"""
        print("\n" + "=" * 70)
        print("FEATURE ENGINEERING")
        print("=" * 70)
        
        features = []

        
        for idx, row in self.df.iterrows():
            patient_features = []
            
            # 1. Demographic features
            patient_features.append(row['age'])
            patient_features.append(1 if row['gender'] == 'Male' else 0)
            
            # 2. Vital signs (will be scaled later)
            patient_features.append(row['heart_rate'])
            patient_features.append(row['sbp'])
            patient_features.append(row['dbp'])
            patient_features.append(row['temp_c'])
            patient_features.append(row['spo2'])
            
            # 3. Derived vital features
            pulse_pressure = row['sbp'] - row['dbp']
            map_pressure = row['dbp'] + (pulse_pressure / 3)
            patient_features.append(pulse_pressure)
            patient_features.append(map_pressure)
            
            # 4. Medical history flags
            history = str(row['medical_history']).lower()
            patient_features.append(1 if 'hypertension' in history else 0)
            patient_features.append(1 if 'diabetes' in history else 0)
            patient_features.append(1 if any(word in history for word in ['cardiac', 'heart', 'mi']) else 0)
            patient_features.append(1 if any(word in history for word in ['copd', 'asthma', 'respiratory']) else 0)
            
            # 5. Symptom features (keyword-based)
            symptom_features = self.extract_symptom_features(row['symptoms'])
            patient_features.extend(symptom_features)
            
            features.append(patient_features)
        
        # Create feature names
        self.feature_names = [
            'age', 'gender_male',
            'heart_rate', 'sbp', 'dbp', 'temp_c', 'spo2',
            'pulse_pressure', 'map',
            'history_hypertension', 'history_diabetes', 'history_cardiac', 'history_respiratory'
        ]
        self.feature_names.extend([f'symptom_{kw.replace(" ", "_")}' for kw in self.symptom_keywords])
        
        self.X = np.array(features)
        
        print(f"✓ Created feature matrix: {self.X.shape}")
        print(f"  - {self.X.shape[0]} patients")
        print(f"  - {self.X.shape[1]} features")
        print(f"\nFeature categories:")
        print(f"  - Demographics: 2")
        print(f"  - Vital signs: 7 (5 raw + 2 derived)")
        print(f"  - Medical history: 4")
        print(f"  - Symptoms: {len(self.symptom_keywords)}")
        
        return self.X
    
    def prepare_targets(self):
        """Encode target variables"""
        print("\n" + "=" * 70)
        print("PREPARING TARGETS")
        print("=" * 70)
        
        # Encode risk levels
        self.y_risk = self.risk_encoder.fit_transform(self.df['risk_level'])
        print(f"✓ Risk Level Classes: {list(self.risk_encoder.classes_)}")
        
        # Encode departments
        self.y_dept = self.dept_encoder.fit_transform(self.df['target_dept'])
        print(f"✓ Department Classes: {list(self.dept_encoder.classes_)}")
        
        return self.y_risk, self.y_dept
    
    def scale_features(self):
        """Scale numerical features"""
        print("\n" + "=" * 70)
        print("SCALING FEATURES")
        print("=" * 70)
        
        self.X = self.scaler.fit_transform(self.X)
        print(f"✓ Features scaled using StandardScaler")
        print(f"  Mean: {self.scaler.mean_[:5]}...")
        print(f"  Std:  {self.scaler.scale_[:5]}...")
        
        return self.X
    
    def train_with_loocv(self):
        """Train models using Leave-One-Out Cross-Validation"""
        print("\n" + "=" * 70)
        print("TRAINING WITH LEAVE-ONE-OUT CROSS-VALIDATION")
        print("=" * 70)
        
        # Initialize models
        self.risk_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            class_weight='balanced'  # Handle class imbalance
        )
        
        self.dept_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )
        
        # LOOCV for Risk Level
        print("\n[1/2] Risk Level Model")
        print("-" * 70)
        loo = LeaveOneOut()
        
        risk_predictions = []
        risk_actuals = []
        
        for train_idx, test_idx in loo.split(self.X):
            X_train, X_test = self.X[train_idx], self.X[test_idx]
            y_train, y_test = self.y_risk[train_idx], self.y_risk[test_idx]
            
            self.risk_model.fit(X_train, y_train)
            pred = self.risk_model.predict(X_test)
            
            risk_predictions.append(pred[0])
            risk_actuals.append(y_test[0])
        
        risk_accuracy = accuracy_score(risk_actuals, risk_predictions)
        print(f"✓ LOOCV Accuracy: {risk_accuracy:.3f} ({risk_accuracy*100:.1f}%)")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(
            risk_actuals, 
            risk_predictions,
            target_names=self.risk_encoder.classes_,
            zero_division=0
        ))
        
        # Confusion matrix
        print("Confusion Matrix:")
        cm = confusion_matrix(risk_actuals, risk_predictions)
        print(f"Classes: {self.risk_encoder.classes_}")
        print(cm)
        
        # LOOCV for Department
        print("\n[2/2] Department Model")
        print("-" * 70)
        
        dept_predictions = []
        dept_actuals = []
        
        for train_idx, test_idx in loo.split(self.X):
            X_train, X_test = self.X[train_idx], self.X[test_idx]
            y_train, y_test = self.y_dept[train_idx], self.y_dept[test_idx]
            
            self.dept_model.fit(X_train, y_train)
            pred = self.dept_model.predict(X_test)
            
            dept_predictions.append(pred[0])
            dept_actuals.append(y_test[0])
        
        dept_accuracy = accuracy_score(dept_actuals, dept_predictions)
        print(f"✓ LOOCV Accuracy: {dept_accuracy:.3f} ({dept_accuracy*100:.1f}%)")
        
        # Train final models on full dataset
        print("\n" + "-" * 70)
        print("Training final models on complete dataset...")
        self.risk_model.fit(self.X, self.y_risk)
        self.dept_model.fit(self.X, self.y_dept)
        print("✓ Final models trained")
        
        return risk_accuracy, dept_accuracy
    
    def analyze_feature_importance(self):
        """Analyze and display feature importance"""
        print("\n" + "=" * 70)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("=" * 70)
        
        # Risk model feature importance
        risk_importance = self.risk_model.feature_importances_
        risk_features = sorted(
            zip(self.feature_names, risk_importance),
            key=lambda x: x[1],
            reverse=True
        )
        
        print("\nTop 10 Features for Risk Prediction:")
        for i, (feature, importance) in enumerate(risk_features[:10], 1):
            print(f"  {i:2d}. {feature:30s}: {importance:.4f}")
        
        # Department model feature importance
        dept_importance = self.dept_model.feature_importances_
        dept_features = sorted(
            zip(self.feature_names, dept_importance),
            key=lambda x: x[1],
            reverse=True
        )
        
        print("\nTop 10 Features for Department Prediction:")
        for i, (feature, importance) in enumerate(dept_features[:10], 1):
            print(f"  {i:2d}. {feature:30s}: {importance:.4f}")

    
    def save_models(self, output_dir='ml/models'):
        """Save trained models and transformers"""
        print("\n" + "=" * 70)
        print("SAVING MODELS")
        print("=" * 70)
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save models
        joblib.dump(self.risk_model, f'{output_dir}/risk_model.pkl')
        print(f"✓ Saved: {output_dir}/risk_model.pkl")
        
        joblib.dump(self.dept_model, f'{output_dir}/dept_model.pkl')
        print(f"✓ Saved: {output_dir}/dept_model.pkl")
        
        # Save transformers
        joblib.dump(self.scaler, f'{output_dir}/scaler.pkl')
        print(f"✓ Saved: {output_dir}/scaler.pkl")
        
        joblib.dump(self.risk_encoder, f'{output_dir}/risk_encoder.pkl')
        print(f"✓ Saved: {output_dir}/risk_encoder.pkl")
        
        joblib.dump(self.dept_encoder, f'{output_dir}/dept_encoder.pkl')
        print(f"✓ Saved: {output_dir}/dept_encoder.pkl")
        
        # Save feature names and symptom keywords
        metadata = {
            'feature_names': self.feature_names,
            'symptom_keywords': self.symptom_keywords,
            'n_features': len(self.feature_names),
            'risk_classes': list(self.risk_encoder.classes_),
            'dept_classes': list(self.dept_encoder.classes_)
        }
        joblib.dump(metadata, f'{output_dir}/metadata.pkl')
        print(f"✓ Saved: {output_dir}/metadata.pkl")
        
        print(f"\n✓ All models saved to {output_dir}/")
    
    def verify_with_test_case(self):
        """Test the model with a sample stroke case"""
        print("\n" + "=" * 70)
        print("VERIFICATION: TESTING WITH STROKE CASE")
        print("=" * 70)
        
        # Find a stroke patient from the dataset
        stroke_patient = self.df[self.df['target_dept'] == 'Neurology'].iloc[0]
        
        print("\nTest Patient:")
        print(f"  ID: {stroke_patient['patient_id']}")
        print(f"  Age: {stroke_patient['age']}, Gender: {stroke_patient['gender']}")
        print(f"  Vitals: HR={stroke_patient['heart_rate']:.0f}, "
              f"BP={stroke_patient['sbp']:.0f}/{stroke_patient['dbp']:.0f}, "
              f"Temp={stroke_patient['temp_c']:.1f}°C, SpO2={stroke_patient['spo2']:.0f}%")
        print(f"  Symptoms: {stroke_patient['symptoms'][:80]}...")
        print(f"  Actual Risk: {stroke_patient['risk_level']}")
        print(f"  Actual Dept: {stroke_patient['target_dept']}")
        
        # Prepare features for this patient
        test_features = []
        test_features.append(stroke_patient['age'])
        test_features.append(1 if stroke_patient['gender'] == 'Male' else 0)
        test_features.append(stroke_patient['heart_rate'])
        test_features.append(stroke_patient['sbp'])
        test_features.append(stroke_patient['dbp'])
        test_features.append(stroke_patient['temp_c'])
        test_features.append(stroke_patient['spo2'])
        
        pulse_pressure = stroke_patient['sbp'] - stroke_patient['dbp']
        map_pressure = stroke_patient['dbp'] + (pulse_pressure / 3)
        test_features.append(pulse_pressure)
        test_features.append(map_pressure)
        
        history = str(stroke_patient['medical_history']).lower()
        test_features.append(1 if 'hypertension' in history else 0)
        test_features.append(1 if 'diabetes' in history else 0)
        test_features.append(1 if any(word in history for word in ['cardiac', 'heart', 'mi']) else 0)
        test_features.append(1 if any(word in history for word in ['copd', 'asthma', 'respiratory']) else 0)
        
        symptom_features = self.extract_symptom_features(stroke_patient['symptoms'])
        test_features.extend(symptom_features)
        
        # Scale features
        test_features = np.array(test_features).reshape(1, -1)
        test_features_scaled = self.scaler.transform(test_features)
        
        # Make predictions
        risk_pred = self.risk_model.predict(test_features_scaled)[0]
        risk_proba = self.risk_model.predict_proba(test_features_scaled)[0]
        
        dept_pred = self.dept_model.predict(test_features_scaled)[0]
        dept_proba = self.dept_model.predict_proba(test_features_scaled)[0]
        
        print("\nModel Predictions:")
        print(f"  Predicted Risk: {self.risk_encoder.inverse_transform([risk_pred])[0]}")
        print(f"  Risk Confidence: {max(risk_proba):.3f}")
        print(f"  Risk Probabilities:")
        for cls, prob in zip(self.risk_encoder.classes_, risk_proba):
            print(f"    {cls:10s}: {prob:.3f}")
        
        print(f"\n  Predicted Dept: {self.dept_encoder.inverse_transform([dept_pred])[0]}")
        print(f"  Dept Confidence: {max(dept_proba):.3f}")
        print(f"  Top 3 Departments:")
        dept_probs = sorted(
            zip(self.dept_encoder.classes_, dept_proba),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        for dept, prob in dept_probs:
            print(f"    {dept:20s}: {prob:.3f}")
        
        # Verification
        actual_risk = stroke_patient['risk_level']
        predicted_risk = self.risk_encoder.inverse_transform([risk_pred])[0]
        
        if actual_risk == predicted_risk:
            print(f"\n✓ VERIFICATION PASSED: Risk level correctly predicted!")
        else:
            print(f"\n⚠ VERIFICATION WARNING: Risk mismatch (Expected: {actual_risk}, Got: {predicted_risk})")


def main():
    """Main training pipeline"""
    
    print("\n" + "=" * 70)
    print("TRIAGE AI MODEL TRAINING PIPELINE")
    print("=" * 70)
    
    # Initialize trainer
    trainer = TriageModelTrainer('data/triage_golden_50.csv')
    
    # Step 1: Load data
    trainer.load_data()
    
    # Step 2: Feature engineering
    trainer.engineer_features()
    
    # Step 3: Prepare targets
    trainer.prepare_targets()
    
    # Step 4: Scale features
    trainer.scale_features()
    
    # Step 5: Train with LOOCV
    risk_acc, dept_acc = trainer.train_with_loocv()
    
    # Step 6: Analyze feature importance
    trainer.analyze_feature_importance()
    
    # Step 7: Save models
    trainer.save_models()
    
    # Step 8: Verify with test case
    trainer.verify_with_test_case()
    
    # Final summary
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"✓ Risk Level Accuracy:  {risk_acc:.3f} ({risk_acc*100:.1f}%)")
    print(f"✓ Department Accuracy:  {dept_acc:.3f} ({dept_acc*100:.1f}%)")
    print(f"✓ Models saved to: ml/models/")
    print("\n💡 Next Steps:")
    print("  1. Integrate models into FastAPI backend")
    print("  2. Implement rule-based safety overrides")
    print("  3. Add SHAP explainability layer")
    print("  4. Build Streamlit dashboard")
    print("=" * 70)


if __name__ == "__main__":
    main()
