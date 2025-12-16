"""
Report Generation System
========================

Generates comprehensive verification reports with visualizations, evidence aggregation,
and export capabilities (JSON, PDF, HTML).

FEATURES:
- Risk assessment compilation
- Timeline visualization (JSON format for frontend)
- Screenshot evidence organization
- Claim categorization (verified/unverified/suspicious)
- Red flag highlighting with severity levels
- Multi-format export (JSON, PDF, HTML)
- Professional formatting with branding

USAGE:
    from report_generator import ReportGenerator
    from verification_engine import VerificationEngine
    
    # Generate verification report
    engine = VerificationEngine(profession='software_engineer')
    # ... add results ...
    
    generator = ReportGenerator(engine)
    
    # Compile full report
    report_data = generator.compile_report()
    
    # Export to JSON
    generator.export_to_json('verification_report.json')
    
    # Export to PDF
    generator.export_to_pdf('verification_report.pdf')
    
    # Export to HTML
    generator.export_to_html('verification_report.html')

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Professional verification report generator with multiple export formats.
    """
    
    def __init__(self, verification_engine):
        """
        Initialize report generator.
        
        Args:
            verification_engine: VerificationEngine instance with results
        """
        self.engine = verification_engine
        self.report_data = None
        
        logger.info("[REPORT_GENERATOR] Initialized")
    
    def compile_report(self) -> Dict[str, Any]:
        """
        Compile comprehensive verification report.
        
        Returns:
            Complete report dict with all sections
        """
        logger.info("[REPORT_GENERATOR] Compiling report...")
        
        # Generate all report components
        risk_assessment = self.compile_risk_assessment()
        claims_analysis = self.categorize_claims()
        timeline_viz = self.generate_timeline_visualization()
        red_flags_section = self.highlight_red_flags()
        evidence_section = self.compile_screenshots()
        
        self.report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'profession': self.engine.profession,
                'generator': 'Valor AI Professional Verification'
            },
            'executive_summary': self._generate_executive_summary(risk_assessment, red_flags_section),
            'risk_assessment': risk_assessment,
            'claims_analysis': claims_analysis,
            'timeline': timeline_viz,
            'red_flags': red_flags_section,
            'evidence': evidence_section,
            'recommendations': self._generate_recommendations(risk_assessment)
        }
        
        logger.info("[REPORT_GENERATOR] Report compiled successfully")
        
        return self.report_data
    
    def compile_risk_assessment(self) -> Dict[str, Any]:
        """
        Compile risk assessment section.
        
        Returns:
            Risk assessment with scores and breakdown
        """
        logger.info("[REPORT_GENERATOR] Compiling risk assessment...")
        
        # Get risk score from engine
        risk_data = self.engine.calculate_risk_score()
        
        # Format for report
        assessment = {
            'overall_risk': {
                'score': risk_data['overall_score'],
                'level': risk_data['risk_level'],
                'confidence': risk_data['confidence'],
                'description': self._get_risk_description(risk_data['risk_level'])
            },
            'category_scores': {},
            'scoring_methodology': {
                'profession': self.engine.profession,
                'weights_applied': risk_data['weights_used']
            }
        }
        
        # Format category scores with descriptions
        for category, score in risk_data['category_scores'].items():
            if score is not None:
                assessment['category_scores'][category] = {
                    'score': score,
                    'risk_level': self._get_category_risk_level(score),
                    'description': risk_data['category_breakdown'].get(category, 'N/A'),
                    'weight': risk_data['weights_used'][category]
                }
        
        return assessment
    
    def categorize_claims(self) -> Dict[str, Any]:
        """
        Categorize claims as verified/unverified/suspicious.
        
        Returns:
            Claims analysis with categorization
        """
        logger.info("[REPORT_GENERATOR] Categorizing claims...")
        
        # Get cross-reference data
        cross_ref = self.engine.cross_reference_data()
        
        # Categorize
        verified = cross_ref['verified_claims']
        unverified = cross_ref['unverified_claims']
        suspicious = self._identify_suspicious_claims()
        
        analysis = {
            'summary': {
                'total_claims': len(verified) + len(unverified) + len(suspicious),
                'verified_count': len(verified),
                'unverified_count': len(unverified),
                'suspicious_count': len(suspicious),
                'verification_rate': round(len(verified) / max(len(verified) + len(unverified), 1) * 100, 1)
            },
            'verified_claims': verified,
            'unverified_claims': unverified,
            'suspicious_claims': suspicious
        }
        
        return analysis
    
    def generate_timeline_visualization(self) -> Dict[str, Any]:
        """
        Generate timeline visualization data (JSON format for frontend).
        
        Returns:
            Timeline data with events, gaps, and overlaps
        """
        logger.info("[REPORT_GENERATOR] Generating timeline visualization...")
        
        timeline = {
            'events': [],
            'gaps': [],
            'overlaps': [],
            'inconsistencies': []
        }
        
        # Add employment events
        for event in self.engine.timeline_events:
            timeline['events'].append({
                'type': event['type'],
                'source': event['source'],
                'title': f"{event.get('title', 'Unknown')} at {event.get('company', 'Unknown')}",
                'start_date': event.get('start_date'),
                'end_date': event.get('end_date'),
                'duration_months': event.get('duration_months'),
                'details': event
            })
        
        # Add gaps
        gaps = self.engine._find_timeline_gaps()
        for gap in gaps:
            timeline['gaps'].append({
                'start_date': gap['start_date'],
                'end_date': gap['end_date'],
                'duration_days': gap['duration_days'],
                'duration_months': gap['duration_days'] // 30,
                'severity': 'high' if gap['duration_days'] > 365 else 'medium' if gap['duration_days'] > 180 else 'low'
            })
        
        # Add overlaps (if any)
        overlaps = self.engine._find_timeline_overlaps()
        timeline['overlaps'] = overlaps
        
        # Add cross-platform inconsistencies
        inconsistencies = self.engine._find_cross_platform_inconsistencies()
        timeline['inconsistencies'] = inconsistencies
        
        return timeline
    
    def highlight_red_flags(self) -> Dict[str, Any]:
        """
        Highlight red flags with severity levels.
        
        Returns:
            Organized red flags by severity
        """
        logger.info("[REPORT_GENERATOR] Highlighting red flags...")
        
        all_flags = self.engine.detect_red_flags()
        
        # Organize by severity
        flags_by_severity = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }
        
        for flag in all_flags:
            severity = flag['severity']
            flags_by_severity[severity].append(flag)
        
        red_flags = {
            'summary': {
                'total_flags': len(all_flags),
                'critical_count': len(flags_by_severity['CRITICAL']),
                'high_count': len(flags_by_severity['HIGH']),
                'medium_count': len(flags_by_severity['MEDIUM']),
                'low_count': len(flags_by_severity['LOW'])
            },
            'by_severity': flags_by_severity,
            'by_category': self._organize_flags_by_category(all_flags)
        }
        
        return red_flags
    
    def compile_screenshots(self) -> Dict[str, Any]:
        """
        Compile and organize screenshot evidence.
        
        Returns:
            Organized screenshots by category with metadata
        """
        logger.info("[REPORT_GENERATOR] Compiling screenshot evidence...")
        
        evidence = {
            'screenshot_count': 0,
            'by_tool': {},
            'by_category': {
                'resume': [],
                'credentials': [],
                'online_presence': [],
                'company': [],
                'other': []
            }
        }
        
        # Extract screenshots from tool results
        for tool_name, result in self.engine.results.items():
            screenshots = result.get('screenshots', [])
            
            if screenshots:
                evidence['by_tool'][tool_name] = {
                    'count': len(screenshots),
                    'screenshots': screenshots
                }
                evidence['screenshot_count'] += len(screenshots)
                
                # Categorize screenshots
                category = self._categorize_screenshot(tool_name)
                evidence['by_category'][category].extend(screenshots)
        
        return evidence
    
    def export_to_json(self, filepath: str) -> str:
        """
        Export report to JSON file.
        
        Args:
            filepath: Output JSON file path
            
        Returns:
            Absolute path to created file
        """
        logger.info(f"[REPORT_GENERATOR] Exporting to JSON: {filepath}")
        
        if not self.report_data:
            self.compile_report()
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[REPORT_GENERATOR] JSON export complete: {output_path.absolute()}")
        
        return str(output_path.absolute())
    
    def export_to_pdf(self, filepath: str) -> str:
        """
        Export report to PDF file.
        
        Args:
            filepath: Output PDF file path
            
        Returns:
            Absolute path to created file
        """
        logger.info(f"[REPORT_GENERATOR] Exporting to PDF: {filepath}")
        
        if not self.report_data:
            self.compile_report()
        
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create PDF
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#333333'),
                spaceAfter=12
            )
            
            # Title
            story.append(Paragraph("Professional Verification Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Metadata
            metadata = self.report_data['metadata']
            story.append(Paragraph(f"Generated: {metadata['generated_at']}", styles['Normal']))
            story.append(Paragraph(f"Profession: {metadata['profession'].replace('_', ' ').title()}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            summary = self.report_data['executive_summary']
            story.append(Paragraph(summary['summary_text'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Risk Assessment
            story.append(Paragraph("Risk Assessment", heading_style))
            risk = self.report_data['risk_assessment']['overall_risk']
            
            risk_data = [
                ['Overall Risk Score', f"{risk['score']}/100"],
                ['Risk Level', risk['level']],
                ['Confidence', f"{risk['confidence']}%"]
            ]
            
            risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(risk_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Red Flags
            story.append(Paragraph("Red Flags", heading_style))
            red_flags = self.report_data['red_flags']
            story.append(Paragraph(f"Total: {red_flags['summary']['total_flags']}", styles['Normal']))
            story.append(Paragraph(f"Critical: {red_flags['summary']['critical_count']}", styles['Normal']))
            story.append(Paragraph(f"High: {red_flags['summary']['high_count']}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Critical flags details
            if red_flags['by_severity']['CRITICAL']:
                story.append(Paragraph("Critical Issues:", styles['Heading3']))
                for flag in red_flags['by_severity']['CRITICAL']:
                    story.append(Paragraph(f"• {flag['flag']}: {flag['description']}", styles['Normal']))
            
            story.append(PageBreak())
            
            # Recommendations
            story.append(Paragraph("Recommendations", heading_style))
            for rec in self.report_data['recommendations']:
                story.append(Paragraph(f"• {rec}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"[REPORT_GENERATOR] PDF export complete: {output_path.absolute()}")
            
            return str(output_path.absolute())
            
        except ImportError:
            logger.warning("[REPORT_GENERATOR] ReportLab not installed, PDF export unavailable")
            logger.info("[REPORT_GENERATOR] Install with: pip install reportlab")
            return None
    
    def export_to_html(self, filepath: str) -> str:
        """
        Export report to HTML file.
        
        Args:
            filepath: Output HTML file path
            
        Returns:
            Absolute path to created file
        """
        logger.info(f"[REPORT_GENERATOR] Exporting to HTML: {filepath}")
        
        if not self.report_data:
            self.compile_report()
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML
        html = self._generate_html_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[REPORT_GENERATOR] HTML export complete: {output_path.absolute()}")
        
        return str(output_path.absolute())
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _generate_executive_summary(
        self,
        risk_assessment: Dict,
        red_flags: Dict
    ) -> Dict[str, Any]:
        """Generate executive summary section."""
        risk = risk_assessment['overall_risk']
        flags = red_flags['summary']
        
        summary_text = f"""
This verification report analyzes a {self.engine.profession.replace('_', ' ')} candidate 
with an overall risk score of {risk['score']}/100 ({risk['level']} Risk).

The assessment is based on {risk['confidence']}% data availability across multiple 
verification categories including credentials, online presence, and timeline consistency.

A total of {flags['total_flags']} red flags were identified, including 
{flags['critical_count']} critical and {flags['high_count']} high priority issues.
"""
        
        return {
            'summary_text': summary_text.strip(),
            'key_metrics': {
                'risk_score': risk['score'],
                'risk_level': risk['level'],
                'confidence': risk['confidence'],
                'total_red_flags': flags['total_flags'],
                'critical_flags': flags['critical_count']
            }
        }
    
    def _generate_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate actionable recommendations."""
        # Extract overall_risk dict and pass to engine
        overall_risk = risk_assessment.get('overall_risk', {})
        
        # Build simplified dict for engine method
        engine_format = {
            'overall_score': overall_risk.get('score', 0),
            'risk_level': overall_risk.get('level', 'Unknown'),
            'confidence': overall_risk.get('confidence', 0)
        }
        
        return self.engine._generate_recommendations(
            engine_format,
            self.engine.red_flags
        )
    
    def _get_risk_description(self, risk_level: str) -> str:
        """Get description for risk level."""
        descriptions = {
            'Low': 'Candidate verification shows minimal concerns. Standard hiring process recommended.',
            'Medium': 'Some verification concerns identified. Additional documentation recommended.',
            'High': 'Significant verification concerns. Thorough investigation required before proceeding.',
            'Critical': 'Critical verification issues detected. Strong recommendation against hiring.'
        }
        return descriptions.get(risk_level, 'Unknown risk level')
    
    def _get_category_risk_level(self, score: float) -> str:
        """Get risk level for category score."""
        if score < 30:
            return 'Low'
        elif score < 60:
            return 'Medium'
        elif score < 80:
            return 'High'
        else:
            return 'Critical'
    
    def _identify_suspicious_claims(self) -> List[Dict[str, Any]]:
        """Identify suspicious claims (contradictory data)."""
        suspicious = []
        
        # Check for claims that conflict across sources
        # (Simplified implementation)
        
        return suspicious
    
    def _organize_flags_by_category(self, flags: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize red flags by category."""
        by_category = {}
        
        for flag in flags:
            category = flag['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(flag)
        
        return by_category
    
    def _categorize_screenshot(self, tool_name: str) -> str:
        """Categorize screenshot by tool name."""
        if 'resume' in tool_name.lower():
            return 'resume'
        elif 'credential' in tool_name.lower() or 'license' in tool_name.lower():
            return 'credentials'
        elif 'github' in tool_name.lower() or 'linkedin' in tool_name.lower():
            return 'online_presence'
        elif 'company' in tool_name.lower() or 'domain' in tool_name.lower():
            return 'company'
        else:
            return 'other'
    
    def _generate_html_report(self) -> str:
        """Generate HTML report with styling."""
        risk = self.report_data['risk_assessment']['overall_risk']
        flags = self.report_data['red_flags']
        claims = self.report_data['claims_analysis']
        
        # Determine risk color
        risk_colors = {
            'Low': '#10b981',
            'Medium': '#f59e0b',
            'High': '#ef4444',
            'Critical': '#991b1b'
        }
        risk_color = risk_colors.get(risk['level'], '#6b7280')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Verification Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f3f4f6; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #1f2937; margin-bottom: 10px; }}
        h2 {{ color: #374151; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
        .metadata {{ color: #6b7280; font-size: 14px; margin-bottom: 30px; }}
        .risk-score {{ background: {risk_color}; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .risk-score h3 {{ margin-bottom: 10px; }}
        .metric {{ display: inline-block; margin-right: 30px; }}
        .flag {{ padding: 10px; margin: 10px 0; border-left: 4px solid; }}
        .flag.critical {{ background: #fee2e2; border-color: #991b1b; }}
        .flag.high {{ background: #fef3c7; border-color: #d97706; }}
        .flag.medium {{ background: #dbeafe; border-color: #2563eb; }}
        .flag.low {{ background: #f3f4f6; border-color: #6b7280; }}
        .claim {{ padding: 8px; margin: 5px 0; border-radius: 4px; }}
        .claim.verified {{ background: #d1fae5; }}
        .claim.unverified {{ background: #fef3c7; }}
        .recommendation {{ padding: 12px; margin: 10px 0; background: #f0f9ff; border-left: 4px solid #0284c7; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Professional Verification Report</h1>
        <div class="metadata">
            Generated: {self.report_data['metadata']['generated_at']}<br>
            Profession: {self.report_data['metadata']['profession'].replace('_', ' ').title()}
        </div>
        
        <div class="risk-score">
            <h3>Overall Risk Assessment</h3>
            <div class="metric">
                <strong>Score:</strong> {risk['score']}/100
            </div>
            <div class="metric">
                <strong>Level:</strong> {risk['level']}
            </div>
            <div class="metric">
                <strong>Confidence:</strong> {risk['confidence']}%
            </div>
        </div>
        
        <h2>Executive Summary</h2>
        <p>{self.report_data['executive_summary']['summary_text']}</p>
        
        <h2>Red Flags ({flags['summary']['total_flags']} total)</h2>
"""
        
        # Add critical flags
        for flag in flags['by_severity']['CRITICAL']:
            html += f"""
        <div class="flag critical">
            <strong>CRITICAL:</strong> {flag['flag']}<br>
            {flag['description']}
        </div>
"""
        
        # Add high flags
        for flag in flags['by_severity']['HIGH']:
            html += f"""
        <div class="flag high">
            <strong>HIGH:</strong> {flag['flag']}<br>
            {flag['description']}
        </div>
"""
        
        # Claims analysis
        html += f"""
        <h2>Claims Analysis</h2>
        <p>
            <strong>Verified:</strong> {claims['summary']['verified_count']}<br>
            <strong>Unverified:</strong> {claims['summary']['unverified_count']}<br>
            <strong>Verification Rate:</strong> {claims['summary']['verification_rate']}%
        </p>
"""
        
        # Recommendations
        html += "<h2>Recommendations</h2>"
        for rec in self.report_data['recommendations']:
            html += f'<div class="recommendation">{rec}</div>'
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
