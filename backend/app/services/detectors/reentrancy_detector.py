"""
Reentrancy vulnerability detector
"""
import re
from typing import List, Dict, Any, Optional

from app.services.detectors.base_detector import BaseDetector
from app.utils.ast_utils import get_line_context


class ReentrancyDetector(BaseDetector):
    """
    Detects reentrancy vulnerabilities in smart contracts

    Pattern: External call followed by state changes
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "SEN-001"
        self.severity = "critical"

    def detect(
        self,
        code: str,
        language: str = "solidity",
        compiler_version: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Detect reentrancy vulnerabilities

        Args:
            code: Contract source code
            language: Programming language
            compiler_version: Compiler version
            **kwargs: Additional context

        Returns:
            List of reentrancy findings
        """
        findings = []

        if language != "solidity":
            return findings

        # Extract functions
        functions = kwargs.get("functions", [])

        # Pattern 1: Look for external calls followed by state changes
        # This is a simplified pattern - in production use proper AST analysis

        # Find functions with external calls
        external_call_patterns = [
            r'\.call\{',
            r'\.call\(',
            r'\.delegatecall\(',
            r'\.send\(',
            r'\.transfer\(',
        ]

        # Find state variable assignments
        state_change_pattern = r'\w+\[[\w\.]+\]\s*=|\w+\s*='

        lines = code.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check if line contains external call
            has_external_call = any(re.search(pattern, line) for pattern in external_call_patterns)

            if has_external_call:
                # Check if state changes occur after this line in the same function
                # Look ahead up to 10 lines
                state_change_after_call = False
                state_change_line = None

                for j in range(i + 1, min(i + 11, len(lines))):
                    # Stop if we hit a function boundary
                    if 'function ' in lines[j] or lines[j].strip().startswith('}'):
                        break

                    if re.search(state_change_pattern, lines[j]):
                        state_change_after_call = True
                        state_change_line = j + 1
                        break

                if state_change_after_call:
                    # Extract function name
                    function_name = self._extract_function_name(code, i)

                    finding = self.create_finding(
                        title="Potential Reentrancy Vulnerability",
                        description=(
                            "External call detected before state changes. This allows for potential "
                            "reentrancy attacks where the called contract can call back into this "
                            "contract before state changes are applied. The external call on line "
                            f"{line_num} occurs before state changes on line {state_change_line}."
                        ),
                        line_number=line_num,
                        function_name=function_name,
                        code_snippet=get_line_context(code, line_num, context_lines=3),
                        recommendation=(
                            "Follow the Checks-Effects-Interactions pattern:\n"
                            "1. Perform all checks (require statements)\n"
                            "2. Update state variables\n"
                            "3. Make external calls last\n\n"
                            "Alternatively, use a ReentrancyGuard modifier from OpenZeppelin."
                        ),
                        fixed_code=self._generate_fixed_code(function_name),
                        exploit_scenario=(
                            "An attacker can create a malicious contract that:\n"
                            "1. Calls the vulnerable function\n"
                            "2. In the fallback/receive function, calls back into the vulnerable contract\n"
                            "3. Drains funds before balances are updated"
                        ),
                        cwe_id="CWE-841",
                        swc_id="SWC-107",
                        references=[
                            "https://consensys.github.io/smart-contract-best-practices/attacks/reentrancy/",
                            "https://swcregistry.io/docs/SWC-107"
                        ]
                    )
                    findings.append(finding)

        # Also check for missing nonReentrant modifier on payable functions
        payable_pattern = r'function\s+(\w+)\([^)]*\)\s+.*payable'
        for match in re.finditer(payable_pattern, code):
            function_context = code[max(0, match.start() - 200):match.end() + 500]

            # Check if nonReentrant modifier is present
            if 'nonReentrant' not in function_context:
                line_num = code[:match.start()].count('\n') + 1
                function_name = match.group(1)

                finding = self.create_finding(
                    title="Missing Reentrancy Guard on Payable Function",
                    description=(
                        f"The payable function '{function_name}' does not have a reentrancy guard. "
                        "Payable functions that make external calls or interact with other contracts "
                        "should be protected against reentrancy attacks."
                    ),
                    line_number=line_num,
                    function_name=function_name,
                    code_snippet=get_line_context(code, line_num, context_lines=2),
                    recommendation=(
                        "Add the 'nonReentrant' modifier from OpenZeppelin's ReentrancyGuard:\n"
                        f"function {function_name}(...) external payable nonReentrant {{\n"
                        "    // function body\n"
                        "}"
                    ),
                    cwe_id="CWE-841",
                    swc_id="SWC-107"
                )
                # Lower severity as this is preventative
                finding["severity"] = "high"
                findings.append(finding)

        return findings

    def _extract_function_name(self, code: str, line_index: int) -> Optional[str]:
        """Extract the function name containing the given line"""
        lines = code.split('\n')

        # Search backwards for function declaration
        for i in range(line_index, -1, -1):
            match = re.search(r'function\s+(\w+)', lines[i])
            if match:
                return match.group(1)

        return None

    def _generate_fixed_code(self, function_name: Optional[str]) -> str:
        """Generate example fixed code"""
        func_name = function_name or "withdraw"
        return f"""// Fixed version following Checks-Effects-Interactions pattern
function {func_name}() external nonReentrant {{
    uint amount = balances[msg.sender];
    require(amount > 0, "No balance");

    // Effects: Update state BEFORE external call
    balances[msg.sender] = 0;

    // Interactions: External call LAST
    (bool success, ) = msg.sender.call{{value: amount}}("");
    require(success, "Transfer failed");
}}"""
