"""
AST parsing and manipulation utilities
"""
import re
from typing import Dict, List, Optional, Any


def extract_functions(code: str, language: str = "solidity") -> List[Dict[str, Any]]:
    """
    Extract function definitions from contract code

    Args:
        code: Contract source code
        language: Programming language

    Returns:
        List of function information dictionaries
    """
    functions = []

    if language == "solidity":
        # Simple regex-based function extraction
        # In production, use proper AST parser
        pattern = r'function\s+(\w+)\s*\([^)]*\)\s*(public|private|internal|external)?'
        matches = re.finditer(pattern, code)

        for match in matches:
            function_name = match.group(1)
            visibility = match.group(2) or "public"
            start_line = code[:match.start()].count('\n') + 1

            functions.append({
                "name": function_name,
                "visibility": visibility,
                "line": start_line,
                "signature": match.group(0)
            })

    return functions


def extract_state_variables(code: str, language: str = "solidity") -> List[Dict[str, Any]]:
    """
    Extract state variable declarations

    Args:
        code: Contract source code
        language: Programming language

    Returns:
        List of state variable information
    """
    variables = []

    if language == "solidity":
        # Pattern for state variables
        pattern = r'(uint256|uint|int|address|bool|string|bytes\d*)\s+(public|private|internal)?\s+(\w+)\s*[;=]'
        matches = re.finditer(pattern, code)

        for match in matches:
            var_type = match.group(1)
            visibility = match.group(2) or "internal"
            var_name = match.group(3)
            line = code[:match.start()].count('\n') + 1

            variables.append({
                "name": var_name,
                "type": var_type,
                "visibility": visibility,
                "line": line
            })

    return variables


def find_external_calls(code: str, language: str = "solidity") -> List[Dict[str, Any]]:
    """
    Find external contract calls

    Args:
        code: Contract source code
        language: Programming language

    Returns:
        List of external call locations
    """
    calls = []

    if language == "solidity":
        # Pattern for .call, .delegatecall, .send, .transfer
        patterns = [
            (r'\.call\{', 'call'),
            (r'\.call\(', 'call'),
            (r'\.delegatecall\(', 'delegatecall'),
            (r'\.send\(', 'send'),
            (r'\.transfer\(', 'transfer'),
        ]

        for pattern, call_type in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line = code[:match.start()].count('\n') + 1
                calls.append({
                    "type": call_type,
                    "line": line,
                    "context": get_line_context(code, line)
                })

    return calls


def get_line_context(code: str, line_number: int, context_lines: int = 3) -> str:
    """
    Get code snippet around a specific line

    Args:
        code: Full source code
        line_number: Target line number (1-indexed)
        context_lines: Number of lines to include before and after

    Returns:
        Code snippet
    """
    lines = code.split('\n')
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)

    return '\n'.join(lines[start:end])


def find_pattern_in_code(code: str, pattern: str) -> List[Dict[str, Any]]:
    """
    Find all occurrences of a regex pattern in code

    Args:
        code: Source code
        pattern: Regex pattern to search for

    Returns:
        List of matches with line numbers
    """
    matches = []
    for match in re.finditer(pattern, code):
        line = code[:match.start()].count('\n') + 1
        matches.append({
            "match": match.group(0),
            "line": line,
            "start": match.start(),
            "end": match.end()
        })

    return matches
