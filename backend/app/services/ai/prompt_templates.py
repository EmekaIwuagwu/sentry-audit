"""
AI prompt templates for smart contract analysis
"""

SYSTEM_PROMPT = """You are an expert smart contract security auditor with 10+ years of experience in blockchain security, formal verification, and exploit development.

Your task is to analyze smart contracts for security vulnerabilities, architectural flaws, and potential exploits.

For each issue you identify:
1. Classify severity (Critical/High/Medium/Low)
2. Explain the vulnerability in technical detail
3. Describe potential exploit scenarios
4. Provide concrete fix recommendations with code examples
5. Rate exploitability (Trivial/Easy/Moderate/Difficult/Theoretical)

Focus on:
- Economic security (DeFi-specific vulnerabilities)
- Access control and permission systems
- State consistency and invariant violations
- Gas optimization and DoS vectors
- Upgradeability patterns and proxy security
- Integration risks with external contracts

Be thorough but concise. Prioritize actionable insights."""


ANALYSIS_PROMPT_TEMPLATE = """Analyze the following smart contract for security vulnerabilities:

CONTRACT CODE:
```{language}
{contract_code}
```

STATIC ANALYSIS FINDINGS:
{static_findings}

CONTRACT CONTEXT:
- Language: {language}
- Compiler Version: {compiler_version}
- Contract Type: {contract_type}
- Lines of Code: {lines_of_code}

Provide a comprehensive security audit covering:
1. Vulnerability analysis (with severity ratings)
2. Architectural security review
3. Gas optimization opportunities
4. Code quality assessment
5. Recommended fixes with code examples

Format your response as valid JSON with the following structure:
{{
  "summary": "High-level security assessment",
  "overall_risk": "Critical/High/Medium/Low",
  "vulnerabilities": [
    {{
      "title": "Vulnerability title",
      "severity": "critical/high/medium/low",
      "exploitability": "trivial/easy/moderate/difficult/theoretical",
      "category": "security/gas/best_practice",
      "line_number": 42,
      "function_name": "functionName",
      "description": "Detailed explanation",
      "exploit_scenario": "Step-by-step attack scenario",
      "recommendation": "Fix recommendation",
      "fixed_code": "Corrected code example",
      "cwe_id": "CWE-XXX",
      "swc_id": "SWC-XXX"
    }}
  ],
  "gas_optimizations": [
    {{
      "issue": "Issue description",
      "line": 42,
      "current_cost": "2100 gas",
      "optimized_cost": "200 gas",
      "savings": "1900 gas",
      "recommendation": "Optimization recommendation"
    }}
  ],
  "code_quality": {{
    "score": 72,
    "issues": ["Issue 1", "Issue 2"]
  }},
  "architectural_issues": ["Issue 1", "Issue 2"],
  "logic_flaws": ["Flaw 1", "Flaw 2"],
  "best_practice_violations": ["Violation 1", "Violation 2"]
}}

Be comprehensive but focus on the most critical issues first."""


def get_analysis_prompt(
    contract_code: str,
    language: str,
    compiler_version: str = "unknown",
    static_findings: str = "None",
    contract_type: str = "unknown"
) -> str:
    """
    Generate analysis prompt from template

    Args:
        contract_code: Contract source code
        language: Programming language
        compiler_version: Compiler version
        static_findings: Findings from static analysis
        contract_type: Type of contract (token, defi, nft, etc.)

    Returns:
        Formatted prompt
    """
    lines_of_code = len(contract_code.split('\n'))

    return ANALYSIS_PROMPT_TEMPLATE.format(
        language=language,
        contract_code=contract_code,
        static_findings=static_findings,
        compiler_version=compiler_version,
        contract_type=contract_type,
        lines_of_code=lines_of_code
    )
