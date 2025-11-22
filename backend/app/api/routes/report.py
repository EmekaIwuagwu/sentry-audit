"""
Report generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import io
import uuid

from app.config import settings
from app.core.database import get_db
from app.models.audit import Audit, AuditStatus
from app.models.report import Report, ReportFormat
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/report/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db)
):
    """
    Generates downloadable audit report

    Args:
        request: Report generation request
        db: Database session

    Returns:
        Report metadata with download URL
    """
    # Get audit from database
    audit = db.query(Audit).filter(Audit.id == request.audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if audit.status != AuditStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Audit is not completed yet")

    try:
        # Generate report
        report_generator = ReportGenerator()
        report_content = report_generator.generate(
            audit=audit,
            format=request.format,
            options=request.options
        )

        # Determine file name
        file_extension = request.format.value
        file_name = f"audit_report_{audit.id[:8]}_{datetime.utcnow().strftime('%Y%m%d')}.{file_extension}"

        # Create report record
        report = Report(
            audit_id=audit.id,
            format=request.format,
            file_name=file_name,
            file_size_bytes=str(len(report_content)),
            content=report_content if len(report_content) < 10 * 1024 * 1024 else None,  # Store if < 10MB
            share_token=str(uuid.uuid4()),
            share_expires_at=datetime.utcnow() + timedelta(days=30)
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        logger.info(f"Generated report {report.id} for audit {audit.id}")

        return ReportResponse(
            report_id=report.id,
            audit_id=audit.id,
            format=request.format,
            file_name=file_name,
            file_size_bytes=int(report.file_size_bytes) if report.file_size_bytes else None,
            download_url=f"/api/v1/report/{report.id}/download",
            created_at=report.created_at,
            share_token=report.share_token
        )

    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{report_id}/download")
async def download_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Download a generated report

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Report file stream
    """
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.content:
        raise HTTPException(status_code=404, detail="Report content not available")

    # Determine media type
    media_types = {
        ReportFormat.PDF: "application/pdf",
        ReportFormat.JSON: "application/json",
        ReportFormat.HTML: "text/html",
        ReportFormat.MARKDOWN: "text/markdown"
    }

    media_type = media_types.get(report.format, "application/octet-stream")

    return StreamingResponse(
        io.BytesIO(report.content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={report.file_name}"
        }
    )


@router.get("/report/{report_id}")
async def get_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Get report metadata

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Report metadata
    """
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report.to_dict()


@router.get("/audit/{audit_id}/reports")
async def list_audit_reports(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """
    List all reports for an audit

    Args:
        audit_id: Audit ID
        db: Database session

    Returns:
        List of reports
    """
    reports = db.query(Report).filter(Report.audit_id == audit_id).all()

    return {
        "audit_id": audit_id,
        "total": len(reports),
        "reports": [report.to_dict() for report in reports]
    }
