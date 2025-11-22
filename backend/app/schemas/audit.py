"""
Audit API schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ContractLanguage(str, Enum):
    """Supported contract languages"""
    SOLIDITY = "solidity"
    VYPER = "vyper"
    MOVE = "move"


class AuditStatus(str, Enum):
    """Audit status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ContractFile(BaseModel):
    """Contract file for multi-file projects"""
    name: str = Field(..., description="File name")
    content: str = Field(..., description="File content")


class AuditRequest(BaseModel):
    """Request schema for creating a new audit"""
    code: str = Field(..., description="Smart contract source code", min_length=1)
    language: ContractLanguage = Field(default=ContractLanguage.SOLIDITY)
    compiler_version: Optional[str] = Field(None, description="Compiler version (e.g., 0.8.20)")
    optimization_enabled: bool = Field(default=False, description="Whether optimization is enabled")
    files: Optional[List[ContractFile]] = Field(None, description="Additional files for multi-file projects")

    @validator("code")
    def validate_code(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Code cannot be empty")
        if len(v) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Code size exceeds 10MB limit")
        return v


class AuditResponse(BaseModel):
    """Response schema for audit creation"""
    audit_id: str
    status: AuditStatus
    estimated_time: int = Field(..., description="Estimated processing time in seconds")
    message: str


class LocationInfo(BaseModel):
    """Code location information"""
    file: Optional[str] = None
    line: Optional[int] = None
    function: Optional[str] = None


class VulnerabilityDetail(BaseModel):
    """Detailed vulnerability information"""
    id: str
    title: str
    severity: VulnerabilitySeverity
    exploitability: Optional[str] = None
    category: Optional[str] = None
    location: LocationInfo
    description: str
    exploit_scenario: Optional[str] = None
    recommendation: Optional[str] = None
    fixed_code: Optional[str] = None
    code_snippet: Optional[str] = None
    cwe_id: Optional[str] = None
    swc_id: Optional[str] = None
    references: Optional[List[str]] = None
    detected_by: Optional[str] = None
    confidence: int = 100


class GasOptimization(BaseModel):
    """Gas optimization suggestion"""
    issue: str
    line: Optional[int] = None
    current_cost: Optional[str] = None
    optimized_cost: Optional[str] = None
    savings: Optional[str] = None
    recommendation: str


class GasAnalysisResult(BaseModel):
    """Gas analysis results"""
    total_estimated_gas: Optional[int] = None
    optimizations: List[GasOptimization] = []
    potential_savings: Optional[str] = None


class ContractInfo(BaseModel):
    """Contract metadata"""
    language: str
    compiler_version: Optional[str] = None
    contract_name: Optional[str] = None
    total_lines: int = 0


class AIAnalysis(BaseModel):
    """AI-powered analysis results"""
    summary: Optional[str] = None
    overall_risk: Optional[str] = None
    architectural_issues: Optional[List[str]] = None
    logic_flaws: Optional[List[str]] = None
    best_practice_violations: Optional[List[str]] = None


class AuditResult(BaseModel):
    """Complete audit result"""
    audit_id: str
    status: AuditStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[int] = None

    contract_info: ContractInfo

    # Vulnerability summary
    vulnerabilities: List[VulnerabilityDetail]
    vulnerability_counts: Dict[str, int] = Field(
        default_factory=lambda: {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
    )

    # Scoring
    risk_score: int = Field(..., ge=0, le=100)
    security_rating: Optional[str] = None

    # Analysis results
    gas_analysis: Optional[GasAnalysisResult] = None
    ai_analysis: Optional[AIAnalysis] = None

    # Recommendations
    recommendations: Optional[List[str]] = None

    error_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
