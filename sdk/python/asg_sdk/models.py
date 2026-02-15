"""
SDK Data Models
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProtectPromptResponse(BaseModel):
    """Response from prompt protection endpoint"""
    status: str
    reason: Optional[str] = None
    sanitized_prompt: Optional[str] = None
    alert_id: Optional[str] = None
    confidence: float
    attack_types: List[str] = []


class ProtectOutputResponse(BaseModel):
    """Response from output protection endpoint"""
    status: str
    sanitized_content: str
    removed_elements: List[str] = []
    warnings: List[str] = []


class Vulnerability(BaseModel):
    """Model vulnerability"""
    id: str
    name: str
    severity: str
    description: str
    affected_component: str


class ScanModelResponse(BaseModel):
    """Response from model scan endpoint"""
    scan_id: str
    status: str
    vulnerabilities: List[Dict[str, Any]] = []
    risk_score: float
    recommendations: List[str] = []


class Alert(BaseModel):
    """Security alert"""
    alert_id: str
    timestamp: datetime
    severity: str
    alert_type: str
    description: str
    affected_resource: str
    status: str


class AlertListResponse(BaseModel):
    """List of alerts"""
    alerts: List[Alert]
    total: int
    page: int
    page_size: int
