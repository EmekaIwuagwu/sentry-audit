"""
Report database model
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ReportFormat(str, enum.Enum):
    """Report output formats"""
    PDF = "pdf"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


class Report(Base):
    """
    Report model - represents a generated audit report
    """
    __tablename__ = "reports"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to audit
    audit_id = Column(String, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)

    # Report metadata
    format = Column(SQLEnum(ReportFormat), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_name = Column(String, nullable=False)
    file_size_bytes = Column(String, nullable=True)

    # Report content (for smaller formats like JSON/HTML)
    content = Column(LargeBinary, nullable=True)

    # S3 or file system path for larger files
    storage_path = Column(String, nullable=True)

    # Share link (optional)
    share_token = Column(String, nullable=True, unique=True)
    share_expires_at = Column(DateTime, nullable=True)

    # Relationships
    audit = relationship("Audit", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, format={self.format}, audit_id={self.audit_id})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "audit_id": self.audit_id,
            "format": self.format.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "share_token": self.share_token,
            "share_expires_at": self.share_expires_at.isoformat() if self.share_expires_at else None,
        }
