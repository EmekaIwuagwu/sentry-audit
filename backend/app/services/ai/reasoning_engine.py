"""
AI-powered reasoning engine for smart contract analysis
"""
import json
import logging
from typing import Dict, List, Any, Optional
from anthropic import Anthropic

from app.config import settings
from app.services.ai.prompt_templates import SYSTEM_PROMPT, get_analysis_prompt

logger = logging.getLogger(__name__)


class AIReasoningEngine:
    """
    Orchestrates AI-powered security analysis using Claude
    """

    def __init__(self):
        """Initialize AI client"""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not configured - AI analysis will be disabled")
            self.client = None
        else:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def analyze(
        self,
        code: str,
        language: str = "solidity",
        static_findings: Optional[List[Dict[str, Any]]] = None,
        compiler_version: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Performs deep reasoning analysis on contract code

        Args:
            code: Contract source code
            language: Programming language
            static_findings: Findings from static analysis
            compiler_version: Compiler version

        Returns:
            AI analysis results including vulnerabilities and insights
        """
        if not self.client:
            logger.warning("AI analysis skipped - no API key configured")
            return {
                "summary": "AI analysis not available - API key not configured",
                "overall_risk": "unknown",
                "vulnerabilities": [],
                "gas_optimizations": [],
                "code_quality": {"score": 0, "issues": []},
                "architectural_issues": [],
                "logic_flaws": [],
                "best_practice_violations": []
            }

        try:
            # Format static findings for prompt
            static_findings_str = "None"
            if static_findings:
                static_findings_str = "\n".join([
                    f"- {f.get('title', 'Unknown')}: {f.get('description', '')}"
                    for f in static_findings
                ])

            # Detect contract type (simple heuristic)
            contract_type = self._detect_contract_type(code)

            # Generate prompt
            prompt = get_analysis_prompt(
                contract_code=code,
                language=language,
                compiler_version=compiler_version,
                static_findings=static_findings_str,
                contract_type=contract_type
            )

            logger.info(f"Sending analysis request to AI (code length: {len(code)} chars)")

            # Call Claude API
            response = self.client.messages.create(
                model=settings.AI_MODEL,
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract response text
            response_text = response.content[0].text

            logger.info(f"Received AI response (length: {len(response_text)} chars)")

            # Parse JSON response
            try:
                # Try to extract JSON from code blocks if present
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()

                analysis_result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                # Fallback to structured text response
                analysis_result = {
                    "summary": response_text[:500],
                    "overall_risk": "medium",
                    "vulnerabilities": [],
                    "gas_optimizations": [],
                    "code_quality": {"score": 50, "issues": []},
                }

            # Validate and normalize the response
            analysis_result = self._normalize_response(analysis_result)

            logger.info(f"AI analysis completed - found {len(analysis_result.get('vulnerabilities', []))} vulnerabilities")

            return analysis_result

        except Exception as e:
            logger.error(f"AI analysis failed: {e}", exc_info=True)
            return {
                "summary": f"AI analysis failed: {str(e)}",
                "overall_risk": "unknown",
                "vulnerabilities": [],
                "gas_optimizations": [],
                "code_quality": {"score": 0, "issues": []},
                "architectural_issues": [],
                "logic_flaws": [],
                "best_practice_violations": []
            }

    def _detect_contract_type(self, code: str) -> str:
        """
        Detect contract type based on code patterns

        Args:
            code: Contract source code

        Returns:
            Contract type (token, defi, nft, etc.)
        """
        code_lower = code.lower()

        if "erc20" in code_lower or "totalsupply" in code_lower:
            return "ERC20 Token"
        elif "erc721" in code_lower or "nft" in code_lower:
            return "NFT/ERC721"
        elif "erc1155" in code_lower:
            return "ERC1155"
        elif "swap" in code_lower or "liquidity" in code_lower:
            return "DeFi/DEX"
        elif "stake" in code_lower or "reward" in code_lower:
            return "Staking"
        elif "governance" in code_lower or "vote" in code_lower:
            return "Governance"
        elif "proxy" in code_lower or "upgradeable" in code_lower:
            return "Proxy/Upgradeable"
        else:
            return "Generic Contract"

    def _normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate AI response

        Args:
            response: Raw AI response

        Returns:
            Normalized response
        """
        normalized = {
            "summary": response.get("summary", ""),
            "overall_risk": response.get("overall_risk", "unknown").lower(),
            "vulnerabilities": [],
            "gas_optimizations": response.get("gas_optimizations", []),
            "code_quality": response.get("code_quality", {"score": 0, "issues": []}),
            "architectural_issues": response.get("architectural_issues", []),
            "logic_flaws": response.get("logic_flaws", []),
            "best_practice_violations": response.get("best_practice_violations", [])
        }

        # Normalize vulnerabilities
        for vuln in response.get("vulnerabilities", []):
            normalized_vuln = {
                "rule_id": vuln.get("rule_id", f"AI-{len(normalized['vulnerabilities']) + 1}"),
                "title": vuln.get("title", "Unknown Vulnerability"),
                "severity": vuln.get("severity", "info").lower(),
                "exploitability": vuln.get("exploitability", "moderate").lower(),
                "category": vuln.get("category", "security"),
                "line_number": vuln.get("line_number") or vuln.get("line"),
                "function_name": vuln.get("function_name") or vuln.get("function"),
                "description": vuln.get("description", ""),
                "exploit_scenario": vuln.get("exploit_scenario"),
                "recommendation": vuln.get("recommendation"),
                "fixed_code": vuln.get("fixed_code"),
                "cwe_id": vuln.get("cwe_id"),
                "swc_id": vuln.get("swc_id"),
                "detected_by": "ai",
                "confidence": vuln.get("confidence", 85)
            }
            normalized["vulnerabilities"].append(normalized_vuln)

        return normalized
