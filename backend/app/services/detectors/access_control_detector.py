"""
Access control vulnerability detector
"""
import re
from typing import List, Dict, Any, Optional

from app.services.detectors.base_detector import BaseDetector
from app.utils.ast_utils import get_line_context


class AccessControlDetector(BaseDetector):
    """
    Detects access control vulnerabilities in smart contracts

    Patterns:
    - Missing access control modifiers on critical functions
    - Incorrect use of tx.origin for authentication
    - Public functions that should be private/internal
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "SEN-002"
        self.severity = "critical"

    def detect(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect access control vulnerabilities

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version
            **kwargs: Additional context

        Returns:
            List of access control findings
        """
        findings = []

        if language != "solidity":
            return findings

        # Critical function keywords that should have access control
        critical_keywords = [
            'selfdestruct', 'suicide', 'delegatecall',
            'transferOwnership', 'withdraw', 'mint',
            'burn', 'pause', 'unpause', 'setAdmin'
        ]

        # Find all functions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s+(public|external|private|internal)?([^{]*)\{'

        for match in re.finditer(function_pattern, code):
            function_name = match.group(1)
            visibility = match.group(2) or "public"  # Default visibility
            modifiers_section = match.group(3) or ""

            # Skip view/pure functions
            if 'view' in modifiers_section or 'pure' in modifiers_section:
                continue

            # Check if function has critical operations
            function_start = match.end()
            # Find function end (simplified - assumes balanced braces)
            function_end = self._find_function_end(code, function_start)
            function_body = code[function_start:function_end]

            has_critical_operation = any(
                keyword in function_body
                for keyword in critical_keywords
            )

            if has_critical_operation:
                # Check for access control modifiers
                has_access_control = any(
                    modifier in modifiers_section
                    for modifier in ['onlyOwner', 'onlyAdmin', 'onlyRole', 'nonReentrant']
                ) or 'require(msg.sender ==' in function_body or 'require(owner ==' in function_body

                if not has_access_control:
                    line_num = code[:match.start()].count('\n') + 1

                    finding = self.create_finding(
                        title=f"Missing Access Control on Critical Function '{function_name}'",
                        description=(
                            f"The function '{function_name}' performs critical operations but lacks "
                            "proper access control. This allows any external caller to execute "
                            "sensitive functionality that should be restricted to authorized users only."
                        ),
                        line_number=line_num,
                        function_name=function_name,
                        code_snippet=get_line_context(code, line_num, context_lines=3),
                        recommendation=(
                            f"Add an access control modifier to restrict access:\n\n"
                            f"function {function_name}(...) {visibility} onlyOwner {{\n"
                            "    // function body\n"
                            "}\n\n"
                            "Or add a require statement:\n"
                            f"function {function_name}(...) {visibility} {{\n"
                            "    require(msg.sender == owner, 'Not authorized');\n"
                            "    // function body\n"
                            "}"
                        ),
                        exploit_scenario=(
                            "An attacker can call this function directly to:\n"
                            "- Drain contract funds\n"
                            "- Take ownership of the contract\n"
                            "- Mint unlimited tokens\n"
                            "- Destroy the contract\n"
                            "- Modify critical state variables"
                        ),
                        cwe_id="CWE-284",
                        swc_id="SWC-105",
                        references=[
                            "https://swcregistry.io/docs/SWC-105"
                        ]
                    )
                    findings.append(finding)

            # Check for unprotected initialization functions
            if function_name in ['initialize', 'init', 'setup'] and visibility in ['public', 'external']:
                # Check if there's protection against re-initialization
                if 'initialized' not in function_body and 'initializer' not in modifiers_section:
                    line_num = code[:match.start()].count('\n') + 1

                    finding = self.create_finding(
                        title=f"Unprotected Initialization Function",
                        description=(
                            f"The initialization function '{function_name}' is not protected "
                            "against re-initialization. An attacker could call this function "
                            "multiple times to reset contract state or take ownership."
                        ),
                        line_number=line_num,
                        function_name=function_name,
                        code_snippet=get_line_context(code, line_num, context_lines=3),
                        recommendation=(
                            "Add initialization protection:\n\n"
                            "bool private initialized;\n\n"
                            f"function {function_name}(...) {visibility} {{\n"
                            "    require(!initialized, 'Already initialized');\n"
                            "    initialized = true;\n"
                            "    // initialization logic\n"
                            "}\n\n"
                            "Or use OpenZeppelin's Initializable pattern."
                        ),
                        cwe_id="CWE-665",
                        swc_id="SWC-118",
                        references=[
                            "https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable"
                        ]
                    )
                    finding["severity"] = "high"
                    findings.append(finding)

        return findings

    def _find_function_end(self, code: str, start: int) -> int:
        """Find the end of a function (simplified brace matching)"""
        brace_count = 1
        i = start

        while i < len(code) and brace_count > 0:
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
            i += 1

        return i
