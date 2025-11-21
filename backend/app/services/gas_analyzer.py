"""
Gas optimization analyzer
"""
import re
from typing import Dict, List, Any, Optional
import logging

from app.utils.ast_utils import extract_functions

logger = logging.getLogger(__name__)


class GasAnalyzer:
    """
    Analyzes gas consumption and provides optimization recommendations
    """

    def analyze(self, code: str, language: str = "solidity") -> Dict[str, Any]:
        """
        Analyze gas consumption and identify optimization opportunities

        Args:
            code: Contract source code
            language: Programming language

        Returns:
            Gas analysis results with optimization recommendations
        """
        if language != "solidity":
            return {
                "total_estimated_gas": None,
                "optimizations": [],
                "potential_savings": "N/A"
            }

        logger.info(f"Starting gas analysis (code length: {len(code)} chars)")

        optimizations = []

        # Check 1: Storage reads in loops
        optimizations.extend(self._detect_storage_in_loops(code))

        # Check 2: Inefficient storage packing
        optimizations.extend(self._detect_poor_storage_packing(code))

        # Check 3: Public vs External
        optimizations.extend(self._detect_public_functions(code))

        # Check 4: Unnecessary storage initialization
        optimizations.extend(self._detect_redundant_initialization(code))

        # Check 5: String vs bytes32
        optimizations.extend(self._detect_string_usage(code))

        # Check 6: Array length caching
        optimizations.extend(self._detect_array_length_in_loops(code))

        # Estimate total potential savings
        total_savings = sum(
            self._extract_gas_value(opt.get("savings", "0"))
            for opt in optimizations
        )

        logger.info(f"Gas analysis complete - found {len(optimizations)} optimization opportunities")

        return {
            "total_estimated_gas": None,  # Would need compiler integration for accurate estimation
            "optimizations": optimizations,
            "potential_savings": f"{total_savings} gas per transaction" if total_savings > 0 else "N/A"
        }

    def _detect_storage_in_loops(self, code: str) -> List[Dict[str, Any]]:
        """Detect storage variable reads inside loops"""
        findings = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            # Simple pattern: for loop followed by storage read
            if 'for(' in line or 'for (' in line:
                # Check next 10 lines for storage reads
                loop_body_end = min(i + 15, len(lines))

                for j in range(i + 1, loop_body_end):
                    # Pattern for storage variable access (simplified)
                    if re.search(r'\w+\[\w+\]', lines[j]) or 'storage' in lines[j]:
                        findings.append({
                            "issue": "Storage read inside loop",
                            "line": i + 1,
                            "current_cost": f"{2100 * 'n'} gas (SLOAD per iteration)",
                            "optimized_cost": "2100 gas (single SLOAD)",
                            "savings": "2100 * (n-1) gas",
                            "recommendation": (
                                "Cache the storage variable in memory before the loop:\n\n"
                                "// Instead of:\n"
                                "for (uint i = 0; i < array.length; i++) {\n"
                                "    total += storageArray[i]; // SLOAD every iteration\n"
                                "}\n\n"
                                "// Do this:\n"
                                "uint[] memory tempArray = storageArray; // Single SLOAD\n"
                                "for (uint i = 0; i < tempArray.length; i++) {\n"
                                "    total += tempArray[i]; // MLOAD (cheaper)\n"
                                "}"
                            )
                        })
                        break

        return findings

    def _detect_poor_storage_packing(self, code: str) -> List[Dict[str, Any]]:
        """Detect inefficient storage variable packing"""
        findings = []

        # Pattern: uint256 followed by smaller types
        pattern = r'uint256\s+\w+;\s*\n\s*uint8\s+\w+;'

        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1

            findings.append({
                "issue": "Inefficient storage packing",
                "line": line_num,
                "current_cost": "2 storage slots (40,000 gas)",
                "optimized_cost": "1 storage slot (20,000 gas)",
                "savings": "20,000 gas on deployment",
                "recommendation": (
                    "Pack smaller types together to fit in one 32-byte slot:\n\n"
                    "// Before:\n"
                    "uint256 bigNumber;  // Slot 0\n"
                    "uint8 smallNumber;  // Slot 1 (wastes 31 bytes)\n\n"
                    "// After:\n"
                    "uint8 smallNumber;  // Slot 0 (uses 1 byte)\n"
                    "uint256 bigNumber;  // Slot 1 (uses 32 bytes)\n\n"
                    "Even better - pack multiple small types:\n"
                    "uint128 a;  // Slot 0 (16 bytes)\n"
                    "uint128 b;  // Slot 0 (16 bytes) - same slot!\n"
                    "uint256 c;  // Slot 1"
                )
            })

        return findings

    def _detect_public_functions(self, code: str) -> List[Dict[str, Any]]:
        """Detect public functions that could be external"""
        findings = []

        # Pattern: public functions that don't call themselves internally
        pattern = r'function\s+(\w+)\([^)]*\)\s+public'

        for match in re.finditer(pattern, code):
            function_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            # Simple heuristic: if function name doesn't appear elsewhere, it's likely not called internally
            # Count occurrences
            occurrences = len(re.findall(rf'\b{function_name}\b', code))

            if occurrences <= 2:  # Definition + possible documentation
                findings.append({
                    "issue": f"Function '{function_name}' can be external instead of public",
                    "line": line_num,
                    "current_cost": "Higher gas (copies calldata to memory)",
                    "optimized_cost": "Lower gas (reads directly from calldata)",
                    "savings": "~200 gas per call",
                    "recommendation": (
                        f"Change visibility to external:\n\n"
                        f"// Before:\n"
                        f"function {function_name}(...) public {{\n"
                        "    // ...\n"
                        "}\n\n"
                        f"// After:\n"
                        f"function {function_name}(...) external {{\n"
                        "    // ...\n"
                        "}\n\n"
                        "External functions are cheaper because they don't copy calldata to memory."
                    )
                })

        return findings

    def _detect_redundant_initialization(self, code: str) -> List[Dict[str, Any]]:
        """Detect redundant zero initialization"""
        findings = []

        # Pattern: explicitly initializing to zero
        patterns = [
            (r'uint\s+\w+\s*=\s*0;', 'uint'),
            (r'bool\s+\w+\s*=\s*false;', 'bool'),
        ]

        for pattern, var_type in patterns:
            for match in re.finditer(pattern, code):
                line_num = code[:match.start()].count('\n') + 1

                findings.append({
                    "issue": f"Redundant initialization of {var_type} to default value",
                    "line": line_num,
                    "current_cost": "Extra gas for initialization",
                    "optimized_cost": "No initialization needed",
                    "savings": "~5 gas",
                    "recommendation": (
                        "Remove explicit initialization to default values:\n\n"
                        "// Before:\n"
                        f"{var_type} myVar = {match.group().split('=')[1].strip()}\n\n"
                        "// After:\n"
                        f"{var_type} myVar;  // Automatically initialized to default\n\n"
                        "Variables are automatically initialized to their default values."
                    )
                })

        return findings

    def _detect_string_usage(self, code: str) -> List[Dict[str, Any]]:
        """Detect inefficient string usage"""
        findings = []

        # Pattern: string for short values
        pattern = r'string\s+(public\s+|private\s+|internal\s+)?(\w+)'

        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1

            findings.append({
                "issue": "Consider using bytes32 instead of string for short values",
                "line": line_num,
                "current_cost": "Higher gas (dynamic type)",
                "optimized_cost": "Lower gas (fixed-size type)",
                "savings": "Variable, typically 1000+ gas",
                "recommendation": (
                    "For values ≤32 bytes, use bytes32 instead of string:\n\n"
                    "// Before:\n"
                    "string public name = 'MyToken';\n\n"
                    "// After:\n"
                    "bytes32 public name = 'MyToken';  // Much cheaper\n\n"
                    "Only use string for values that can exceed 32 bytes."
                )
            })

        return findings

    def _detect_array_length_in_loops(self, code: str) -> List[Dict[str, Any]]:
        """Detect array.length called repeatedly in loop condition"""
        findings = []

        # Pattern: for loop with array.length in condition
        pattern = r'for\s*\([^;]*;\s*\w+\s*<\s*(\w+)\.length'

        for match in re.finditer(pattern, code):
            array_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            findings.append({
                "issue": f"Array length '{array_name}.length' called repeatedly in loop",
                "line": line_num,
                "current_cost": "SLOAD or MLOAD per iteration",
                "optimized_cost": "Single read before loop",
                "savings": "~100 gas per iteration",
                "recommendation": (
                    f"Cache array length before the loop:\n\n"
                    "// Before:\n"
                    f"for (uint i = 0; i < {array_name}.length; i++) {{\n"
                    "    // ...\n"
                    "}\n\n"
                    "// After:\n"
                    f"uint length = {array_name}.length;\n"
                    "for (uint i = 0; i < length; i++) {\n"
                    "    // ...\n"
                    "}"
                )
            })

        return findings

    def _extract_gas_value(self, savings_str: str) -> int:
        """Extract numeric gas value from string"""
        # Extract first number from string
        match = re.search(r'(\d+)', savings_str)
        if match:
            return int(match.group(1))
        return 0
