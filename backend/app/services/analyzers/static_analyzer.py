"""
Static code analysis orchestrator
"""
import logging
from typing import List, Dict, Any, Optional

from app.services.detectors.reentrancy_detector import ReentrancyDetector
from app.services.detectors.access_control_detector import AccessControlDetector
from app.services.detectors.integer_overflow_detector import IntegerOverflowDetector
from app.services.detectors.unchecked_call_detector import UncheckedCallDetector
from app.services.detectors.tx_origin_detector import TxOriginDetector
from app.utils.ast_utils import extract_functions, find_external_calls

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """
    Orchestrates static analysis of smart contracts using multiple detectors
    """

    def __init__(self):
        """Initialize all detectors"""
        self.detectors = [
            ReentrancyDetector(),
            AccessControlDetector(),
            IntegerOverflowDetector(),
            UncheckedCallDetector(),
            TxOriginDetector(),
        ]

        logger.info(f"Initialized {len(self.detectors)} vulnerability detectors")

    def analyze(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform static analysis on contract code

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version

        Returns:
            List of vulnerability findings
        """
        if language not in ["solidity", "vyper"]:
            logger.warning(f"Unsupported language: {language}")
            return []

        logger.info(f"Starting static analysis (language: {language}, {len(code)} chars)")

        findings = []

        try:
            # Extract code structure
            functions = extract_functions(code, language)
            external_calls = find_external_calls(code, language)

            logger.info(f"Found {len(functions)} functions, {len(external_calls)} external calls")

            # Run all detectors
            for detector in self.detectors:
                try:
                    detector_findings = detector.detect(
                        code=code,
                        language=language,
                        compiler_version=compiler_version,
                        functions=functions,
                        external_calls=external_calls
                    )

                    if detector_findings:
                        logger.info(f"{detector.__class__.__name__} found {len(detector_findings)} issues")
                        findings.extend(detector_findings)

                except Exception as e:
                    logger.error(f"Detector {detector.__class__.__name__} failed: {e}")
                    continue

            logger.info(f"Static analysis completed - total findings: {len(findings)}")

            return findings

        except Exception as e:
            logger.error(f"Static analysis failed: {e}", exc_info=True)
            return []

    def analyze_with_slither(self, code: str, temp_file_path: str) -> List[Dict[str, Any]]:
        """
        Run Slither analysis (optional - requires slither-analyzer installed)

        Args:
            code: Contract source code
            temp_file_path: Path to temporary file with code

        Returns:
            List of findings from Slither
        """
        findings = []

        try:
            from slither.slither import Slither

            logger.info("Running Slither analysis")

            slither = Slither(temp_file_path)

            for detector_result in slither.detector_results:
                finding = {
                    "rule_id": f"SLITHER-{detector_result.get('check', 'UNKNOWN')}",
                    "title": detector_result.get('description', 'Slither Finding'),
                    "severity": self._map_slither_severity(detector_result.get('impact', 'Medium')),
                    "category": "security",
                    "description": detector_result.get('description', ''),
                    "recommendation": detector_result.get('recommendation', ''),
                    "detected_by": "slither",
                    "confidence": self._map_slither_confidence(detector_result.get('confidence', 'Medium'))
                }
                findings.append(finding)

            logger.info(f"Slither found {len(findings)} issues")

        except ImportError:
            logger.warning("Slither not installed - skipping Slither analysis")
        except Exception as e:
            logger.error(f"Slither analysis failed: {e}")

        return findings

    def _map_slither_severity(self, impact: str) -> str:
        """Map Slither impact to our severity levels"""
        mapping = {
            "High": "critical",
            "Medium": "high",
            "Low": "medium",
            "Informational": "info"
        }
        return mapping.get(impact, "medium")

    def _map_slither_confidence(self, confidence: str) -> int:
        """Map Slither confidence to percentage"""
        mapping = {
            "High": 95,
            "Medium": 75,
            "Low": 50
        }
        return mapping.get(confidence, 75)
