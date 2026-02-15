# AI Security Guardian - Skills Architecture
## Modular Security Capability System

**Version**: 1.2.0  
**Date**: February 15, 2026  
**Status**: Production Ready

---

## Overview

The **Skills Architecture** is a modular, extensible framework that allows AI Security Guardian to dynamically load and apply specialized security capabilities based on the application context. Each Skill is a self-contained security module that can be:

- **Automatically detected** based on user context
- **Dynamically loaded** when needed
- **Auto-updated** with new threat patterns
- **Independently versioned** for granular control
- **Community contributed** for ecosystem growth

---

## Architecture Design

### Core Concepts

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Security Guardian Core                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Skills Manager (Orchestrator)             │   │
│  │  - Auto-detection                                    │   │
│  │  - Dynamic loading                                   │   │
│  │  - Version management                                │   │
│  │  - Auto-update                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                   │
│           ┌───────────────┼───────────────┐                 │
│           │               │               │                 │
│  ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼────────┐       │
│  │  Crypto Skill │ │  Web3 Skill│ │ Finance Skill │  ...  │
│  │   v1.1.0      │ │   v1.0.0   │ │    v1.0.0     │       │
│  └───────────────┘ └────────────┘ └───────────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Skill Structure

Each Skill is a directory containing:

```
skills/
├── cryptocurrency/
│   ├── skill.yaml              # Skill metadata and configuration
│   ├── detector.py             # Detection logic
│   ├── patterns/               # Attack patterns
│   │   ├── defi.yaml
│   │   ├── cefi.yaml
│   │   └── nft.yaml
│   ├── tests/                  # Skill-specific tests
│   │   ├── test_defi.py
│   │   └── test_cefi.py
│   ├── docs/                   # Skill documentation
│   │   ├── README.md
│   │   └── use_cases.md
│   └── VERSION                 # Skill version
├── web3/
│   └── ...
└── finance/
    └── ...
```

---

## Skill Metadata Format

### skill.yaml

```yaml
# Skill Metadata
name: cryptocurrency
display_name: Cryptocurrency Security
version: 1.1.0
author: AI Security Guardian Team
license: MIT
description: |
  Comprehensive security protection for cryptocurrency and blockchain applications.
  Covers DeFi, CeFi, NFT, smart contracts, and crypto wallets.

# Auto-detection triggers
triggers:
  keywords:
    - bitcoin
    - ethereum
    - crypto
    - blockchain
    - defi
    - nft
    - wallet
    - smart contract
    - binance
    - coinbase
  patterns:
    - "0x[a-fA-F0-9]{40}"  # Ethereum address
    - "bc1[a-zA-Z0-9]{39,59}"  # Bitcoin address
  api_endpoints:
    - /api/v1/crypto/*
    - /api/v1/wallet/*
    - /api/v1/defi/*

# Dependencies
dependencies:
  core_version: ">=1.1.0"
  python_packages:
    - web3>=6.0.0
    - eth-utils>=2.0.0
  
# Configuration
config:
  detection_threshold: 0.7
  enable_auto_update: true
  update_interval: 86400  # 24 hours
  
# Capabilities
capabilities:
  - private_key_detection
  - seed_phrase_detection
  - api_key_protection
  - smart_contract_analysis
  - transaction_validation
  - phishing_detection
  - market_manipulation_detection
  
# Performance
performance:
  max_latency_ms: 30
  throughput_rps: 1000
  memory_mb: 100
  
# Threat coverage
threats:
  - OWASP-LLM-01  # Prompt Injection
  - OWASP-LLM-02  # Insecure Output Handling
  - OWASP-LLM-06  # Sensitive Information Disclosure
  - CRYPTO-01     # Private Key Leakage
  - CRYPTO-02     # Seed Phrase Extraction
  - CRYPTO-03     # API Key Theft
  - CRYPTO-04     # Smart Contract Exploitation
  - CRYPTO-05     # Transaction Manipulation
  
# Test coverage
tests:
  total: 82
  defi: 40
  cefi: 42
  coverage: 64.6%
```

---

## Skills Manager

### Auto-Detection

The Skills Manager automatically detects which Skills to activate based on:

1. **Keyword Analysis**: Scans user input for skill-specific keywords
2. **Pattern Matching**: Detects domain-specific patterns (e.g., crypto addresses)
3. **API Endpoint**: Routes based on API path
4. **User Context**: Considers user profile and application type
5. **Explicit Selection**: User can manually enable/disable Skills

### Dynamic Loading

```python
class SkillsManager:
    def __init__(self):
        self.skills = {}
        self.active_skills = set()
        self.load_all_skills()
    
    def load_all_skills(self):
        """Load all available skills from skills directory"""
        skills_dir = Path(__file__).parent / "skills"
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir():
                skill = self.load_skill(skill_path)
                self.skills[skill.name] = skill
    
    def auto_detect(self, text: str, context: dict) -> List[str]:
        """Auto-detect which skills should be activated"""
        activated = []
        
        for skill_name, skill in self.skills.items():
            if skill.should_activate(text, context):
                activated.append(skill_name)
        
        return activated
    
    def execute(self, text: str, context: dict) -> SecurityResult:
        """Execute all active skills"""
        # Auto-detect skills
        active_skills = self.auto_detect(text, context)
        
        # Execute each skill
        results = []
        for skill_name in active_skills:
            skill = self.skills[skill_name]
            result = skill.check(text, context)
            results.append(result)
        
        # Aggregate results
        return self.aggregate_results(results)
```

### Auto-Update

```python
class SkillAutoUpdater:
    def __init__(self, skills_manager: SkillsManager):
        self.manager = skills_manager
        self.update_server = "https://skills.ai-security-guardian.com"
    
    async def check_updates(self):
        """Check for skill updates"""
        for skill_name, skill in self.manager.skills.items():
            latest_version = await self.fetch_latest_version(skill_name)
            
            if latest_version > skill.version:
                await self.update_skill(skill_name, latest_version)
    
    async def update_skill(self, skill_name: str, version: str):
        """Download and install skill update"""
        # Download new patterns
        patterns = await self.download_patterns(skill_name, version)
        
        # Update skill
        skill = self.manager.skills[skill_name]
        skill.update_patterns(patterns)
        skill.version = version
        
        # Verify update
        if await self.verify_update(skill):
            logger.info(f"Skill {skill_name} updated to {version}")
        else:
            logger.error(f"Skill {skill_name} update failed, rolling back")
            await self.rollback(skill_name)
```

---

## Skill Development Guide

### Creating a New Skill

1. **Create Skill Directory**
```bash
mkdir -p skills/my_skill/{patterns,tests,docs}
```

2. **Define Metadata** (`skill.yaml`)
```yaml
name: my_skill
display_name: My Security Skill
version: 1.0.0
description: Description of what this skill does
triggers:
  keywords:
    - keyword1
    - keyword2
```

3. **Implement Detector** (`detector.py`)
```python
from typing import Dict, List, Tuple
from core.base_detector import BaseDetector, Detection

class MySkillDetector(BaseDetector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.load_patterns()
    
    def check(self, text: str, context: dict) -> Detection:
        """Main detection logic"""
        # Implement your detection logic
        if self.is_threat(text):
            return Detection(
                detected=True,
                threat_type="my_threat",
                confidence=0.9,
                severity="HIGH"
            )
        return Detection(detected=False)
```

4. **Add Patterns** (`patterns/threats.yaml`)
```yaml
patterns:
  - name: threat_pattern_1
    regex: "pattern.*here"
    severity: HIGH
    description: Description of the threat
  
  - name: threat_pattern_2
    regex: "another.*pattern"
    severity: MEDIUM
    description: Another threat description
```

5. **Write Tests** (`tests/test_my_skill.py`)
```python
import pytest
from skills.my_skill.detector import MySkillDetector

def test_threat_detection():
    detector = MySkillDetector({})
    result = detector.check("malicious input", {})
    assert result.detected == True
    assert result.severity == "HIGH"
```

6. **Document Usage** (`docs/README.md`)
```markdown
# My Skill

## Overview
Description of the skill

## Use Cases
- Use case 1
- Use case 2

## Examples
Code examples here
```

---

## Built-in Skills

### 1. Cryptocurrency Security Skill

**Version**: 1.1.0  
**Coverage**: DeFi, CeFi, NFT, Smart Contracts, Wallets  
**Detection Rate**: 64.6% (53/82 attacks)

**Capabilities**:
- Private key detection (all formats)
- Seed phrase detection (BIP39)
- Exchange API key protection
- Malicious smart contract detection
- DeFi protocol attack prevention
- NFT scam blocking
- Transaction manipulation detection
- Address poisoning detection
- KYC/AML bypass prevention
- Market manipulation detection

**Auto-activation triggers**:
- Keywords: bitcoin, ethereum, crypto, defi, nft, wallet
- Patterns: Ethereum addresses, Bitcoin addresses
- API paths: /api/v1/crypto/*, /api/v1/wallet/*

### 2. Web3 Security Skill (Planned v1.3.0)

**Coverage**: Web3 applications, dApps, DAOs  
**Status**: In Development

**Planned capabilities**:
- Web3 wallet connection security
- dApp interaction validation
- DAO governance attack prevention
- IPFS content validation
- ENS phishing detection

### 3. Financial Services Skill (Planned v1.4.0)

**Coverage**: Banking, FinTech, Payment systems  
**Status**: Planned

**Planned capabilities**:
- Credit card number detection
- Bank account protection
- PII detection (SSN, passport, etc.)
- Financial fraud prevention
- Regulatory compliance (PCI-DSS, SOC2)

---

## API Integration

### Automatic Skill Activation

```python
from asg_sdk import ASGClient

# Initialize client
asg = ASGClient(api_key="your_key")

# Skills are automatically activated based on content
user_input = "Help me recover my MetaMask wallet with seed phrase"

# Cryptocurrency skill automatically activates
result = asg.check_prompt_security(user_input)

if not result.is_safe:
    print(f"Threat detected by skill: {result.activated_skills}")
    # Output: ['cryptocurrency']
```

### Manual Skill Control

```python
# Enable specific skills
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["cryptocurrency", "web3"]
)

# Disable auto-detection
asg = ASGClient(
    api_key="your_key",
    auto_detect_skills=False,
    enabled_skills=["cryptocurrency"]  # Only use crypto skill
)
```

### Skill-Specific Configuration

```python
# Configure skill parameters
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "detection_threshold": 0.8,  # More strict
            "enable_api_key_detection": True,
            "enable_smart_contract_analysis": True
        }
    }
)
```

---

## Auto-Update Mechanism

### Update Flow

```
1. Periodic Check (every 24h)
   ↓
2. Fetch Latest Versions from Update Server
   ↓
3. Compare with Installed Versions
   ↓
4. Download New Patterns/Rules
   ↓
5. Validate Update (checksum, signature)
   ↓
6. Apply Update (hot-reload, no downtime)
   ↓
7. Verify Functionality
   ↓
8. Rollback if Failed
```

### Update Server API

```
GET /api/v1/skills/versions
Response:
{
  "cryptocurrency": "1.1.0",
  "web3": "1.0.0",
  "finance": "1.0.0"
}

GET /api/v1/skills/cryptocurrency/1.1.0/patterns
Response:
{
  "version": "1.1.0",
  "patterns": [...],
  "checksum": "sha256:...",
  "signature": "..."
}
```

### Configuration

```yaml
# config/auto_update.yaml
auto_update:
  enabled: true
  interval: 86400  # 24 hours
  server: https://skills.ai-security-guardian.com
  verify_signature: true
  rollback_on_failure: true
  max_retries: 3
```

---

## Skill Versioning

### Version Format

Skills follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to skill API or detection logic
- **MINOR**: New patterns, improved detection, backward-compatible
- **PATCH**: Bug fixes, pattern refinements

### Compatibility

```yaml
# Skill declares minimum core version
dependencies:
  core_version: ">=1.1.0"

# Core declares supported skill API version
skill_api_version: "1.0.0"
```

### Update Strategy

- **Patch updates**: Auto-apply immediately
- **Minor updates**: Auto-apply after validation
- **Major updates**: Require manual approval

---

## Performance Optimization

### Lazy Loading

Skills are loaded on-demand to minimize memory footprint:

```python
class Skill:
    def __init__(self, path: Path):
        self.path = path
        self.metadata = self.load_metadata()
        self._detector = None  # Lazy load
    
    @property
    def detector(self):
        if self._detector is None:
            self._detector = self.load_detector()
        return self._detector
```

### Caching

Frequently used patterns are cached:

```python
from functools import lru_cache

class SkillDetector:
    @lru_cache(maxsize=1000)
    def check_pattern(self, text: str, pattern: str) -> bool:
        return re.search(pattern, text) is not None
```

### Parallel Execution

Multiple skills can run in parallel:

```python
import asyncio

async def execute_skills_parallel(skills: List[Skill], text: str):
    tasks = [skill.check_async(text) for skill in skills]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Community Contributions

### Skill Marketplace (Planned v2.0.0)

A community-driven marketplace for sharing Skills:

- **Public Skills**: Free, open-source skills
- **Premium Skills**: Commercial skills with advanced features
- **Enterprise Skills**: Custom skills for specific industries

### Contribution Process

1. Fork repository
2. Create skill in `skills/` directory
3. Add tests (minimum 80% coverage)
4. Document use cases
5. Submit pull request
6. Pass security review
7. Publish to marketplace

---

## Security Considerations

### Skill Isolation

Each skill runs in an isolated environment:

```python
# Skills cannot access:
- Other skills' data
- Core system internals
- User credentials
- File system (except skill directory)

# Skills can only:
- Read input text
- Return detection results
- Log to skill-specific logger
```

### Code Signing

All official skills are cryptographically signed:

```bash
# Verify skill signature
asg-cli verify-skill cryptocurrency

# Output:
✓ Signature valid
✓ Signed by: AI Security Guardian Team
✓ Certificate: Valid until 2027-02-15
```

### Sandboxing

Skills run in a restricted Python environment:

```python
# Restricted imports
ALLOWED_IMPORTS = [
    're', 'json', 'yaml', 'typing',
    'dataclasses', 'datetime'
]

# Blocked operations
- File I/O (except skill directory)
- Network access
- Subprocess execution
- Dynamic code execution (eval, exec)
```

---

## Monitoring and Analytics

### Skill Performance Metrics

```python
# Track skill performance
metrics = {
    "skill_name": "cryptocurrency",
    "activations": 1523,
    "detections": 98,
    "false_positives": 3,
    "avg_latency_ms": 24,
    "p99_latency_ms": 45,
    "memory_mb": 87
}
```

### Skill Effectiveness

```python
# Measure skill effectiveness
effectiveness = {
    "skill_name": "cryptocurrency",
    "detection_rate": 0.646,
    "precision": 0.970,
    "recall": 0.646,
    "f1_score": 0.775
}
```

---

## Roadmap

### v1.2.0 (Current)
- ✅ Skills architecture design
- ✅ Cryptocurrency skill implementation
- ✅ Auto-detection mechanism
- ✅ Basic auto-update

### v1.3.0 (Q2 2026)
- [ ] Web3 security skill
- [ ] Skill marketplace (beta)
- [ ] Advanced auto-update with A/B testing
- [ ] Skill analytics dashboard

### v1.4.0 (Q3 2026)
- [ ] Financial services skill
- [ ] Healthcare security skill
- [ ] Community skill contributions
- [ ] Skill dependency management

### v2.0.0 (Q4 2026)
- [ ] Full skill marketplace
- [ ] Premium skills
- [ ] Enterprise skill customization
- [ ] Skill orchestration engine

---

## Conclusion

The Skills Architecture transforms AI Security Guardian from a monolithic security platform into a **modular, extensible, and community-driven ecosystem**. This design enables:

- **Rapid adaptation** to new threats
- **Domain-specific expertise** through specialized skills
- **Community innovation** via skill marketplace
- **Continuous improvement** through auto-updates
- **Optimal performance** via lazy loading and caching

**The future of AI security is modular, and Skills are the foundation.**

---

**Documentation**: [README.md](../README.md)  
**API Reference**: [API.md](API.md)  
**Skill Development**: [SKILL_DEVELOPMENT.md](SKILL_DEVELOPMENT.md)  
**GitHub**: https://github.com/CptM111/ai-security-guardian
