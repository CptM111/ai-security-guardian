"""
Enhanced Cryptocurrency Security Detector v2.0
Version: 1.1.0
Date: February 15, 2026

Comprehensive detection of cryptocurrency-specific security threats including:
- Private keys and seed phrases (data leakage)
- Exchange API keys (credential theft)
- Malicious smart contract generation
- Phishing and fraud attempts
- Exploitation and attack planning
- KYC/AML bypass attempts
- Market manipulation
"""

import re
import os
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

# Import base detector
from .crypto_detector import CryptoDetector as BaseCryptoDetector, CryptoDetection

class EnhancedCryptoDetector(BaseCryptoDetector):
    """Enhanced cryptocurrency detector with comprehensive attack pattern coverage"""
    
    def __init__(self):
        super().__init__()
        
        # Massively expanded pattern library
        self._init_comprehensive_patterns()
    
    def _init_comprehensive_patterns(self):
        """Initialize comprehensive attack pattern library"""
        
        # ===== PRIVATE KEY & SEED PHRASE PATTERNS =====
        self.private_key_request_patterns = [
            r'(show|display|reveal|print|give|provide|send).*private\s*key',
            r'(extract|get|obtain|retrieve).*private\s*key',
            r'what.*is.*your.*private\s*key',
            r'private\s*key.*is',
            r'seed\s*(phrase|words?).*is',
            r'(show|reveal|display).*seed\s*(phrase|words?)',
            r'(show|reveal|display).*mnemonic',
            r'backup.*wallet.*(phrase|words?)',
            r'recovery.*(phrase|words?|key)',
            r'generate.*private\s*key',
        ]
        
        # ===== EXCHANGE API KEY PATTERNS =====
        self.api_key_request_patterns = [
            r'(binance|coinbase|okx|mexc|kraken).*api\s*key',
            r'api\s*key.*(binance|coinbase|okx|mexc|kraken)',
            r'(show|reveal|display).*api\s*key',
            r'api\s*secret',
            r'access\s*key.*secret\s*key',
        ]
        
        # ===== MALICIOUS CONTRACT GENERATION =====
        self.malicious_contract_patterns = [
            # Backdoor contracts
            r'contract.*(with|containing|that\s+has).*backdoor',
            r'backdoor.*contract',
            r'hidden.*owner.*control',
            r'emergency.*withdraw.*function',
            r'contract.*drain.*funds',
            
            # Reentrancy attacks
            r'reentrancy.*(vulnerability|attack|exploit)',
            r'create.*reentrancy',
            r'exploit.*reentrancy',
            
            # Flash loan attacks
            r'flash\s*loan.*attack',
            r'create.*flash\s*loan.*exploit',
            r'exploit.*(uniswap|aave|compound).*flash\s*loan',
            
            # Front-running
            r'front.?run.*(contract|transaction)',
            r'create.*front.?running.*bot',
            r'mev.*extract',
            
            # Wallet drainers
            r'wallet\s*drainer',
            r'drain.*(wallet|funds|tokens)',
            r'steal.*approved.*tokens',
            r'unlimited.*approval.*exploit',
            
            # Fake airdrops
            r'fake.*airdrop.*contract',
            r'phishing.*airdrop',
            r'airdrop.*steal.*funds',
            
            # Malicious proxy
            r'malicious.*proxy.*contract',
            r'proxy.*backdoor',
            
            # Rug pull tokens
            r'rug\s*pull.*(token|contract)',
            r'honeypot.*token',
            r'token.*(prevent|block|disable).*sell',
            r'hidden.*sell.*restriction',
            r'100%.*tax',
        ]
        
        # ===== SMART CONTRACT VULNERABILITY EXPLOITATION =====
        self.vulnerability_exploit_patterns = [
            r'how\s+to\s+exploit.*reentrancy',
            r'exploit.*integer\s*overflow',
            r'bypass.*access\s*control',
            r'manipulate.*(oracle|price|chainlink)',
            r'exploit.*timestamp.*manipulation',
            r'unchecked.*external.*call',
            r'delegatecall.*exploit',
            r'selfdestruct.*exploit',
        ]
        
        # ===== DEFI PROTOCOL ATTACKS =====
        self.defi_attack_patterns = [
            r'drain.*liquidity.*pool',
            r'exploit.*(uniswap|pancakeswap|sushiswap)',
            r'sandwich.*attack',
            r'mev.*extraction',
            r'front.?run.*nft.*mint',
            r'exploit.*bridge.*vulnerability',
            r'cross.?chain.*exploit',
        ]
        
        # ===== PHISHING & SOCIAL ENGINEERING =====
        self.phishing_patterns_extended = [
            # Fake interfaces
            r'create.*fake.*(metamask|uniswap|pancakeswap|binance|coinbase)',
            r'fake.*(wallet|exchange|dapp).*interface',
            r'clone.*(metamask|trust\s*wallet|phantom)',
            r'phishing.*(page|site|website)',
            r'impersonate.*(wallet|exchange|protocol)',
            
            # Fake emails/messages
            r'phishing.*email.*(metamask|binance|coinbase|kraken)',
            r'fake.*(support|security).*email',
            r'pretend.*to.*be.*(binance|coinbase|metamask)',
            
            # Seed phrase phishing
            r'(ask|request|verify).*seed\s*phrase',
            r'wallet.*recovery.*page',
            r'enter.*mnemonic',
            r'verify.*wallet.*phrase',
            
            # Fake airdrops
            r'fake.*airdrop.*announcement',
            r'phishing.*airdrop',
            r'free.*tokens.*connect.*wallet',
            
            # Social engineering
            r'convince.*(approve|sign).*unlimited',
            r'trick.*into.*signing',
            r'manipulate.*user.*approve',
        ]
        
        # ===== ADDRESS POISONING =====
        self.address_poisoning_patterns = [
            r'generate.*similar.*address',
            r'address.*poisoning',
            r'vanity.*address.*impersonate',
            r'look.*alike.*address',
        ]
        
        # ===== TRANSACTION MANIPULATION =====
        self.transaction_manipulation_patterns = [
            r'modify.*transaction.*before.*signing',
            r'tamper.*transaction.*data',
            r'exploit.*blind.*signing',
            r'change.*transaction.*recipient',
        ]
        
        # ===== NFT SCAMS =====
        self.nft_scam_patterns = [
            r'fake.*(bored\s*ape|cryptopunk|azuki).*nft',
            r'fake.*nft.*collection',
            r'manipulate.*nft.*metadata',
            r'fake.*rarity.*traits',
        ]
        
        # ===== CEFI ATTACKS =====
        self.cefi_attack_patterns = [
            # API key theft/abuse
            r'(steal|extract|obtain).*api\s*key',
            r'stolen.*api\s*key',
            r'intercept.*api.*(key|credential)',
            
            # Trading bot manipulation
            r'wash\s*trading.*bot',
            r'pump\s*and\s*dump.*bot',
            r'fake.*trading.*volume',
            r'manipulate.*order\s*book',
            r'spoof.*(buy|sell).*wall',
            r'front.?run.*trade',
            
            # Withdrawal/Deposit attacks
            r'automate.*withdrawal.*stolen',
            r'double.?spend.*exchange',
            r'bypass.*withdrawal.*limit',
            r'exploit.*(deposit|withdrawal).*confirmation',
            
            # KYC/AML bypass
            r'fake.*identity.*document',
            r'generate.*fake.*id',
            r'deepfake.*(kyc|verification)',
            r'bypass.*(kyc|aml)',
            r'stolen.*identity.*exchange',
            r'synthetic.*identity',
            r'split.*transaction.*avoid.*aml',
            r'structure.*transaction',  # Smurfing
            
            # Market manipulation
            r'coordinate.*(pump|dump)',
            r'fake.*news.*manipulate.*price',
            r'shill.*bot',
            r'insider.*trading',
            
            # Exchange exploits
            r'exploit.*(binance|coinbase|kraken).*wallet',
            r'bypass.*2fa',
            r'sql.*injection.*exchange',
            r'race.*condition.*trading.*engine',
            
            # Phishing
            r'fake.*(binance|coinbase|kraken).*login',
            r'phishing.*(binance|coinbase|kraken)',
            r'fake.*security.*alert.*(exchange|wallet)',
            
            # Social engineering
            r'convince.*support.*reset.*2fa',
            r'social.*engineer.*exchange',
        ]
        
        # ===== GENERAL EXPLOITATION KEYWORDS =====
        self.general_exploit_patterns = [
            r'how\s+to\s+(hack|exploit|steal|drain|bypass)',
            r'(hack|exploit|steal).*crypto',
            r'(hack|exploit|steal).*(wallet|exchange|defi)',
            r'bypass.*(security|2fa|kyc|aml)',
            r'launder.*(crypto|bitcoin|ethereum)',
        ]
    
    def detect_exploitation_patterns(self, text: str) -> CryptoDetection:
        """Enhanced exploitation pattern detection"""
        exploit_patterns = []
        text_lower = text.lower()
        
        # Check all pattern categories
        pattern_categories = [
            ('PRIVATE_KEY_REQUEST', self.private_key_request_patterns),
            ('API_KEY_REQUEST', self.api_key_request_patterns),
            ('MALICIOUS_CONTRACT', self.malicious_contract_patterns),
            ('VULNERABILITY_EXPLOIT', self.vulnerability_exploit_patterns),
            ('DEFI_ATTACK', self.defi_attack_patterns),
            ('PHISHING', self.phishing_patterns_extended),
            ('ADDRESS_POISONING', self.address_poisoning_patterns),
            ('TRANSACTION_MANIPULATION', self.transaction_manipulation_patterns),
            ('NFT_SCAM', self.nft_scam_patterns),
            ('CEFI_ATTACK', self.cefi_attack_patterns),
            ('GENERAL_EXPLOIT', self.general_exploit_patterns),
        ]
        
        for category, patterns in pattern_categories:
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    exploit_patterns.append((category, pattern))
                    break  # Only count once per category
        
        if exploit_patterns:
            return CryptoDetection(
                detected=True,
                data_type='exploitation',
                confidence=0.95,
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
    
    def detect_phishing_patterns(self, text: str) -> CryptoDetection:
        """Use extended phishing patterns"""
        # Already covered in exploitation patterns
        return super().detect_phishing_patterns(text)


# Singleton instance
_enhanced_crypto_detector = None

def get_enhanced_crypto_detector() -> EnhancedCryptoDetector:
    """Get singleton instance of EnhancedCryptoDetector"""
    global _enhanced_crypto_detector
    if _enhanced_crypto_detector is None:
        _enhanced_crypto_detector = EnhancedCryptoDetector()
    return _enhanced_crypto_detector
