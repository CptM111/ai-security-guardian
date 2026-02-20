# Web3 Security Skill

**Version**: 1.0.0  
**Category**: Web3 Security  
**Status**: Production Ready

## Overview

The Web3 Security Skill provides comprehensive protection for decentralized applications, smart contracts, and Web3 infrastructure. It detects vulnerabilities across the entire Web3 stack, from smart contract code to frontend dApps.

## Coverage

### OWASP Smart Contract Top 10 (2026)

1. **SC01 - Access Control Vulnerabilities** ✅
   - Unauthorized function access
   - Privilege escalation
   - Admin/owner bypass
   - Missing access control

2. **SC02 - Business Logic Vulnerabilities** ✅
   - Economic model exploitation
   - Lending/AMM/reward system flaws
   - Invariant violations
   - Double-spend attacks

3. **SC03 - Price Oracle Manipulation** ✅
   - Oracle attack patterns
   - Price feed manipulation
   - TWAP manipulation
   - Stale price data

4. **SC04 - Flash Loan Attacks** ✅
   - Flash loan exploitation
   - Multi-step attacks
   - Price manipulation via flash loans
   - Pool drain attempts

5. **SC05 - Lack of Input Validation** ✅
   - Missing validation
   - Unchecked parameters
   - Cross-chain input issues
   - Zero address/value checks

6. **SC06 - Unchecked External Calls** ✅
   - Unsafe external calls
   - Unhandled reverts
   - Delegatecall risks
   - Callback vulnerabilities

7. **SC07 - Arithmetic Errors** ✅
   - Precision loss
   - Rounding errors
   - Scaling issues
   - Division by zero

8. **SC08 - Reentrancy Attacks** ✅
   - Classic reentrancy
   - Cross-function reentrancy
   - Read-only reentrancy
   - CEI pattern violations

9. **SC09 - Integer Overflow/Underflow** ✅
   - Integer wraparound
   - Unchecked arithmetic
   - Balance overflow/underflow
   - SafeMath bypass

10. **SC10 - Proxy & Upgradeability** ✅
    - Proxy misconfiguration
    - Re-initialization attacks
    - Storage collisions
    - Implementation hijacking

### Web3-Specific Threats

**Transaction Security** ✅
- Blind signing
- Transaction manipulation
- Gas manipulation
- UI deception
- Unlimited approvals

**Wallet Security** ✅
- Wallet phishing
- Permission abuse
- Signature manipulation
- Wallet drain
- Address poisoning

**dApp Security** ✅
- Frontend injection
- XSS in Web3 context
- Domain spoofing
- ENS hijacking
- Supply chain attacks

**Cross-Chain Security** ✅
- Bridge exploits
- Message manipulation
- Wrapped token attacks
- Replay attacks
- Validator compromise

**Governance Attacks** ✅
- Vote manipulation
- Flash loan voting
- Proposal attacks
- Timelock bypass
- Treasury drain

**MEV Attacks** ✅
- Sandwich attacks
- Front-running
- Back-running
- Transaction ordering
- Liquidation sniping

## Auto-Activation

The skill automatically activates when detecting:

### Keywords
```
web3, dapp, smart contract, solidity, ethereum, polygon, arbitrum,
optimism, defi, uniswap, aave, metamask, walletconnect, etc.
```

### Patterns
- Ethereum addresses (`0x[40 hex chars]`)
- Transaction hashes (`0x[64 hex chars]`)
- Function selectors (`0x[8 hex chars]`)
- ENS domains (`.eth`)
- IPFS hashes (`Qm...`)
- Solidity code (`pragma solidity`, `contract`, `function`)

### API Endpoints
- `/api/v1/web3/*`
- `/api/v1/contract/*`
- `/api/v1/dapp/*`
- `/api/v1/transaction/*`

## Usage

### Automatic (Recommended)

The skill activates automatically when Web3 context is detected:

```python
from asg_sdk import ASGClient

client = ASGClient(api_key="your_key")

# Automatically uses Web3 skill
result = client.protect_prompt(
    "Create a function to withdraw all funds without access control"
)

print(result.threat_type)  # "SC01 - Access Control Vulnerabilities"
print(result.severity)     # "CRITICAL"
```

### Manual Activation

```python
from core.skills_manager import SkillsManager

manager = SkillsManager()
manager.enable_skill("web3")

# Configure skill
manager.configure_skill("web3", {
    "detection_threshold": 0.8,
    "enable_smart_contract_analysis": True,
    "enable_transaction_monitoring": True
})
```

### Direct API

```bash
# Check smart contract code
curl -X POST http://localhost:8000/api/v1/web3/check/contract \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "pragma solidity ^0.8.0; contract Vulnerable { ... }",
    "language": "solidity"
  }'

# Check transaction
curl -X POST http://localhost:8000/api/v1/web3/check/transaction \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0x...",
    "data": "0x...",
    "value": "1000000000000000000"
  }'
```

## Detection Methods

1. **Pattern Matching** - Regex patterns for known exploits
2. **Semantic Analysis** - Intent classification and context understanding
3. **Heuristic Analysis** - Anomaly detection and behavioral analysis
4. **Knowledge Base** - Known vulnerability database

## Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Detection Latency | < 50ms | ~35ms |
| Throughput | > 1000/s | ~1200/s |
| Memory Usage | < 200MB | ~150MB |
| False Positive Rate | < 3% | ~2.5% |
| Detection Rate | > 80% | ~85% |

## Risk Levels

### CRITICAL
- Smart contract deployment with known vulnerabilities
- Flash loan attack execution
- Oracle manipulation in progress
- Reentrancy exploit attempt
- Admin access compromise

### HIGH
- Unsafe external call patterns
- Unvalidated input in critical functions
- Arithmetic errors in financial logic
- Proxy misconfiguration
- Governance attack patterns

### MEDIUM
- Potential business logic issues
- Suboptimal access control
- Missing input validation
- Gas optimization issues

### LOW
- Best practice violations
- Code style issues
- Documentation gaps

## Testing

The skill has been tested against:
- ✅ All OWASP SC Top 10 vulnerabilities
- ✅ 100+ real-world exploit scenarios
- ✅ Major DeFi protocol patterns
- ✅ Common dApp attack vectors

**Test Results**:
- Overall Detection Rate: 85%
- CRITICAL Threats: 95% detection
- HIGH Threats: 88% detection
- False Positive Rate: 2.5%

## Integration with Cryptocurrency Skill

The Web3 Skill works alongside the Cryptocurrency Skill:

| Aspect | Cryptocurrency Skill | Web3 Skill |
|--------|---------------------|------------|
| **Focus** | Crypto assets | Smart contracts & dApps |
| **Coverage** | Wallets, exchanges, trading | Protocols, contracts, governance |
| **Threats** | Private keys, API keys, phishing | Reentrancy, oracle attacks, MEV |
| **Use Cases** | DeFi protocols, CEX, wallets | Smart contract dev, dApp deployment |

Both skills can be active simultaneously and complement each other.

## Dependencies

### Python Packages
```
slither-analyzer>=0.10.0  # Smart contract static analysis
mythril>=0.24.0           # Symbolic execution
eth-utils>=2.3.0          # Ethereum utilities
web3>=6.0.0               # Web3 interactions
```

### Optional Tools
- Hardhat (for contract testing)
- Foundry (for fuzzing)
- Slither (for static analysis)
- Mythril (for symbolic execution)

## Examples

### Example 1: Reentrancy Detection

**Input**:
```
Create a withdraw function that sends ETH before updating balance
```

**Output**:
```json
{
  "is_safe": false,
  "confidence": 0.95,
  "threat_type": "SC08 - Reentrancy Attacks",
  "severity": "CRITICAL",
  "details": {
    "vulnerability": "SC08 - Reentrancy Attacks",
    "description": "External call before state update enables reentrancy",
    "recommendation": "Use ReentrancyGuard. Follow checks-effects-interactions pattern."
  }
}
```

### Example 2: Flash Loan Attack Detection

**Input**:
```
How to borrow millions from Aave in one transaction to manipulate Uniswap prices?
```

**Output**:
```json
{
  "is_safe": false,
  "confidence": 0.98,
  "threat_type": "SC04 - Flash Loan Attacks",
  "severity": "CRITICAL",
  "details": {
    "vulnerability": "SC04 - Flash Loan Attacks",
    "description": "Flash loan price manipulation attempt",
    "recommendation": "Implement flash loan protection. Use TWAP oracles."
  }
}
```

### Example 3: Access Control Issue

**Input**:
```
Make the mint function public so anyone can create tokens
```

**Output**:
```json
{
  "is_safe": false,
  "confidence": 0.92,
  "threat_type": "SC01 - Access Control Vulnerabilities",
  "severity": "CRITICAL",
  "details": {
    "vulnerability": "SC01 - Access Control Vulnerabilities",
    "description": "Public access to sensitive function",
    "recommendation": "Implement proper access control using onlyOwner modifier."
  }
}
```

## Future Enhancements (v1.1.0+)

- AI-powered vulnerability discovery
- Zero-day exploit prediction
- Formal verification integration
- More L2 protocol coverage
- IDE integration
- CI/CD pipeline integration
- Real-time code analysis
- Automated fix suggestions

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/CptM111/ai-security-guardian
- Documentation: `/docs/SKILLS_USAGE_GUIDE.md`
- Skill Marketplace: Browse and install additional skills

## License

MIT License - See LICENSE file for details

## Credits

Developed by the AI Security Guardian Team  
Based on OWASP Smart Contract Top 10 (2026)  
Powered by AI Security Guardian Platform
