"""
Cryptocurrency Security Detector
Version: 1.1.0
Date: February 15, 2026

This module detects and redacts sensitive cryptocurrency data including:
- Private keys (all formats)
- Seed phrases (BIP39)
- Exchange API keys (Binance, Coinbase, OKX, MEXC, Kraken)
- Wallet addresses
- Smart contract vulnerabilities
- Phishing/fraud patterns
"""

import re
import os
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

@dataclass
class CryptoDetection:
    """Result of cryptocurrency data detection"""
    detected: bool
    data_type: str
    confidence: float
    redacted_text: str
    original_matches: List[str]
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    
class CryptoDetector:
    """Detects sensitive cryptocurrency data in text"""
    
    def __init__(self):
        self.bip39_words = self._load_bip39_wordlist()
        
    def _load_bip39_wordlist(self) -> Set[str]:
        """Load BIP39 English wordlist"""
        wordlist_path = os.path.join(os.path.dirname(__file__), 'bip39_english.txt')
        try:
            with open(wordlist_path, 'r') as f:
                return set(word.strip().lower() for word in f.readlines())
        except:
            # Fallback to common words if file not found
            return set(['abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb'])
    
    # ========================================================================
    # PRIVATE KEY DETECTION
    # ========================================================================
    
    def detect_private_keys(self, text: str) -> CryptoDetection:
        """Detect cryptocurrency private keys in various formats"""
        matches = []
        
        # Ethereum/EVM private key (64 hex chars, with or without 0x prefix)
        eth_pattern = r'(?:0x)?[0-9a-fA-F]{64}\b'
        eth_matches = re.findall(eth_pattern, text)
        
        # Filter out non-private-key hex strings (need context)
        for match in eth_matches:
            # Check if it's in a private key context
            context = text[max(0, text.find(match)-50):text.find(match)+len(match)+50].lower()
            if any(keyword in context for keyword in ['private', 'key', 'secret', 'priv', 'pk']):
                matches.append(('ETH_PRIVATE_KEY', match))
        
        # Bitcoin WIF format (starts with 5, K, or L, 51 base58 chars)
        wif_pattern = r'\b[5KL][1-9A-HJ-NP-Za-km-z]{51}\b'
        wif_matches = re.findall(wif_pattern, text)
        for match in wif_matches:
            matches.append(('BTC_WIF_PRIVATE_KEY', match))
        
        # Solana private key (base58, ~88 chars)
        # Note: Hard to distinguish from other base58 data without context
        
        if matches:
            redacted_text = text
            for key_type, key_value in matches:
                redacted_text = redacted_text.replace(key_value, f'[REDACTED_{key_type}]')
            
            return CryptoDetection(
                detected=True,
                data_type='private_key',
                confidence=0.95,
                redacted_text=redacted_text,
                original_matches=[m[1] for m in matches],
                severity='CRITICAL'
            )
        
        return CryptoDetection(
            detected=False,
            data_type='private_key',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # SEED PHRASE DETECTION (BIP39)
    # ========================================================================
    
    def detect_seed_phrases(self, text: str) -> CryptoDetection:
        """Detect BIP39 seed phrases (12 or 24 words)"""
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Check for sequences of BIP39 words
        matches = []
        
        for i in range(len(words)):
            # Check for 12-word phrase
            if i + 12 <= len(words):
                sequence = words[i:i+12]
                if all(word in self.bip39_words for word in sequence):
                    matches.append((' '.join(sequence), 12))
            
            # Check for 24-word phrase
            if i + 24 <= len(words):
                sequence = words[i:i+24]
                if all(word in self.bip39_words for word in sequence):
                    matches.append((' '.join(sequence), 24))
        
        if matches:
            redacted_text = text
            for phrase, word_count in matches:
                redacted_text = redacted_text.replace(phrase, f'[REDACTED_SEED_PHRASE_{word_count}_WORDS]')
            
            return CryptoDetection(
                detected=True,
                data_type='seed_phrase',
                confidence=0.98,
                redacted_text=redacted_text,
                original_matches=[m[0] for m in matches],
                severity='CRITICAL'
            )
        
        return CryptoDetection(
            detected=False,
            data_type='seed_phrase',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # EXCHANGE API KEY DETECTION
    # ========================================================================
    
    def detect_exchange_api_keys(self, text: str) -> CryptoDetection:
        """Detect cryptocurrency exchange API keys"""
        matches = []
        
        # Binance API Key (64 alphanumeric)
        binance_pattern = r'\b[A-Za-z0-9]{64}\b'
        binance_matches = re.findall(binance_pattern, text)
        for match in binance_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+len(match)+100].lower()
            if 'binance' in context or 'api' in context:
                matches.append(('BINANCE_API_KEY', match))
        
        # Coinbase API Key (32 hex chars)
        coinbase_key_pattern = r'\b[a-f0-9]{32}\b'
        coinbase_matches = re.findall(coinbase_key_pattern, text)
        for match in coinbase_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+len(match)+100].lower()
            if 'coinbase' in context or 'cb-access' in context:
                matches.append(('COINBASE_API_KEY', match))
        
        # Coinbase API Secret (88 base64 chars)
        coinbase_secret_pattern = r'\b[A-Za-z0-9+/]{88}={0,2}\b'
        coinbase_secret_matches = re.findall(coinbase_secret_pattern, text)
        for match in coinbase_secret_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+len(match)+100].lower()
            if 'coinbase' in context or 'secret' in context:
                matches.append(('COINBASE_API_SECRET', match))
        
        # OKX API Key (UUID format)
        okx_pattern = r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b'
        okx_matches = re.findall(okx_pattern, text)
        for match in okx_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+100].lower()
            if 'okx' in context or 'api' in context:
                matches.append(('OKX_API_KEY', match))
        
        # OKX Secret Key (32 uppercase alphanumeric)
        okx_secret_pattern = r'\b[A-Z0-9]{32}\b'
        okx_secret_matches = re.findall(okx_secret_pattern, text)
        for match in okx_secret_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+100].lower()
            if 'okx' in context and 'secret' in context:
                matches.append(('OKX_SECRET_KEY', match))
        
        # MEXC Access Key (starts with mx0)
        mexc_pattern = r'\bmx0[A-Za-z0-9]{32}\b'
        mexc_matches = re.findall(mexc_pattern, text)
        for match in mexc_matches:
            matches.append(('MEXC_ACCESS_KEY', match))
        
        # MEXC Secret Key (64 hex chars)
        mexc_secret_pattern = r'\b[a-f0-9]{64}\b'
        mexc_secret_matches = re.findall(mexc_secret_pattern, text)
        for match in mexc_secret_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+100].lower()
            if 'mexc' in context and 'secret' in context:
                matches.append(('MEXC_SECRET_KEY', match))
        
        # Kraken API Key (base64, ~56 chars ending with ==)
        kraken_pattern = r'\b[A-Za-z0-9+/]{56}==\b'
        kraken_matches = re.findall(kraken_pattern, text)
        for match in kraken_matches:
            context = text[max(0, text.find(match)-100):text.find(match)+100].lower()
            if 'kraken' in context:
                matches.append(('KRAKEN_API_KEY', match))
        
        if matches:
            redacted_text = text
            for key_type, key_value in matches:
                # Redact but show first 4 and last 4 chars for debugging
                if len(key_value) > 8:
                    masked = key_value[:4] + '...' + key_value[-4:]
                else:
                    masked = '***'
                redacted_text = redacted_text.replace(key_value, f'[REDACTED_{key_type}:{masked}]')
            
            return CryptoDetection(
                detected=True,
                data_type='exchange_api_key',
                confidence=0.90,
                redacted_text=redacted_text,
                original_matches=[m[1] for m in matches],
                severity='CRITICAL'
            )
        
        return CryptoDetection(
            detected=False,
            data_type='exchange_api_key',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # WALLET ADDRESS DETECTION
    # ========================================================================
    
    def detect_wallet_addresses(self, text: str) -> CryptoDetection:
        """Detect cryptocurrency wallet addresses"""
        matches = []
        
        # Ethereum address (0x + 40 hex chars)
        eth_pattern = r'\b0x[0-9a-fA-F]{40}\b'
        eth_matches = re.findall(eth_pattern, text)
        for match in eth_matches:
            matches.append(('ETH_ADDRESS', match))
        
        # Bitcoin Legacy (starts with 1, 26-35 base58 chars)
        btc_legacy_pattern = r'\b1[1-9A-HJ-NP-Za-km-z]{25,34}\b'
        btc_legacy_matches = re.findall(btc_legacy_pattern, text)
        for match in btc_legacy_matches:
            matches.append(('BTC_LEGACY_ADDRESS', match))
        
        # Bitcoin SegWit (starts with 3, 26-35 base58 chars)
        btc_segwit_pattern = r'\b3[1-9A-HJ-NP-Za-km-z]{25,34}\b'
        btc_segwit_matches = re.findall(btc_segwit_pattern, text)
        for match in btc_segwit_matches:
            matches.append(('BTC_SEGWIT_ADDRESS', match))
        
        # Bitcoin Bech32 (starts with bc1, 39-59 chars)
        btc_bech32_pattern = r'\bbc1[a-z0-9]{39,59}\b'
        btc_bech32_matches = re.findall(btc_bech32_pattern, text)
        for match in btc_bech32_matches:
            matches.append(('BTC_BECH32_ADDRESS', match))
        
        # Solana address (base58, 32-44 chars)
        # Note: This is approximate and may have false positives
        sol_pattern = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
        sol_matches = re.findall(sol_pattern, text)
        for match in sol_matches:
            # Only flag if in Solana context
            context = text[max(0, text.find(match)-50):text.find(match)+50].lower()
            if 'solana' in context or 'sol' in context:
                matches.append(('SOLANA_ADDRESS', match))
        
        # Note: Wallet addresses are not always sensitive, so we don't redact by default
        # But we detect them for context awareness
        
        if matches:
            return CryptoDetection(
                detected=True,
                data_type='wallet_address',
                confidence=0.85,
                redacted_text=text,  # Don't redact addresses by default
                original_matches=[m[1] for m in matches],
                severity='LOW'  # Addresses are public, not sensitive
            )
        
        return CryptoDetection(
            detected=False,
            data_type='wallet_address',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # SMART CONTRACT VULNERABILITY DETECTION
    # ========================================================================
    
    def detect_malicious_contract_patterns(self, text: str) -> CryptoDetection:
        """Detect malicious smart contract patterns in code"""
        malicious_patterns = []
        
        # Backdoor patterns
        backdoor_keywords = [
            r'onlyOwner.*selfdestruct',
            r'function\s+emergencyWithdraw',
            r'function\s+backdoor',
            r'function\s+drain',
            r'hidden.*owner',
            r'_mint.*unlimited',
        ]
        
        for pattern in backdoor_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                malicious_patterns.append(('BACKDOOR', pattern))
        
        # Reentrancy patterns
        reentrancy_keywords = [
            r'\.call\{value:',
            r'\.transfer.*before.*balance',
            r'external.*call.*state.*update',
        ]
        
        for pattern in reentrancy_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                # Check if there's a reentrancy guard
                if 'nonReentrant' not in text and 'ReentrancyGuard' not in text:
                    malicious_patterns.append(('REENTRANCY_RISK', pattern))
        
        # Honeypot/Rug pull patterns
        scam_keywords = [
            r'canSell\s*=\s*false',
            r'tradingEnabled\s*=\s*false',
            r'function\s+enableTrading.*onlyOwner',
            r'maxSellAmount\s*=\s*0',
            r'sellTax\s*=\s*100',
        ]
        
        for pattern in scam_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                malicious_patterns.append(('SCAM_PATTERN', pattern))
        
        # Wallet drainer patterns
        drainer_keywords = [
            r'transferFrom.*approve',
            r'setApprovalForAll.*true',
            r'permit.*signature',
            r'drain.*wallet',
        ]
        
        for pattern in drainer_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                malicious_patterns.append(('WALLET_DRAINER', pattern))
        
        if malicious_patterns:
            return CryptoDetection(
                detected=True,
                data_type='malicious_contract',
                confidence=0.80,
                redacted_text=text,
                original_matches=[p[0] for p in malicious_patterns],
                severity='CRITICAL'
            )
        
        return CryptoDetection(
            detected=False,
            data_type='malicious_contract',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # PHISHING/FRAUD PATTERN DETECTION
    # ========================================================================
    
    def detect_phishing_patterns(self, text: str) -> CryptoDetection:
        """Detect cryptocurrency phishing and fraud patterns"""
        phishing_patterns = []
        
        # Fake website/interface creation
        fake_interface_keywords = [
            r'create.*fake.*(metamask|uniswap|binance|coinbase)',
            r'fake.*(wallet|exchange|login).*page',
            r'phishing.*(site|page|email)',
            r'clone.*(dapp|interface)',
            r'impersonate.*(wallet|exchange)',
        ]
        
        for pattern in fake_interface_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                phishing_patterns.append(('FAKE_INTERFACE', pattern))
        
        # Seed phrase phishing
        seed_phishing_keywords = [
            r'(ask|request|verify|confirm).*seed phrase',
            r'enter.*mnemonic',
            r'provide.*recovery.*phrase',
            r'wallet.*recovery.*page',
        ]
        
        for pattern in seed_phishing_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                phishing_patterns.append(('SEED_PHISHING', pattern))
        
        # Fake airdrop/giveaway
        airdrop_scam_keywords = [
            r'fake.*airdrop',
            r'free.*token.*claim',
            r'connect.*wallet.*receive',
            r'approve.*unlimited.*airdrop',
        ]
        
        for pattern in airdrop_scam_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                phishing_patterns.append(('FAKE_AIRDROP', pattern))
        
        # Social engineering
        social_eng_keywords = [
            r'convince.*approve.*unlimited',
            r'trick.*into.*signing',
            r'manipulate.*user.*transaction',
        ]
        
        for pattern in social_eng_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                phishing_patterns.append(('SOCIAL_ENGINEERING', pattern))
        
        if phishing_patterns:
            return CryptoDetection(
                detected=True,
                data_type='phishing',
                confidence=0.85,
                redacted_text=text,
                original_matches=[p[0] for p in phishing_patterns],
                severity='CRITICAL'
            )
        
        return CryptoDetection(
            detected=False,
            data_type='phishing',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # EXPLOITATION/ATTACK PATTERN DETECTION
    # ========================================================================
    
    def detect_exploitation_patterns(self, text: str) -> CryptoDetection:
        """Detect cryptocurrency exploitation and attack patterns"""
        exploit_patterns = []
        
        # Direct exploitation requests
        exploit_keywords = [
            r'how to (exploit|hack|steal|drain)',
            r'bypass.*(kyc|aml|2fa|security)',
            r'(wash trading|pump and dump|front.?run)',
            r'manipulate.*(price|market|oracle)',
            r'double.?spend',
            r'51%.?attack',
        ]
        
        for pattern in exploit_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                exploit_patterns.append(('EXPLOITATION_REQUEST', pattern))
        
        # Fraud/scam planning
        fraud_keywords = [
            r'rug pull.*contract',
            r'honeypot.*token',
            r'fake.*(identity|document|kyc)',
            r'deepfake.*(verification|kyc)',
            r'synthetic.*identity',
            r'launder.*(money|funds)',
        ]
        
        for pattern in fraud_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                exploit_patterns.append(('FRAUD_PLANNING', pattern))
        
        # Market manipulation
        manipulation_keywords = [
            r'spoof.*(order|volume)',
            r'fake.*trading.*volume',
            r'coordinate.*(pump|dump)',
            r'insider.*trading',
        ]
        
        for pattern in manipulation_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                exploit_patterns.append(('MARKET_MANIPULATION', pattern))
        
        if exploit_patterns:
            return CryptoDetection(
                detected=True,
                data_type='exploitation',
                confidence=0.90,
                redacted_text=text,
                original_matches=[p[0] for p in exploit_patterns],
                severity='CRITICAL'
            )
        
        return CryptoDetection(
            detected=False,
            data_type='exploitation',
            confidence=0.0,
            redacted_text=text,
            original_matches=[],
            severity='NONE'
        )
    
    # ========================================================================
    # COMPREHENSIVE SCAN
    # ========================================================================
    
    def scan(self, text: str) -> Dict[str, CryptoDetection]:
        """Run all cryptocurrency detection checks"""
        results = {
            'private_keys': self.detect_private_keys(text),
            'seed_phrases': self.detect_seed_phrases(text),
            'api_keys': self.detect_exchange_api_keys(text),
            'wallet_addresses': self.detect_wallet_addresses(text),
            'malicious_contracts': self.detect_malicious_contract_patterns(text),
            'phishing': self.detect_phishing_patterns(text),
            'exploitation': self.detect_exploitation_patterns(text),
        }
        
        return results
    
    def get_redacted_text(self, text: str) -> Tuple[str, List[str]]:
        """Get fully redacted text and list of detected issues"""
        results = self.scan(text)
        redacted = text
        issues = []
        
        # Apply redactions in order of severity
        for check_name, detection in results.items():
            if detection.detected and detection.severity in ['CRITICAL', 'HIGH']:
                redacted = detection.redacted_text
                issues.append(f"{detection.data_type}: {len(detection.original_matches)} detected")
        
        return redacted, issues
    
    def is_safe(self, text: str, block_threshold: float = 0.7) -> Tuple[bool, str, List[str]]:
        """
        Check if text is safe from cryptocurrency security perspective
        
        Returns:
            (is_safe, reason, detected_issues)
        """
        results = self.scan(text)
        detected_issues = []
        
        for check_name, detection in results.items():
            if detection.detected and detection.confidence >= block_threshold:
                if detection.severity == 'CRITICAL':
                    detected_issues.append(f"CRITICAL: {detection.data_type}")
                    return False, f"Detected {detection.data_type}", detected_issues
                elif detection.severity == 'HIGH':
                    detected_issues.append(f"HIGH: {detection.data_type}")
        
        if detected_issues:
            return False, f"Detected {len(detected_issues)} high-risk patterns", detected_issues
        
        return True, "No cryptocurrency security issues detected", []


# Singleton instance
_crypto_detector = None

def get_crypto_detector() -> CryptoDetector:
    """Get singleton instance of CryptoDetector"""
    global _crypto_detector
    if _crypto_detector is None:
        _crypto_detector = CryptoDetector()
    return _crypto_detector
