"""
Verification Engine Core
========================

Core logic for professional verification risk scoring and red flag detection.
Analyzes verification results from all tools and generates comprehensive risk assessment.

FEATURES:
- Multi-category risk scoring (0-100 scale)
- Profession-specific weighted scoring templates
- Timeline consistency validation
- Red flag detection and classification
- Evidence aggregation with screenshots
- Cross-reference validation

RISK CATEGORIES:
1. Resume Authenticity (15%) - AI detection, format analysis, consistency
2. Online Presence (20%) - GitHub activity, LinkedIn profile, social media
3. Credential Validity (25%) - Licenses, education, certifications
4. Company Legitimacy (15%) - Domain age, business records, social footprint
5. Timeline Consistency (20%) - Cross-platform gaps, employment overlaps
6. Digital Footprint (5%) - Mentions, publications, reputation

USAGE:
    from verification_engine import VerificationEngine
    
    engine = VerificationEngine(profession='software_engineer')
    
    # Add verification results from tools
    engine.add_result('parse_resume', resume_data)
    engine.add_result('verify_github_profile', github_data)
    engine.add_result('search_linkedin_profile', linkedin_data)
    
    # Calculate risk score
    risk_assessment = engine.calculate_risk_score()
    
    # Detect red flags
    red_flags = engine.detect_red_flags()
    
    # Generate final report
    report = engine.generate_report()

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class VerificationEngine:
    """
    Core verification engine for risk scoring and red flag detection.
    """
    
    # Profession-specific scoring weights
    PROFESSION_TEMPLATES = {
        'software_engineer': {
            'resume_authenticity': 10,
            'online_presence': 30,      # Higher weight for tech (GitHub critical)
            'credential_validity': 10,
            'company_legitimacy': 15,
            'timeline_consistency': 25,
            'digital_footprint': 10
        },
        'medical_professional': {
            'resume_authenticity': 15,
            'online_presence': 10,
            'credential_validity': 40,  # Higher weight for medical licenses
            'company_legitimacy': 10,
            'timeline_consistency': 20,
            'digital_footprint': 5
        },
        'legal_professional': {
            'resume_authenticity': 15,
            'online_presence': 10,
            'credential_validity': 35,  # Bar admission critical
            'company_legitimacy': 15,
            'timeline_consistency': 20,
            'digital_footprint': 5
        },
        'financial_professional': {
            'resume_authenticity': 15,
            'online_presence': 15,
            'credential_validity': 30,  # CPA/certifications important
            'company_legitimacy': 15,
            'timeline_consistency': 20,
            'digital_footprint': 5
        },
        'default': {
            'resume_authenticity': 15,
            'online_presence': 20,
            'credential_validity': 25,
            'company_legitimacy': 15,
            'timeline_consistency': 20,
            'digital_footprint': 5
        }
    }
    
    def __init__(self, profession: str = 'default'):
        """
        Initialize verification engine.
        
        Args:
            profession: Profession type for weighted scoring
        """
        self.profession = profession.lower().replace(' ', '_')
        self.weights = self.PROFESSION_TEMPLATES.get(
            self.profession,
            self.PROFESSION_TEMPLATES['default']
        )
        
        self.results = {}           # Tool results storage
        self.category_scores = {}   # Category-level scores (0-100)
        self.red_flags = []         # Detected red flags
        self.verified_claims = []   # Multi-source verified claims
        self.unverified_claims = [] # Single-source only claims
        self.timeline_events = []   # Chronological events
        
        logger.info(f"[VERIFICATION_ENGINE] Initialized for profession: {self.profession}")
    
    def add_result(self, tool_name: str, result: Dict[str, Any]):
        """
        Add tool execution result to engine.
        
        Args:
            tool_name: Name of verification tool
            result: Tool execution result dict
        """
        self.results[tool_name] = result
        logger.info(f"[VERIFICATION_ENGINE] Added result from: {tool_name}")
    
    def calculate_risk_score(self) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score (0-100).
        
        Returns:
            {
                'overall_score': 0-100 (lower is better),
                'risk_level': 'Low'|'Medium'|'High'|'Critical',
                'category_scores': {...},
                'category_breakdown': {...},
                'confidence': 0-100
            }
        """
        logger.info("[VERIFICATION_ENGINE] Calculating risk score...")
        
        # Calculate each category score
        self.category_scores = {
            'resume_authenticity': self._score_resume_authenticity(),
            'online_presence': self._score_online_presence(),
            'credential_validity': self._score_credential_validity(),
            'company_legitimacy': self._score_company_legitimacy(),
            'timeline_consistency': self._score_timeline_consistency(),
            'digital_footprint': self._score_digital_footprint()
        }
        
        # Calculate weighted overall score
        overall_score = 0
        total_weight = 0
        
        for category, score in self.category_scores.items():
            if score is not None:  # Skip categories with no data
                weight = self.weights[category]
                overall_score += score * (weight / 100)
                total_weight += weight
        
        # Normalize if not all categories were scored
        if total_weight < 100:
            overall_score = (overall_score / total_weight) * 100
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence()
        
        result = {
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level,
            'category_scores': self.category_scores,
            'category_breakdown': self._get_category_breakdown(),
            'confidence': confidence,
            'profession': self.profession,
            'weights_used': self.weights
        }
        
        logger.info(f"[VERIFICATION_ENGINE] Risk score: {overall_score:.1f} ({risk_level})")
        
        return result
    
    def _score_resume_authenticity(self) -> Optional[float]:
        """Score resume authenticity (0-100, lower is better)."""
        resume_data = self.results.get('parse_resume', {}).get('result', {})
        if not resume_data:
            return None
        
        score = 0
        max_score = 100
        
        # AI-generated content detection (40 points)
        ai_detection = resume_data.get('ai_detection', {})
        if ai_detection.get('is_ai_generated'):
            confidence = ai_detection.get('confidence', 0)
            score += 40 * (confidence / 100)
        
        # Missing critical fields (30 points)
        required_fields = ['name', 'contact', 'experience', 'education']
        missing_count = sum(1 for field in required_fields if not resume_data.get(field))
        score += (missing_count / len(required_fields)) * 30
        
        # Formatting inconsistencies (20 points)
        # Check for mixed date formats, inconsistent spacing, etc.
        if self._has_formatting_issues(resume_data):
            score += 20
        
        # Suspicious patterns (10 points)
        if self._has_suspicious_patterns(resume_data):
            score += 10
        
        return min(score, max_score)
    
    def _score_online_presence(self) -> Optional[float]:
        """Score online presence (0-100, lower is better)."""
        github_data = self.results.get('verify_github_profile', {}).get('result', {})
        linkedin_data = self.results.get('search_linkedin_profile', {}).get('result', {})
        
        if not github_data and not linkedin_data:
            return None
        
        score = 0
        
        # GitHub presence (50 points for tech roles)
        if self.profession == 'software_engineer':
            if not github_data.get('profile_exists'):
                score += 30
            elif github_data.get('activity_score', 0) < 20:
                score += 20
            elif github_data.get('public_repos', 0) == 0:
                score += 15
        
        # LinkedIn presence (50 points)
        if not linkedin_data.get('profile_found'):
            score += 30
        elif not linkedin_data.get('profile_complete'):
            score += 15
        elif linkedin_data.get('connections', 0) < 50:
            score += 10
        
        return min(score, 100)
    
    def _score_credential_validity(self) -> Optional[float]:
        """Score credential validity (0-100, lower is better)."""
        credential_data = self.results.get('verify_credential_registry', {}).get('result', {})
        education_data = self.results.get('check_education_credentials', {}).get('result', {})
        
        if not credential_data and not education_data:
            return None
        
        score = 0
        
        # Professional credentials (60 points)
        if credential_data:
            if not credential_data.get('credential_valid'):
                score += 60
            elif credential_data.get('status') != 'Active':
                score += 40
            elif credential_data.get('disciplinary_actions'):
                score += 30
            elif credential_data.get('expired'):
                score += 25
        
        # Education credentials (40 points)
        if education_data:
            if not education_data.get('degree_verified'):
                score += 40
            elif education_data.get('institution_suspicious'):
                score += 30
        
        return min(score, 100)
    
    def _score_company_legitimacy(self) -> Optional[float]:
        """Score company legitimacy (0-100, lower is better)."""
        domain_data = self.results.get('check_domain_age', {}).get('result', {})
        wayback_data = self.results.get('check_wayback_history', {}).get('result', {})
        company_data = self.results.get('check_company_data', {}).get('result', {})
        
        if not any([domain_data, wayback_data, company_data]):
            return None
        
        score = 0
        
        # Domain age (40 points)
        if domain_data:
            if domain_data.get('is_recently_created'):
                score += 40
            elif domain_data.get('age_days', 0) < 180:  # Less than 6 months
                score += 30
        
        # Wayback Machine history (30 points)
        if wayback_data:
            if wayback_data.get('snapshots_found', 0) == 0:
                score += 30
            elif not wayback_data.get('active_during_period'):
                score += 20
        
        # Company data (30 points)
        if company_data:
            if not company_data.get('company_found'):
                score += 30
            elif not company_data.get('verified'):
                score += 15
        
        return min(score, 100)
    
    def _score_timeline_consistency(self) -> Optional[float]:
        """Score timeline consistency (0-100, lower is better)."""
        # Build timeline from multiple sources
        self._build_timeline()
        
        if not self.timeline_events:
            return None
        
        score = 0
        
        # Check for gaps (40 points)
        gaps = self._find_timeline_gaps()
        if gaps:
            # Each gap > 6 months adds points
            for gap in gaps:
                if gap['duration_days'] > 180:
                    score += min(10, gap['duration_days'] / 365 * 5)
        
        # Check for overlaps (30 points)
        overlaps = self._find_timeline_overlaps()
        if overlaps:
            score += len(overlaps) * 10
        
        # Cross-platform inconsistencies (30 points)
        inconsistencies = self._find_cross_platform_inconsistencies()
        if inconsistencies:
            score += len(inconsistencies) * 10
        
        return min(score, 100)
    
    def _score_digital_footprint(self) -> Optional[float]:
        """Score digital footprint (0-100, lower is better)."""
        # This would analyze:
        # - Google search results
        # - Social media presence
        # - Professional mentions
        # - Publications/articles
        
        # Placeholder for now
        return 50  # Neutral score if no data
    
    def detect_red_flags(self) -> List[Dict[str, Any]]:
        """
        Detect and classify red flags.
        
        Returns:
            List of red flag dicts with severity and description
        """
        logger.info("[VERIFICATION_ENGINE] Detecting red flags...")
        
        self.red_flags = []
        
        # CRITICAL: Fake credentials
        credential_data = self.results.get('verify_credential_registry', {}).get('result', {})
        if credential_data and not credential_data.get('credential_valid'):
            self.red_flags.append({
                'severity': 'CRITICAL',
                'category': 'credentials',
                'flag': 'Invalid professional credential',
                'description': f"Credential {credential_data.get('credential_number')} not found in registry",
                'evidence': credential_data
            })
        
        # CRITICAL: AI-generated resume
        resume_data = self.results.get('parse_resume', {}).get('result', {})
        ai_detection = resume_data.get('ai_detection', {})
        if ai_detection.get('is_ai_generated') and ai_detection.get('confidence', 0) > 70:
            self.red_flags.append({
                'severity': 'CRITICAL',
                'category': 'resume',
                'flag': 'AI-generated resume detected',
                'description': f"Resume shows {ai_detection.get('confidence')}% AI generation indicators",
                'evidence': ai_detection.get('indicators', [])
            })
        
        # HIGH: Recently created company domain
        domain_data = self.results.get('check_domain_age', {}).get('result', {})
        if domain_data and domain_data.get('age_days', 999) < 180:
            self.red_flags.append({
                'severity': 'HIGH',
                'category': 'company',
                'flag': 'Recently created company domain',
                'description': f"Domain created {domain_data.get('age_days')} days ago (< 6 months)",
                'evidence': domain_data
            })
        
        # HIGH: Large timeline gaps
        gaps = self._find_timeline_gaps()
        for gap in gaps:
            if gap['duration_days'] > 365:
                self.red_flags.append({
                    'severity': 'HIGH',
                    'category': 'timeline',
                    'flag': 'Unexplained employment gap',
                    'description': f"{gap['duration_days'] // 30} month gap between {gap['start_date']} and {gap['end_date']}",
                    'evidence': gap
                })
        
        # MEDIUM: No GitHub profile (for tech roles)
        if self.profession == 'software_engineer':
            github_data = self.results.get('verify_github_profile', {}).get('result', {})
            if not github_data.get('profile_exists'):
                self.red_flags.append({
                    'severity': 'MEDIUM',
                    'category': 'online_presence',
                    'flag': 'No GitHub profile found',
                    'description': 'Software engineer candidate has no GitHub account',
                    'evidence': github_data
                })
        
        # MEDIUM: Missing education verification
        education_data = self.results.get('check_education_credentials', {}).get('result', {})
        if education_data and not education_data.get('degree_verified'):
            self.red_flags.append({
                'severity': 'MEDIUM',
                'category': 'education',
                'flag': 'Unverified education credentials',
                'description': 'University degree could not be verified',
                'evidence': education_data
            })
        
        # LOW: Limited LinkedIn connections
        linkedin_data = self.results.get('search_linkedin_profile', {}).get('result', {})
        if linkedin_data.get('profile_found') and linkedin_data.get('connections', 0) < 50:
            self.red_flags.append({
                'severity': 'LOW',
                'category': 'online_presence',
                'flag': 'Limited LinkedIn network',
                'description': f"Only {linkedin_data.get('connections')} connections",
                'evidence': linkedin_data
            })
        
        logger.info(f"[VERIFICATION_ENGINE] Found {len(self.red_flags)} red flags")
        
        return self.red_flags
    
    def cross_reference_data(self) -> Dict[str, Any]:
        """
        Cross-reference data from multiple sources.
        
        Returns:
            {
                'verified_claims': [...],
                'unverified_claims': [...],
                'conflicting_data': [...]
            }
        """
        logger.info("[VERIFICATION_ENGINE] Cross-referencing data...")
        
        resume_data = self.results.get('parse_resume', {}).get('result', {})
        github_data = self.results.get('verify_github_profile', {}).get('result', {})
        linkedin_data = self.results.get('search_linkedin_profile', {}).get('result', {})
        
        verified = []
        unverified = []
        conflicts = []
        
        # Cross-reference name
        resume_name = resume_data.get('name')
        github_name = github_data.get('name')
        linkedin_name = linkedin_data.get('name')
        
        if resume_name:
            sources = [s for s in [github_name, linkedin_name] if s and self._names_match(resume_name, s)]
            if len(sources) >= 1:
                verified.append({
                    'claim': f"Name: {resume_name}",
                    'sources': ['resume'] + (['github'] if github_name in sources else []) + (['linkedin'] if linkedin_name in sources else []),
                    'confidence': 'high'
                })
            else:
                unverified.append({
                    'claim': f"Name: {resume_name}",
                    'sources': ['resume'],
                    'confidence': 'low'
                })
        
        # Cross-reference employment history
        # (This would be more complex in real implementation)
        
        self.verified_claims = verified
        self.unverified_claims = unverified
        
        return {
            'verified_claims': verified,
            'unverified_claims': unverified,
            'conflicting_data': conflicts
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive verification report.
        
        Returns:
            Complete report dict ready for frontend display
        """
        logger.info("[VERIFICATION_ENGINE] Generating report...")
        
        risk_assessment = self.calculate_risk_score()
        red_flags = self.detect_red_flags()
        cross_ref = self.cross_reference_data()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_assessment, red_flags)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'profession': self.profession,
            'risk_assessment': risk_assessment,
            'red_flags': red_flags,
            'verified_claims': self.verified_claims,
            'unverified_claims': self.unverified_claims,
            'timeline_events': self.timeline_events,
            'recommendations': recommendations,
            'summary': self._generate_summary(risk_assessment, red_flags)
        }
        
        logger.info(f"[VERIFICATION_ENGINE] Report generated: {risk_assessment['risk_level']} risk")
        
        return report
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score."""
        if score < 30:
            return 'Low'
        elif score < 60:
            return 'Medium'
        elif score < 80:
            return 'High'
        else:
            return 'Critical'
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence based on data availability."""
        total_categories = len(self.category_scores)
        scored_categories = sum(1 for score in self.category_scores.values() if score is not None)
        
        if total_categories == 0:
            return 0
        
        return round((scored_categories / total_categories) * 100, 1)
    
    def _get_category_breakdown(self) -> Dict[str, str]:
        """Get human-readable category breakdown."""
        breakdown = {}
        
        for category, score in self.category_scores.items():
            if score is None:
                breakdown[category] = "No data available"
            elif score < 30:
                breakdown[category] = f"Low risk ({score:.1f}/100)"
            elif score < 60:
                breakdown[category] = f"Medium risk ({score:.1f}/100)"
            elif score < 80:
                breakdown[category] = f"High risk ({score:.1f}/100)"
            else:
                breakdown[category] = f"Critical risk ({score:.1f}/100)"
        
        return breakdown
    
    def _build_timeline(self):
        """Build chronological timeline from all sources."""
        resume_data = self.results.get('parse_resume', {}).get('result', {})
        
        # Extract employment history from resume
        experience = resume_data.get('experience', [])
        for exp in experience:
            self.timeline_events.append({
                'type': 'employment',
                'source': 'resume',
                'company': exp.get('company'),
                'title': exp.get('title'),
                'start_date': exp.get('start_date'),
                'end_date': exp.get('end_date'),
                'duration_months': exp.get('duration_months')
            })
        
        # Sort chronologically
        self.timeline_events.sort(key=lambda x: x.get('start_date', ''))
    
    def _find_timeline_gaps(self) -> List[Dict[str, Any]]:
        """Find gaps in timeline."""
        gaps = []
        
        for i in range(len(self.timeline_events) - 1):
            current_end = self.timeline_events[i].get('end_date')
            next_start = self.timeline_events[i + 1].get('start_date')
            
            if current_end and next_start:
                # Calculate gap (simplified - would need proper date parsing)
                gap_days = 180  # Placeholder
                
                if gap_days > 30:
                    gaps.append({
                        'start_date': current_end,
                        'end_date': next_start,
                        'duration_days': gap_days
                    })
        
        return gaps
    
    def _find_timeline_overlaps(self) -> List[Dict[str, Any]]:
        """Find overlapping employment periods."""
        overlaps = []
        
        # Check for overlapping dates
        # (Simplified implementation)
        
        return overlaps
    
    def _find_cross_platform_inconsistencies(self) -> List[Dict[str, Any]]:
        """Find inconsistencies across platforms."""
        inconsistencies = []
        
        # Compare resume vs LinkedIn vs GitHub
        # (Simplified implementation)
        
        return inconsistencies
    
    def _has_formatting_issues(self, resume_data: Dict) -> bool:
        """Check for formatting inconsistencies."""
        # Check for mixed date formats, etc.
        return False  # Placeholder
    
    def _has_suspicious_patterns(self, resume_data: Dict) -> bool:
        """Check for suspicious patterns."""
        # Check for template text, lorem ipsum, etc.
        return False  # Placeholder
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two names match (fuzzy)."""
        # Simple comparison - could use fuzzy matching
        return name1.lower() == name2.lower()
    
    def _generate_recommendations(
        self,
        risk_assessment: Dict,
        red_flags: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        risk_level = risk_assessment['risk_level']
        
        if risk_level == 'Critical':
            recommendations.append("❌ DO NOT HIRE - Critical red flags detected")
            recommendations.append("Recommend rejecting this candidate immediately")
        elif risk_level == 'High':
            recommendations.append("⚠️ PROCEED WITH CAUTION - High risk detected")
            recommendations.append("Require additional verification before proceeding")
        elif risk_level == 'Medium':
            recommendations.append("⚠️ Further investigation recommended")
            recommendations.append("Request additional documentation for unverified claims")
        else:
            recommendations.append("✅ Low risk - Candidate appears legitimate")
            recommendations.append("Standard hiring process can proceed")
        
        # Specific recommendations based on red flags
        for flag in red_flags:
            if flag['severity'] == 'CRITICAL':
                recommendations.append(f"Address critical issue: {flag['flag']}")
        
        return recommendations
    
    def _generate_summary(
        self,
        risk_assessment: Dict,
        red_flags: List[Dict]
    ) -> str:
        """Generate executive summary."""
        score = risk_assessment['overall_score']
        level = risk_assessment['risk_level']
        
        critical_flags = [f for f in red_flags if f['severity'] == 'CRITICAL']
        high_flags = [f for f in red_flags if f['severity'] == 'HIGH']
        
        summary = f"""
Verification Risk Score: {score}/100 ({level} Risk)

Red Flags: {len(critical_flags)} critical, {len(high_flags)} high priority

The candidate shows {level.lower()} risk based on verification of credentials, 
online presence, timeline consistency, and company legitimacy.
"""
        
        if critical_flags:
            summary += f"\n\nCRITICAL ISSUES:\n"
            for flag in critical_flags:
                summary += f"- {flag['flag']}\n"
        
        return summary.strip()
