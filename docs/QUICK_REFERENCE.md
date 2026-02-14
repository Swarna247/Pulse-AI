# Quick Reference Guide

## 🚀 Getting Started (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Data & Train Models
```bash
python scripts/generate_golden_50.py
python scripts/train_final.py
```

### 3. Start Services
```bash
# Terminal 1
python scripts/run_api.py

# Terminal 2
python scripts/run_dashboard.py
```

### 4. Access Application
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Login: `admin@gmail.com` / `admin@123`

---

## 📂 Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `app/main.py` | Streamlit Dashboard | 1,122 |
| `api/main.py` | FastAPI Backend | ~500 |
| `utils/parser.py` | Clinical Note Parser | ~400 |
| `utils/auth.py` | Authentication | ~150 |
| `integrations/ehr_adapter.py` | EHR Integration | ~300 |
| `scripts/train_final.py` | Model Training | ~400 |

---

## 🎯 Common Tasks

### Run Tests
```bash
# All tests
python tests/test_api.py
python tests/test_ehr_integration.py
python tests/test_parser_with_dataset.py

# Single test
python tests/test_api.py
```

### Retrain Models
```bash
python scripts/train_final.py
```

### Generate New Data
```bash
python scripts/generate_golden_50.py
```

### Check API Health
```bash
curl http://localhost:8000/health
```

---

## 🔧 Configuration

Edit `config/settings.py`:

```python
# Change ports
API_PORT = 8000
DASHBOARD_PORT = 8501

# Change safety thresholds
SAFETY_THRESHOLDS = {
    "spo2_critical": 90,
    "sbp_high": 180,
    ...
}
```

---

## 🌐 API Endpoints

### Triage
```bash
POST http://localhost:8000/api/triage
```

### Health Check
```bash
GET http://localhost:8000/health
```

### EHR Import
```bash
POST http://localhost:8000/ehr/import
```

### EHR Export
```bash
POST http://localhost:8000/ehr/export
```

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details.

---

## 🎨 Dashboard Features

### 1. Authentication
- Login with admin credentials
- Session-based authentication
- Logout button in sidebar

### 2. Language Selection
- English (default)
- Tamil (தமிழ்)
- Hindi (हिंदी)

### 3. Input Methods
- **Manual Entry**: Form with sliders and dropdowns
- **Clinical Note**: Upload text file or paste
- **Voice Assistant**: Speak or type symptoms

### 4. Results Display
- Color-coded risk badge (RED/YELLOW/GREEN)
- Department recommendation
- Confidence score
- Clinical reasoning
- Contributing factors
- Patient queue

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| Risk Accuracy | 96.0% |
| Department Accuracy | 98.0% |
| HIGH Risk Recall | 90% |
| Parser Confidence | 85.7% |

---

## 🔒 Safety Overrides

| Condition | Threshold | Action |
|-----------|-----------|--------|
| SpO2 | < 90% | HIGH → Emergency |
| Systolic BP | > 180 mmHg | HIGH → Emergency |
| Systolic BP | < 90 mmHg | HIGH → Emergency |
| Heart Rate | > 120 bpm | HIGH → Cardiology |
| Heart Rate | < 50 bpm | HIGH → Cardiology |
| Temperature | > 39.5°C | HIGH → Emergency |
| Infant Fever | Age < 2 & Temp > 38°C | HIGH → Emergency |

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Models Not Found
```bash
# Check models exist
dir ml\models  # Windows
ls ml/models   # Mac/Linux

# Retrain if missing
python scripts/train_final.py
```

### Import Errors
```bash
# Ensure in project root
cd pulse-triage-ai

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### API Connection Error
```bash
# Check API is running
curl http://localhost:8000/health

# Restart API
python scripts/run_api.py
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview |
| [SETUP.md](SETUP.md) | Installation guide |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API endpoints |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | File organization |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment |
| [requirements.md](requirements.md) | Requirements spec |
| [design.md](design.md) | Technical design |

---

## 🎓 Demo Script

### 1. Login (30 seconds)
- Open http://localhost:8501
- Login: admin@gmail.com / admin@123

### 2. Language Switch (15 seconds)
- Select Tamil or Hindi from sidebar
- Show multilingual interface

### 3. Voice Assistant (1 minute)
- Type: "I'm a 65 year old male with chest pain and shortness of breath"
- Click Analyze
- Show auto-filled form

### 4. Manual Entry (1 minute)
- Enter patient details
- Adjust vital signs
- Select symptoms

### 5. Run Triage (30 seconds)
- Click "RUN AI TRIAGE"
- Show risk badge
- Explain clinical reasoning

### 6. Patient Queue (15 seconds)
- Show last 5 patients in sidebar
- Demonstrate queue management

### 7. EHR Integration (1 minute)
- Open http://localhost:8000/docs
- Show HL7 and FHIR endpoints
- Demonstrate import/export

**Total Demo Time: ~5 minutes**

---

## 💡 Tips

1. **Use Voice Assistant** for fastest data entry
2. **Check Patient Queue** to see recent assessments
3. **Review Clinical Reasoning** for detailed explanations
4. **Test Safety Overrides** with extreme vital signs
5. **Try Different Languages** to show accessibility
6. **Use API Docs** for integration testing

---

## 🆘 Support

### Common Questions

**Q: How do I change admin password?**
A: Edit `utils/auth.py` and update the password hash.

**Q: Can I add more languages?**
A: Yes! Edit the `TRANSLATIONS` dictionary in `app/main.py`.

**Q: How do I add more symptoms?**
A: Update `SYMPTOM_OPTIONS` list in `app/main.py`.

**Q: Can I retrain with my own data?**
A: Yes! Replace `data/triage_golden_50.csv` and run `scripts/train_final.py`.

**Q: How do I deploy to production?**
A: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide.

---

## 📞 Contact

For issues or questions:
1. Check documentation in `docs/` folder
2. Review troubleshooting section above
3. Check API logs for errors
4. Verify all dependencies installed

---

**Last Updated**: February 14, 2026
**Version**: 1.0.0
