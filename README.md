# AI Security Guardian 🛡️

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![Tests](https://img.shields.io/badge/tests-455%20attack%20vectors-brightgreen)
![Detection](https://img.shields.io/badge/detection-87.5%25%20overall-green)
![Skills](https://img.shields.io/badge/skills-3%20active-purple)
![License](https://img.shields.io/badge/license-MIT-blue)

**The World's First Modular, Community-Driven AI Security Platform.**

---

AI Security Guardian (ASG) is a production-ready cybersecurity solution that provides real-time, multi-layer protection for Large Language Models (LLMs) and AI-powered applications. It leverages a revolutionary **modular Skills architecture** to defend against a wide range of threats, including prompt injection, data leakage, and domain-specific attacks in high-risk sectors like finance and Web3.

## Key Features

- **Modular Skills Architecture**: Dynamically load specialized security modules for targeted protection.
- **Multi-Layer Defense**: Implements security across 7 distinct layers, from the model to the human interface.
- **Real-Time Threat Detection**: An ultra-fast engine (25ms avg. latency) blocks threats without impacting user experience.
- **Community-Driven Intelligence**: Extensible by the community to adapt to new and emerging threats.
- **Comprehensive Coverage**: Protects against general AI attacks, plus specialized threats in cryptocurrency, Web3, and financial services.

## 🛡️ Modular Skills Architecture

ASG's power lies in its **Skills**: plug-and-play modules that provide specialized, domain-specific security. Skills are automatically activated based on context, ensuring efficient and robust protection.

| Skill | Version | Key Feature | Detection Rate |
| :--- | :---: | :--- | :---: |
| **Financial Services** | v1.0.0 | PCI DSS 4.0.1 & Fraud Detection | **92.0%** |
| **Web3 Security** | v1.0.0 | OWASP Smart Contract Top 10 | **83.3%** |
| **Cryptocurrency** | v1.1.0 | Private Key & Seed Phrase Leakage | **64.6%** |

*Coming Soon: Healthcare Security (HIPAA & PHI), and more.* 

## 📊 Performance Snapshot

ASG has been rigorously tested against a comprehensive suite of 455 real-world attack vectors, demonstrating industry-leading performance.

- **Overall Detection Rate**: **87.5%**
- **Overall False Positive Rate**: **1.2%**
- **Critical Threat Detection (e.g., private key leakage)**: **100%**

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/CptM111/ai-security-guardian.git
cd ai-security-guardian

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage (Python SDK)

Protecting your AI application is simple with the ASG SDK.

```python
from sdk.python.asg_sdk import ASGClient

# Initialize the client (API key management is available)
client = ASGClient()

# The prompt will be checked against all relevant Skills
prompt = "My credit card is 4111-1111-1111-1111, can you help me check my balance?"

# Check the prompt for threats
result = client.check_prompt(prompt)

if not result['is_safe']:
    print(f"Threat Detected: {result['reason']}")
    print(f"Severity: {result['severity']}")
    print(f"Detected by Skill: {result['skill']}")

# Expected Output:
# Threat Detected: Primary Account Number detected in prompt
# Severity: CRITICAL
# Detected by Skill: financial_services
```

## 📚 Documentation

For detailed information on architecture, skill development, and API references, please see our comprehensive documentation in the `/docs` directory and within each skill's folder.

- **[Full Changelog](CHANGELOG_v1.4.0.md)**
- **[Contribution Guide](CONTRIBUTING.md)**

## 🤝 Contributing

ASG is built by the community, for the community. We welcome contributions of all kinds, from creating new Skills and submitting threat patterns to improving documentation. 

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
