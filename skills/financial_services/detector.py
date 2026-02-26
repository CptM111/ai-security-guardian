"""
Financial Services Security Detector

Comprehensive security detection for financial services, banking, and fintech applications.
Covers PCI DSS 4.0.1, GLBA, SOX, and other financial regulatory requirements.

Author: AI Security Guardian Team
Version: 1.0.0
License: MIT
"""

import re
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.base_detector import BaseDetector, Detection


class FinancialServicesDetector(BaseDetector):
    """
    Detector for financial services security threats.
    
    Covers:
    - PCI DSS 4.0.1 compliance violations
    - Banking data leakage
    - Transaction security
    - Fraud patterns
    - Regulatory compliance (GLBA, SOX)
    - Money laundering detection
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config or {})
        self.name = "Financial Services Security"
        self.version = "1.0.0"
        
        # Luhn algorithm for card validation
        self._init_card_patterns()
        self._init_banking_patterns()
        self._init_fraud_patterns()
        self._init_compliance_patterns()
        
    def _init_card_patterns(self):
        """Initialize credit/debit card detection patterns"""
        
        # Card number patterns (13-19 digits)
        self.card_patterns = [
            # Visa: starts with 4
            r'\b4\d{12}(?:\d{3})?\b',
            # Mastercard: starts with 51-55 or 2221-2720
            r'\b5[1-5]\d{14}\b',
            r'\b2(?:22[1-9]|2[3-9]\d|[3-6]\d{2}|7[01]\d|720)\d{12}\b',
            # American Express: starts with 34 or 37
            r'\b3[47]\d{13}\b',
            # Discover: starts with 6011, 622126-622925, 644-649, 65
            r'\b6011\d{12}\b',
            r'\b62212[6-9]\d{10}\b',
            r'\b6229[01]\d{11}\b',
            r'\b622[2-8]\d{12}\b',
            r'\b6229[2-9]\d{11}\b',
            r'\b64[4-9]\d{13}\b',
            r'\b65\d{14}\b',
            # Generic card pattern
            r'\b\d{13,19}\b'
        ]
        
        # Card-related keywords
        self.card_keywords = [
            'card number', 'card#', 'cardnumber', 'cc#', 'ccn',
            'credit card', 'debit card', 'payment card',
            'pan', 'primary account number',
            'card holder', 'cardholder', 'card-holder',
            'expiry', 'expiration', 'exp date', 'valid thru',
            'cvv', 'cvc', 'cid', 'csc', 'cvv2', 'cvc2',
            'security code', 'verification code',
            'magnetic stripe', 'magstripe', 'track data', 'track 1', 'track 2',
            'chip data', 'emv'
        ]
        
        # CVV/CVC patterns
        self.cvv_patterns = [
            r'\b\d{3,4}\b.*\b(cvv|cvc|cid|csc)\b',
            r'\b(cvv|cvc|cid|csc)[:\s]*\d{3,4}\b',
            r'security\s*code[:\s]*\d{3,4}',
            r'verification\s*code[:\s]*\d{3,4}'
        ]
        
        # Track data patterns (magnetic stripe)
        self.track_patterns = [
            r'%[A-Z]\d{13,19}\^[^\^]+\^\d{4}',  # Track 1
            r';\d{13,19}=\d{4}',  # Track 2
            r'track\s*[12]\s*data',
            r'magnetic\s*stripe',
            r'magstripe'
        ]
        
    def _init_banking_patterns(self):
        """Initialize banking data detection patterns"""
        
        # Bank account number patterns
        self.account_patterns = [
            r'\b\d{8,17}\b.*\b(account|acct)\b',
            r'\baccount\s*(?:number|#|no)[:\s]*\d{8,17}\b',
            r'\bacct\s*(?:number|#|no)[:\s]*\d{8,17}\b',
            r'\b(account|acct)\s+\d{8,17}\b',
            r'to\s+account\s+\d{8,17}\b',
            r'from\s+account\s+\d{8,17}\b'
        ]
        
        # Routing number patterns (US: 9 digits)
        self.routing_patterns = [
            r'\b\d{9}\b.*\brouting\b',
            r'\brouting\b.*\d{9}\b',
            r'\brouting\s*(?:number|#|no)[:\s]*\d{9}\b',
            r'\baba\s*(?:number|#|no)[:\s]*\d{9}\b',
            r'\brtn[:\s]*\d{9}\b',
            r'\brouting\s+\d{9}\b',
            r'\bank\s+routing.*\d{9}\b'
        ]
        
        # SWIFT code patterns (8 or 11 characters)
        self.swift_patterns = [
            r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
            r'\bswift\s*(?:code|bic)[:\s]*[A-Z]{6}[A-Z0-9]{2,5}\b'
        ]
        
        # IBAN patterns (up to 34 alphanumeric)
        self.iban_patterns = [
            r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b',
            r'\biban[:\s]*[A-Z]{2}\d{2}[A-Z0-9]+\b'
        ]
        
        # Wire transfer keywords
        self.wire_keywords = [
            'wire transfer', 'bank transfer', 'ach transfer',
            'swift transfer', 'international transfer',
            'beneficiary', 'remittance', 'wire instruction'
        ]
        
    def _init_fraud_patterns(self):
        """Initialize fraud detection patterns"""
        
        self.fraud_patterns = {
            'social_engineering': [
                r'verify.*account.*urgently',
                r'confirm.*identity.*immediately',
                r'suspend.*account.*unless',
                r'unusual.*activity.*detected',
                r'click.*link.*verify',
                r'provide.*credentials.*restore',
                r'update.*payment.*method.*now',
                r'account.*compromised.*action.*required',
                r'account.*will.*be.*suspended.*unless'
            ],
            'phishing': [
                r'reset.*password.*link',
                r'verify.*email.*click',
                r'confirm.*transaction.*here',
                r'secure.*account.*login',
                r'unusual.*login.*attempt',
                r'verify.*identity.*document',
                r'secure.*account.*by.*logging'
            ],
            'account_takeover': [
                r'change.*email.*address',
                r'update.*phone.*number',
                r'modify.*security.*questions',
                r'disable.*two.*factor',
                r'remove.*authentication',
                r'bypass.*verification'
            ],
            'wire_fraud': [
                r'change.*wire.*instructions',
                r'update.*bank.*account',
                r'new.*routing.*number',
                r'different.*beneficiary',
                r'urgent.*wire.*transfer',
                r'modified.*payment.*details'
            ],
            'money_laundering': [
                r'split.*transaction.*smaller',
                r'multiple.*transfers.*avoid',
                r'structure.*payments.*below',
                r'cash.*transaction.*\$[\d,]+',
                r'\$[\d,]+.*cash.*transaction',
                r'cash.*\$[\d,]+',
                r'smurfing',
                r'layering.*transactions',
                r'shell.*company.*transfer',
                r'offshore.*account.*transfer',
                r'split.*\$[\d,]+.*transaction',
                r'\$[\d,]+.*transaction.*smaller.*transfers'
            ],
            'transaction_manipulation': [
                r'modify.*transaction.*amount',
                r'alter.*payment.*record',
                r'change.*transaction.*date',
                r'delete.*transaction.*history',
                r'forge.*transaction.*receipt',
                r'duplicate.*transaction'
            ],
            'insider_trading': [
                r'non.*public.*information.*trade',
                r'material.*information.*stock',
                r'insider.*knowledge.*profit',
                r'confidential.*earnings.*trade',
                r'advance.*knowledge.*merger',
                r'non.?public.*information',
                r'insider.*knowledge'
            ]
        }
        
    def _init_compliance_patterns(self):
        """Initialize regulatory compliance patterns"""
        
        # PCI DSS sensitive data
        self.pci_sensitive_data = [
            'cardholder data', 'sensitive authentication data',
            'full track data', 'cav2', 'cvc2', 'cvv2', 'cid',
            'pin', 'pin block', 'magnetic stripe'
        ]
        
        # GLBA sensitive data
        self.glba_sensitive_data = [
            'customer financial information', 'nonpublic personal information',
            'account balance', 'transaction history', 'credit report',
            'loan application', 'investment portfolio'
        ]
        
        # SOX sensitive data
        self.sox_sensitive_data = [
            'financial statement', 'earnings report', 'audit report',
            'internal control', 'material weakness', 'significant deficiency',
            'financial disclosure'
        ]
        
    def check(self, text: str, context: Dict = None) -> Detection:
        """
        Check text for financial security threats.
        
        Args:
            text: Input text to analyze
            context: Optional context information
            
        Returns:
            Detection with detection details
        """
        text_lower = text.lower()
        threats = []
        max_severity = "LOW"
        max_confidence = 0.0
        
        # Check for PCI DSS violations
        pci_threats = self._check_pci_dss(text, text_lower)
        if pci_threats:
            threats.extend(pci_threats)
            max_severity = "CRITICAL"
            max_confidence = max(max_confidence, 0.95)
            
        # Check for banking data leakage
        banking_threats = self._check_banking_data(text, text_lower)
        if banking_threats:
            threats.extend(banking_threats)
            max_severity = "CRITICAL" if max_severity != "CRITICAL" else max_severity
            max_confidence = max(max_confidence, 0.90)
            
        # Check for fraud patterns
        fraud_threats = self._check_fraud_patterns(text_lower)
        if fraud_threats:
            threats.extend(fraud_threats)
            if max_severity not in ["CRITICAL"]:
                max_severity = "HIGH"
            max_confidence = max(max_confidence, 0.85)
            
        # Check for compliance violations
        compliance_threats = self._check_compliance(text_lower)
        if compliance_threats:
            threats.extend(compliance_threats)
            if max_severity not in ["CRITICAL", "HIGH"]:
                max_severity = "MEDIUM"
            max_confidence = max(max_confidence, 0.80)
            
        detected = len(threats) > 0
        threat_type = threats[0]['type'] if threats else "None"
        details_str = f"Detected {len(threats)} threat(s): " + ", ".join([t['subtype'] for t in threats]) if threats else "No threats detected"
        
        return Detection(
            detected=detected,
            skill_name=self.name,
            threat_type=threat_type,
            confidence=max_confidence if detected else 1.0,
            severity=max_severity if detected else "NONE",
            details=details_str,
            matches=threats
        )
        
    def _check_pci_dss(self, text: str, text_lower: str) -> List[Dict]:
        """Check for PCI DSS compliance violations"""
        threats = []
        
        # Check for card numbers - match patterns that allow spaces/dashes
        card_patterns_flexible = [
            r'\b4[\s\-]?\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',  # Visa 16
            r'\b4[\s\-]?\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{3}\b',  # Visa 13
            r'\b5[1-5][\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',  # Mastercard
            r'\b3[47][\s\-]?\d{2}[\s\-]?\d{6}[\s\-]?\d{5}\b',  # Amex
            r'\b6011[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',  # Discover
            r'\b\d{13,19}\b'  # Generic
        ]
        
        for pattern in card_patterns_flexible:
            matches = re.finditer(pattern, text)
            for match in matches:
                card_num_raw = match.group()
                # Normalize by removing spaces and dashes
                card_num = card_num_raw.replace(' ', '').replace('-', '')
                if len(card_num) >= 13 and len(card_num) <= 19 and self._validate_luhn(card_num):
                    threats.append({
                        'type': 'PCI DSS Violation',
                        'subtype': 'Primary Account Number (PAN)',
                        'pattern': card_num[:6] + '****' + card_num[-4:],
                        'severity': 'CRITICAL',
                        'confidence': 0.98,
                        'framework': 'PCI DSS',
                        'pci_requirement': 'Requirement 3',
                        'data_type': 'Cardholder Data',
                        'description': 'Primary Account Number detected in prompt'
                    })
                    break
                    
        # Check for CVV/CVC codes
        for pattern in self.cvv_patterns:
            if re.search(pattern, text_lower):
                threats.append({
                    'type': 'PCI DSS Violation',
                    'subtype': 'CVV/CVC Code',
                    'pattern': pattern,
                    'severity': 'CRITICAL',
                    'confidence': 0.95,
                    'framework': 'PCI DSS',
                    'pci_requirement': 'Requirement 3.2',
                    'data_type': 'Sensitive Authentication Data',
                    'description': 'CVV/CVC security code detected'
                })
                break
                
        # Check for track data
        for pattern in self.track_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append({
                    'type': 'PCI DSS Violation',
                    'subtype': 'Magnetic Stripe Data',
                    'pattern': pattern,
                    'severity': 'CRITICAL',
                    'confidence': 0.97,
                    'framework': 'PCI DSS',
                    'pci_requirement': 'Requirement 3.2',
                    'data_type': 'Sensitive Authentication Data',
                    'description': 'Magnetic stripe/track data detected'
                })
                break
                
        # Check for card-related keywords with numbers
        for keyword in self.card_keywords:
            if keyword in text_lower and re.search(r'\d{3,}', text):
                threats.append({
                    'type': 'PCI DSS Violation',
                    'subtype': 'Cardholder Data Context',
                    'pattern': keyword,
                    'severity': 'HIGH',
                    'confidence': 0.85,
                    'framework': 'PCI DSS',
                    'pci_requirement': 'Requirement 3',
                    'data_type': 'Cardholder Data Environment',
                    'description': f'Card-related keyword "{keyword}" with numeric data'
                })
                break
                
        return threats
        
    def _check_banking_data(self, text: str, text_lower: str) -> List[Dict]:
        """Check for banking data leakage"""
        threats = []
        
        # Check for account numbers
        for pattern in self.account_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                threats.append({
                    'type': 'Banking Data Leakage',
                    'subtype': 'Bank Account Number',
                    'pattern': pattern,
                    'severity': 'CRITICAL',
                    'confidence': 0.90,
                    'framework': 'GLBA',
                    'data_type': 'Customer Financial Information',
                    'description': 'Bank account number detected'
                })
                break
                
        # Check for routing numbers
        for pattern in self.routing_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                threats.append({
                    'type': 'Banking Data Leakage',
                    'subtype': 'Routing Number',
                    'pattern': pattern,
                    'severity': 'CRITICAL',
                    'confidence': 0.92,
                    'framework': 'GLBA',
                    'data_type': 'Bank Routing Information',
                    'description': 'Bank routing number detected'
                })
                break
                
        # Check for SWIFT codes
        for pattern in self.swift_patterns:
            if re.search(pattern, text):
                threats.append({
                    'type': 'Banking Data Leakage',
                    'subtype': 'SWIFT Code',
                    'pattern': pattern,
                    'severity': 'HIGH',
                    'confidence': 0.88,
                    'framework': 'GLBA',
                    'data_type': 'International Banking Code',
                    'description': 'SWIFT/BIC code detected'
                })
                break
                
        # Check for IBAN
        for pattern in self.iban_patterns:
            if re.search(pattern, text):
                threats.append({
                    'type': 'Banking Data Leakage',
                    'subtype': 'IBAN',
                    'pattern': pattern,
                    'severity': 'HIGH',
                    'confidence': 0.87,
                    'framework': 'GLBA',
                    'data_type': 'International Bank Account Number',
                    'description': 'IBAN detected'
                })
                break
                
        # Check for wire transfer context
        for keyword in self.wire_keywords:
            if keyword in text_lower and re.search(r'\d{8,}', text):
                threats.append({
                    'type': 'Banking Data Leakage',
                    'subtype': 'Wire Transfer Information',
                    'pattern': keyword,
                    'severity': 'HIGH',
                    'confidence': 0.82,
                    'framework': 'GLBA',
                    'data_type': 'Wire Transfer Details',
                    'description': f'Wire transfer keyword "{keyword}" with financial data'
                })
                break
                
        return threats
        
    def _check_fraud_patterns(self, text_lower: str) -> List[Dict]:
        """Check for fraud patterns"""
        threats = []
        
        for fraud_type, patterns in self.fraud_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    severity = "CRITICAL" if fraud_type in ['wire_fraud', 'money_laundering'] else "HIGH"
                    confidence = 0.85 if fraud_type in ['wire_fraud', 'money_laundering'] else 0.80
                    
                    threats.append({
                        'type': 'Fraud Pattern',
                        'subtype': fraud_type.replace('_', ' ').title(),
                        'pattern': pattern,
                        'severity': severity,
                        'confidence': confidence,
                        'framework': 'AML/KYC' if fraud_type == 'money_laundering' else 'Fraud Detection',
                        'data_type': 'Suspicious Activity',
                        'description': f'{fraud_type.replace("_", " ").title()} pattern detected'
                    })
                    break
                    
        return threats
        
    def _check_compliance(self, text_lower: str) -> List[Dict]:
        """Check for regulatory compliance violations"""
        threats = []
        
        # Check PCI DSS sensitive data keywords (only if not educational context)
        educational_keywords = ['what', 'how', 'explain', 'best practice', 'implement', 'design', 'should']
        is_educational = any(kw in text_lower for kw in educational_keywords)
        
        if not is_educational:
            for keyword in self.pci_sensitive_data:
                if keyword in text_lower:
                    threats.append({
                    'type': 'Compliance Violation',
                    'subtype': 'PCI DSS Sensitive Data',
                    'pattern': keyword,
                    'severity': 'MEDIUM',
                    'confidence': 0.75,
                    'framework': 'PCI DSS',
                    'data_type': 'Sensitive Data Reference',
                    'description': f'PCI DSS sensitive data keyword: {keyword}'
                    })
                    break
                
        # Check GLBA sensitive data keywords (only if not educational context)
        if not is_educational:
            for keyword in self.glba_sensitive_data:
                if keyword in text_lower:
                    threats.append({
                    'type': 'Compliance Violation',
                    'subtype': 'GLBA Sensitive Data',
                    'pattern': keyword,
                    'severity': 'MEDIUM',
                    'confidence': 0.72,
                    'framework': 'GLBA',
                    'data_type': 'Customer Financial Information',
                    'description': f'GLBA sensitive data keyword: {keyword}'
                    })
                    break
                
        # Check SOX sensitive data keywords (only if not educational context)
        if not is_educational:
            for keyword in self.sox_sensitive_data:
                if keyword in text_lower:
                    threats.append({
                    'type': 'Compliance Violation',
                    'subtype': 'SOX Sensitive Data',
                    'pattern': keyword,
                    'severity': 'MEDIUM',
                    'confidence': 0.70,
                    'framework': 'SOX',
                    'data_type': 'Financial Reporting Data',
                    'description': f'SOX sensitive data keyword: {keyword}'
                    })
                    break
                
        return threats
        
    def _validate_luhn(self, card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm.
        
        Args:
            card_number: Card number string
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = [int(d) for d in card_number if d.isdigit()]
        
        if len(digits) < 13 or len(digits) > 19:
            return False
            
        # Luhn algorithm
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
            
        return checksum % 10 == 0


# Export detector class
__all__ = ['FinancialServicesDetector']
