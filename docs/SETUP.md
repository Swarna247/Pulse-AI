# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional)

## Installation Steps

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd pulse-triage-ai
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Training Data

```bash
python scripts/generate_golden_50.py
```

This creates `data/triage_golden_50.csv` with 50 synthetic patients.

### 5. Train Models

```bash
python scripts/train_final.py
```

This trains the ML models and saves them to `ml/models/`.

### 6. Run Tests (Optional)

```bash
# Test API
python tests/test_api.py

# Test Parser
python -m pytest tests/test_parser_with_dataset.py

# Test EHR Integration
python tests/test_ehr_integration.py
```

## Running the System

### Option 1: Using Scripts (Recommended)

**Terminal 1 - API Server:**
```bash
python scripts/run_api.py
```

**Terminal 2 - Dashboard:**
```bash
python scripts/run_dashboard.py
```

### Option 2: Direct Execution

**Terminal 1 - API Server:**
```bash
python api/main.py
```

**Terminal 2 - Dashboard:**
```bash
streamlit run app/main.py --server.port 8501
```

## Access the Application

1. Open browser to: http://localhost:8501
2. Login with:
   - Email: `admin@gmail.com`
   - Password: `admin@123`

## Troubleshooting

### Port Already in Use

If port 8000 or 8501 is already in use:

```bash
# Windows - Kill process on port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Module Not Found Errors

Make sure you're in the project root directory and virtual environment is activated:

```bash
# Check current directory
pwd  # Mac/Linux
cd   # Windows

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Models Not Found

Ensure you've run the training script:

```bash
python scripts/train_final.py
```

Check that `ml/models/` contains 6 .pkl files.

## Configuration

Edit `config/settings.py` to customize:
- API host and port
- Dashboard port
- Model paths
- Safety thresholds
- EHR integration settings

## Next Steps

- Read [README.md](../README.md) for feature overview
- Check [requirements.md](requirements.md) for detailed requirements
- Review [design.md](design.md) for technical architecture
