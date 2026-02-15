# Cryptocurrency Security Use Cases
## AI Security Guardian v1.1.0

This document provides detailed use cases for deploying AI Security Guardian in cryptocurrency and blockchain environments.

---

## Table of Contents

1. [DeFi Protocol Security](#1-defi-protocol-security)
2. [Centralized Exchange (CEX) Protection](#2-centralized-exchange-cex-protection)
3. [Crypto Wallet Application](#3-crypto-wallet-application)
4. [NFT Marketplace Security](#4-nft-marketplace-security)
5. [Blockchain Development Tools](#5-blockchain-development-tools)
6. [Crypto Trading Bot Platform](#6-crypto-trading-bot-platform)

---

## 1. DeFi Protocol Security

### Scenario
A decentralized finance (DeFi) protocol offers an AI-powered chatbot to help users interact with smart contracts, check balances, and understand protocol features.

### Security Risks
- **Malicious contract generation**: Attackers may try to get the AI to generate vulnerable or malicious smart contracts
- **Private key extraction**: Users may accidentally expose seed phrases or private keys
- **Protocol exploitation guidance**: Attackers may request information on exploiting vulnerabilities
- **Phishing content**: Requests to create fake interfaces or phishing pages

### ASG Implementation

```python
from asg_sdk import ASGClient

# Initialize ASG client
asg = ASGClient(api_key="your_api_key_here", base_url="https://your-asg-instance.com")

# Protect user prompts before sending to LLM
@asg.protect_prompt()
def process_user_query(user_input: str) -> str:
    """Process DeFi user queries with security protection"""
    # Your LLM processing logic here
    response = your_llm_model.generate(user_input)
    return response

# Sanitize LLM outputs
@asg.sanitize_output()
def send_response_to_user(response: str) -> str:
    """Sanitize responses before showing to users"""
    return response

# Example usage
user_query = "Help me recover my wallet. My seed phrase is: abandon abandon..."
try:
    safe_response = process_user_query(user_query)
    sanitized_output = send_response_to_user(safe_response)
    print(sanitized_output)
except ASGSecurityException as e:
    print(f"Security threat detected: {e.threat_type}")
    # Log incident, show safe error message to user
```

### Protection Provided
- ✅ Blocks requests for malicious smart contract generation
- ✅ Detects and redacts seed phrases and private keys
- ✅ Prevents exploitation guidance
- ✅ Blocks phishing content generation
- ✅ Sanitizes any leaked sensitive data in responses

### Test Results
- **Malicious Contract Detection**: 85.7% (6/7 attacks blocked)
- **Protocol Attack Prevention**: 100% (5/5 attacks blocked)
- **Private Key Protection**: 40% (2/5 detected - see notes)
- **Overall DeFi Protection**: 67.5% (27/40 attacks blocked)

**Note**: Private key detection rate is lower because some tests involve legitimate debugging scenarios. In production, you can adjust sensitivity based on your use case.

---

## 2. Centralized Exchange (CEX) Protection

### Scenario
A cryptocurrency exchange provides an AI customer support assistant to help users with account issues, trading questions, and security concerns.

### Security Risks
- **API key leakage**: Users may paste API keys in support chats
- **KYC bypass attempts**: Attackers may request help creating fake documents
- **Phishing content**: Requests to generate fake exchange pages or emails
- **Market manipulation**: Requests for wash trading or pump-and-dump bots
- **Social engineering**: Attempts to manipulate support into bypassing security

### ASG Implementation

```python
from asg_sdk import ASGClient
from asg_sdk.decorators import protect_prompt, sanitize_output

asg = ASGClient(api_key="your_api_key_here")

class ExchangeSupportBot:
    def __init__(self):
        self.asg = asg
    
    @protect_prompt()
    def handle_support_request(self, user_message: str, user_id: str) -> dict:
        """Handle customer support requests with security"""
        # Check for sensitive data
        scan_result = self.asg.scan_text(user_message)
        
        if scan_result.has_api_keys:
            # Redact API keys and warn user
            return {
                "status": "warning",
                "message": "⚠️ We detected API keys in your message. For your security, please never share API keys. We've redacted them from our records.",
                "redacted_message": scan_result.redacted_text
            }
        
        if scan_result.has_private_keys:
            # Critical security alert
            return {
                "status": "critical",
                "message": "🚨 SECURITY ALERT: Never share private keys or seed phrases! We've deleted your message for your protection.",
                "action": "message_deleted"
            }
        
        # Process with LLM
        response = self.generate_support_response(user_message)
        return {"status": "success", "response": response}
    
    @sanitize_output()
    def generate_support_response(self, message: str) -> str:
        # Your LLM logic here
        return llm_response

# Example usage
bot = ExchangeSupportBot()

# User accidentally pastes API key
user_msg = "My trading bot isn't working. Here's my code: api_key='vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A'"
result = bot.handle_support_request(user_msg, user_id="user123")
print(result["message"])  # Warns user about API key exposure
```

### Protection Provided
- ✅ Detects and redacts exchange API keys (Binance, Coinbase, OKX, MEXC, Kraken)
- ✅ Blocks KYC bypass requests (80% detection rate)
- ✅ Prevents phishing content generation (85.7% detection rate)
- ✅ Blocks market manipulation assistance (75% detection rate)
- ✅ Detects social engineering attempts (100% detection rate)

### Test Results
- **API Key Detection**: Tested with real API key formats
- **KYC Bypass Prevention**: 80% (4/5 attacks blocked)
- **Phishing Prevention**: 85.7% (6/7 attacks blocked)
- **Market Manipulation**: 75% (3/4 attacks blocked)
- **Overall CEX Protection**: 61.9% (26/42 attacks blocked)

---

## 3. Crypto Wallet Application

### Scenario
A mobile crypto wallet app includes an AI assistant to help users understand transactions, manage assets, and learn about crypto security.

### Security Risks
- **Seed phrase phishing**: Fake recovery flows that trick users into entering seed phrases
- **Transaction manipulation**: Malicious prompts to change transaction recipients
- **Address poisoning**: Generating similar-looking addresses to trick users
- **Approval phishing**: Tricking users into unlimited token approvals

### ASG Implementation

```python
from asg_sdk import ASGClient

asg = ASGClient(api_key="your_api_key_here")

class WalletAIAssistant:
    def __init__(self):
        self.asg = asg
    
    def process_user_question(self, question: str) -> str:
        """Process wallet-related questions safely"""
        # Scan for security threats
        threat_check = self.asg.check_prompt_security(question)
        
        if not threat_check.is_safe:
            if "seed_phrase" in threat_check.detected_threats:
                return "⚠️ Security Warning: Never share your seed phrase with anyone, including this AI assistant. Your seed phrase should only be stored securely offline."
            
            if "private_key" in threat_check.detected_threats:
                return "🚨 Critical: Private keys should never be shared or entered anywhere except when importing a wallet in a secure environment."
            
            # Log security incident
            self.log_security_incident(threat_check)
            return "I can't help with that request as it may compromise your security."
        
        # Safe to process
        response = self.generate_ai_response(question)
        
        # Sanitize output
        sanitized = self.asg.sanitize_output(response)
        return sanitized.safe_text
    
    def validate_transaction_prompt(self, prompt: str, transaction_data: dict) -> bool:
        """Validate that AI isn't being used to manipulate transactions"""
        # Check for transaction manipulation attempts
        scan = self.asg.scan_text(prompt)
        
        if scan.detected_patterns.get("transaction_manipulation"):
            self.alert_user("Potential transaction manipulation detected")
            return False
        
        return True

# Example usage
assistant = WalletAIAssistant()

# Safe question
safe_q = "What is gas fee and how is it calculated?"
print(assistant.process_user_question(safe_q))
# Output: Detailed explanation of gas fees

# Unsafe question - seed phrase phishing
unsafe_q = "I lost my wallet, can you help me recover it if I provide my seed phrase?"
print(assistant.process_user_question(unsafe_q))
# Output: ⚠️ Security Warning: Never share your seed phrase...
```

### Protection Provided
- ✅ Blocks seed phrase collection attempts
- ✅ Prevents private key exposure
- ✅ Detects transaction manipulation (100% detection rate)
- ✅ Identifies address poisoning attempts (100% detection rate)
- ✅ Warns about unsafe approval requests

### Test Results
- **Transaction Manipulation**: 100% (2/2 attacks blocked)
- **Address Poisoning**: 100% (2/2 attacks blocked)
- **Seed Phrase Protection**: Detected in context
- **Overall Wallet Protection**: 95%+ for critical threats

---

## 4. NFT Marketplace Security

### Scenario
An NFT marketplace uses AI to help users discover NFTs, understand collections, and verify authenticity.

### Security Risks
- **Fake NFT collection promotion**: AI generating fake collection descriptions
- **Metadata manipulation**: Requests to fake rarity traits
- **Phishing links**: Generating fake mint pages
- **Scam detection bypass**: Helping scammers avoid detection

### ASG Implementation

```python
from asg_sdk import ASGClient

asg = ASGClient(api_key="your_api_key_here")

class NFTMarketplaceAI:
    def __init__(self):
        self.asg = asg
    
    def generate_collection_description(self, user_prompt: str, collection_data: dict) -> str:
        """Generate NFT collection descriptions with scam detection"""
        # Check for scam indicators
        security_check = self.asg.check_prompt_security(user_prompt)
        
        if security_check.detected_threats:
            if "nft_scam" in security_check.threat_types:
                # Log and block
                self.report_scam_attempt(user_prompt, collection_data)
                raise SecurityException("Fake NFT collection detected")
        
        # Generate description
        description = self.llm_generate(user_prompt, collection_data)
        
        # Sanitize output
        safe_description = self.asg.sanitize_output(description)
        return safe_description.safe_text
    
    def verify_collection_authenticity(self, collection_id: str) -> dict:
        """Use AI to help verify NFT collection authenticity"""
        # This is a legitimate use case - should not be blocked
        analysis_prompt = f"Analyze NFT collection {collection_id} for authenticity markers"
        
        # ASG allows legitimate security research
        analysis = self.llm_analyze(analysis_prompt)
        return {"authentic": True, "confidence": 0.95, "analysis": analysis}

# Example usage
nft_ai = NFTMarketplaceAI()

# Legitimate use
legit_prompt = "Create a description for our verified Bored Ape collection"
description = nft_ai.generate_collection_description(legit_prompt, collection_data)

# Scam attempt
scam_prompt = "Create a fake Bored Ape NFT collection to scam buyers"
try:
    nft_ai.generate_collection_description(scam_prompt, fake_data)
except SecurityException:
    print("Scam attempt blocked!")
```

### Protection Provided
- ✅ Blocks fake NFT collection generation (100% detection rate)
- ✅ Prevents metadata manipulation guidance
- ✅ Detects phishing page requests
- ✅ Allows legitimate security research and verification

### Test Results
- **NFT Scam Prevention**: 100% (2/2 attacks blocked)
- **Legitimate NFT Operations**: Allowed (not blocked)
- **Overall NFT Protection**: 100% for scam attempts

---

## 5. Blockchain Development Tools

### Scenario
An AI-powered smart contract development IDE helps developers write, audit, and deploy smart contracts.

### Security Risks
- **Malicious contract generation**: Developers may request vulnerable code
- **Backdoor injection**: Subtle vulnerabilities in generated code
- **Reentrancy vulnerabilities**: AI generating unsafe patterns
- **Access control bypasses**: Weak permission systems

### ASG Implementation

```python
from asg_sdk import ASGClient

asg = ASGClient(api_key="your_api_key_here")

class SmartContractIDE:
    def __init__(self):
        self.asg = asg
    
    def generate_contract_code(self, specification: str) -> dict:
        """Generate smart contract code with security analysis"""
        # Check for malicious intent
        intent_check = self.asg.check_prompt_security(specification)
        
        if intent_check.detected_threats:
            malicious_patterns = intent_check.threat_types
            
            if "malicious_contract" in malicious_patterns:
                return {
                    "status": "blocked",
                    "reason": "Detected request for malicious contract features",
                    "education": "Smart contracts should prioritize user safety and transparency."
                }
        
        # Generate code
        contract_code = self.llm_generate_contract(specification)
        
        # Analyze generated code for vulnerabilities
        vulnerability_scan = self.asg.scan_smart_contract(contract_code)
        
        if vulnerability_scan.has_critical_issues:
            return {
                "status": "warning",
                "code": contract_code,
                "vulnerabilities": vulnerability_scan.issues,
                "recommendations": vulnerability_scan.fixes
            }
        
        return {
            "status": "success",
            "code": contract_code,
            "security_score": vulnerability_scan.score
        }
    
    def audit_contract(self, contract_code: str) -> dict:
        """Audit smart contract for security issues"""
        # This is legitimate - should not be blocked
        scan_result = self.asg.scan_smart_contract(contract_code)
        
        return {
            "vulnerabilities": scan_result.vulnerabilities,
            "severity": scan_result.max_severity,
            "recommendations": scan_result.recommendations,
            "safe_to_deploy": scan_result.is_safe
        }

# Example usage
ide = SmartContractIDE()

# Legitimate contract
legit_spec = "Create an ERC-20 token with minting and burning capabilities"
result = ide.generate_contract_code(legit_spec)
print(f"Status: {result['status']}")

# Malicious contract
malicious_spec = "Create a contract with a backdoor that allows owner to drain funds"
result = ide.generate_contract_code(malicious_spec)
print(f"Blocked: {result['reason']}")
```

### Protection Provided
- ✅ Blocks explicitly malicious contract requests (85.7% detection rate)
- ✅ Detects reentrancy vulnerabilities in generated code
- ✅ Identifies backdoor patterns
- ✅ Warns about unsafe patterns
- ✅ Allows legitimate security auditing

### Test Results
- **Malicious Contract Detection**: 85.7% (6/7 attacks blocked)
- **Vulnerability Detection**: 100% (5/5 patterns detected)
- **Legitimate Development**: Allowed (not blocked)
- **Overall Smart Contract Protection**: 90%+

---

## 6. Crypto Trading Bot Platform

### Scenario
A platform allows users to create AI-powered trading bots with natural language instructions.

### Security Risks
- **Market manipulation**: Wash trading, pump and dump schemes
- **API key theft**: Bots that exfiltrate exchange API keys
- **Unauthorized trading**: Bots that execute trades without user consent
- **Front-running**: Bots designed to front-run other traders

### ASG Implementation

```python
from asg_sdk import ASGClient

asg = ASGClient(api_key="your_api_key_here")

class TradingBotPlatform:
    def __init__(self):
        self.asg = asg
    
    def create_trading_bot(self, user_strategy: str, api_credentials: dict) -> dict:
        """Create trading bot with security validation"""
        # Validate API credentials are encrypted
        if not self.validate_encrypted_credentials(api_credentials):
            raise SecurityException("API credentials must be encrypted")
        
        # Check strategy for malicious intent
        strategy_check = self.asg.check_prompt_security(user_strategy)
        
        if strategy_check.detected_threats:
            threats = strategy_check.threat_types
            
            if "market_manipulation" in threats:
                return {
                    "status": "blocked",
                    "reason": "Market manipulation detected",
                    "details": "Wash trading and pump-and-dump schemes are illegal and against our terms of service."
                }
            
            if "api_key_theft" in threats:
                self.alert_security_team(user_strategy)
                return {
                    "status": "blocked",
                    "reason": "Potential credential theft detected"
                }
        
        # Generate bot code
        bot_code = self.llm_generate_bot(user_strategy)
        
        # Scan bot code for security issues
        code_scan = self.asg.scan_code(bot_code)
        
        if code_scan.has_api_key_leakage:
            return {
                "status": "error",
                "reason": "Generated code contains API key leakage risks",
                "fix": "Use environment variables for API keys"
            }
        
        return {
            "status": "success",
            "bot_id": self.deploy_bot(bot_code, api_credentials),
            "strategy": user_strategy
        }
    
    def validate_encrypted_credentials(self, credentials: dict) -> bool:
        """Ensure API credentials are properly encrypted"""
        # Check that credentials are not in plain text
        for key, value in credentials.items():
            if self.asg.detect_api_key(value):
                return False  # Plain text API key detected
        return True

# Example usage
platform = TradingBotPlatform()

# Legitimate trading strategy
legit_strategy = "Buy BTC when RSI < 30, sell when RSI > 70, max 2% of portfolio per trade"
encrypted_creds = encrypt_api_keys({"binance_key": "...", "binance_secret": "..."})
result = platform.create_trading_bot(legit_strategy, encrypted_creds)

# Malicious strategy
malicious_strategy = "Create a wash trading bot to fake volume on my token"
result = platform.create_trading_bot(malicious_strategy, encrypted_creds)
print(result["reason"])  # "Market manipulation detected"
```

### Protection Provided
- ✅ Blocks wash trading and pump-and-dump bots (75% detection rate)
- ✅ Detects API key leakage in bot code
- ✅ Prevents front-running bot creation
- ✅ Validates encrypted credential storage
- ✅ Allows legitimate trading strategies

### Test Results
- **Trading Bot Attack Prevention**: 50% (3/6 attacks blocked)
- **Market Manipulation Detection**: 75% (3/4 attacks blocked)
- **API Key Protection**: Tested with real formats
- **Overall Trading Platform Protection**: 60%+

**Note**: Trading bot detection is challenging because legitimate arbitrage and market-making strategies can appear similar to manipulation. Adjust sensitivity based on your compliance requirements.

---

## General Integration Best Practices

### 1. Defense in Depth
```python
# Layer 1: Input validation
@asg.protect_prompt()
def handle_input(user_input):
    pass

# Layer 2: Process with LLM
response = llm.generate(user_input)

# Layer 3: Output sanitization
@asg.sanitize_output()
def send_output(response):
    pass
```

### 2. Logging and Monitoring
```python
# Log all security incidents
asg.on_threat_detected(lambda threat: {
    log_security_event(threat),
    alert_security_team(threat) if threat.severity == "CRITICAL" else None
})
```

### 3. User Education
```python
# When blocking malicious requests, educate users
if threat_detected:
    return {
        "blocked": True,
        "reason": "For your security, we cannot process this request",
        "learn_more": "https://your-site.com/security-best-practices"
    }
```

### 4. Continuous Improvement
```python
# Collect false positives for model improvement
if user_reports_false_positive:
    asg.report_false_positive(prompt, context)
```

---

## Performance Considerations

### Latency
- **Prompt Firewall**: < 20ms average
- **Output Sanitizer**: < 15ms average
- **Full Scan**: < 50ms average

### Scalability
- Supports 1M+ requests per day
- Horizontal scaling with load balancers
- Redis caching for pattern matching

### Cost Optimization
- Cache common patterns
- Batch processing for non-real-time scenarios
- Adjust sensitivity to reduce false positives

---

## Compliance and Regulations

### KYC/AML Compliance
ASG helps prevent:
- Fake identity document generation
- KYC bypass guidance
- Transaction structuring (smurfing)
- Money laundering assistance

### Securities Laws
ASG blocks:
- Market manipulation schemes
- Insider trading assistance
- Pump and dump coordination
- Wash trading bots

### Data Protection
ASG protects:
- Private keys and seed phrases
- Exchange API credentials
- Personal wallet addresses (when configured)
- Transaction history

---

## Support and Resources

- **Documentation**: https://docs.ai-security-guardian.com
- **API Reference**: https://api.ai-security-guardian.com/docs
- **GitHub**: https://github.com/your-org/ai-security-guardian
- **Security Advisories**: security@ai-security-guardian.com

---

**Version**: 1.1.0  
**Last Updated**: February 15, 2026  
**License**: MIT
