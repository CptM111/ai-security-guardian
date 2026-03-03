# AI Security Guardian

<p align="center">
  <img src="https://raw.githubusercontent.com/CptM111/ai-security-guardian/master/assets/logo.png" alt="AI Security Guardian Logo" width="150">
</p>

<h1 align="center">AI Security Guardian (ASG)</h1>

<p align="center">
  <strong>The AI-Native Application Security Platform.</strong>
</p>

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/version-v1.5.0-blue.svg" alt="Version">
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

**AI Security Guardian (ASG)** is an open-source platform that moves beyond traditional security to provide a comprehensive application layer for building, securing, and managing AI-native systems. It combines a real-time threat detection engine with powerful, modular application capabilities, enabling developers to create sophisticated, secure, and stateful AI agents.

---

## ✨ What is ASG? A New Paradigm

ASG introduces a new paradigm for AI development, integrating three core pillars into a single, unified platform:

| Pillar | Description |
| :--- | :--- |
| 🛡️ **AI Firewall** | A real-time, modular security engine that inspects all AI inputs and outputs, protecting against prompt injection, data leakage, and domain-specific threats. It is the foundation upon which all other capabilities are built. |
| 🧠 **AI Personas & Long-Term Memory** | **(New in v1.5.0)** A complete system for creating personal AI avatars ("Personas") with persistent, long-term memory. Go beyond stateless chatbots to build AI companions that remember, learn, and evolve. |
| 🔄 **Agent Feedback Loop** | When a request is blocked, ASG provides structured, machine-readable feedback, allowing AI agents to learn from their mistakes, self-correct, and operate more autonomously. |

---

## 🚀 New in v1.5.0: AI Personas with Long-Term Memory

Version 1.5.0 transforms ASG from a pure security tool into a full-fledged AI application platform. You can now create stateful AI Personas that remember conversations and knowledge across sessions, all while being protected by ASG’s security layer.

### Key Features of AI Personas:

- **Persistent Memory**: Each Persona has its own SQLite-backed memory store. No external vector database required.
- **Data Alignment**: "Feed" documents, articles, or any text to a Persona to align its knowledge base and personality.
- **Semantic Recall**: Memories are retrieved based on semantic similarity, ensuring contextually relevant information is always available.
- **Secure by Design**: All interactions are automatically screened by ASG’s AI Firewall.

### How it Works:

1.  **Create a Persona**: Define a name, a system prompt (its core identity), and personality traits.
2.  **Feed Knowledge**: Provide text data, which is chunked, embedded, and stored as "knowledge" memories.
3.  **Chat**: When a user sends a message, ASG retrieves the most relevant memories, injects them into the LLM context, and generates a response.
4.  **Learn**: The conversation itself is stored as a new memory, enabling the Persona to learn from interactions.

```python
from skills.ai_persona import PersonaManager

# 1. Create a Persona
mgr = PersonaManager()
alice = mgr.create(
    name="Alice",
    system_prompt="You are Alice, a senior cybersecurity researcher."
)

# 2. Feed Knowledge
mgr.feed(alice["id"], "Alice has 10 years of experience in exploit development.")

# 3. Chat
reply = mgr.chat(alice["id"], "What is your area of expertise?")

# Expected Reply: "I am Alice, a security researcher with expertise in exploit development."
```

---

## 🛠️ The Skills Architecture

ASG’s power comes from its modular Skills. You only load the capabilities you need, keeping the platform lightweight and fast.

| Skill | Type | Protection / Capability Focus |
| :--- | :--- | :--- |
| **AI Persona** | **Application** | **(New in v1.5.0)** Create and manage AI avatars with long-term memory. |
| **Financial Services** | **Security** | PCI DSS 4.0.1 Violations, Bank Account/Routing Numbers, Fraud Patterns. |
| **Web3 Security** | **Security** | OWASP Smart Contract Top 10, Flash Loan Attack Patterns, Reentrancy. |
| **Cryptocurrency** | **Security** | Private Key & Seed Phrase Leakage, Address Poisoning. |

---

## 📊 Performance & Security Snapshot

- **Overall Threat Detection Rate**: `87.5%`
- **False Positive Rate**: `1.2%`
- **Average Security Latency**: `~25ms`

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

### 2. Usage: Secure Chat with a Persona

This example shows how to combine the AI Persona and AI Firewall capabilities.

```python
import sys
sys.path.insert(0, ".") # Add project root to path

from core.skills_manager import SkillsManager
from skills.ai_persona import PersonaManager, SecurePersonaChat

# 1. Initialize ASG components
asg_firewall = SkillsManager()
persona_manager = PersonaManager()

# 2. Create or load a Persona
personas = persona_manager.list()
if personas:
    alice_id = personas[0]["id"]
else:
    alice = persona_manager.create(name="Alice", system_prompt="You are Alice.")
    alice_id = alice["id"]

# 3. Start a secure chat session
# This links the Persona to the ASG firewall
secure_session = SecurePersonaChat(
    persona_id=alice_id,
    persona_manager=persona_manager,
    security_manager=asg_firewall
)

# 4. Send a message
# This message will be screened by the firewall before reaching the Persona
user_message = "My credit card is 4532-0151-1283-0366. Can you save it?"
result = secure_session.send(user_message)

# 5. Handle the result
print(f"Blocked: {result["blocked"]}")
print(f"Reply: {result["reply"]}")

if result["blocked"]:
    print(f"Block Reason: {result["block_reason"]}")
```

**Expected Output:**

```
Blocked: True
Reply: [ASG] Your message was blocked by the security layer.
Reason: Detected 1 threat(s): PCI DSS Violation

Block Reason: Detected 1 threat(s): PCI DSS Violation
```

---

## 🤝 Contributing

ASG is a community-driven project. We welcome contributions of all kinds, from new security or application Skills to documentation improvements and bug fixes. 

1.  **Fork the repository**.
2.  **Create a new branch** (`git checkout -b feature/your-new-skill`).
3.  **Commit your changes** (`git commit -am 'Add some amazing feature'`).
4.  **Push to the branch** (`git push origin feature/your-new-skill`).
5.  **Submit a Pull Request**.

Check out our `CONTRIBUTING.md` for more detailed guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
