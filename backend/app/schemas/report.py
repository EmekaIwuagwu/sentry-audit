"""
Report API schemas
"""
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


class ReportOptions(BaseModel):
    """Report generation options"""
    include_code_snippets: bool = Field(default=True)
    include_gas_analysis: bool = Field(default=True)
    include_ai_insights: bool = Field(default=True)
    include_recommendations: bool = Field(default=True)
    include_executive_summary: bool = Field(default=True)


class ReportRequest(BaseModel):
    """Request schema for report generation"""
    audit_id: str = Field(..., description="Audit ID to generate report for")
    format: ReportFormat = Field(default=ReportFormat.PDF)
    options: Optional[ReportOptions] = Field(default_factory=ReportOptions)


class ReportResponse(BaseModel):
    """Response schema for report generation"""
    report_id: str
    audit_id: str
    format: ReportFormat
    file_name: str
    file_size_bytes: Optional[int] = None
    download_url: str
    created_at: datetime
    share_token: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
