"""
Base detector class for all vulnerability detectors
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseDetector(ABC):
    """
    Abstract base class for vulnerability detectors
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.rule_id = "UNKNOWN"
        self.severity = "info"

    @abstractmethod
    def detect(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect vulnerabilities in contract code

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version
            **kwargs: Additional context (functions, external_calls, etc.)

        Returns:
            List of vulnerability findings
        """
        pass

    def create_finding(
        self,
        title: str,
        description: str,
        line_number: Optional[int] = None,
        function_name: Optional[str] = None,
        code_snippet: Optional[str] = None,
        recommendation: Optional[str] = None,
        fixed_code: Optional[str] = None,
        exploit_scenario: Optional[str] = None,
        cwe_id: Optional[str] = None,
        swc_id: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized finding dictionary

        Args:
            title: Vulnerability title
            description: Detailed description
            line_number: Line number where vulnerability is found
            function_name: Function name containing the vulnerability
            code_snippet: Relevant code snippet
            recommendation: Fix recommendation
            fixed_code: Corrected code example
            exploit_scenario: How to exploit this vulnerability
            cwe_id: CWE identifier
            swc_id: SWC identifier
            references: Reference URLs

        Returns:
            Standardized finding dictionary
        """
        return {
            "rule_id": self.rule_id,
            "title": title,
            "severity": self.severity,
            "category": "security",
            "line_number": line_number,
            "function_name": function_name,
            "code_snippet": code_snippet,
            "description": description,
            "recommendation": recommendation,
            "fixed_code": fixed_code,
            "exploit_scenario": exploit_scenario,
            "cwe_id": cwe_id,
            "swc_id": swc_id,
            "references": references or [],
            "detected_by": "static",
            "confidence": 90
        }
