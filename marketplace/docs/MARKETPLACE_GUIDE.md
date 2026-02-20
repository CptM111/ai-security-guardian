# Skill Marketplace Guide (Beta)

**Version**: 1.0.0-beta  
**Status**: Beta Release

## Overview

The AI Security Guardian Skill Marketplace is a centralized repository for discovering, installing, and managing security skills. It enables the community to share and benefit from specialized security capabilities.

## Features

### ✅ Current Features (v1.0.0-beta)

- **Skill Discovery** - Browse and search available skills
- **Easy Installation** - One-command skill installation
- **Automatic Updates** - Check and update skills
- **Skill Ratings** - Community-driven skill ratings
- **Categories** - Organized skill categories
- **CLI Interface** - Full command-line interface
- **Skill Metadata** - Detailed skill information
- **Performance Metrics** - Skill performance data
- **Test Results** - Skill test coverage and results

### 🚧 Planned Features (v1.1.0+)

- Web UI for marketplace
- Skill publishing workflow
- User reviews and comments
- Skill dependencies management
- Version pinning
- Skill analytics dashboard
- Community contributions
- Skill verification badges

## Getting Started

### Installation

The marketplace is included with AI Security Guardian v1.3.0+. No additional installation required.

### Basic Usage

```bash
# List all available skills
python tools/marketplace_cli.py list

# Search for skills
python tools/marketplace_cli.py search "web3"

# Show skill details
python tools/marketplace_cli.py show web3

# Install a skill
python tools/marketplace_cli.py install web3

# Update all skills
python tools/marketplace_cli.py update

# Show marketplace statistics
python tools/marketplace_cli.py stats
```

## CLI Reference

### `list` - List Skills

List all available skills with optional filters.

```bash
# List all skills
python tools/marketplace_cli.py list

# Filter by category
python tools/marketplace_cli.py list --category web3

# Filter by status
python tools/marketplace_cli.py list --status stable
```

**Options**:
- `--category` - Filter by skill category
- `--status` - Filter by status (stable, beta, alpha)

### `search` - Search Skills

Search for skills by name, description, or tags.

```bash
# Search for Web3 skills
python tools/marketplace_cli.py search "web3"

# Search for cryptocurrency skills
python tools/marketplace_cli.py search "crypto"

# Search for DeFi skills
python tools/marketplace_cli.py search "defi"
```

### `show` - Show Skill Details

Display detailed information about a specific skill.

```bash
# Show Web3 skill details
python tools/marketplace_cli.py show web3

# Show cryptocurrency skill details
python tools/marketplace_cli.py show cryptocurrency
```

**Displays**:
- Skill metadata (name, version, author, license)
- Description and capabilities
- Installation status
- Performance metrics
- Test results
- Dependencies
- Ratings and downloads

### `install` - Install Skill

Install a skill from the marketplace.

```bash
# Install Web3 skill
python tools/marketplace_cli.py install web3

# Force reinstall
python tools/marketplace_cli.py install web3 --force
```

**Options**:
- `--force` - Force reinstall if already installed

### `uninstall` - Uninstall Skill

Remove an installed skill.

```bash
# Uninstall Web3 skill (with confirmation)
python tools/marketplace_cli.py uninstall web3

# Skip confirmation
python tools/marketplace_cli.py uninstall web3 --yes
```

**Options**:
- `--yes` - Skip confirmation prompt

### `update` - Update Skills

Check for and install skill updates.

```bash
# Check for updates
python tools/marketplace_cli.py update

# Update specific skill
python tools/marketplace_cli.py update web3

# Update all skills without confirmation
python tools/marketplace_cli.py update --yes
```

**Options**:
- `--yes` - Skip confirmation for bulk updates

### `categories` - List Categories

Display all skill categories.

```bash
python tools/marketplace_cli.py categories
```

### `stats` - Marketplace Statistics

Show marketplace statistics.

```bash
python tools/marketplace_cli.py stats
```

**Displays**:
- Total skills
- Total categories
- Total downloads
- Average rating
- Featured skills count
- New skills count

## Python API

### Basic Usage

```python
from marketplace.marketplace_manager import SkillMarketplace

# Initialize marketplace
marketplace = SkillMarketplace()

# List all skills
skills = marketplace.list_skills()

# Search for skills
results = marketplace.search_skills("web3")

# Get skill details
skill = marketplace.get_skill("web3")

# Install skill
result = marketplace.install_skill("web3")

# Check for updates
updates = marketplace.check_updates()

# Update skill
result = marketplace.update_skill("web3")

# Uninstall skill
result = marketplace.uninstall_skill("web3")

# Rate skill
result = marketplace.rate_skill("web3", 5.0, "Excellent skill!")

# Get statistics
stats = marketplace.get_marketplace_stats()
```

### Advanced Usage

```python
# Filter by category
web3_skills = marketplace.list_skills(category="web3")

# Filter by status
stable_skills = marketplace.list_skills(status="stable")

# Check if skill is installed
is_installed = marketplace.is_installed("web3")

# Get installed version
version = marketplace.get_installed_version("web3")

# Get featured skills
featured = marketplace.get_featured_skills()

# Get popular skills
popular = marketplace.get_popular_skills(limit=5)

# Get new skills
new_skills = marketplace.get_new_skills(limit=5)
```

## Available Skills

### Cryptocurrency Security

**ID**: `cryptocurrency`  
**Version**: 1.1.0  
**Category**: Cryptocurrency  
**Status**: Stable

Comprehensive cryptocurrency security protection for DeFi protocols, centralized exchanges, wallets, and trading platforms.

**Capabilities**:
- Private key detection
- Seed phrase detection
- API key detection
- Phishing detection
- Scam detection
- Transaction analysis

**Test Results**:
- Overall Detection: 64.6%
- Critical Detection: 100%
- False Positives: 2%

### Web3 Security

**ID**: `web3`  
**Version**: 1.0.0  
**Category**: Web3 Security  
**Status**: Stable

Comprehensive Web3 security protection for decentralized applications, smart contracts, and Web3 infrastructure.

**Capabilities**:
- Smart contract analysis
- OWASP SC Top 10 detection
- Transaction security
- dApp protection
- Oracle manipulation detection
- Flash loan attack detection
- Reentrancy detection
- Governance attack prevention
- MEV detection
- Cross-chain security

**Test Results**:
- Overall Detection: 85%
- Critical Detection: 95%
- False Positives: 2.5%

## Skill Categories

### Cryptocurrency
Skills for protecting cryptocurrency assets, wallets, and trading platforms.

**Skills**: 1 (Cryptocurrency Security)

### Web3 Security
Skills for securing Web3 applications, smart contracts, and decentralized protocols.

**Skills**: 1 (Web3 Security)

### AI Security
Skills for protecting AI models, training data, and inference systems.

**Skills**: 0 (Coming soon)

### Cloud Security
Skills for securing cloud infrastructure and services.

**Skills**: 0 (Coming soon)

### Application Security
Skills for protecting web and mobile applications.

**Skills**: 0 (Coming soon)

## Skill Development

### Creating a Skill

Want to create your own skill? Follow these steps:

1. **Create skill directory**
   ```bash
   mkdir -p skills/my_skill/docs
   ```

2. **Create skill.yaml**
   ```yaml
   id: my_skill
   name: My Security Skill
   version: 1.0.0
   category: Custom
   description: My custom security skill
   author: Your Name
   license: MIT
   ```

3. **Create detector.py**
   ```python
   class MySkillDetector:
       def check(self, text: str) -> Dict:
           # Your detection logic
           pass
   ```

4. **Create documentation**
   - `docs/README.md` - Skill documentation
   - `VERSION` - Version file

5. **Test your skill**
   ```bash
   python -m pytest tests/test_my_skill.py
   ```

6. **Submit to marketplace**
   (Coming in v1.1.0)

### Skill Structure

```
skills/
└── my_skill/
    ├── skill.yaml          # Skill metadata
    ├── detector.py         # Detection logic
    ├── VERSION             # Version number
    ├── __init__.py         # Python package init
    ├── docs/
    │   └── README.md       # Documentation
    └── tests/
        └── test_detector.py # Unit tests
```

## Best Practices

### For Users

1. **Review skill details** before installation
2. **Check ratings and reviews** from community
3. **Keep skills updated** for latest protection
4. **Report issues** to skill authors
5. **Rate skills** to help others

### For Developers

1. **Follow skill structure** guidelines
2. **Write comprehensive tests** (>80% coverage)
3. **Document capabilities** clearly
4. **Optimize performance** (< 50ms latency)
5. **Keep false positives low** (< 3%)
6. **Version properly** (semantic versioning)
7. **Update regularly** with new threats

## Troubleshooting

### Skill Installation Fails

**Problem**: Skill installation fails with error.

**Solutions**:
1. Check internet connection
2. Verify skill exists: `python tools/marketplace_cli.py show SKILL_ID`
3. Check dependencies are met
4. Try force reinstall: `--force` flag
5. Check disk space

### Skill Not Activating

**Problem**: Installed skill doesn't activate automatically.

**Solutions**:
1. Verify installation: `python tools/marketplace_cli.py list`
2. Check skill triggers in `skill.yaml`
3. Restart API server
4. Check logs for errors
5. Manually enable: `SkillsManager().enable_skill("skill_id")`

### Update Check Fails

**Problem**: Cannot check for updates.

**Solutions**:
1. Check registry file exists: `marketplace/registry/skills.json`
2. Verify JSON is valid
3. Check file permissions
4. Re-download registry

## FAQ

### Q: How do I know which skills to install?

A: Start with featured skills (cryptocurrency, web3). Check ratings, downloads, and test results. Install skills relevant to your use case.

### Q: Can I install multiple skills?

A: Yes! Multiple skills can be active simultaneously. They work together to provide comprehensive protection.

### Q: How often should I update skills?

A: Check for updates weekly. Critical security updates should be installed immediately.

### Q: Are skills free?

A: Yes, all skills in the marketplace are free and open source (MIT license).

### Q: Can I create my own skill?

A: Yes! Follow the skill development guide. Skill publishing will be available in v1.1.0.

### Q: How are skills verified?

A: Currently manual review. Automated verification and badges coming in v1.1.0.

### Q: Can I use skills offline?

A: Yes, once installed. Installation and updates require internet connection.

### Q: How do I report a bug in a skill?

A: Open an issue on the skill's GitHub repository or the main ASG repository.

## Roadmap

### v1.1.0 (Q2 2026)
- Web UI for marketplace
- Skill publishing workflow
- User reviews system
- Enhanced search
- Skill analytics

### v1.2.0 (Q3 2026)
- Community contributions
- Skill verification badges
- Version pinning
- Dependency management
- Skill bundles

### v2.0.0 (Q4 2026)
- Decentralized marketplace
- On-chain skill registry
- Token-based incentives
- Skill NFTs
- DAO governance

## Support

- **Documentation**: `/docs/SKILLS_USAGE_GUIDE.md`
- **GitHub**: https://github.com/CptM111/ai-security-guardian
- **Issues**: https://github.com/CptM111/ai-security-guardian/issues
- **Discussions**: https://github.com/CptM111/ai-security-guardian/discussions

## License

The Skill Marketplace is part of AI Security Guardian and is licensed under the MIT License.

---

**Note**: This is a beta release. Features and API may change in future versions. Feedback welcome!
