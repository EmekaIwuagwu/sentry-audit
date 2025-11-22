"""
Audit endpoints
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime

from app.config import settings
from app.core.database import get_db
from app.models.audit import Audit, AuditStatus
from app.models.vulnerability import Vulnerability
from app.schemas.audit import (
    AuditRequest,
    AuditResponse,
    AuditResult,
    ContractInfo,
    VulnerabilityDetail,
    LocationInfo,
    GasAnalysisResult,
    AIAnalysis,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def process_audit_task(audit_id: str, db_url: str):
    """
    Background task to process audit
    This will be moved to Celery worker in production
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.services.analyzers.static_analyzer import StaticAnalyzer
    from app.services.ai.reasoning_engine import AIReasoningEngine
    from app.services.gas_analyzer import GasAnalyzer
    from app.utils.scoring import calculate_risk_score, calculate_security_rating

    # Create new DB session for background task
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Get audit from database
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            logger.error(f"Audit {audit_id} not found")
            return

        # Update status to processing
        audit.status = AuditStatus.PROCESSING
        db.commit()

        start_time = datetime.utcnow()
        logger.info(f"Starting audit processing for {audit_id}")

        # Initialize analyzers
        static_analyzer = StaticAnalyzer()
        ai_engine = AIReasoningEngine()
        gas_analyzer = GasAnalyzer()

        # Parse and analyze contract
        vulnerabilities = []

        # Static analysis
        try:
            static_findings = static_analyzer.analyze(
                code=audit.contract_code,
                language=audit.language.value,
                compiler_version=audit.compiler_version
            )
            vulnerabilities.extend(static_findings)
        except Exception as e:
            logger.error(f"Static analysis failed: {e}")

        # AI analysis
        try:
            ai_findings = ai_engine.analyze(
                code=audit.contract_code,
                language=audit.language.value,
                static_findings=vulnerabilities
            )
            vulnerabilities.extend(ai_findings.get("vulnerabilities", []))

            # Store AI analysis
            audit.ai_summary = ai_findings.get("summary")
            audit.ai_overall_risk = ai_findings.get("overall_risk")
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")

        # Gas analysis
        try:
            gas_results = gas_analyzer.analyze(audit.contract_code)
            audit.gas_analysis = gas_results
        except Exception as e:
            logger.error(f"Gas analysis failed: {e}")

        # Save vulnerabilities to database
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

        for vuln_data in vulnerabilities:
            vuln = Vulnerability(
                audit_id=audit.id,
                rule_id=vuln_data.get("rule_id"),
                title=vuln_data.get("title"),
                severity=vuln_data.get("severity"),
                exploitability=vuln_data.get("exploitability"),
                category=vuln_data.get("category"),
                file_name=vuln_data.get("file_name"),
                line_number=vuln_data.get("line_number"),
                function_name=vuln_data.get("function_name"),
                code_snippet=vuln_data.get("code_snippet"),
                description=vuln_data.get("description"),
                exploit_scenario=vuln_data.get("exploit_scenario"),
                recommendation=vuln_data.get("recommendation"),
                fixed_code=vuln_data.get("fixed_code"),
                cwe_id=vuln_data.get("cwe_id"),
                swc_id=vuln_data.get("swc_id"),
                references=vuln_data.get("references"),
                detected_by=vuln_data.get("detected_by"),
                confidence=vuln_data.get("confidence", 100),
            )
            db.add(vuln)

            # Update counts
            severity = vuln_data.get("severity", "info")
            if severity in severity_counts:
                severity_counts[severity] += 1

        # Update audit with results
        audit.critical_count = severity_counts["critical"]
        audit.high_count = severity_counts["high"]
        audit.medium_count = severity_counts["medium"]
        audit.low_count = severity_counts["low"]
        audit.info_count = severity_counts["info"]

        # Calculate scores
        audit.risk_score = calculate_risk_score(severity_counts)
        audit.security_rating = calculate_security_rating(audit.risk_score)

        # Calculate total lines
        audit.total_lines = len(audit.contract_code.split("\n"))

        # Mark as completed
        audit.status = AuditStatus.COMPLETED
        audit.completed_at = datetime.utcnow()
        audit.processing_time_seconds = int((datetime.utcnow() - start_time).total_seconds())

        db.commit()
        logger.info(f"Audit {audit_id} completed successfully")

    except Exception as e:
        logger.error(f"Audit processing failed: {e}", exc_info=True)
        audit.status = AuditStatus.FAILED
        audit.error_message = str(e)
        db.commit()
    finally:
        db.close()


@router.post("/audit", response_model=AuditResponse)
async def create_audit(
    request: AuditRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Initiates a new smart contract audit

    Args:
        request: Audit request with contract code
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Audit response with audit ID and status
    """
    try:
        # Create audit record
        audit = Audit(
            status=AuditStatus.PENDING,
            contract_code=request.code,
            language=request.language,
            compiler_version=request.compiler_version,
            optimization_enabled=1 if request.optimization_enabled else 0,
            additional_files=[f.dict() for f in request.files] if request.files else None,
        )

        db.add(audit)
        db.commit()
        db.refresh(audit)

        # Queue background processing
        background_tasks.add_task(process_audit_task, audit.id, settings.DATABASE_URL)

        logger.info(f"Created audit {audit.id}")

        return AuditResponse(
            audit_id=audit.id,
            status=AuditStatus.PENDING,
            estimated_time=30,
            message="Audit initiated successfully"
        )

    except Exception as e:
        logger.error(f"Failed to create audit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/{audit_id}", response_model=AuditResult)
async def get_audit_result(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves audit results by ID

    Args:
        audit_id: Audit ID
        db: Database session

    Returns:
        Complete audit results
    """
    # Get audit from database
    audit = db.query(Audit).filter(Audit.id == audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Get vulnerabilities
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.audit_id == audit_id).all()

    # Build response
    vulnerability_details = [
        VulnerabilityDetail(
            id=v.id,
            title=v.title,
            severity=v.severity,
            exploitability=v.exploitability.value if v.exploitability else None,
            category=v.category,
            location=LocationInfo(
                file=v.file_name,
                line=v.line_number,
                function=v.function_name
            ),
            description=v.description,
            exploit_scenario=v.exploit_scenario,
            recommendation=v.recommendation,
            fixed_code=v.fixed_code,
            code_snippet=v.code_snippet,
            cwe_id=v.cwe_id,
            swc_id=v.swc_id,
            references=v.references,
            detected_by=v.detected_by,
            confidence=v.confidence
        )
        for v in vulnerabilities
    ]

    return AuditResult(
        audit_id=audit.id,
        status=audit.status,
        created_at=audit.created_at,
        completed_at=audit.completed_at,
        processing_time_seconds=audit.processing_time_seconds,
        contract_info=ContractInfo(
            language=audit.language.value,
            compiler_version=audit.compiler_version,
            contract_name=audit.contract_name,
            total_lines=audit.total_lines
        ),
        vulnerabilities=vulnerability_details,
        vulnerability_counts={
            "critical": audit.critical_count,
            "high": audit.high_count,
            "medium": audit.medium_count,
            "low": audit.low_count,
            "info": audit.info_count
        },
        risk_score=audit.risk_score,
        security_rating=audit.security_rating,
        gas_analysis=audit.gas_analysis,
        ai_analysis=AIAnalysis(
            summary=audit.ai_summary,
            overall_risk=audit.ai_overall_risk
        ) if audit.ai_summary else None,
        recommendations=None,
        error_message=audit.error_message
    )


@router.get("/audits")
async def list_audits(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all audits with pagination

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status
        db: Database session

    Returns:
        List of audits
    """
    query = db.query(Audit)

    if status:
        query = query.filter(Audit.status == status)

    audits = query.order_by(Audit.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": query.count(),
        "skip": skip,
        "limit": limit,
        "audits": [audit.to_dict() for audit in audits]
    }


@router.delete("/audit/{audit_id}")
async def delete_audit(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an audit

    Args:
        audit_id: Audit ID
        db: Database session

    Returns:
        Success message
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    db.delete(audit)
    db.commit()

    return {"message": "Audit deleted successfully"}
