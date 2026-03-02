"""
AI Security Guardian - Skills Manager
Version: 1.4.1
Date: March 2, 2026

The Skills Manager orchestrates modular security capabilities through:
- Auto-detection of relevant skills based on context
- Dynamic loading and unloading of skills
- Version management and auto-updates
- Performance optimization through caching
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import importlib.util

from core.rejection_log import (
    RejectionLogBuilder,
    RejectionEntry,
    get_store as get_rejection_store,
)

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Skill metadata from skill.yaml"""
    name: str
    display_name: str
    version: str
    author: str
    license: str
    description: str
    triggers: Dict
    dependencies: Dict
    config: Dict
    capabilities: List[str]
    performance: Dict
    threats: List[str]
    tests: Dict


@dataclass
class Detection:
    """Detection result from a skill"""
    detected: bool
    skill_name: str
    threat_type: str
    confidence: float
    severity: str
    details: str = ""
    matches: List[str] = None
    
    def __post_init__(self):
        if self.matches is None:
            self.matches = []


@dataclass
class SecurityResult:
    """Aggregated security check result"""
    is_safe: bool
    activated_skills: List[str]
    detections: List[Detection]
    confidence: float
    severity: str
    reason: str
    rejection_logs: List[RejectionEntry] = None

    def __post_init__(self):
        if self.rejection_logs is None:
            self.rejection_logs = []
    
    def to_dict(self) -> Dict:
        result = {
            "is_safe": self.is_safe,
            "activated_skills": self.activated_skills,
            "detections": [
                {
                    "skill": d.skill_name,
                    "threat": d.threat_type,
                    "confidence": d.confidence,
                    "severity": d.severity,
                    "details": d.details
                }
                for d in self.detections
            ],
            "confidence": self.confidence,
            "severity": self.severity,
            "reason": self.reason,
        }
        if self.rejection_logs:
            result["rejection_logs"] = [log.to_dict() for log in self.rejection_logs]
            result["agent_hints"] = [log.to_agent_hint() for log in self.rejection_logs]
        return result


class Skill:
    """Represents a loaded security skill"""
    
    def __init__(self, path: Path):
        self.path = path
        self.metadata = self._load_metadata()
        self._detector = None  # Lazy load
        self.last_used = None
        self.activation_count = 0
    
    def _load_metadata(self) -> SkillMetadata:
        """Load skill metadata from skill.yaml"""
        metadata_path = self.path / "skill.yaml"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"skill.yaml not found in {self.path}")
        
        with open(metadata_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return SkillMetadata(
            name=data.get('name', data.get('id', 'unknown')),
            display_name=data.get('display_name', data.get('name', 'Unknown Skill')),
            version=data['version'],
            author=data['author'],
            license=data['license'],
            description=data['description'],
            triggers=data.get('triggers', {}),
            dependencies=data.get('dependencies', {}),
            config=data.get('config', {}),
            capabilities=data.get('capabilities', []),
            performance=data.get('performance', {}),
            threats=data.get('threats', []),
            tests=data.get('tests', {})
        )
    
    @property
    def detector(self):
        """Lazy load detector module"""
        if self._detector is None:
            self._detector = self._load_detector()
        return self._detector
    
    def _load_detector(self):
        """Dynamically import detector module"""
        detector_path = self.path / "detector.py"
        
        if not detector_path.exists():
            raise FileNotFoundError(f"detector.py not found in {self.path}")
        
        # Import module dynamically
        spec = importlib.util.spec_from_file_location(
            f"skills.{self.metadata.name}.detector",
            detector_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get detector class — try several naming conventions
        # Use the raw skill directory name (from path), not the display name
        # e.g. financial_services -> FinancialServicesDetector
        #      web3 -> Web3Detector
        dir_name = self.path.name  # e.g. 'financial_services', 'web3'
        candidates = [
            "".join(part.capitalize() for part in dir_name.split("_")) + "Detector",
            dir_name.capitalize() + "Detector",
        ]
        detector_class = None
        for class_name in candidates:
            if hasattr(module, class_name):
                detector_class = getattr(module, class_name)
                break
        if detector_class is None:
            raise AttributeError(
                f"Could not find detector class in {detector_path}. "
                f"Tried: {candidates}"
            )
        
        # Instantiate detector with config
        return detector_class(self.metadata.config)
    
    def should_activate(self, text: str, context: Dict) -> bool:
        """Determine if this skill should be activated"""
        triggers = self.metadata.triggers
        
        # Check keywords
        keywords = triggers.get('keywords', [])
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in keywords):
            return True
        
        # Check patterns
        patterns = triggers.get('patterns', [])
        for pattern in patterns:
            if not isinstance(pattern, str):
                continue
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            except re.error:
                continue
        
        # Check API endpoint
        if 'api_endpoint' in context:
            endpoint_patterns = triggers.get('api_endpoints', [])
            for pattern in endpoint_patterns:
                # Convert glob pattern to regex
                regex_pattern = pattern.replace('*', '.*')
                if re.match(regex_pattern, context['api_endpoint']):
                    return True
        
        return False
    
    def check(self, text: str, context: Dict) -> Detection:
        """Execute skill detection"""
        self.last_used = datetime.now()
        self.activation_count += 1
        
        try:
            # Call detector's check method
            result = self.detector.check(text, context)
            
            # Ensure result is a Detection object
            if not isinstance(result, Detection):
                if isinstance(result, dict):
                    result = Detection(
                        detected=result.get('detected', False),
                        skill_name=self.path.name,
                        threat_type=result.get('threat_type', 'unknown'),
                        confidence=result.get('confidence', 0.0),
                        severity=result.get('severity', 'UNKNOWN'),
                        details=result.get('details', ''),
                        matches=result.get('matches', [])
                    )
                else:
                    result.skill_name = self.path.name
            else:
                result.skill_name = self.path.name
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing skill {self.metadata.name}: {e}")
            return Detection(
                detected=False,
                skill_name=self.metadata.name,
                threat_type="error",
                confidence=0.0,
                severity="NONE",
                details=f"Skill execution error: {str(e)}"
            )


class SkillsManager:
    """Manages all security skills"""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir is None:
            # Default to skills/ directory relative to this file
            skills_dir = Path(__file__).parent.parent / "skills"
        
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self.enabled_skills: Set[str] = set()
        self.auto_detect = True
        
        # Load all available skills
        self.load_all_skills()
    
    def load_all_skills(self):
        """Load all skills from skills directory"""
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return
        
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and (skill_path / "skill.yaml").exists():
                try:
                    skill = Skill(skill_path)
                    # Key by directory name for consistent resolution
                    self.skills[skill_path.name] = skill
                    logger.info(f"Loaded skill: {skill.metadata.display_name} v{skill.metadata.version}")
                except Exception as e:
                    logger.error(f"Failed to load skill from {skill_path}: {e}")
    
    def enable_skill(self, skill_name: str):
        """Manually enable a skill"""
        if skill_name in self.skills:
            self.enabled_skills.add(skill_name)
            logger.info(f"Enabled skill: {skill_name}")
        else:
            logger.warning(f"Skill not found: {skill_name}")
    
    def disable_skill(self, skill_name: str):
        """Manually disable a skill"""
        self.enabled_skills.discard(skill_name)
        logger.info(f"Disabled skill: {skill_name}")
    
    def set_auto_detect(self, enabled: bool):
        """Enable or disable auto-detection"""
        self.auto_detect = enabled
    
    def auto_detect_skills(self, text: str, context: Dict) -> List[str]:
        """Auto-detect which skills should be activated"""
        if not self.auto_detect:
            return list(self.enabled_skills)
        
        activated = set(self.enabled_skills)  # Start with manually enabled
        
        for skill_name, skill in self.skills.items():
            if skill.should_activate(text, context):
                activated.add(skill_name)
        
        return list(activated)
    
    def check(self, text: str, context: Optional[Dict] = None) -> SecurityResult:
        """Execute security check with relevant skills"""
        if context is None:
            context = {}
        
        # Auto-detect skills
        active_skill_names = self.auto_detect_skills(text, context)
        
        if not active_skill_names:
            # No skills activated
            return SecurityResult(
                is_safe=True,
                activated_skills=[],
                detections=[],
                confidence=1.0,
                severity="NONE",
                reason="No security skills activated"
            )
        
        # Execute each active skill
        detections = []
        for skill_name in active_skill_names:
            skill = self.skills.get(skill_name)
            if skill:
                detection = skill.check(text, context)
                if detection.detected:
                    detections.append(detection)
        
        # Build rejection logs for all detections
        rejection_logs = []
        store = get_rejection_store()
        for detection in detections:
            skill = self.skills.get(detection.skill_name)
            skill_version = skill.metadata.version if skill else "unknown"
            log_entry = RejectionLogBuilder.from_detection(
                detection, input_text=text, skill_version=skill_version
            )
            store.append(log_entry)
            rejection_logs.append(log_entry)
        
        # Aggregate results
        return self._aggregate_results(active_skill_names, detections, rejection_logs)
    
    def _aggregate_results(self, activated_skills: List[str], detections: List[Detection], rejection_logs: List[RejectionEntry] = None) -> SecurityResult:
        """Aggregate detection results from multiple skills"""
        if not detections:
            return SecurityResult(
                is_safe=True,
                activated_skills=activated_skills,
                detections=[],
                confidence=1.0,
                severity="NONE",
                reason="No threats detected"
            )
        
        # Find highest severity
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
        max_severity = max(detections, key=lambda d: severity_order.get(d.severity, 0)).severity
        
        # Calculate overall confidence (max confidence among detections)
        max_confidence = max(d.confidence for d in detections)
        
        # Build reason
        threat_types = [d.threat_type for d in detections]
        reason = f"Detected {len(detections)} threat(s): {', '.join(set(threat_types))}"
        
        return SecurityResult(
            is_safe=False,
            activated_skills=activated_skills,
            detections=detections,
            confidence=max_confidence,
            severity=max_severity,
            reason=reason,
            rejection_logs=rejection_logs or []
        )
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get information about a skill"""
        skill = self.skills.get(skill_name)
        if not skill:
            return None
        
        return {
            "name": skill.metadata.name,
            "display_name": skill.metadata.display_name,
            "version": skill.metadata.version,
            "author": skill.metadata.author,
            "description": skill.metadata.description,
            "capabilities": skill.metadata.capabilities,
            "threats": skill.metadata.threats,
            "activation_count": skill.activation_count,
            "last_used": skill.last_used.isoformat() if skill.last_used else None
        }
    
    def list_skills(self) -> List[Dict]:
        """List all available skills"""
        return [self.get_skill_info(name) for name in self.skills.keys()]


# Singleton instance
_skills_manager = None

def get_skills_manager() -> SkillsManager:
    """Get singleton instance of SkillsManager"""
    global _skills_manager
    if _skills_manager is None:
        _skills_manager = SkillsManager()
    return _skills_manager
