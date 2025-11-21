"""
Unchecked external call detector
"""
import re
from typing import List, Dict, Any, Optional

from app.services.detectors.base_detector import BaseDetector
from app.utils.ast_utils import get_line_context


class UncheckedCallDetector(BaseDetector):
    """
    Detects unchecked external call return values

    Low-level calls (.call, .delegatecall, .send) return false on failure
    instead of reverting. Ignoring these return values can lead to silent failures.
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "SEN-004"
        self.severity = "high"

    def detect(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect unchecked external calls

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version
            **kwargs: Additional context

        Returns:
            List of unchecked call findings
        """
        findings = []

        if language != "solidity":
            return findings

        # Patterns for different types of external calls
        call_patterns = [
            (r'\.call\{[^}]*\}\([^)]*\)', 'call'),
            (r'\.call\([^)]*\)', 'call'),
            (r'\.delegatecall\([^)]*\)', 'delegatecall'),
            (r'\.send\([^)]*\)', 'send'),
        ]

        lines = code.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped_line = line.strip()

            # Skip comments
            if stripped_line.startswith('//') or stripped_line.startswith('/*'):
                continue

            for pattern, call_type in call_patterns:
                if re.search(pattern, line):
                    # Check if return value is captured and checked
                    is_checked = False

                    # Pattern 1: (bool success, ) = ...
                    if re.search(r'\(\s*bool\s+\w+\s*,?\s*\)', line):
                        # Check if the success value is used in subsequent lines
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if 'require(' in lines[j] or 'assert(' in lines[j] or 'if(' in lines[j]:
                                is_checked = True
                                break
                    # Pattern 2: bool success = ...
                    elif re.search(r'bool\s+\w+\s*=', line):
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if 'require(' in lines[j] or 'assert(' in lines[j] or 'if(' in lines[j]:
                                is_checked = True
                                break
                    # Pattern 3: require(...call(...))
                    elif 'require(' in line or 'assert(' in line:
                        is_checked = True

                    if not is_checked:
                        # Extract function name
                        function_name = None
                        for k in range(i, -1, -1):
                            func_match = re.search(r'function\s+(\w+)', lines[k])
                            if func_match:
                                function_name = func_match.group(1)
                                break

                        finding = self.create_finding(
                            title=f"Unchecked {call_type.title()} Return Value",
                            description=(
                                f"The return value of a low-level {call_type} is not checked. "
                                f"Low-level calls return false on failure instead of reverting. "
                                "Ignoring this return value means the contract will continue execution "
                                "even if the call failed, potentially leading to incorrect state changes "
                                "or loss of funds."
                            ),
                            line_number=line_num,
                            function_name=function_name,
                            code_snippet=get_line_context(code, line_num, context_lines=2),
                            recommendation=(
                                "Always check the return value of low-level calls:\n\n"
                                f"// Option 1: Capture and require\n"
                                f"(bool success, bytes memory data) = address.{call_type}(...);\n"
                                "require(success, 'Call failed');\n\n"
                                "// Option 2: Use require inline\n"
                                f"require(address.{call_type}(...), 'Call failed');\n\n"
                                "// Option 3: Use .transfer() which reverts on failure (for ETH transfers)"
                            ),
                            exploit_scenario=(
                                "If the external call fails:\n"
                                "1. The contract assumes the call succeeded\n"
                                "2. State changes continue as if funds were transferred\n"
                                "3. Attacker can exploit this to:\n"
                                "   - Receive tokens/assets without paying\n"
                                "   - Bypass payment requirements\n"
                                "   - Cause accounting inconsistencies"
                            ),
                            cwe_id="CWE-252",
                            swc_id="SWC-104",
                            references=[
                                "https://swcregistry.io/docs/SWC-104",
                                "https://consensys.github.io/smart-contract-best-practices/development-recommendations/general/external-calls/"
                            ]
                        )
                        findings.append(finding)
                        break  # Only report once per line

        return findings
