"""
Audit database model
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class AuditStatus(str, enum.Enum):
    """Audit status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContractLanguage(str, enum.Enum):
    """Supported contract languages"""
    SOLIDITY = "solidity"
    VYPER = "vyper"
    MOVE = "move"


class Audit(Base):
    """
    Audit model - represents a single smart contract audit
    """
    __tablename__ = "audits"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Audit metadata
    status = Column(SQLEnum(AuditStatus), default=AuditStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Contract information
    contract_code = Column(Text, nullable=False)
    contract_name = Column(String, nullable=True)
    language = Column(SQLEnum(ContractLanguage), nullable=False)
    compiler_version = Column(String, nullable=True)
    optimization_enabled = Column(Integer, default=0)

    # Multi-file support
    additional_files = Column(JSON, nullable=True)  # List of {name, content}

    # Analysis results
    total_lines = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)  # 0-100
    security_rating = Column(String, nullable=True)  # A+, A, B, C, D, F

    # Vulnerability counts
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)

    # AI analysis
    ai_summary = Column(Text, nullable=True)
    ai_overall_risk = Column(String, nullable=True)

    # Gas analysis
    gas_analysis = Column(JSON, nullable=True)

    # Processing metadata
    processing_time_seconds = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    vulnerabilities = relationship("Vulnerability", back_populates="audit", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="audit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Audit(id={self.id}, status={self.status}, language={self.language})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "contract_name": self.contract_name,
            "language": self.language.value,
            "compiler_version": self.compiler_version,
            "total_lines": self.total_lines,
            "risk_score": self.risk_score,
            "security_rating": self.security_rating,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "info_count": self.info_count,
            "processing_time_seconds": self.processing_time_seconds,
        }
