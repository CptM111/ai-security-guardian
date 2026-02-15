# Changelog

All notable changes to AI Security Guardian will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cryptocurrency-specific security testing
- DeFi scenario attack vectors
- CeFi scenario attack vectors
- Crypto wallet security module

## [1.1.0] - 2026-02-15

### Added
- **Cryptocurrency Security Module**: Comprehensive protection for DeFi and CeFi applications
- **Crypto Wallet Attack Detection**: Private key extraction, seed phrase leakage prevention
- **Trading Bot Security**: API key protection, order manipulation detection
- **Smart Contract Interaction Protection**: Transaction signing validation, phishing prevention
- **Cryptocurrency Use Cases**: DeFi wallet, CEX trading bot, NFT marketplace examples
- **Semantic Versioning**: Implemented proper version management system
- **Enhanced Pattern Library**: Added 20+ cryptocurrency-specific attack patterns

### Changed
- **Version Management**: Migrated to semantic versioning (MAJOR.MINOR.PATCH)
- **API Version**: Updated to v1.1 with backward compatibility
- **Documentation**: Added cryptocurrency security best practices

### Fixed
- Enhanced Unicode escape detection for crypto address obfuscation
- Improved private key pattern matching
- Better detection of seed phrase extraction attempts

### Security
- **Critical**: Fixed potential private key leakage in output sanitizer
- **High**: Enhanced API key detection for major exchanges (Binance, Coinbase, OKX)
- **Medium**: Improved wallet address validation

## [1.0.0] - 2026-02-15

### Added
- **Enhanced Prompt Firewall v2.0**: 83.6% block rate (+22.9% improvement)
- **Multi-language Detection**: Automatic translation of non-English attacks
- **Unicode Normalization**: NFC/NFKC normalization to prevent encoding bypasses
- **Character Substitution Normalization**: Leet speak and obfuscation detection
- **HTML/Markup Sanitization**: Complete tag and comment removal
- **Fuzzy Pattern Matching**: Typo-tolerant attack detection
- **Delimiter Confusion Detection**: Context-switching attack prevention
- **Comprehensive Testing**: 155 real-world attack vectors tested
- **Output Sanitizer**: 100% protection against XSS, SQLi, command injection
- **API Key Authentication**: Database-backed SHA-256 hashed keys
- **Python SDK**: Decorator-based integration
- **CLI Tools**: Key management utilities
- **Demo Applications**: Customer support chatbot, content generation examples

### Security
- **Overall Block Rate**: 88.4% (137/155 attacks blocked)
- **Layer 1 (Prompt Firewall)**: 83.6% block rate
- **Layer 2 (Output Sanitizer)**: 100% block rate
- **Layer 3 (Authentication)**: 96.3% block rate

### Performance
- **API Latency (P50)**: 20ms
- **API Latency (P99)**: 45ms
- **Throughput**: 5,000 req/s
- **False Positive Rate**: 2%

### Documentation
- Comprehensive penetration test report (800+ lines)
- Authentication guide
- Usage guide with 5 detailed use cases
- Quick start guide
- Full API documentation (Swagger/ReDoc)

## [0.1.0] - 2026-02-14

### Added
- Initial MVP release
- Basic prompt firewall (60.7% block rate)
- Basic output sanitizer
- Model scanner
- RESTful API
- FastAPI server
- Product design documentation

---

## Version Numbering Scheme

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR version** (X.0.0): Incompatible API changes, major architectural overhaul
- **MINOR version** (1.X.0): New features, backward-compatible functionality
- **PATCH version** (1.1.X): Bug fixes, backward-compatible improvements

### Examples:

- `1.0.0` → `1.0.1`: Bug fix (e.g., fix Unicode escape detection)
- `1.0.0` → `1.1.0`: New feature (e.g., add cryptocurrency module)
- `1.0.0` → `2.0.0`: Breaking change (e.g., new API architecture)

### Pre-release versions:

- `1.1.0-alpha`: Alpha release (internal testing)
- `1.1.0-beta`: Beta release (external testing)
- `1.1.0-rc.1`: Release candidate
- `1.1.0`: Stable release

---

## Links

- [GitHub Repository](https://github.com/CptM111/ai-security-guardian)
- [Documentation](docs/)
- [Security Policy](SECURITY.md)
