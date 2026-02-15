"""
Cryptocurrency Security Skill Detector
Version: 1.1.0
Date: February 15, 2026

Wrapper around the enhanced crypto detector to match Skills interface.
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
skill_dir = Path(__file__).parent
project_root = skill_dir.parent.parent
sys.path.insert(0, str(project_root))

from core.base_detector import BaseDetector, Detection
from components.crypto_detector_v2 import get_enhanced_crypto_detector


class CryptocurrencyDetector(BaseDetector):
    """Cryptocurrency security detector for Skills framework"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # Get the enhanced crypto detector
        self.crypto_detector = get_enhanced_crypto_detector()
    
    def check(self, text: str, context: dict) -> Detection:
        """
        Check text for cryptocurrency security threats.
        
        Args:
            text: Input text to analyze
            context: Additional context (API endpoint, user info, etc.)
        
        Returns:
            Detection object with results
        """
        # Use the enhanced crypto detector
        result = self.crypto_detector.is_safe(text)
        
        # Convert to Skills Detection format
        if result['is_safe']:
            return Detection(
                detected=False,
                skill_name='cryptocurrency',
                threat_type='none',
                confidence=0.0,
                severity='NONE',
                details='No cryptocurrency threats detected'
            )
        else:
            # Extract threat information
            threat_type = result.get('reason', 'unknown_crypto_threat')
            confidence = result.get('confidence', 0.9)
            severity = result.get('severity', 'HIGH')
            details = result.get('details', result.get('reason', ''))
            
            # Extract matches if available
            matches = []
            if 'matches' in result:
                matches = result['matches']
            
            return Detection(
                detected=True,
                skill_name='cryptocurrency',
                threat_type=threat_type,
                confidence=confidence,
                severity=severity,
                details=details,
                matches=matches
            )
