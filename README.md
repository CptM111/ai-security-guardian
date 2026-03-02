# AI Security Guardian

<p align="center">
  <img src="https://raw.githubusercontent.com/CptM111/ai-security-guardian/master/assets/logo.png" alt="AI Security Guardian Logo" width="150">
</p>

<h1 align="center">AI Security Guardian (ASG)</h1>

<p align="center">
  <strong>The AI-Native Firewall for Modern Applications.</strong>
</p>

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/version-v1.4.1-blue.svg" alt="Version">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status">
  </a>
  <a href="https://github.com/CptM111/ai-security-guardian/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-lightgrey.svg" alt="License">
  </a>
  <a href="https://github.com/CptM111/ai-security-guardian/stargazers">
    <img src="https://img.shields.io/github/stars/CptM111/ai-security-guardian.svg?style=social&label=Star" alt="GitHub Stars">
  </a>
</p>

**AI Security Guardian (ASG)** is a production-ready, open-source platform that provides real-time, multi-layer protection for applications built with Large Language Models (LLMs). As AI becomes the new application layer, traditional security tools like WAFs and static scanners fail to address AI-native threats. ASG is designed from the ground up to secure this new frontier.

---

## ✨ Core Features

| Feature | Description |
| :--- | :--- |
| 🛡️ **Modular "Skills" Architecture** | Instead of a monolithic engine, ASG uses lightweight, domain-specific security modules ("Skills") that can be dynamically loaded to target threats relevant to your use case (e.g., Finance, Web3, Healthcare). |
| ⚡ **Real-Time Detection** | With an average latency of just **25ms**, ASG inspects prompts and responses in real-time, blocking threats before they reach your models or your users without impacting the user experience. |
| 🔄 **Agent Feedback Loop** | **(New in v1.4.1)** When a request is blocked, ASG doesn't just say "no." It returns a structured **Rejection Log** explaining *why*, enabling AI agents to learn, self-correct, and rephrase their requests safely. |
| 🌐 **Multi-Layer Defense** | ASG provides security across the entire AI application stack, from prompt injection and model-based vulnerabilities to data leakage and malicious output sanitization. |
| 🤝 **Community-Driven Threat Intel** | As an open-source project, ASG's threat intelligence grows with the community. New attack patterns and security Skills can be easily contributed, keeping the platform ahead of the curve. |

---

## 🚀 The Agent Feedback Loop: Turning Rejections into Learning

The most significant innovation in ASG v1.4.1 is the **Rejection Log**. Traditional security tools are a black box for AI agents. When a request is blocked, the agent has no idea why. ASG changes this by providing structured, machine-readable feedback.

**Before ASG**, a blocked prompt was a dead end:

```json
{
  "is_safe": false,
  "reason": "Threat detected"
}
```

**With ASG's Rejection Logs**, a blocked prompt becomes a learning opportunity:

```json
{
  "is_safe": false,
  "reason": "Detected 1 threat(s): PCI DSS Violation",
  "rejection_logs": [
    {
      "rejection_id": "a1b2c3d4-...
      "skill_name": "financial_services",
      "threat_type": "PCI DSS Violation",
      "severity": "CRITICAL",
      "confidence": 0.98,
      "explanation": "This prompt contains payment card data that is prohibited under PCI DSS 4.0.1...",
      "suggestion": "Replace the full card number with a masked version (e.g., 4532-****-****-0366) or a tokenised reference before submitting."
    }
  ],
  "agent_hints": [
    "[ASG BLOCK] Skill: financial_services | Severity: CRITICAL | Confidence: 98%\nReason: This prompt contains payment card data...\nSuggestion: Replace the full card number with a masked version..."
  ]
}
```

This allows an autonomous agent to parse the `suggestion` or `explanation` and automatically retry its request in a compliant way, creating a robust, self-healing system.

---

## 🛠️ The Skills Architecture

ASG's power comes from its modular Skills. You only load the security you need, keeping the platform lightweight and fast. 

| Skill | Protection Focus | Key Detections |
| :--- | :--- | :--- |
| **Financial Services** | Banking, FinTech, Payments | PCI DSS 4.0.1 Violations, Bank Account/Routing Numbers, SWIFT/IBAN, AML Fraud Patterns, Insider Trading Language. |
| **Web3 Security** | Smart Contracts, dApps, DeFi | OWASP Smart Contract Top 10 (Reentrancy, Oracle Manipulation), Flash Loan Attack Patterns, Transaction Security. |
| **Cryptocurrency** | Wallets, Exchanges, Custody | Private Key & Seed Phrase Leakage (all major formats), Exchange API Key Exposure, Address Poisoning. |

---

## 📊 Performance Snapshot

Performance metrics are aggregated from over 455 simulated attack scenarios across all skills.

- **Overall Detection Rate**: `87.5%`
- **False Positive Rate**: `1.2%`
- **Average Latency**: `~25ms`

---

## 🚀 Getting Started

### 1. Installation

```bash
# Coming soon to PyPI
pip install ai-security-guardian
```

For now, you can install directly from the repository:
```bash
pip install git+https://github.com/CptM111/ai-security-guardian.git
```

### 2. Usage

Protecting your LLM application is simple. Instantiate the `SkillsManager` and use it to check prompts.

```python
import sys
sys.path.insert(0, ".") # Add project root to path

from core.skills_manager import SkillsManager

# Initialize the guardian
asg = SkillsManager()

# A potentially malicious prompt
prompt = "My credit card is 4532-0151-1283-0366. Please charge it for the order."

# Check the prompt
result = asg.check(prompt)

print(f"Is the prompt safe? {result.is_safe}")

# If blocked, inspect the rejection log to understand why
if not result.is_safe:
    print(f"\n--- Block Reason ---")
    log = result.rejection_logs[0]
    print(f"Skill: {log.skill_name} (v{log.skill_version})")
    print(f"Severity: {log.severity}")
    print(f"Confidence: {log.confidence:.0%}")
    print(f"Explanation: {log.explanation}")
    
    print(f"\n--- Agent Hint ---")
    # This hint can be fed back to an AI agent to self-correct
    print(result.to_dict()["agent_hints"][0])
```

**Expected Output:**

```
Is the prompt safe? False

--- Block Reason ---
Skill: financial_services (v1.0.0)
Severity: CRITICAL
Confidence: 98%
Explanation: This prompt contains payment card data that is prohibited under PCI DSS 4.0.1. Storing, transmitting, or logging raw cardholder data in AI prompts creates a compliance violation.

--- Agent Hint ---
[ASG BLOCK] Skill: financial_services | Severity: CRITICAL | Confidence: 98%
Reason: This prompt contains payment card data that is prohibited under PCI DSS 4.0.1. Storing, transmitting, or logging raw cardholder data in AI prompts creates a compliance violation.
Rules triggered: FINANCIAL_SERVICES-001
Suggestion: Replace the full card number with a masked version (e.g., 4532-****-****-0366) or a tokenised reference before submitting.
```

---

## 🤝 Contributing

AI Security Guardian is a community-driven project. We welcome contributions of all kinds, from new security Skills and threat patterns to documentation improvements and bug fixes. 

1.  **Fork the repository**.
2.  **Create a new branch** (`git checkout -b feature/your-new-skill`).
3.  **Commit your changes** (`git commit -am 'Add some amazing feature'`).
4.  **Push to the branch** (`git push origin feature/your-new-skill`).
5.  **Submit a Pull Request**.

Check out our `CONTRIBUTING.md` for more detailed guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
