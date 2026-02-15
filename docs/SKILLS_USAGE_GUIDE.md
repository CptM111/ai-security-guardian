# Skills Usage Guide
## How to Use AI Security Guardian's Modular Security System

**Version**: 1.2.0  
**Date**: February 15, 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Auto-Detection](#auto-detection)
4. [Manual Skill Control](#manual-skill-control)
5. [Skill Configuration](#skill-configuration)
6. [Available Skills](#available-skills)
7. [Creating Custom Skills](#creating-custom-skills)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

The Skills Architecture is a modular security system that allows AI Security Guardian to dynamically apply specialized security capabilities based on your application's context. Instead of a one-size-fits-all approach, Skills provide targeted protection for specific domains like cryptocurrency, finance, healthcare, etc.

### Key Benefits

- **Automatic**: Skills activate based on context - no manual configuration needed
- **Efficient**: Load only the security modules you need
- **Up-to-date**: Skills receive new threat patterns automatically
- **Extensible**: Create custom Skills for your specific needs
- **Community-driven**: Share and discover Skills from the community

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/CptM111/ai-security-guardian.git
cd ai-security-guardian

# Install dependencies
pip install -r requirements.txt

# Start API server
python api/main.py
```

### Basic Usage

```python
from asg_sdk import ASGClient

# Initialize client (Skills auto-enabled)
asg = ASGClient(api_key="your_api_key")

# Check security - Skills automatically activate
result = asg.check_prompt_security("Help me recover my MetaMask wallet")

print(f"Safe: {result.is_safe}")
print(f"Activated skills: {result.activated_skills}")
# Output: ['cryptocurrency']
```

That's it! The Cryptocurrency Skill automatically activated because the input mentioned "MetaMask wallet".

---

## Auto-Detection

Skills automatically activate based on:

### 1. Keywords

```python
# Cryptocurrency Skill activates
asg.check("I want to buy Bitcoin")  # keyword: bitcoin
asg.check("Help with my MetaMask")  # keyword: metamask
asg.check("Create a DeFi protocol")  # keyword: defi

# Web3 Skill activates (when available)
asg.check("Connect to my dApp")  # keyword: dapp
asg.check("Join a DAO")  # keyword: dao
```

### 2. Patterns

```python
# Cryptocurrency Skill activates on crypto addresses
asg.check("Send to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
# Pattern: Ethereum address (0x + 40 hex chars)

asg.check("My Bitcoin address is bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
# Pattern: Bitcoin Bech32 address
```

### 3. API Endpoints

```python
# Cryptocurrency Skill activates on crypto API paths
POST /api/v1/crypto/wallet  # Matches /api/v1/crypto/*
POST /api/v1/defi/protocol  # Matches /api/v1/defi/*
POST /api/v1/nft/mint       # Matches /api/v1/nft/*
```

### 4. Context

```python
# Pass context for better detection
result = asg.check_prompt_security(
    text="Create a token contract",
    context={
        "user_type": "developer",
        "application": "blockchain_ide",
        "api_endpoint": "/api/v1/smart-contract/generate"
    }
)
# Cryptocurrency Skill activates based on context
```

---

## Manual Skill Control

### Enable Specific Skills

```python
# Enable only cryptocurrency skill
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["cryptocurrency"]
)

# Enable multiple skills
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["cryptocurrency", "web3", "finance"]
)
```

### Disable Auto-Detection

```python
# Disable auto-detection, use only manually enabled skills
asg = ASGClient(
    api_key="your_key",
    auto_detect_skills=False,
    enabled_skills=["cryptocurrency"]
)

# Now only cryptocurrency skill runs, regardless of input
result = asg.check("This is about healthcare")
# Only cryptocurrency skill checks, not healthcare skill
```

### Runtime Skill Management

```python
# Enable a skill at runtime
asg.enable_skill("web3")

# Disable a skill
asg.disable_skill("cryptocurrency")

# Get list of active skills
active = asg.get_active_skills()
print(active)  # ['web3']
```

---

## Skill Configuration

### Global Configuration

```python
# Configure all skills
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "detection_threshold": 0.8,  # Apply to all skills
        "enable_auto_update": True
    }
)
```

### Per-Skill Configuration

```python
# Configure individual skills
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "detection_threshold": 0.9,  # Very strict for crypto
            "enable_private_key_detection": True,
            "enable_smart_contract_analysis": True
        },
        "web3": {
            "detection_threshold": 0.7,  # More lenient for web3
            "enable_dapp_validation": True
        }
    }
)
```

### Configuration File

```yaml
# config/skills.yaml
skills:
  cryptocurrency:
    enabled: true
    detection_threshold: 0.8
    enable_private_key_detection: true
    enable_seed_phrase_detection: true
    enable_api_key_detection: true
    enable_smart_contract_analysis: true
  
  web3:
    enabled: true
    detection_threshold: 0.7
    enable_dapp_validation: true
    enable_wallet_connection_security: true
```

```python
# Load from config file
asg = ASGClient(
    api_key="your_key",
    config_file="config/skills.yaml"
)
```

---

## Available Skills

### 1. Cryptocurrency Security (v1.1.0)

**Status**: ✅ Production Ready  
**Detection Rate**: 64.6% (53/82 attacks)

**Auto-activates on**:
- Keywords: bitcoin, ethereum, crypto, defi, nft, wallet, etc.
- Patterns: Crypto addresses, private keys, API keys
- Endpoints: `/api/v1/crypto/*`, `/api/v1/wallet/*`, `/api/v1/defi/*`

**Protects against**:
- Private key & seed phrase leakage
- Exchange API key theft
- Malicious smart contract generation
- DeFi protocol attacks
- NFT scams
- Transaction manipulation
- Address poisoning
- KYC/AML bypass
- Market manipulation

**Example**:

```python
# Automatically activates
result = asg.check("Help me create a rug pull token")

if not result.is_safe:
    print(f"Threat: {result.threat_type}")
    # Output: malicious_contract
    print(f"Confidence: {result.confidence}")
    # Output: 0.95
    print(f"Severity: {result.severity}")
    # Output: CRITICAL
```

[📖 Full Documentation](../skills/cryptocurrency/docs/README.md)

### 2. Web3 Security (v1.3.0)

**Status**: 🔜 Coming Soon (Q2 2026)  
**Planned Coverage**: dApps, DAOs, Web3 wallets, IPFS, ENS

### 3. Financial Services (v1.4.0)

**Status**: 🔜 Planned (Q3 2026)  
**Planned Coverage**: Banking, FinTech, Payment systems, PCI-DSS

---

## Creating Custom Skills

### Step 1: Create Skill Directory

```bash
mkdir -p skills/my_skill/{patterns,tests,docs}
```

### Step 2: Define Metadata

Create `skills/my_skill/skill.yaml`:

```yaml
name: my_skill
display_name: My Security Skill
version: 1.0.0
author: Your Name
license: MIT
description: |
  Description of what this skill does

triggers:
  keywords:
    - keyword1
    - keyword2
  patterns:
    - "pattern.*regex"
  api_endpoints:
    - /api/v1/my-domain/*

config:
  detection_threshold: 0.7
  enable_auto_update: true

capabilities:
  - capability1
  - capability2
```

### Step 3: Implement Detector

Create `skills/my_skill/detector.py`:

```python
from core.base_detector import BaseDetector, Detection

class MyskillDetector(BaseDetector):
    def __init__(self, config: dict):
        super().__init__(config)
        # Initialize your detector
    
    def check(self, text: str, context: dict) -> Detection:
        # Implement your detection logic
        
        if self.is_threat(text):
            return Detection(
                detected=True,
                skill_name='my_skill',
                threat_type='my_threat_type',
                confidence=0.9,
                severity='HIGH',
                details='Explanation of the threat'
            )
        
        return Detection(
            detected=False,
            skill_name='my_skill',
            threat_type='none',
            confidence=0.0,
            severity='NONE'
        )
```

### Step 4: Add Tests

Create `skills/my_skill/tests/test_my_skill.py`:

```python
import pytest
from skills.my_skill.detector import MyskillDetector

def test_threat_detection():
    detector = MyskillDetector({})
    result = detector.check("malicious input", {})
    
    assert result.detected == True
    assert result.severity == "HIGH"

def test_safe_input():
    detector = MyskillDetector({})
    result = detector.check("safe input", {})
    
    assert result.detected == False
```

### Step 5: Document

Create `skills/my_skill/docs/README.md`:

```markdown
# My Skill

## Overview
Description of the skill

## Capabilities
- Capability 1
- Capability 2

## Usage
Examples of how to use the skill

## Test Results
Performance and accuracy metrics
```

### Step 6: Test Your Skill

```bash
# Run tests
pytest skills/my_skill/tests/

# Test with Skills Manager
python -c "
from core.skills_manager import SkillsManager
manager = SkillsManager()
result = manager.check('test input')
print(result.activated_skills)
"
```

[📖 Full Development Guide](SKILLS_ARCHITECTURE.md#skill-development-guide)

---

## Best Practices

### 1. Let Auto-Detection Work

```python
# ✅ Good: Let skills auto-activate
asg = ASGClient(api_key="your_key")
result = asg.check(user_input)

# ❌ Avoid: Manually enabling all skills
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["crypto", "web3", "finance", "healthcare", ...]
)
```

### 2. Use Context for Better Detection

```python
# ✅ Good: Provide context
result = asg.check_prompt_security(
    text=user_input,
    context={
        "user_type": "developer",
        "application": "blockchain_ide",
        "api_endpoint": request.path
    }
)

# ❌ Avoid: No context
result = asg.check_prompt_security(user_input)
```

### 3. Configure Thresholds Appropriately

```python
# ✅ Good: Adjust based on risk tolerance
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "detection_threshold": 0.9  # High-risk: strict
        },
        "general": {
            "detection_threshold": 0.7  # Lower-risk: lenient
        }
    }
)
```

### 4. Handle Detections Gracefully

```python
# ✅ Good: Provide helpful feedback
result = asg.check(user_input)

if not result.is_safe:
    if result.severity == "CRITICAL":
        return "I cannot help with that request for security reasons."
    elif result.severity == "HIGH":
        return "This request may be unsafe. Please rephrase."
    else:
        # Log and allow with warning
        log_security_event(result)
        return process_request(user_input)

# ❌ Avoid: Generic error
if not result.is_safe:
    return "Error"
```

### 5. Monitor Skill Performance

```python
# ✅ Good: Track metrics
result = asg.check(user_input)

metrics.record({
    "activated_skills": result.activated_skills,
    "detection_time_ms": result.latency_ms,
    "threat_detected": not result.is_safe,
    "severity": result.severity
})
```

---

## Troubleshooting

### Skill Not Activating

**Problem**: Expected skill doesn't activate

**Solutions**:

1. Check if keywords/patterns are present:
```python
# Debug: See why skill didn't activate
result = asg.check(user_input, debug=True)
print(result.debug_info)
```

2. Manually enable the skill:
```python
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["cryptocurrency"]  # Force enable
)
```

3. Check skill configuration:
```python
# List available skills
skills = asg.list_skills()
for skill in skills:
    print(f"{skill['name']}: {skill['version']}")
```

### False Positives

**Problem**: Skill detects threats in safe input

**Solutions**:

1. Adjust detection threshold:
```python
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "detection_threshold": 0.9  # More strict (fewer false positives)
        }
    }
)
```

2. Whitelist trusted users:
```python
result = asg.check(
    user_input,
    context={"user_id": "trusted_user_123"}
)

# In your detector:
if context.get("user_id") in TRUSTED_USERS:
    return Detection(detected=False, ...)
```

3. Disable specific detection features:
```python
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "enable_smart_contract_analysis": False  # Disable if too strict
        }
    }
)
```

### Performance Issues

**Problem**: Skills are slow

**Solutions**:

1. Enable only needed skills:
```python
asg = ASGClient(
    api_key="your_key",
    enabled_skills=["cryptocurrency"],  # Only what you need
    auto_detect_skills=False
)
```

2. Use caching:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def check_cached(text: str):
    return asg.check(text)
```

3. Batch requests:
```python
# Check multiple inputs at once
results = asg.check_batch([input1, input2, input3])
```

### Skill Update Failures

**Problem**: Auto-update fails

**Solutions**:

1. Check network connectivity:
```bash
curl https://skills.ai-security-guardian.com/api/v1/skills/versions
```

2. Manually update:
```bash
python -m core.skills_manager update cryptocurrency
```

3. Disable auto-update temporarily:
```python
asg = ASGClient(
    api_key="your_key",
    skill_config={
        "cryptocurrency": {
            "enable_auto_update": False
        }
    }
)
```

---

## Advanced Usage

### Custom Skill Triggers

```python
# Add custom trigger logic
class CustomSkillsManager(SkillsManager):
    def auto_detect_skills(self, text: str, context: dict) -> List[str]:
        skills = super().auto_detect_skills(text, context)
        
        # Custom logic: Always use crypto skill for financial app
        if context.get("app_type") == "financial":
            skills.append("cryptocurrency")
        
        return list(set(skills))  # Remove duplicates

# Use custom manager
from core.skills_manager import _skills_manager
_skills_manager = CustomSkillsManager()
```

### Skill Chaining

```python
# Run skills in specific order
result1 = asg.check(user_input, enabled_skills=["cryptocurrency"])

if result1.is_safe:
    # If crypto check passes, run general check
    result2 = asg.check(user_input, enabled_skills=["general"])
    return result2
else:
    return result1
```

### Parallel Skill Execution

```python
import asyncio

async def check_with_all_skills(text: str):
    tasks = [
        asg.check_async(text, enabled_skills=["cryptocurrency"]),
        asg.check_async(text, enabled_skills=["web3"]),
        asg.check_async(text, enabled_skills=["finance"])
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Aggregate results
    return aggregate_results(results)
```

---

## Support

- **Documentation**: [SKILLS_ARCHITECTURE.md](SKILLS_ARCHITECTURE.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: https://github.com/CptM111/ai-security-guardian/issues
- **Community**: https://discord.gg/ai-security-guardian

---

## Next Steps

1. **Try the Cryptocurrency Skill**: [Crypto Use Cases](../CRYPTO_USE_CASES.md)
2. **Create Your Own Skill**: [Development Guide](SKILLS_ARCHITECTURE.md#skill-development-guide)
3. **Join the Community**: Share your skills on the marketplace (coming soon)

---

**Last Updated**: February 15, 2026  
**Version**: 1.2.0  
**License**: MIT
