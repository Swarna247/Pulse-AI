"""
EHR Integration API Endpoints
FastAPI endpoints for hospital system integration
"""

from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.ehr_adapter import EHRAdapter

router = APIRouter(prefix="/ehr", tags=["EHR Integration"])

# Initialize EHR adapter
ehr_adapter = EHRAdapter(default_format='fhir')


class EHRImportRequest(BaseModel):
    """Request model for importing patient data from EHR"""
    data: str = Field(..., description="Raw EHR data (HL7 message, FHIR JSON, or custom format)")
    format: Optional[Literal['hl7', 'fhir', 'json']] = Field(None, description="Data format (auto-detected if not specified)")
    
    class Config:
        schema_extra = {
            "example": {
                "data": '{"resourceType": "Patient", "id": "PT-001", "name": [{"given": ["John"], "family": "Doe"}]}',
                "format": "fhir"
            }
        }


class EHRExportRequest(BaseModel):
    """Request model for exporting triage results to EHR"""
    triage_result: Dict[str, Any] = Field(..., description="Triage prediction results")
    patient_data: Dict[str, Any] = Field(..., description="Patient information")
    format: Optional[Literal['hl7', 'fhir', 'json']] = Field('fhir', description="Export format")
    
    class Config:
        schema_extra = {
            "example": {
                "triage_result": {
                    "risk": "High",
                    "department": "Cardiology",
                    "confidence": 0.85,
                    "explanation": "Elevated BP and tachycardia"
                },
                "patient_data": {
                    "patient_id": "PT-001",
                    "name": "John Doe",
                    "age": 50,
                    "gender": "Male",
                    "vitals": {
                        "heart_rate": 110,
                        "sbp": 165,
                        "dbp": 95
                    }
                },
                "format": "fhir"
            }
        }


class HL7Message(BaseModel):
    """HL7 message model"""
    message: str = Field(..., description="HL7 v2.x message")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "MSH|^~\\&|APP|HOSPITAL|EHR|HOSPITAL|20240214120000||ADT^A01|MSG001|P|2.5\nPID|1||PT-001||DOE^JOHN||19740515|M"
            }
        }


class FHIRResource(BaseModel):
    """FHIR resource model"""
    resource: Dict[str, Any] = Field(..., description="FHIR R4 resource (JSON)")
    
    class Config:
        schema_extra = {
            "example": {
                "resource": {
                    "resourceType": "Patient",
                    "id": "PT-001",
                    "name": [{"given": ["John"], "family": "Doe"}],
                    "gender": "male",
                    "birthDate": "1974-05-15"
                }
            }
        }


@router.post("/import", summary="Import patient data from EHR system")
async def import_patient_data(request: EHRImportRequest):
    """
    Import patient data from EHR/EMR system
    
    Supports:
    - HL7 v2.x messages (ADT, ORU)
    - FHIR R4 resources (Patient, Observation, Bundle)
    - Custom JSON format
    
    Returns standardized patient data ready for triage
    """
    try:
        # Validate input
        is_valid, error_msg = ehr_adapter.validate_import(request.data, request.format)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid data: {error_msg}")
        
        # Import and parse data
        patient_data = ehr_adapter.import_patient_data(request.data, request.format)
        
        return {
            "success": True,
            "format_detected": request.format or ehr_adapter._detect_format(request.data),
            "patient_data": patient_data,
            "message": "Patient data imported successfully"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")


@router.post("/export", summary="Export triage results to EHR system")
async def export_triage_results(request: EHRExportRequest):
    """
    Export triage results to EHR/EMR system
    
    Formats:
    - HL7 v2.x ORU message (Observation Result)
    - FHIR R4 Bundle (Patient + Observations + DiagnosticReport)
    - Custom JSON format
    
    Returns formatted data ready for EHR system
    """
    try:
        # Export results
        exported_data = ehr_adapter.export_triage_results(
            request.triage_result,
            request.patient_data,
            request.format
        )
        
        return {
            "success": True,
            "format": request.format,
            "data": exported_data,
            "message": "Triage results exported successfully"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.post("/hl7/parse", summary="Parse HL7 message")
async def parse_hl7_message(request: HL7Message):
    """
    Parse HL7 v2.x message and extract patient data
    
    Supports:
    - ADT^A01 (Patient Admission)
    - ORU^R01 (Observation Result)
    - Other HL7 message types with PID, OBX, DG1 segments
    """
    try:
        # Validate HL7 message
        is_valid, error_msg = ehr_adapter.hl7_handler.validate_hl7_message(request.message)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid HL7 message: {error_msg}")
        
        # Parse message
        patient_data = ehr_adapter.hl7_handler.parse_hl7_message(request.message)
        
        return {
            "success": True,
            "patient_data": patient_data,
            "message": "HL7 message parsed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")


@router.post("/hl7/generate", summary="Generate HL7 ORU message")
async def generate_hl7_message(request: EHRExportRequest):
    """
    Generate HL7 v2.x ORU^R01 message with triage results
    
    Returns HL7 message ready to send to hospital system
    """
    try:
        hl7_message = ehr_adapter.hl7_handler.generate_oru_message(
            request.triage_result,
            request.patient_data
        )
        
        return {
            "success": True,
            "message_type": "ORU^R01",
            "hl7_message": hl7_message
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@router.post("/fhir/parse", summary="Parse FHIR resource")
async def parse_fhir_resource(request: FHIRResource):
    """
    Parse FHIR R4 resource and extract patient data
    
    Supports:
    - Patient resource
    - Bundle (collection of resources)
    - Observation resources
    - Condition resources
    """
    try:
        # Validate FHIR resource
        is_valid, error_msg = ehr_adapter.fhir_handler.validate_fhir_resource(request.resource)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid FHIR resource: {error_msg}")
        
        # Parse resource
        patient_data = ehr_adapter._parse_fhir_bundle(request.resource)
        
        return {
            "success": True,
            "resource_type": request.resource.get('resourceType'),
            "patient_data": patient_data,
            "message": "FHIR resource parsed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")


@router.post("/fhir/generate", summary="Generate FHIR Bundle")
async def generate_fhir_bundle(request: EHRExportRequest):
    """
    Generate FHIR R4 Bundle with triage results
    
    Includes:
    - Patient resource
    - Observation resources (vital signs)
    - DiagnosticReport resource (triage results)
    """
    try:
        fhir_bundle = ehr_adapter._create_fhir_bundle(
            request.triage_result,
            request.patient_data
        )
        
        return {
            "success": True,
            "resource_type": "Bundle",
            "fhir_bundle": fhir_bundle
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@router.get("/formats", summary="Get supported formats")
async def get_supported_formats():
    """
    Get list of supported EHR/EMR formats
    """
    return {
        "formats": [
            {
                "name": "HL7 v2.x",
                "code": "hl7",
                "description": "Health Level 7 version 2.x messages",
                "message_types": ["ADT^A01", "ORU^R01"],
                "use_case": "Legacy hospital systems, lab interfaces"
            },
            {
                "name": "FHIR R4",
                "code": "fhir",
                "description": "Fast Healthcare Interoperability Resources version 4",
                "resource_types": ["Patient", "Observation", "Condition", "DiagnosticReport", "Bundle"],
                "use_case": "Modern EHR systems, cloud-based healthcare platforms"
            },
            {
                "name": "JSON",
                "code": "json",
                "description": "Custom JSON format",
                "use_case": "Custom integrations, mobile apps, web services"
            }
        ]
    }


@router.get("/health", summary="EHR integration health check")
async def ehr_health_check():
    """
    Check EHR integration module health
    """
    return {
        "status": "healthy",
        "hl7_handler": "active",
        "fhir_handler": "active",
        "supported_formats": ["hl7", "fhir", "json"]
    }
