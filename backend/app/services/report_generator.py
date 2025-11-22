"""
Report generation service
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from jinja2 import Template

from app.models.audit import Audit
from app.models.report import ReportFormat
from app.schemas.report import ReportOptions

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates audit reports in multiple formats
    """

    def generate(
        self,
        audit: Audit,
        format: ReportFormat,
        options: Optional[ReportOptions] = None
    ) -> bytes:
        """
        Generate audit report in specified format

        Args:
            audit: Audit model instance
            format: Report format
            options: Report generation options

        Returns:
            Report content as bytes
        """
        if options is None:
            options = ReportOptions()

        logger.info(f"Generating {format.value} report for audit {audit.id}")

        if format == ReportFormat.JSON:
            return self._generate_json(audit, options)
        elif format == ReportFormat.HTML:
            return self._generate_html(audit, options)
        elif format == ReportFormat.MARKDOWN:
            return self._generate_markdown(audit, options)
        elif format == ReportFormat.PDF:
            return self._generate_pdf(audit, options)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json(self, audit: Audit, options: ReportOptions) -> bytes:
        """Generate JSON report"""
        report_data = {
            "audit_id": audit.id,
            "generated_at": datetime.utcnow().isoformat(),
            "contract_info": {
                "language": audit.language.value,
                "compiler_version": audit.compiler_version,
                "total_lines": audit.total_lines,
            },
            "summary": {
                "risk_score": audit.risk_score,
                "security_rating": audit.security_rating,
                "vulnerability_counts": {
                    "critical": audit.critical_count,
                    "high": audit.high_count,
                    "medium": audit.medium_count,
                    "low": audit.low_count,
                    "info": audit.info_count,
                },
                "total_vulnerabilities": (
                    audit.critical_count + audit.high_count +
                    audit.medium_count + audit.low_count + audit.info_count
                )
            },
            "vulnerabilities": [vuln.to_dict() for vuln in audit.vulnerabilities] if options.include_code_snippets else [],
            "gas_analysis": audit.gas_analysis if options.include_gas_analysis else None,
            "ai_analysis": {
                "summary": audit.ai_summary,
                "overall_risk": audit.ai_overall_risk
            } if options.include_ai_insights else None,
        }

        return json.dumps(report_data, indent=2).encode('utf-8')

    def _generate_html(self, audit: Audit, options: ReportOptions) -> bytes:
        """Generate HTML report"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentryAudit Report - {{ audit.id }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #8B0000; }
        .logo { color: #8B0000; font-size: 36px; font-weight: bold; margin-bottom: 10px; }
        .title { font-size: 24px; color: #666; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .summary-card { background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-card h3 { font-size: 14px; text-transform: uppercase; margin-bottom: 10px; opacity: 0.9; }
        .summary-card .value { font-size: 36px; font-weight: bold; }
        .rating { display: inline-block; background: #10B981; color: white; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 18px; }
        .rating.A { background: #10B981; }
        .rating.B { background: #3B82F6; }
        .rating.C { background: #F59E0B; }
        .rating.D, .rating.F { background: #DC143C; }
        .section { margin: 40px 0; }
        .section-title { font-size: 22px; color: #8B0000; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #eee; }
        .vulnerability { background: #f9f9f9; padding: 20px; margin: 15px 0; border-left: 4px solid #ccc; border-radius: 4px; }
        .vulnerability.critical { border-left-color: #8B0000; }
        .vulnerability.high { border-left-color: #DC143C; }
        .vulnerability.medium { border-left-color: #F59E0B; }
        .vulnerability.low { border-left-color: #3B82F6; }
        .vulnerability.info { border-left-color: #6B7280; }
        .vuln-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
        .vuln-title { font-size: 18px; font-weight: bold; color: #333; }
        .severity-badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; color: white; }
        .severity-badge.critical { background: #8B0000; }
        .severity-badge.high { background: #DC143C; }
        .severity-badge.medium { background: #F59E0B; }
        .severity-badge.low { background: #3B82F6; }
        .severity-badge.info { background: #6B7280; }
        .vuln-description { margin: 15px 0; color: #555; }
        .code-block { background: #1a1a1a; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; margin: 15px 0; font-family: 'Courier New', monospace; font-size: 13px; }
        .recommendation { background: #e8f5e9; padding: 15px; border-radius: 4px; margin: 15px 0; border-left: 4px solid #10B981; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🛡️ SENTRYAUDIT AI</div>
            <div class="title">Smart Contract Security Audit Report</div>
            <p style="color: #999; margin-top: 10px;">Generated: {{ now }}</p>
        </div>

        {% if options.include_executive_summary %}
        <div class="section">
            <h2 class="section-title">Executive Summary</h2>
            <div class="summary">
                <div class="summary-card">
                    <h3>Security Rating</h3>
                    <div class="value"><span class="rating {{ audit.security_rating[0] }}">{{ audit.security_rating or 'N/A' }}</span></div>
                </div>
                <div class="summary-card">
                    <h3>Risk Score</h3>
                    <div class="value">{{ audit.risk_score }}/100</div>
                </div>
                <div class="summary-card">
                    <h3>Critical Issues</h3>
                    <div class="value">{{ audit.critical_count }}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Issues</h3>
                    <div class="value">{{ audit.critical_count + audit.high_count + audit.medium_count + audit.low_count + audit.info_count }}</div>
                </div>
            </div>

            {% if audit.ai_summary %}
            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #8B0000; margin-bottom: 10px;">AI Analysis Summary</h3>
                <p>{{ audit.ai_summary }}</p>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="section">
            <h2 class="section-title">Vulnerabilities Found ({{ audit.vulnerabilities|length }})</h2>
            {% for vuln in audit.vulnerabilities %}
            <div class="vulnerability {{ vuln.severity.value }}">
                <div class="vuln-header">
                    <div class="vuln-title">{{ vuln.title }}</div>
                    <span class="severity-badge {{ vuln.severity.value }}">{{ vuln.severity.value }}</span>
                </div>
                <p class="vuln-description">{{ vuln.description }}</p>

                {% if vuln.code_snippet and options.include_code_snippets %}
                <div>
                    <strong>Location:</strong> Line {{ vuln.line_number }}
                    {% if vuln.function_name %} in function <code>{{ vuln.function_name }}()</code>{% endif %}
                </div>
                <pre class="code-block">{{ vuln.code_snippet }}</pre>
                {% endif %}

                {% if vuln.recommendation and options.include_recommendations %}
                <div class="recommendation">
                    <strong>💡 Recommendation:</strong><br>
                    {{ vuln.recommendation }}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        {% if options.include_gas_analysis and audit.gas_analysis %}
        <div class="section">
            <h2 class="section-title">Gas Optimization Opportunities</h2>
            {% if audit.gas_analysis.optimizations %}
                {% for opt in audit.gas_analysis.optimizations %}
                <div class="vulnerability info">
                    <div class="vuln-title">{{ opt.issue }}</div>
                    <p style="margin: 10px 0;"><strong>Line:</strong> {{ opt.line }}</p>
                    <p style="margin: 10px 0;"><strong>Potential Savings:</strong> {{ opt.savings }}</p>
                    <div class="recommendation">
                        {{ opt.recommendation }}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p>No gas optimization opportunities identified.</p>
            {% endif %}
        </div>
        {% endif %}

        <div class="footer">
            <p><strong>SentryAudit AI</strong> - Enterprise-Grade Smart Contract Security Auditor</p>
            <p>This report was generated by automated analysis. For production contracts, consider a manual security review.</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(html_template)
        html_content = template.render(
            audit=audit,
            options=options,
            now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        )

        return html_content.encode('utf-8')

    def _generate_markdown(self, audit: Audit, options: ReportOptions) -> bytes:
        """Generate Markdown report"""
        md_lines = [
            "# 🛡️ SentryAudit AI - Security Audit Report",
            "",
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Audit ID:** {audit.id}",
            "",
            "---",
            "",
        ]

        if options.include_executive_summary:
            md_lines.extend([
                "## Executive Summary",
                "",
                f"- **Security Rating:** {audit.security_rating or 'N/A'}",
                f"- **Risk Score:** {audit.risk_score}/100",
                f"- **Critical Issues:** {audit.critical_count}",
                f"- **High Issues:** {audit.high_count}",
                f"- **Medium Issues:** {audit.medium_count}",
                f"- **Low Issues:** {audit.low_count}",
                f"- **Info Issues:** {audit.info_count}",
                "",
            ])

            if audit.ai_summary:
                md_lines.extend([
                    "### AI Analysis Summary",
                    "",
                    audit.ai_summary,
                    "",
                ])

            md_lines.append("---\n")

        md_lines.extend([
            f"## Vulnerabilities ({len(audit.vulnerabilities)})",
            "",
        ])

        for i, vuln in enumerate(audit.vulnerabilities, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
                "info": "⚪"
            }
            emoji = severity_emoji.get(vuln.severity.value, "⚪")

            md_lines.extend([
                f"### {i}. {emoji} {vuln.title}",
                "",
                f"**Severity:** {vuln.severity.value.upper()}",
                "",
                f"**Description:** {vuln.description}",
                "",
            ])

            if vuln.line_number:
                location = f"Line {vuln.line_number}"
                if vuln.function_name:
                    location += f" in function `{vuln.function_name}()`"
                md_lines.extend([f"**Location:** {location}", ""])

            if vuln.code_snippet and options.include_code_snippets:
                md_lines.extend([
                    "**Code:**",
                    "```solidity",
                    vuln.code_snippet,
                    "```",
                    ""
                ])

            if vuln.recommendation and options.include_recommendations:
                md_lines.extend([
                    "**Recommendation:**",
                    vuln.recommendation,
                    ""
                ])

            md_lines.append("---\n")

        if options.include_gas_analysis and audit.gas_analysis:
            md_lines.extend([
                "## Gas Optimization Opportunities",
                "",
            ])

            if audit.gas_analysis.get("optimizations"):
                for opt in audit.gas_analysis["optimizations"]:
                    md_lines.extend([
                        f"### {opt['issue']}",
                        "",
                        f"**Line:** {opt.get('line', 'N/A')}",
                        f"**Savings:** {opt.get('savings', 'N/A')}",
                        "",
                        f"**Recommendation:** {opt.get('recommendation', 'N/A')}",
                        "",
                        "---",
                        ""
                    ])

        md_lines.extend([
            "",
            "---",
            "",
            "*This report was generated by **SentryAudit AI** - Enterprise-Grade Smart Contract Security Auditor*",
            ""
        ])

        return "\n".join(md_lines).encode('utf-8')

    def _generate_pdf(self, audit: Audit, options: ReportOptions) -> bytes:
        """Generate PDF report (requires WeasyPrint)"""
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration

            # Generate HTML first
            html_content = self._generate_html(audit, options).decode('utf-8')

            # Convert to PDF
            font_config = FontConfiguration()
            pdf_bytes = HTML(string=html_content).write_pdf(font_config=font_config)

            return pdf_bytes

        except ImportError:
            logger.warning("WeasyPrint not installed - falling back to HTML")
            # Fallback to HTML if WeasyPrint is not available
            return self._generate_html(audit, options)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            # Fallback to HTML
            return self._generate_html(audit, options)
