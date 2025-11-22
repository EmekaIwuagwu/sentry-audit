"""
Integer overflow/underflow detector
"""
import re
from typing import List, Dict, Any, Optional

from app.services.detectors.base_detector import BaseDetector
from app.utils.ast_utils import get_line_context


class IntegerOverflowDetector(BaseDetector):
    """
    Detects integer overflow/underflow vulnerabilities

    Note: Solidity 0.8.0+ has built-in overflow protection
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "SEN-003"
        self.severity = "high"

    def detect(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect integer overflow/underflow vulnerabilities

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version
            **kwargs: Additional context

        Returns:
            List of overflow/underflow findings
        """
        findings = []

        if language != "solidity":
            return findings

        # Check Solidity version
        version_pattern = r'pragma\s+solidity\s+[\^~]?(\d+\.\d+\.\d+)'
        version_match = re.search(version_pattern, code)

        if version_match:
            version = version_match.group(1)
            major, minor, _ = map(int, version.split('.'))

            # Solidity 0.8.0+ has built-in overflow protection
            if major > 0 or (major == 0 and minor >= 8):
                # Check for unchecked blocks which disable overflow protection
                unchecked_pattern = r'unchecked\s*\{'
                for match in re.finditer(unchecked_pattern, code):
                    line_num = code[:match.start()].count('\n') + 1

                    finding = self.create_finding(
                        title="Unchecked Math Operations",
                        description=(
                            "The 'unchecked' block disables Solidity's built-in overflow/underflow "
                            "protection. Arithmetic operations within this block can overflow or "
                            "underflow without reverting, potentially leading to incorrect calculations."
                        ),
                        line_number=line_num,
                        code_snippet=get_line_context(code, line_num, context_lines=4),
                        recommendation=(
                            "Only use 'unchecked' blocks when you are certain that overflow/underflow "
                            "cannot occur (e.g., in loop counters with known bounds). For all other "
                            "arithmetic operations, rely on Solidity's default checked arithmetic.\n\n"
                            "If unchecked math is necessary for gas optimization, add detailed comments "
                            "explaining why overflow/underflow is impossible."
                        ),
                        cwe_id="CWE-190",
                        swc_id="SWC-101",
                        references=[
                            "https://docs.soliditylang.org/en/v0.8.0/080-breaking-changes.html"
                        ]
                    )
                    finding["severity"] = "medium"
                    findings.append(finding)

                return findings

        # For Solidity < 0.8.0, check for arithmetic without SafeMath
        arithmetic_patterns = [
            (r'\w+\s*\+=\s*\w+', 'addition'),
            (r'\w+\s*-=\s*\w+', 'subtraction'),
            (r'\w+\s*\*=\s*\w+', 'multiplication'),
            (r'\w+\s*=\s*\w+\s*\+\s*\w+', 'addition'),
            (r'\w+\s*=\s*\w+\s*-\s*\w+', 'subtraction'),
            (r'\w+\s*=\s*\w+\s*\*\s*\w+', 'multiplication'),
        ]

        # Check if SafeMath is used
        uses_safemath = 'SafeMath' in code or 'using SafeMath for' in code

        if not uses_safemath:
            for pattern, operation in arithmetic_patterns:
                for match in re.finditer(pattern, code):
                    # Skip if in comments
                    line_start = code.rfind('\n', 0, match.start()) + 1
                    line = code[line_start:code.find('\n', match.start())]
                    if '//' in line and line.index('//') < match.start() - line_start:
                        continue

                    line_num = code[:match.start()].count('\n') + 1

                    finding = self.create_finding(
                        title=f"Potential Integer Overflow in {operation.title()}",
                        description=(
                            f"Arithmetic {operation} operation detected without SafeMath protection "
                            "in Solidity version < 0.8.0. This can lead to integer overflow or "
                            "underflow vulnerabilities where calculations wrap around unexpectedly."
                        ),
                        line_number=line_num,
                        code_snippet=get_line_context(code, line_num, context_lines=2),
                        recommendation=(
                            "Use OpenZeppelin's SafeMath library for all arithmetic operations:\n\n"
                            "using SafeMath for uint256;\n\n"
                            "Then use:\n"
                            "- value.add(other) instead of value + other\n"
                            "- value.sub(other) instead of value - other\n"
                            "- value.mul(other) instead of value * other\n"
                            "- value.div(other) instead of value / other\n\n"
                            "Or upgrade to Solidity 0.8.0+ for built-in overflow protection."
                        ),
                        exploit_scenario=(
                            "An attacker can:\n"
                            "1. Cause an overflow by providing large values\n"
                            "2. Wrap the value back to zero or a small number\n"
                            "3. Exploit the incorrect calculation (e.g., bypass balance checks)\n"
                            "4. Drain funds or mint unlimited tokens"
                        ),
                        cwe_id="CWE-190",
                        swc_id="SWC-101",
                        references=[
                            "https://swcregistry.io/docs/SWC-101",
                            "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/math/SafeMath.sol"
                        ]
                    )
                    findings.append(finding)
                    # Only report once per line
                    break

        return findings
