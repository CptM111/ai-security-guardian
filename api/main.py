"""
AI Security Guardian - Main API Server
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import uvicorn
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.prompt_firewall_v2 import EnhancedPromptFirewall
from components.output_sanitizer import OutputSanitizer
from components.model_scanner import ModelScanner
from auth.api_key_manager import APIKeyManager

# Initialize FastAPI app
app = FastAPI(
    title="AI Security Guardian API",
    description="Comprehensive AI security platform for the AI era",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize security components
prompt_firewall = EnhancedPromptFirewall()
output_sanitizer = OutputSanitizer()
model_scanner = ModelScanner()
api_key_manager = APIKeyManager("data/api_keys.db")

# ============================================================================
# Models
# ============================================================================

class StatusEnum(str, Enum):
    SAFE = "safe"
    BLOCKED = "blocked"
    WARNING = "warning"

class PromptProtectRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to analyze")
    model_id: str = Field(..., description="The target model ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class PromptProtectResponse(BaseModel):
    status: StatusEnum
    reason: Optional[str] = None
    sanitized_prompt: Optional[str] = None
    alert_id: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    attack_types: List[str] = []

class OutputProtectRequest(BaseModel):
    content: str = Field(..., description="The output content to sanitize")
    context: str = Field("general", description="Output context (html, json, sql, etc.)")
    model_id: Optional[str] = Field(None, description="Source model ID")

class OutputProtectResponse(BaseModel):
    status: StatusEnum
    sanitized_content: str
    removed_elements: List[str] = []
    warnings: List[str] = []

class ModelScanRequest(BaseModel):
    model_path: Optional[str] = Field(None, description="Path to model file")
    model_url: Optional[str] = Field(None, description="URL to model")
    model_id: str = Field(..., description="Model identifier")
    scan_type: str = Field("full", description="Scan type: quick, full, deep")

class ModelScanResponse(BaseModel):
    scan_id: str
    status: str
    vulnerabilities: List[Dict[str, Any]] = []
    risk_score: float = Field(..., ge=0.0, le=10.0)
    recommendations: List[str] = []

class Alert(BaseModel):
    alert_id: str
    timestamp: datetime
    severity: str
    alert_type: str
    description: str
    affected_resource: str
    status: str

class AlertListResponse(BaseModel):
    alerts: List[Alert]
    total: int
    page: int
    page_size: int

# ============================================================================
# Authentication
# ============================================================================

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """
    Verify API key from Authorization header
    
    Validates against database and checks:
    - Key exists
    - Key is active (not revoked)
    - Key has not expired
    
    Raises:
        HTTPException: If authentication fails
    
    Returns:
        str: The validated API key
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include 'Authorization: Bearer <your-key>' header."
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Use 'Bearer <your-key>'."
        )
    
    api_key = authorization.replace("Bearer ", "")
    
    # Validate against database
    is_valid, reason = api_key_manager.validate_key(api_key)
    
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {reason}"
        )
    
    return api_key

# ============================================================================
# Routes
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Security Guardian API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "prompt_firewall": "operational",
            "output_sanitizer": "operational",
            "model_scanner": "operational"
        }
    }

# ============================================================================
# Protect Endpoints
# ============================================================================

@app.post("/api/v1/protect/prompt", response_model=PromptProtectResponse)
async def protect_prompt(
    request: PromptProtectRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze and protect prompts against injection attacks, jailbreaking, and other threats.
    
    This endpoint uses the Prompt Firewall to detect:
    - Prompt injection attacks
    - Jailbreak attempts
    - System prompt leakage attempts
    - Malicious instructions
    """
    try:
        result = prompt_firewall.check_prompt(request.prompt)
        
        return PromptProtectResponse(
            status=StatusEnum.BLOCKED if result.is_threat else StatusEnum.SAFE,
            reason=result.details if result.is_threat else None,
            sanitized_prompt=request.prompt if not result.is_threat else "",
            alert_id=f"alert-{datetime.utcnow().timestamp()}" if result.is_threat else None,
            confidence=result.confidence,
            attack_types=result.attack_types
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protection failed: {str(e)}")

@app.post("/api/v1/protect/output", response_model=OutputProtectResponse)
async def protect_output(
    request: OutputProtectRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Sanitize and validate LLM outputs to prevent XSS, SQLi, and other injection attacks.
    
    This endpoint uses the Output Sanitizer to:
    - Remove malicious code (XSS, SQLi)
    - Validate output format
    - Apply data loss prevention (DLP)
    - Filter harmful content
    """
    try:
        result = output_sanitizer.sanitize(
            content=request.content,
            context=request.context
        )
        
        return OutputProtectResponse(
            status=StatusEnum.WARNING if result["warnings"] else StatusEnum.SAFE,
            sanitized_content=result["sanitized_content"],
            removed_elements=result.get("removed_elements", []),
            warnings=result.get("warnings", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sanitization failed: {str(e)}")

# ============================================================================
# Scan Endpoints
# ============================================================================

@app.post("/api/v1/scan/model", response_model=ModelScanResponse)
async def scan_model(
    request: ModelScanRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Scan AI models for vulnerabilities, backdoors, and integrity issues.
    
    This endpoint performs:
    - Static analysis of model files
    - Backdoor detection
    - Integrity verification
    - Vulnerability assessment
    """
    try:
        result = model_scanner.scan(
            model_path=request.model_path,
            model_url=request.model_url,
            model_id=request.model_id,
            scan_type=request.scan_type
        )
        
        return ModelScanResponse(
            scan_id=result["scan_id"],
            status=result["status"],
            vulnerabilities=result.get("vulnerabilities", []),
            risk_score=result["risk_score"],
            recommendations=result.get("recommendations", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

# ============================================================================
# Monitor Endpoints
# ============================================================================

@app.get("/api/v1/monitor/alerts", response_model=AlertListResponse)
async def get_alerts(
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Retrieve security alerts.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - severity: Filter by severity (critical, high, medium, low)
    """
    # In production, fetch from database
    # For prototype, return mock data
    mock_alerts = [
        Alert(
            alert_id=f"alert-{i}",
            timestamp=datetime.utcnow(),
            severity="high" if i % 2 == 0 else "medium",
            alert_type="prompt_injection",
            description=f"Potential prompt injection detected in request {i}",
            affected_resource=f"model-gpt-4-{i}",
            status="active"
        )
        for i in range(1, 6)
    ]
    
    return AlertListResponse(
        alerts=mock_alerts,
        total=len(mock_alerts),
        page=page,
        page_size=page_size
    )

@app.post("/api/v1/monitor/feedback")
async def submit_feedback(
    alert_id: str,
    feedback: str,
    is_false_positive: bool = False,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit human feedback on an alert to improve the ATI Engine.
    """
    return {
        "status": "success",
        "message": "Feedback recorded",
        "alert_id": alert_id
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
