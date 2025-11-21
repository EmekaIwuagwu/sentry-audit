"""
tx.origin authentication vulnerability detector
"""
import re
from typing import List, Dict, Any, Optional

from app.services.detectors.base_detector import BaseDetector
from app.utils.ast_utils import get_line_context


class TxOriginDetector(BaseDetector):
    """
    Detects use of tx.origin for authentication

    tx.origin should never be used for authorization as it can be exploited
    through phishing attacks
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "SEN-005"
        self.severity = "high"

    def detect(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect tx.origin usage for authentication

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version
            **kwargs: Additional context

        Returns:
            List of tx.origin findings
        """
        findings = []

        if language != "solidity":
            return findings

        # Pattern for tx.origin in authorization contexts
        tx_origin_patterns = [
            r'require\s*\(\s*tx\.origin\s*==',
            r'require\s*\(\s*tx\.origin\s*!=',
            r'if\s*\(\s*tx\.origin\s*==',
            r'if\s*\(\s*tx\.origin\s*!=',
            r'tx\.origin\s*==\s*owner',
            r'tx\.origin\s*==\s*admin',
        ]

        lines = code.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check if line uses tx.origin in authorization context
            for pattern in tx_origin_patterns:
                if re.search(pattern, line):
                    # Extract function name
                    function_name = None
                    for k in range(i, -1, -1):
                        func_match = re.search(r'function\s+(\w+)', lines[k])
                        if func_match:
                            function_name = func_match.group(1)
                            break

                    finding = self.create_finding(
                        title="Dangerous Use of tx.origin for Authentication",
                        description=(
                            "The contract uses tx.origin for authentication/authorization. "
                            "tx.origin represents the original external account that started the "
                            "transaction chain, not the immediate caller (msg.sender). This can be "
                            "exploited through phishing attacks where a malicious contract tricks "
                            "a user into calling it, then calls the vulnerable contract with the "
                            "user's tx.origin."
                        ),
                        line_number=line_num,
                        function_name=function_name,
                        code_snippet=get_line_context(code, line_num, context_lines=2),
                        recommendation=(
                            "Always use msg.sender instead of tx.origin for authentication:\n\n"
                            "// Vulnerable (DON'T USE)\n"
                            "require(tx.origin == owner, 'Not authorized');\n\n"
                            "// Secure (USE THIS)\n"
                            "require(msg.sender == owner, 'Not authorized');\n\n"
                            "msg.sender represents the immediate caller, which prevents phishing attacks."
                        ),
                        fixed_code=line.replace('tx.origin', 'msg.sender'),
                        exploit_scenario=(
                            "Attack scenario:\n"
                            "1. Attacker deploys a malicious contract\n"
                            "2. Attacker tricks the owner into calling their contract (via phishing)\n"
                            "3. The malicious contract calls the vulnerable contract\n"
                            "4. Since tx.origin is still the owner, authentication passes\n"
                            "5. Attacker executes privileged operations (drain funds, take ownership, etc.)"
                        ),
                        cwe_id="CWE-477",
                        swc_id="SWC-115",
                        references=[
                            "https://swcregistry.io/docs/SWC-115",
                            "https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/tx-origin/"
                        ]
                    )
                    findings.append(finding)
                    break  # Only report once per line

        return findings
