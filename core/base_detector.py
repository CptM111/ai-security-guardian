"""
AI Security Guardian - Base Detector Interface
Version: 1.2.0

Base class for all skill detectors to ensure consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Detection:
    """Standard detection result"""
    detected: bool
    skill_name: str
    threat_type: str
    confidence: float
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, NONE
    details: str = ""
    matches: list = None
    
    def __post_init__(self):
        if self.matches is None:
            self.matches = []


class BaseDetector(ABC):
    """Base class for all skill detectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detection_threshold = config.get('detection_threshold', 0.7)
    
    @abstractmethod
    def check(self, text: str, context: Dict[str, Any]) -> Detection:
        """
        Main detection method that all skills must implement.
        
        Args:
            text: The input text to analyze
            context: Additional context (API endpoint, user info, etc.)
        
        Returns:
            Detection object with results
        """
        pass
    
    def is_above_threshold(self, confidence: float) -> bool:
        """Check if confidence is above detection threshold"""
        return confidence >= self.detection_threshold
