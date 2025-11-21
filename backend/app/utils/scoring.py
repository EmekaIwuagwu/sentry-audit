"""
Risk scoring and rating utilities
"""
from typing import Dict


def calculate_risk_score(severity_counts: Dict[str, int]) -> int:
    """
    Calculate risk score (0-100) based on vulnerability severity and count

    Lower score = Higher risk
    Higher score = Lower risk

    Args:
        severity_counts: Dictionary with vulnerability counts by severity

    Returns:
        Risk score from 0 to 100
    """
    weights = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3,
        "info": 1
    }

    score = 100

    for severity, count in severity_counts.items():
        if severity in weights:
            score -= (weights[severity] * count)

    return max(0, score)


def calculate_security_rating(risk_score: int) -> str:
    """
    Calculate letter grade based on risk score

    Args:
        risk_score: Risk score from 0 to 100

    Returns:
        Security rating (A+ to F)
    """
    if risk_score >= 95:
        return "A+"
    elif risk_score >= 90:
        return "A"
    elif risk_score >= 85:
        return "A-"
    elif risk_score >= 80:
        return "B+"
    elif risk_score >= 75:
        return "B"
    elif risk_score >= 70:
        return "B-"
    elif risk_score >= 65:
        return "C+"
    elif risk_score >= 60:
        return "C"
    elif risk_score >= 55:
        return "C-"
    elif risk_score >= 50:
        return "D"
    else:
        return "F"


def get_overall_risk_level(risk_score: int) -> str:
    """
    Get overall risk level (Low, Medium, High, Critical)

    Args:
        risk_score: Risk score from 0 to 100

    Returns:
        Risk level string
    """
    if risk_score >= 80:
        return "Low"
    elif risk_score >= 60:
        return "Medium"
    elif risk_score >= 40:
        return "High"
    else:
        return "Critical"
