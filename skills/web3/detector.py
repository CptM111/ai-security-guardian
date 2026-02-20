"""
Web3 Security Detector

Comprehensive Web3 security protection for decentralized applications,
smart contracts, and Web3 infrastructure.

Detects:
- OWASP Smart Contract Top 10 vulnerabilities
- Web3-specific threats (transaction security, dApp attacks)
- Protocol-specific issues (DeFi, NFT, DAO, L2)
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

class RiskLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class VulnerabilityType(Enum):
    # OWASP SC Top 10
    SC01_ACCESS_CONTROL = "SC01 - Access Control Vulnerabilities"
    SC02_BUSINESS_LOGIC = "SC02 - Business Logic Vulnerabilities"
    SC03_ORACLE_MANIPULATION = "SC03 - Price Oracle Manipulation"
    SC04_FLASH_LOAN = "SC04 - Flash Loan Attacks"
    SC05_INPUT_VALIDATION = "SC05 - Lack of Input Validation"
    SC06_EXTERNAL_CALLS = "SC06 - Unchecked External Calls"
    SC07_ARITHMETIC = "SC07 - Arithmetic Errors"
    SC08_REENTRANCY = "SC08 - Reentrancy Attacks"
    SC09_OVERFLOW = "SC09 - Integer Overflow/Underflow"
    SC10_PROXY = "SC10 - Proxy & Upgradeability Vulnerabilities"
    
    # Web3-Specific
    TRANSACTION_SECURITY = "Transaction Security Issue"
    WALLET_SECURITY = "Wallet Security Issue"
    DAPP_SECURITY = "dApp Security Issue"
    CROSS_CHAIN_SECURITY = "Cross-Chain Security Issue"
    GOVERNANCE_ATTACK = "Governance Attack"
    MEV_ATTACK = "MEV Attack"

class Web3Detector:
    """Web3 Security Detector"""
    
    def __init__(self):
        self.version = "1.0.0"
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize detection patterns"""
        
        # SC01 - Access Control Vulnerabilities
        self.access_control_patterns = [
            # Privileged function access
            (r'(owner|admin|governance|privileged)\s*(function|role|access)', 0.85, "Privileged function access"),
            (r'(bypass|circumvent|escalate)\s*(owner|admin|access|privilege)', 0.90, "Access control bypass"),
            (r'(become|make me|grant me)\s*(owner|admin|superuser)', 0.95, "Privilege escalation attempt"),
            (r'(change|modify|update)\s*(owner|admin)\s*(address|role)', 0.85, "Owner/admin modification"),
            (r'onlyOwner|onlyAdmin|onlyGovernance', 0.75, "Modifier bypass attempt"),
            (r'(remove|disable)\s*(access control|modifier|require)', 0.90, "Access control removal"),
            (r'(public|external)\s+function\s+\w*(transfer|withdraw|mint|burn)Ownership', 0.80, "Ownership transfer function"),
            (r'(missing|no|without)\s*(access control|modifier|authorization)', 0.85, "Missing access control"),
            (r'(unauthorized|unauthenticated)\s*(access|call|execution)', 0.85, "Unauthorized access"),
            (r'(anyone can|public can)\s*(call|execute|access)', 0.80, "Public access to sensitive function"),
        ]
        
        # SC02 - Business Logic Vulnerabilities
        self.business_logic_patterns = [
            # Economic model exploitation
            (r'(exploit|manipulate|abuse)\s*(lending|borrowing|liquidity|reward)', 0.85, "Economic model exploitation"),
            (r'(exploit|manipulate)\s*(the)?\s*(lending|borrowing)\s*(protocol|system)', 0.90, "Protocol exploitation"),
            (r'(infinite|unlimited)\s*(mint|borrow|withdraw|claim|funds)', 0.95, "Infinite resource exploit"),
            (r'(double|multiple)\s*(claim|withdraw|spend|redeem)', 0.90, "Double-spend attempt"),
            (r'(bypass|skip|avoid)\s*(fee|interest|penalty|liquidation)', 0.85, "Fee/penalty bypass"),
            (r'(manipulate|game|exploit)\s*(reward|incentive|distribution)', 0.85, "Reward manipulation"),
            (r'(break|violate|circumvent)\s*(invariant|constraint|rule)', 0.90, "Invariant violation"),
            (r'(incorrect|wrong|flawed)\s*(calculation|formula|logic)', 0.80, "Calculation error"),
            (r'(under|over)collateralized\s*(loan|position|borrow)', 0.85, "Collateral issue"),
            (r'(arbitrage|sandwich|front.?run)\s*(opportunity|attack|exploit)', 0.85, "Arbitrage exploitation"),
            (r'(rounding|precision)\s*(error|exploit|manipulation)', 0.80, "Precision exploit"),
            (r'(drain|empty|steal)\s*(the)?\s*(liquidity|pool|vault)', 0.95, "Pool drain attack"),
            (r'(claim|withdraw)\s*(multiple times|repeatedly|again)', 0.90, "Multiple claim exploit"),
            (r'(borrow|loan)\s*unlimited', 0.95, "Unlimited borrow"),
        ]
        
        # SC03 - Oracle Manipulation
        self.oracle_patterns = [
            # Price oracle attacks
            (r'(manipulate|attack|exploit)\s*(oracle|price feed|price data)', 0.90, "Oracle manipulation"),
            (r'(fake|false|malicious)\s*(price|oracle|feed)', 0.90, "Fake price data"),
            (r'(flash loan|large trade)\s*(to|for)\s*(manipulate|skew|move)\s*price', 0.95, "Flash loan price manipulation"),
            (r'(outdated|stale|old)\s*(price|oracle|data)', 0.75, "Stale oracle data"),
            (r'(single|one|centralized)\s*(oracle|price source)', 0.70, "Single oracle dependency"),
            (r'(bypass|ignore|skip)\s*(oracle|price check)', 0.85, "Oracle check bypass"),
            (r'(chainlink|uniswap|band)\s*(manipulation|exploit|attack)', 0.85, "Specific oracle attack"),
            (r'(twap|spot price)\s*(manipulation|exploit)', 0.85, "Price calculation exploit"),
            (r'(low liquidity|thin market)\s*(manipulation|exploit)', 0.80, "Low liquidity manipulation"),
            (r'(oracle.?free|no oracle|without oracle)', 0.75, "Missing oracle protection"),
        ]
        
        # SC04 - Flash Loan Attacks
        self.flash_loan_patterns = [
            # Flash loan exploitation
            (r'flash\s*loan\s*(attack|exploit|manipulation)', 0.95, "Flash loan attack"),
            (r'(borrow|loan)\s*(large amount|millions?)\s*(in one transaction|atomically)', 0.90, "Large atomic loan"),
            (r'(borrow|loan)\s*millions?\s*(from|on)\s*(aave|dydx|balancer)', 0.95, "Large loan from protocol"),
            (r'(aave|dydx|balancer|uniswap)\s*(flash\s*loan|to\s*manipulate)', 0.85, "Specific flash loan protocol"),
            (r'use\s*(a)?\s*flash\s*loan\s*to', 0.90, "Flash loan usage"),
            (r'(uncollateralized|zero.?collateral)\s*(loan|borrow)', 0.85, "Uncollateralized loan"),
            (r'(multi.?step|complex|chained)\s*(attack|exploit)\s*(with|using)\s*flash', 0.90, "Multi-step flash loan attack"),
            (r'(drain|empty|steal)\s*(pool|vault|treasury)\s*(with|using|via)\s*flash', 0.95, "Pool drain via flash loan"),
            (r'flash\s*loan\s*(arbitrage|sandwich|front.?run)', 0.85, "Flash loan MEV"),
            (r'(leverage|amplify|magnify)\s*(small bug|exploit)\s*(with|using)\s*flash', 0.90, "Bug amplification"),
            (r'(price|oracle)\s*manipulation\s*(via|using|with)\s*flash', 0.95, "Flash loan price manipulation"),
            (r'(reentrancy|callback)\s*(with|using)\s*flash\s*loan', 0.95, "Flash loan reentrancy"),
            (r'(manipulate|skew|move)\s*(uniswap|dex)\s*price', 0.85, "DEX price manipulation"),
        ]
        
        # SC05 - Input Validation
        self.input_validation_patterns = [
            # Missing validation
            (r'(no|missing|without|lack of)\s*(validation|check|verification)', 0.85, "Missing validation"),
            (r'(unchecked|unvalidated|unsanitized)\s*(input|parameter|argument)', 0.85, "Unchecked input"),
            (r'(arbitrary|malicious|crafted)\s*(input|parameter|data)', 0.85, "Malicious input"),
            (r'(zero|null|empty)\s*(address|value|amount)\s*(allowed|accepted)', 0.80, "Zero value allowed"),
            (r'(negative|overflow|underflow)\s*(value|amount)\s*(allowed|possible)', 0.85, "Invalid value range"),
            (r'(cross.?chain|bridge)\s*(message|data)\s*(not validated|unchecked)', 0.90, "Cross-chain input not validated"),
            (r'(array|string)\s*(length|size)\s*(not checked|unlimited)', 0.80, "Array/string length not checked"),
            (r'(user.?supplied|external)\s*(address|contract)\s*(not validated|unchecked)', 0.85, "External address not validated"),
            (r'(parameter|argument)\s*(tampering|manipulation|injection)', 0.85, "Parameter tampering"),
            (r'(bypass|skip)\s*(input check|validation|require)', 0.85, "Validation bypass"),
        ]
        
        # Ethereum address pattern
        self.eth_address_pattern = re.compile(r'0x[a-fA-F0-9]{40}')
        
        # Transaction hash pattern
        self.tx_hash_pattern = re.compile(r'0x[a-fA-F0-9]{64}')
        
        # Function selector pattern
        self.function_selector_pattern = re.compile(r'0x[a-fA-F0-9]{8}')
        
        # Solidity code patterns
        self.solidity_patterns = [
            re.compile(r'pragma\s+solidity'),
            re.compile(r'contract\s+\w+\s+(is\s+)?'),
            re.compile(r'function\s+\w+\s*\([^)]*\)\s+(public|external|internal|private)'),
            re.compile(r'modifier\s+\w+'),
        ]
    
    def check(self, text: str, context: Optional[Dict] = None) -> Dict:
        """
        Check text for Web3 security threats
        
        Args:
            text: Input text to check
            context: Optional context information
            
        Returns:
            Detection result dictionary
        """
        text_lower = text.lower()
        
        # Detect all vulnerabilities
        vulnerabilities = []
        
        # Check OWASP SC Top 10
        vulnerabilities.extend(self._check_access_control(text_lower))
        vulnerabilities.extend(self._check_business_logic(text_lower))
        vulnerabilities.extend(self._check_oracle_manipulation(text_lower))
        vulnerabilities.extend(self._check_flash_loans(text_lower))
        vulnerabilities.extend(self._check_input_validation(text_lower))
        
        # Check extended patterns (SC06-SC10 and Web3-specific)
        vulnerabilities.extend(self.check_extended(text_lower))
        
        # Determine overall risk
        if not vulnerabilities:
            return {
                "is_safe": True,
                "confidence": 1.0,
                "threat_type": None,
                "severity": None,
                "details": None,
                "skill": "web3"
            }
        
        # Get highest severity vulnerability
        severity_order = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1,
            RiskLevel.INFO: 0
        }
        
        top_vuln = max(vulnerabilities, key=lambda v: (severity_order[v['severity']], v['confidence']))
        
        return {
            "is_safe": False,
            "confidence": top_vuln['confidence'],
            "threat_type": top_vuln['type'].value,
            "severity": top_vuln['severity'].value,
            "details": {
                "vulnerability": top_vuln['type'].value,
                "description": top_vuln['description'],
                "recommendation": top_vuln['recommendation'],
                "all_findings": len(vulnerabilities),
                "critical_findings": sum(1 for v in vulnerabilities if v['severity'] == RiskLevel.CRITICAL),
                "high_findings": sum(1 for v in vulnerabilities if v['severity'] == RiskLevel.HIGH)
            },
            "skill": "web3"
        }
    
    def _check_access_control(self, text: str) -> List[Dict]:
        """Check for SC01 - Access Control Vulnerabilities"""
        findings = []
        
        for pattern, confidence, description in self.access_control_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Determine severity based on pattern
                severity = RiskLevel.CRITICAL if confidence >= 0.90 else RiskLevel.HIGH
                
                findings.append({
                    'type': VulnerabilityType.SC01_ACCESS_CONTROL,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential access control vulnerability: {description}",
                    'recommendation': "Implement proper access control using modifiers (onlyOwner, onlyRole). Use OpenZeppelin's AccessControl or Ownable. Ensure all privileged functions are protected."
                })
        
        return findings
    
    def _check_business_logic(self, text: str) -> List[Dict]:
        """Check for SC02 - Business Logic Vulnerabilities"""
        findings = []
        
        for pattern, confidence, description in self.business_logic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL if confidence >= 0.90 else RiskLevel.HIGH
                
                findings.append({
                    'type': VulnerabilityType.SC02_BUSINESS_LOGIC,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential business logic vulnerability: {description}",
                    'recommendation': "Review economic model for edge cases. Implement proper checks and balances. Use invariant testing. Consider formal verification for critical logic."
                })
        
        return findings
    
    def _check_oracle_manipulation(self, text: str) -> List[Dict]:
        """Check for SC03 - Price Oracle Manipulation"""
        findings = []
        
        for pattern, confidence, description in self.oracle_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL if confidence >= 0.90 else RiskLevel.HIGH
                
                findings.append({
                    'type': VulnerabilityType.SC03_ORACLE_MANIPULATION,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential oracle manipulation: {description}",
                    'recommendation': "Use multiple oracle sources. Implement TWAP (Time-Weighted Average Price). Add price deviation checks. Use Chainlink or other decentralized oracles. Validate price freshness."
                })
        
        return findings
    
    def _check_flash_loans(self, text: str) -> List[Dict]:
        """Check for SC04 - Flash Loan Attacks"""
        findings = []
        
        for pattern, confidence, description in self.flash_loan_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL
                
                findings.append({
                    'type': VulnerabilityType.SC04_FLASH_LOAN,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential flash loan attack: {description}",
                    'recommendation': "Implement flash loan protection. Use reentrancy guards. Check for price manipulation. Validate state consistency. Consider using Aave's flash loan protection patterns."
                })
        
        return findings
    
    def _check_input_validation(self, text: str) -> List[Dict]:
        """Check for SC05 - Lack of Input Validation"""
        findings = []
        
        for pattern, confidence, description in self.input_validation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.HIGH if confidence >= 0.85 else RiskLevel.MEDIUM
                
                findings.append({
                    'type': VulnerabilityType.SC05_INPUT_VALIDATION,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential input validation issue: {description}",
                    'recommendation': "Validate all inputs. Check for zero addresses. Validate array lengths. Sanitize cross-chain messages. Use require() statements. Implement proper bounds checking."
                })
        
        return findings
    
    def is_safe(self, text: str, threshold: float = 0.7) -> Tuple[bool, Optional[str]]:
        """
        Quick safety check
        
        Args:
            text: Input text
            threshold: Confidence threshold
            
        Returns:
            (is_safe, reason)
        """
        result = self.check(text)
        
        if result['is_safe']:
            return True, None
        
        if result['confidence'] >= threshold:
            return False, result['details']['description']
        
        return True, None
    
    def get_version(self) -> str:
        """Get detector version"""
        return self.version

    def _init_patterns_extended(self):
        """Initialize extended detection patterns (SC06-SC10 and Web3-specific)"""
        
        # SC06 - Unchecked External Calls
        self.external_call_patterns = [
            (r'(unchecked|unsafe|unverified)\s*(external call|call|delegatecall)', 0.90, "Unchecked external call"),
            (r'(call|delegatecall|staticcall)\s*(without|no|missing)\s*(check|verification)', 0.85, "Call without check"),
            (r'(ignore|skip)\s*(return value|success|result)', 0.85, "Ignored return value"),
            (r'(low.?level call|assembly call)\s*(unsafe|unchecked)', 0.85, "Unsafe low-level call"),
            (r'(arbitrary|untrusted|malicious)\s*(contract|address)\s*call', 0.90, "Call to untrusted contract"),
            (r'delegatecall\s*(to|on)\s*(user|external|untrusted)', 0.95, "Delegatecall to untrusted"),
            (r'(callback|hook)\s*(not checked|unsafe|vulnerable)', 0.85, "Unsafe callback"),
            (r'(external call|interaction)\s*before\s*state\s*(change|update)', 0.85, "External call before state update"),
            (r'(call|send|transfer)\s*(eth|ether|value)\s*(unsafe|unchecked)', 0.85, "Unsafe ETH transfer"),
            (r'(revert|fail)\s*(not handled|ignored|unchecked)', 0.80, "Unhandled revert"),
        ]
        
        # SC07 - Arithmetic Errors
        self.arithmetic_patterns = [
            (r'(arithmetic|math|calculation)\s*(error|bug|issue|overflow|underflow)', 0.85, "Arithmetic error"),
            (r'(rounding|precision|truncation)\s*(error|loss|issue)', 0.80, "Precision error"),
            (r'(division|divide)\s*by\s*zero', 0.95, "Division by zero"),
            (r'(unchecked|unsafe)\s*(math|arithmetic|calculation)', 0.85, "Unchecked arithmetic"),
            (r'(interest|share|reward)\s*calculation\s*(error|bug|exploit)', 0.85, "Financial calculation error"),
            (r'(scaling|conversion)\s*(error|issue|bug)', 0.80, "Scaling error"),
            (r'(decimal|precision)\s*(mismatch|error|issue)', 0.80, "Decimal precision issue"),
            (r'(compound|cumulative)\s*rounding\s*(error|exploit)', 0.85, "Cumulative rounding error"),
            (r'(manipulate|exploit)\s*(rounding|precision)', 0.85, "Precision manipulation"),
            (r'(no|without|missing)\s*SafeMath', 0.75, "Missing SafeMath"),
        ]
        
        # SC08 - Reentrancy Attacks
        self.reentrancy_patterns = [
            (r'reentrancy\s*(attack|vulnerability|exploit)', 0.95, "Reentrancy attack"),
            (r'(recursive|repeated)\s*(call|callback|invocation)', 0.85, "Recursive call"),
            (r'(external call|interaction)\s*before\s*state\s*(update|change)', 0.85, "State update after external call"),
            (r'(withdraw|transfer)\s*(before|without)\s*balance\s*update', 0.90, "Withdrawal before balance update"),
            (r'(cross.?function|cross.?contract)\s*reentrancy', 0.90, "Cross-function reentrancy"),
            (r'(no|missing|without)\s*(reentrancy guard|nonReentrant|mutex)', 0.85, "Missing reentrancy guard"),
            (r'(checks.?effects.?interactions|CEI)\s*(violation|not followed)', 0.85, "CEI pattern violation"),
            (r'(callback|hook)\s*reentrancy', 0.90, "Callback reentrancy"),
            (r'(read.?only|view)\s*reentrancy', 0.85, "Read-only reentrancy"),
            (r'(dao|the dao)\s*hack', 0.95, "DAO hack reference"),
        ]
        
        # SC09 - Integer Overflow/Underflow
        self.overflow_patterns = [
            (r'(integer|int|uint)\s*(overflow|underflow)', 0.90, "Integer overflow/underflow"),
            (r'(wrap|wraparound)\s*(integer|value|number)', 0.85, "Integer wraparound"),
            (r'(unchecked|unsafe)\s*(increment|decrement|addition|subtraction)', 0.85, "Unchecked arithmetic operation"),
            (r'(overflow|underflow)\s*(check|protection)\s*(missing|disabled|removed)', 0.90, "Missing overflow protection"),
            (r'(solidity\s*<\s*0\.8|pragma.*0\.[0-7])\s*(without|no)\s*SafeMath', 0.85, "Old Solidity without SafeMath"),
            (r'(bypass|disable|remove)\s*(overflow check|SafeMath)', 0.90, "Overflow check bypass"),
            (r'(max|maximum)\s*(uint|int)\s*(value|limit)\s*(exceed|overflow)', 0.85, "Max value overflow"),
            (r'(negative|minus)\s*(uint|unsigned)', 0.85, "Unsigned underflow"),
            (r'(balance|supply|amount)\s*(overflow|underflow)', 0.90, "Balance overflow/underflow"),
            (r'unchecked\s*\{[^}]*(\+\+|--|\+|-|\*)\s*\}', 0.85, "Unchecked block with arithmetic"),
        ]
        
        # SC10 - Proxy & Upgradeability
        self.proxy_patterns = [
            (r'(proxy|upgradeable|upgradable)\s*(vulnerability|exploit|attack)', 0.90, "Proxy vulnerability"),
            (r'(initialize|constructor)\s*(twice|multiple|again)', 0.95, "Re-initialization attack"),
            (r'(storage|slot)\s*collision', 0.90, "Storage collision"),
            (r'(implementation|logic)\s*(hijack|takeover|steal)', 0.95, "Implementation hijacking"),
            (r'(uninitialized|not initialized)\s*(proxy|implementation)', 0.90, "Uninitialized proxy"),
            (r'(selfdestruct|suicide)\s*(in|on)\s*(implementation|logic)', 0.95, "Selfdestruct in implementation"),
            (r'(delegatecall|proxy)\s*(to|on)\s*(malicious|attacker)', 0.95, "Delegatecall to malicious contract"),
            (r'(upgrade|change)\s*implementation\s*(without|no)\s*(governance|timelock)', 0.85, "Unprotected upgrade"),
            (r'(transparent|UUPS|beacon)\s*proxy\s*(vulnerability|exploit)', 0.85, "Specific proxy pattern vulnerability"),
            (r'(storage layout|variable order)\s*(mismatch|conflict)', 0.85, "Storage layout mismatch"),
        ]
        
        # Transaction Security
        self.transaction_patterns = [
            (r'blind\s*sign(ing|ature)?', 0.90, "Blind signing"),
            (r'(fake|phishing|malicious)\s*(transaction|signature request)', 0.90, "Phishing transaction"),
            (r'(manipulate|tamper|modify)\s*(transaction|tx)\s*(parameter|data)', 0.90, "Transaction manipulation"),
            (r'(gas price|gas limit)\s*(manipulation|exploit)', 0.80, "Gas manipulation"),
            (r'(nonce|sequence)\s*(manipulation|reuse|replay)', 0.85, "Nonce manipulation"),
            (r'(front.?run|sandwich|back.?run)\s*(transaction|tx)', 0.85, "MEV attack"),
            (r'(ui|interface)\s*(deception|spoofing|fake)', 0.85, "UI deception"),
            (r'(approve|allowance)\s*(unlimited|infinite|max)', 0.80, "Unlimited approval"),
            (r'(sign|approve)\s*(without|no)\s*(review|check|verification)', 0.85, "Signing without review"),
            (r'(transaction|tx)\s*(simulation|preview)\s*(bypass|skip)', 0.85, "Transaction simulation bypass"),
        ]
        
        # Wallet Security
        self.wallet_patterns = [
            (r'(wallet|metamask|walletconnect)\s*(phishing|fake|malicious)', 0.90, "Wallet phishing"),
            (r'connect\s*(your)?\s*(metamask|wallet)\s*(to|on)\s*(this|phishing)', 0.95, "Malicious wallet connection"),
            (r'(connect|link)\s*wallet\s*(to|on)\s*(malicious|fake|phishing)\s*(site|dapp)', 0.95, "Malicious wallet connection"),
            (r'enter\s*(your)?\s*seed\s*phrase\s*(to|for)\s*(recover|restore)', 0.95, "Seed phrase phishing"),
            (r'(permission|access)\s*(abuse|exploit|excessive)', 0.85, "Permission abuse"),
            (r'(signature|sign)\s*(request|prompt)\s*(malicious|fake)', 0.90, "Malicious signature request"),
            (r'(wallet|account|dapp)\s*(drain|empty|steal)', 0.95, "Wallet drain"),
            (r'(seed phrase|private key|mnemonic)\s*(phishing|steal|extract)', 0.95, "Credential phishing"),
            (r'(fake|malicious)\s*(wallet|extension|plugin)', 0.90, "Fake wallet"),
            (r'(clipboard|copy.?paste)\s*(hijack|replace|swap)', 0.90, "Clipboard hijacking"),
            (r'(address|recipient)\s*(swap|replace|poison)', 0.90, "Address poisoning"),
            (r'(wallet|account)\s*(takeover|compromise|hack)', 0.95, "Wallet compromise"),
        ]
        
        # dApp Security
        self.dapp_patterns = [
            (r'(dapp|frontend|website)\s*(injection|xss|attack)', 0.90, "dApp injection attack"),
            (r'inject\s*(xss|payload|script)\s*(into|in)\s*(dapp|frontend)', 0.90, "XSS injection"),
            (r'(malicious|fake|phishing)\s*(dapp|website|frontend)', 0.90, "Malicious dApp"),
            (r'(domain|url|link|ens)\s*(spoofing|fake|phishing|looks like)', 0.85, "Domain spoofing"),
            (r'fake\s*ens\s*domain', 0.90, "Fake ENS domain"),
            (r'(ens|domain)\s*(hijack|takeover|steal)', 0.90, "ENS hijacking"),
            (r'(ipfs|content)\s*(manipulation|tampering|replace)', 0.85, "Content manipulation"),
            (r'(cdn|script|library)\s*(compromise|inject|malicious)', 0.90, "Supply chain attack"),
            (r'compromise\s*(the)?\s*cdn\s*to\s*inject', 0.95, "CDN compromise"),
            (r'(web3|frontend)\s*(vulnerability|exploit|attack)', 0.85, "Web3 frontend attack"),
            (r'(javascript|script)\s*injection\s*(in|on)\s*dapp', 0.90, "Script injection"),
            (r'(cors|csp|security header)\s*(misconfiguration|missing)', 0.75, "Security header issue"),
            (r'(api key|secret|token)\s*(exposed|leaked)\s*(in|on)\s*frontend', 0.90, "Frontend secret exposure"),
        ]
        
        # Cross-Chain Security
        self.cross_chain_patterns = [
            (r'(bridge|cross.?chain)\s*(exploit|attack|hack)', 0.95, "Bridge exploit"),
            (r'exploit\s*(the)?\s*bridge\s*to\s*(mint|steal)', 0.95, "Bridge exploitation"),
            (r'(message|data)\s*(manipulation|tampering)\s*(cross.?chain|bridge)', 0.90, "Cross-chain message manipulation"),
            (r'manipulate\s*cross.?chain\s*message', 0.90, "Cross-chain message manipulation"),
            (r'(wrapped|bridged)\s*(token|asset)\s*(exploit|attack)', 0.85, "Wrapped token exploit"),
            (r'mint\s*fake\s*wrapped\s*token', 0.95, "Fake wrapped token minting"),
            (r'(replay|duplicate)\s*attack\s*(cross.?chain|multi.?chain)', 0.90, "Cross-chain replay attack"),
            (r'replay\s*attack\s*on\s*multi.?chain', 0.90, "Multi-chain replay attack"),
            (r'(validator|relayer)\s*(compromise|malicious|attack)', 0.90, "Validator compromise"),
            (r'(bridge|cross.?chain)\s*contract\s*(vulnerability|bug)', 0.85, "Bridge contract vulnerability"),
            (r'(liquidity|pool)\s*drain\s*(via|through)\s*bridge', 0.95, "Bridge liquidity drain"),
            (r'(merkle|proof)\s*(manipulation|fake|invalid)', 0.90, "Merkle proof manipulation"),
            (r'(finality|confirmation)\s*(issue|attack|exploit)', 0.85, "Finality issue"),
            (r'(cross.?chain|bridge)\s*(reentrancy|callback)', 0.90, "Cross-chain reentrancy"),
        ]
        
        # Governance Attacks
        self.governance_patterns = [
            (r'(governance|voting|proposal)\s*(attack|exploit|manipulation)', 0.90, "Governance attack"),
            (r'(vote|voting power)\s*(buying|manipulation|bribe)', 0.90, "Vote manipulation"),
            (r'(flash loan|borrow)\s*(for|to)\s*(vote|voting|governance)', 0.95, "Flash loan governance attack"),
            (r'(proposal|vote)\s*(spam|flood|dos)', 0.85, "Governance DoS"),
            (r'(timelock|delay)\s*(bypass|skip|circumvent)', 0.90, "Timelock bypass"),
            (r'(quorum|threshold)\s*(manipulation|gaming)', 0.85, "Quorum manipulation"),
            (r'(delegate|delegation)\s*(attack|exploit|manipulation)', 0.85, "Delegation attack"),
            (r'(malicious|hostile)\s*(proposal|vote|takeover)', 0.90, "Malicious proposal"),
            (r'(treasury|fund)\s*drain\s*(via|through)\s*governance', 0.95, "Treasury drain via governance"),
            (r'(governance|admin)\s*key\s*(compromise|steal|hack)', 0.95, "Governance key compromise"),
        ]
        
        # MEV Attacks
        self.mev_patterns = [
            (r'mev\s*(attack|exploit|extraction)', 0.90, "MEV attack"),
            (r'(sandwich|front.?run|back.?run)\s*(attack|bot|this)', 0.90, "MEV bot attack"),
            (r'sandwich\s*attack\s*on', 0.90, "Sandwich attack"),
            (r'front.?run\s*(the)?\s*(liquidation|transaction)', 0.90, "Front-running"),
            (r'use\s*mev\s*bot\s*to', 0.90, "MEV bot usage"),
            (r'extract\s*value\s*from\s*mempool', 0.90, "MEV extraction"),
            (r'(searcher|builder|proposer)\s*(manipulation|collusion)', 0.85, "MEV actor manipulation"),
            (r'(transaction|tx)\s*ordering\s*(manipulation|attack)', 0.85, "Transaction ordering attack"),
            (r'(mempool|pending tx)\s*(monitoring|sniping)', 0.80, "Mempool monitoring"),
            (r'(priority|gas)\s*fee\s*(manipulation|bidding war)', 0.80, "Gas fee manipulation"),
            (r'(flashbots|mev.?boost|mev.?relay)', 0.75, "MEV infrastructure"),
            (r'(atomic|multi.?step)\s*arbitrage', 0.80, "Atomic arbitrage"),
            (r'(liquidation|liquidate)\s*(front.?run|snipe)', 0.85, "Liquidation front-running"),
            (r'(jit|just.?in.?time)\s*liquidity', 0.75, "JIT liquidity"),
        ]
        
        # Store all extended patterns
        self.extended_patterns_initialized = True
    
    def check_extended(self, text: str) -> List[Dict]:
        """Check for SC06-SC10 and Web3-specific threats"""
        if not hasattr(self, 'extended_patterns_initialized'):
            self._init_patterns_extended()
        
        findings = []
        text_lower = text.lower()
        
        # Check SC06-SC10
        findings.extend(self._check_external_calls(text_lower))
        findings.extend(self._check_arithmetic(text_lower))
        findings.extend(self._check_reentrancy(text_lower))
        findings.extend(self._check_overflow(text_lower))
        findings.extend(self._check_proxy(text_lower))
        
        # Check Web3-specific
        findings.extend(self._check_transaction_security(text_lower))
        findings.extend(self._check_wallet_security(text_lower))
        findings.extend(self._check_dapp_security(text_lower))
        findings.extend(self._check_cross_chain(text_lower))
        findings.extend(self._check_governance(text_lower))
        findings.extend(self._check_mev(text_lower))
        
        return findings
    
    def _check_external_calls(self, text: str) -> List[Dict]:
        """Check for SC06 - Unchecked External Calls"""
        findings = []
        for pattern, confidence, description in self.external_call_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL if confidence >= 0.90 else RiskLevel.HIGH
                findings.append({
                    'type': VulnerabilityType.SC06_EXTERNAL_CALLS,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential unchecked external call: {description}",
                    'recommendation': "Always check return values of external calls. Use try/catch for external calls. Follow checks-effects-interactions pattern. Avoid delegatecall to untrusted contracts."
                })
        return findings
    
    def _check_arithmetic(self, text: str) -> List[Dict]:
        """Check for SC07 - Arithmetic Errors"""
        findings = []
        for pattern, confidence, description in self.arithmetic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.HIGH if confidence >= 0.85 else RiskLevel.MEDIUM
                findings.append({
                    'type': VulnerabilityType.SC07_ARITHMETIC,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential arithmetic error: {description}",
                    'recommendation': "Use Solidity 0.8+ with built-in overflow checks. For older versions, use SafeMath. Be careful with division and rounding. Test edge cases thoroughly."
                })
        return findings
    
    def _check_reentrancy(self, text: str) -> List[Dict]:
        """Check for SC08 - Reentrancy Attacks"""
        findings = []
        for pattern, confidence, description in self.reentrancy_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL
                findings.append({
                    'type': VulnerabilityType.SC08_REENTRANCY,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential reentrancy vulnerability: {description}",
                    'recommendation': "Use ReentrancyGuard from OpenZeppelin. Follow checks-effects-interactions pattern. Update state before external calls. Consider using pull over push pattern."
                })
        return findings
    
    def _check_overflow(self, text: str) -> List[Dict]:
        """Check for SC09 - Integer Overflow/Underflow"""
        findings = []
        for pattern, confidence, description in self.overflow_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL if confidence >= 0.90 else RiskLevel.HIGH
                findings.append({
                    'type': VulnerabilityType.SC09_OVERFLOW,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential integer overflow/underflow: {description}",
                    'recommendation': "Use Solidity 0.8+ with automatic overflow checks. Avoid unchecked blocks unless necessary. For older versions, use SafeMath library. Test boundary conditions."
                })
        return findings
    
    def _check_proxy(self, text: str) -> List[Dict]:
        """Check for SC10 - Proxy & Upgradeability Vulnerabilities"""
        findings = []
        for pattern, confidence, description in self.proxy_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL
                findings.append({
                    'type': VulnerabilityType.SC10_PROXY,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Potential proxy vulnerability: {description}",
                    'recommendation': "Use OpenZeppelin's upgradeable contracts. Implement proper initialization. Protect upgrade functions. Avoid storage collisions. Use storage gaps. Test upgrades thoroughly."
                })
        return findings
    
    def _check_transaction_security(self, text: str) -> List[Dict]:
        """Check for transaction security issues"""
        findings = []
        for pattern, confidence, description in self.transaction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.HIGH if confidence >= 0.85 else RiskLevel.MEDIUM
                findings.append({
                    'type': VulnerabilityType.TRANSACTION_SECURITY,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Transaction security issue: {description}",
                    'recommendation': "Always review transactions before signing. Use transaction simulation. Avoid blind signing. Check transaction parameters. Use limited approvals."
                })
        return findings
    
    def _check_wallet_security(self, text: str) -> List[Dict]:
        """Check for wallet security issues"""
        findings = []
        for pattern, confidence, description in self.wallet_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL
                findings.append({
                    'type': VulnerabilityType.WALLET_SECURITY,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Wallet security threat: {description}",
                    'recommendation': "Verify dApp URLs before connecting. Review wallet permissions. Never share private keys or seed phrases. Use hardware wallets for large amounts. Enable wallet security features."
                })
        return findings
    
    def _check_dapp_security(self, text: str) -> List[Dict]:
        """Check for dApp security issues"""
        findings = []
        for pattern, confidence, description in self.dapp_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.HIGH if confidence >= 0.85 else RiskLevel.MEDIUM
                findings.append({
                    'type': VulnerabilityType.DAPP_SECURITY,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"dApp security issue: {description}",
                    'recommendation': "Sanitize all inputs. Implement CSP headers. Use HTTPS. Verify ENS domains. Audit frontend code. Use secure CDNs. Never expose secrets in frontend."
                })
        return findings
    
    def _check_cross_chain(self, text: str) -> List[Dict]:
        """Check for cross-chain security issues"""
        findings = []
        for pattern, confidence, description in self.cross_chain_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL
                findings.append({
                    'type': VulnerabilityType.CROSS_CHAIN_SECURITY,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Cross-chain security threat: {description}",
                    'recommendation': "Validate cross-chain messages. Use trusted bridges. Implement replay protection. Verify proofs. Monitor bridge contracts. Use multiple validators."
                })
        return findings
    
    def _check_governance(self, text: str) -> List[Dict]:
        """Check for governance attacks"""
        findings = []
        for pattern, confidence, description in self.governance_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.CRITICAL if confidence >= 0.90 else RiskLevel.HIGH
                findings.append({
                    'type': VulnerabilityType.GOVERNANCE_ATTACK,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"Governance attack threat: {description}",
                    'recommendation': "Implement timelocks. Use snapshot voting. Prevent flash loan voting. Set appropriate quorums. Monitor proposals. Use multi-sig for critical operations."
                })
        return findings
    
    def _check_mev(self, text: str) -> List[Dict]:
        """Check for MEV attacks"""
        findings = []
        for pattern, confidence, description in self.mev_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                severity = RiskLevel.HIGH if confidence >= 0.85 else RiskLevel.MEDIUM
                findings.append({
                    'type': VulnerabilityType.MEV_ATTACK,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f"MEV attack threat: {description}",
                    'recommendation': "Use private mempools. Implement MEV protection. Use Flashbots Protect. Add slippage protection. Consider batch auctions. Monitor for sandwich attacks."
                })
        return findings
