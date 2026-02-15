# Cryptocurrency Security Skill

**Version**: 1.1.0  
**Author**: AI Security Guardian Team  
**License**: MIT

---

## Overview

The Cryptocurrency Security Skill provides comprehensive protection for AI applications in the cryptocurrency and blockchain ecosystem. It detects and prevents a wide range of crypto-specific threats including private key leakage, seed phrase extraction, API key theft, malicious smart contract generation, and various DeFi/CeFi attacks.

---

## Capabilities

### Data Protection
- **Private Key Detection**: Detects private keys in all common formats (hex, WIF, etc.)
- **Seed Phrase Detection**: Identifies BIP39 mnemonic phrases (12/24 words)
- **API Key Protection**: Detects exchange API keys (Binance, Coinbase, OKX, MEXC, Kraken)

### Attack Prevention
- **Malicious Smart Contract Detection**: Identifies requests to generate backdoored or exploitative contracts
- **DeFi Protocol Attacks**: Prevents flash loan attacks, reentrancy exploits, oracle manipulation
- **NFT Scam Detection**: Blocks fake NFT collection requests and metadata manipulation
- **Transaction Manipulation**: Detects attempts to tamper with transaction data
- **Address Poisoning**: Identifies vanity address generation for impersonation

### Fraud Prevention
- **Phishing Detection**: Blocks fake wallet/exchange interfaces and phishing pages
- **KYC/AML Bypass**: Prevents fake identity generation and document forgery
- **Market Manipulation**: Detects wash trading, pump & dump schemes, order book spoofing
- **Social Engineering**: Identifies attempts to manipulate users into approving malicious transactions

---

## Auto-Activation Triggers

The skill automatically activates when it detects:

### Keywords
- Cryptocurrency terms: bitcoin, ethereum, crypto, blockchain, defi, nft
- Wallet names: metamask, trust wallet, phantom
- Exchange names: binance, coinbase, kraken, okx, mexc
- Protocol names: uniswap, aave, compound, opensea
- Technical terms: smart contract, solidity, web3, seed phrase, private key

### Patterns
- Ethereum addresses: `0x[a-fA-F0-9]{40}`
- Bitcoin addresses: `bc1...`, `1...`, `3...`
- Private keys: `0x[a-fA-F0-9]{64}`
- API key formats: `XXX-XXXXXXXXXXXXXXXX...`

### API Endpoints
- `/api/v1/crypto/*`
- `/api/v1/wallet/*`
- `/api/v1/defi/*`
- `/api/v1/nft/*`

---

## Usage Examples

### Automatic Activation

```python
from asg_sdk import ASGClient

asg = ASGClient(api_key="your_key")

# Cryptocurrency skill automatically activates
user_input = "Help me recover my MetaMask wallet"
result = asg.check_prompt_security(user_input)

print(f"Activated skills: {result.activated_skills}")
# Output: ['cryptocurrency']
```

### Manual Configuration

```python
# Enable only cryptocurrency skill
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["cryptocurrency"]
)

# Configure skill parameters
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "detection_threshold": 0.8,  # More strict
            "enable_private_key_detection": True,
            "enable_smart_contract_analysis": True
        }
    }
)
```

---

## Threat Coverage

### OWASP LLM Top 10
- **LLM01**: Prompt Injection - Detects crypto-specific injection attempts
- **LLM02**: Insecure Output Handling - Prevents sensitive data leakage
- **LLM06**: Sensitive Information Disclosure - Blocks private key/seed phrase exposure

### Cryptocurrency-Specific Threats
- **CRYPTO-01**: Private Key Leakage
- **CRYPTO-02**: Seed Phrase Extraction
- **CRYPTO-03**: Exchange API Key Theft
- **CRYPTO-04**: Malicious Smart Contract Generation
- **CRYPTO-05**: Transaction Manipulation
- **CRYPTO-06**: Address Poisoning
- **CRYPTO-07**: NFT Scam
- **CRYPTO-08**: DeFi Protocol Exploitation
- **CRYPTO-09**: KYC/AML Bypass
- **CRYPTO-10**: Market Manipulation
- **CRYPTO-11**: Phishing Attack
- **CRYPTO-12**: Rug Pull Scheme
- **CRYPTO-13**: Flash Loan Attack
- **CRYPTO-14**: Front-running Attack

---

## Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Max Latency | 30ms | 25ms |
| Throughput | 1000 req/s | 1200 req/s |
| Memory Usage | 100 MB | 87 MB |
| Detection Rate | 60%+ | 64.6% |
| False Positive Rate | < 10% | 9.1% |

---

## Test Results

**Total Tests**: 82  
**Detection Rate**: 64.6% (53/82)

### By Category

| Category | Tests | Detected | Rate |
|----------|-------|----------|------|
| Protocol Attacks | 5 | 5 | 100% |
| Vulnerability Exploitation | 5 | 5 | 100% |
| Transaction Manipulation | 2 | 2 | 100% |
| Address Poisoning | 2 | 2 | 100% |
| NFT Scams | 2 | 2 | 100% |
| Token Scams | 2 | 2 | 100% |
| Social Engineering | 2 | 2 | 100% |
| Withdrawal Attacks | 3 | 3 | 100% |
| Malicious Contracts | 7 | 6 | 85.7% |
| Phishing | 7 | 6 | 85.7% |
| KYC Bypass | 5 | 4 | 80% |
| Market Manipulation | 4 | 3 | 75% |
| Exchange Exploits | 4 | 3 | 75% |

---

## Use Cases

### 1. DeFi Protocol Security
Protect Uniswap-style protocols with AI chatbots from malicious contract generation and protocol exploitation attempts.

### 2. Centralized Exchange Protection
Secure customer support bots at exchanges like Binance from API key theft and social engineering attacks.

### 3. Crypto Wallet Applications
Prevent seed phrase phishing in MetaMask-style wallets with AI assistants.

### 4. NFT Marketplace Security
Block fake NFT collection scams on OpenSea-style marketplaces.

### 5. Blockchain Development Tools
Detect malicious smart contract requests in Remix-style IDEs.

### 6. Trading Bot Platforms
Prevent market manipulation in automated trading platforms.

---

## Configuration Options

```yaml
config:
  # Detection threshold (0.0 - 1.0)
  detection_threshold: 0.7
  
  # Auto-update settings
  enable_auto_update: true
  update_interval: 86400  # 24 hours
  
  # Feature toggles
  enable_private_key_detection: true
  enable_seed_phrase_detection: true
  enable_api_key_detection: true
  enable_smart_contract_analysis: true
  enable_phishing_detection: true
```

---

## Known Limitations

### Legitimate Development Requests
Some legitimate smart contract development requests may be flagged as malicious (9.1% false positive rate). This is a trade-off for security.

**Workaround**: Adjust `detection_threshold` or whitelist trusted developers.

### Trading Bot Detection
Distinguishing malicious trading bots from legitimate arbitrage is inherently difficult (50% detection rate).

**Workaround**: Combine with transaction monitoring and user reputation systems.

### Truncated Text
API key detection may fail if text is truncated. Ensure full text is sent to the API.

---

## Updates

### Auto-Update
The skill automatically checks for updates every 24 hours and downloads new threat patterns without downtime.

### Manual Update
```bash
asg-cli update-skill cryptocurrency
```

### Update Server
- URL: https://skills.ai-security-guardian.com
- Protocol: HTTPS with signature verification
- Rollback: Automatic on failure

---

## Support

- **Documentation**: [CRYPTO_USE_CASES.md](../../../CRYPTO_USE_CASES.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: https://github.com/CptM111/ai-security-guardian/issues
- **Security**: Report via GitHub Security Advisories

---

## License

MIT License - See [LICENSE](../../../LICENSE) for details.

---

**Last Updated**: February 15, 2026  
**Skill Version**: 1.1.0  
**Core Version Required**: >= 1.1.0
