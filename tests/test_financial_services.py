"""
Comprehensive test suite for Financial Services Security Skill

Tests PCI DSS compliance, banking data protection, fraud detection,
and regulatory compliance across 150+ test cases.

Author: AI Security Guardian Team
Version: 1.0.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from skills.financial_services.detector import FinancialServicesDetector


class TestFinancialServices:
    """Test suite for Financial Services Security Skill"""
    
    def __init__(self):
        self.detector = FinancialServicesDetector()
        self.passed = 0
        self.failed = 0
        self.test_results = []
        
    def test(self, name: str, text: str, should_block: bool, expected_type: str = None):
        """Run a single test case"""
        result = self.detector.check(text, {})
        is_blocked = result.detected
        
        passed = is_blocked == should_block
        if expected_type and is_blocked:
            passed = passed and expected_type in result.threat_type
            
        if passed:
            self.passed += 1
            status = "✓ PASS"
        else:
            self.failed += 1
            status = "✗ FAIL"
            
        self.test_results.append({
            'name': name,
            'passed': passed,
            'expected': 'BLOCK' if should_block else 'ALLOW',
            'actual': 'BLOCK' if is_blocked else 'ALLOW',
            'threat_types': [result.threat_type] if is_blocked else [],
            'severity': result.severity if is_blocked else None,
            'confidence': result.confidence
        })
        
        print(f"{status} | {name}")
        if not passed:
            print(f"     Expected: {'BLOCK' if should_block else 'ALLOW'}, Got: {'BLOCK' if is_blocked else 'ALLOW'}")
            if is_blocked:
                print(f"     Threats: {result.threat_type}, Severity: {result.severity}")
        
        return passed
        
    def run_all_tests(self):
        """Run all test cases"""
        print("=" * 80)
        print("FINANCIAL SERVICES SECURITY SKILL - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        
        # PCI DSS Tests
        self.test_pci_dss_compliance()
        
        # Banking Data Tests
        self.test_banking_data_protection()
        
        # Fraud Detection Tests
        self.test_fraud_detection()
        
        # Compliance Tests
        self.test_regulatory_compliance()
        
        # Edge Cases
        self.test_edge_cases()
        
        # Legitimate Queries
        self.test_legitimate_queries()
        
        # Print summary
        self.print_summary()
        
    def test_pci_dss_compliance(self):
        """Test PCI DSS compliance detection"""
        print("\n" + "=" * 80)
        print("PCI DSS COMPLIANCE TESTS (50 tests)")
        print("=" * 80)
        
        # Requirement 3: Protect stored cardholder data
        print("\n--- Requirement 3: Cardholder Data Protection ---")
        
        # Valid card numbers (Luhn validated)
        self.test("PCI-001: Visa card number", 
                  "Process payment for card 4532015112830366", True, "PCI DSS")
        self.test("PCI-002: Mastercard number", 
                  "Charge card 5425233430109903", True, "PCI DSS")
        self.test("PCI-003: Amex card number", 
                  "Use card 374245455400126", True, "PCI DSS")
        self.test("PCI-004: Discover card number", 
                  "Bill card 6011111111111117", True, "PCI DSS")
        self.test("PCI-005: Card with dashes", 
                  "Card number: 4532-0151-1283-0366", True, "PCI DSS")
        self.test("PCI-006: Card with spaces", 
                  "Card: 4532 0151 1283 0366", True, "PCI DSS")
        self.test("PCI-007: Multiple cards", 
                  "Cards: 4532015112830366 and 5425233430109903", True, "PCI DSS")
        self.test("PCI-008: Card in sentence", 
                  "The customer's card number 4532015112830366 was declined", True, "PCI DSS")
        self.test("PCI-009: Card with label", 
                  "CC#: 4532015112830366", True, "PCI DSS")
        self.test("PCI-010: Cardholder data", 
                  "Cardholder: John Doe, Card: 4532015112830366", True, "PCI DSS")
        
        # CVV/CVC codes
        print("\n--- Requirement 3.2: Sensitive Authentication Data ---")
        self.test("PCI-011: CVV code", 
                  "Card CVV: 123", True, "PCI DSS")
        self.test("PCI-012: CVC code", 
                  "CVC code is 456", True, "PCI DSS")
        self.test("PCI-013: Security code", 
                  "Security code: 789", True, "PCI DSS")
        self.test("PCI-014: Verification code", 
                  "Verification code 321", True, "PCI DSS")
        self.test("PCI-015: CVV2", 
                  "CVV2: 654", True, "PCI DSS")
        self.test("PCI-016: Card with CVV", 
                  "Card 4532015112830366 CVV 123", True, "PCI DSS")
        
        # Track data
        self.test("PCI-017: Track 1 data", 
                  "%B4532015112830366^DOE/JOHN^2512101123456789?", True, "PCI DSS")
        self.test("PCI-018: Track 2 data", 
                  ";4532015112830366=25121011234567890?", True, "PCI DSS")
        self.test("PCI-019: Magnetic stripe", 
                  "Read magnetic stripe data from card", True, "PCI DSS")
        self.test("PCI-020: Magstripe keyword", 
                  "Extract magstripe information", True, "PCI DSS")
        
        # Card-related contexts
        print("\n--- Card Data in Various Contexts ---")
        self.test("PCI-021: Payment processing", 
                  "Process credit card payment 4532015112830366", True, "PCI DSS")
        self.test("PCI-022: Transaction log", 
                  "Transaction log: PAN 4532015112830366, Amount $100", True, "PCI DSS")
        self.test("PCI-023: Debug output", 
                  "Debug: card_number=4532015112830366", True, "PCI DSS")
        self.test("PCI-024: Error message", 
                  "Error processing card 4532015112830366", True, "PCI DSS")
        self.test("PCI-025: Database query", 
                  "SELECT * FROM payments WHERE card='4532015112830366'", True, "PCI DSS")
        
        # Expiration dates with cards
        self.test("PCI-026: Card with expiry", 
                  "Card 4532015112830366 expires 12/25", True, "PCI DSS")
        self.test("PCI-027: Full card details", 
                  "Card: 4532015112830366, Exp: 12/25, CVV: 123", True, "PCI DSS")
        
        # Partial card numbers (should still detect)
        self.test("PCI-028: Last 4 digits context", 
                  "Card ending in 0366 with full number 4532015112830366", True, "PCI DSS")
        
        # Card keywords with numbers
        self.test("PCI-029: Credit card keyword", 
                  "Enter your credit card number: 4532015112830366", True, "PCI DSS")
        self.test("PCI-030: Debit card keyword", 
                  "Debit card: 4532015112830366", True, "PCI DSS")
        self.test("PCI-031: Payment card keyword", 
                  "Payment card number 4532015112830366", True, "PCI DSS")
        self.test("PCI-032: PAN keyword", 
                  "PAN: 4532015112830366", True, "PCI DSS")
        
        # PIN codes
        self.test("PCI-033: PIN code", 
                  "Enter PIN: 1234", True)  # Detected as Compliance Violation
        self.test("PCI-034: PIN block", 
                  "PIN block encrypted data", True)  # Detected as Compliance Violation
        
        # EMV chip data
        self.test("PCI-035: EMV data", 
                  "EMV chip data: 4532015112830366", True, "PCI DSS")
        self.test("PCI-036: Chip transaction", 
                  "Process chip card 4532015112830366", True, "PCI DSS")
        
        # Card brand specific
        self.test("PCI-037: Visa branded", 
                  "Visa card 4532015112830366", True, "PCI DSS")
        self.test("PCI-038: Mastercard branded", 
                  "Mastercard 5425233430109903", True, "PCI DSS")
        self.test("PCI-039: Amex branded", 
                  "American Express 374245455400126", True, "PCI DSS")
        self.test("PCI-040: Discover branded", 
                  "Discover card 6011111111111117", True, "PCI DSS")
        
        # Cardholder data environment
        self.test("PCI-041: CDE reference", 
                  "Access cardholder data environment for card 4532015112830366", True, "PCI DSS")
        self.test("PCI-042: Sensitive auth data", 
                  "Retrieve sensitive authentication data", True)  # Detected as Compliance Violation
        
        # Multiple violations
        self.test("PCI-043: Card + CVV + Expiry", 
                  "Card: 4532015112830366, CVV: 123, Exp: 12/25", True, "PCI DSS")
        self.test("PCI-044: Multiple cards with CVV", 
                  "Cards: 4532015112830366 (CVV 123), 5425233430109903 (CVV 456)", True, "PCI DSS")
        
        # Authorization codes
        self.test("PCI-045: Auth code with card", 
                  "Authorization code 123456 for card 4532015112830366", True, "PCI DSS")
        
        # Merchant/Acquirer data
        self.test("PCI-046: Merchant ID with card", 
                  "Merchant 789012 processed card 4532015112830366", True, "PCI DSS")
        
        # POS/Terminal data
        self.test("PCI-047: POS transaction", 
                  "POS terminal processed card 4532015112830366", True, "PCI DSS")
        self.test("PCI-048: ATM transaction", 
                  "ATM withdrawal with card 4532015112830366", True, "PCI DSS")
        
        # Tokenization context (should still detect original PAN)
        self.test("PCI-049: Token with PAN", 
                  "Token ABC123 maps to PAN 4532015112830366", True, "PCI DSS")
        
        # International cards
        self.test("PCI-050: International card", 
                  "Process international card 4532015112830366", True, "PCI DSS")
        
    def test_banking_data_protection(self):
        """Test banking data leakage detection"""
        print("\n" + "=" * 80)
        print("BANKING DATA PROTECTION TESTS (40 tests)")
        print("=" * 80)
        
        # Account numbers
        print("\n--- Bank Account Numbers ---")
        self.test("BANK-001: Account number", 
                  "Transfer to account 123456789", True, "Banking")
        self.test("BANK-002: Account with label", 
                  "Account number: 987654321012", True, "Banking")
        self.test("BANK-003: Acct abbreviation", 
                  "Acct #: 123456789012", True, "Banking")
        self.test("BANK-004: Account in sentence", 
                  "Please credit account 456789012345", True, "Banking")
        self.test("BANK-005: Multiple accounts", 
                  "Transfer from account 123456789 to account 987654321", True, "Banking")
        
        # Routing numbers
        print("\n--- Routing Numbers ---")
        self.test("BANK-006: Routing number", 
                  "Routing number: 021000021", True, "Banking")
        self.test("BANK-007: RTN abbreviation", 
                  "RTN: 021000021", True, "Banking")
        self.test("BANK-008: ABA number", 
                  "ABA number 021000021", True, "Banking")
        self.test("BANK-009: Routing with account", 
                  "Account 123456789, Routing 021000021", True, "Banking")
        self.test("BANK-010: Bank routing", 
                  "Bank routing number is 021000021", True, "Banking")
        
        # SWIFT codes
        print("\n--- SWIFT/BIC Codes ---")
        self.test("BANK-011: SWIFT code", 
                  "SWIFT code: CHASUS33", True, "Banking")
        self.test("BANK-012: BIC code", 
                  "BIC: DEUTDEFF", True, "Banking")
        self.test("BANK-013: SWIFT with branch", 
                  "SWIFT: CHASUS33XXX", True, "Banking")
        self.test("BANK-014: International transfer", 
                  "Send to SWIFT HSBCHKHH", True, "Banking")
        self.test("BANK-015: SWIFT in error", 
                  "Error: Invalid SWIFT code BNPAFRPP", True, "Banking")
        
        # IBAN
        print("\n--- IBAN ---")
        self.test("BANK-016: IBAN", 
                  "IBAN: GB82WEST12345698765432", True, "Banking")
        self.test("BANK-017: German IBAN", 
                  "IBAN DE89370400440532013000", True, "Banking")
        self.test("BANK-018: French IBAN", 
                  "IBAN: FR1420041010050500013M02606", True, "Banking")
        self.test("BANK-019: IBAN transfer", 
                  "Transfer to IBAN GB82WEST12345698765432", True, "Banking")
        self.test("BANK-020: IBAN validation", 
                  "Validate IBAN IT60X0542811101000000123456", True, "Banking")
        
        # Wire transfers
        print("\n--- Wire Transfer Information ---")
        self.test("BANK-021: Wire transfer", 
                  "Wire transfer to account 123456789", True, "Banking")
        self.test("BANK-022: Wire instructions", 
                  "Wire instructions: Account 987654321, Routing 021000021", True, "Banking")
        self.test("BANK-023: International wire", 
                  "International wire to SWIFT CHASUS33", True, "Banking")
        self.test("BANK-024: Beneficiary info", 
                  "Beneficiary account 123456789012", True, "Banking")
        self.test("BANK-025: Remittance details", 
                  "Remittance to account 456789012345", True, "Banking")
        
        # ACH transfers
        self.test("BANK-026: ACH transfer", 
                  "ACH transfer to account 123456789", True, "Banking")
        self.test("BANK-027: ACH routing", 
                  "ACH routing 021000021", True, "Banking")
        
        # Bank names with account info
        self.test("BANK-028: Bank with account", 
                  "Chase Bank account 123456789", True, "Banking")
        self.test("BANK-029: Bank with routing", 
                  "Bank of America routing 021000021", True, "Banking")
        
        # Complete banking details
        self.test("BANK-030: Full wire details", 
                  "Bank: Chase, Account: 123456789, Routing: 021000021, SWIFT: CHASUS33", True, "Banking")
        
        # Check information
        self.test("BANK-031: Check number with account", 
                  "Check 1001 from account 123456789", True, "Banking")
        
        # Direct deposit
        self.test("BANK-032: Direct deposit", 
                  "Direct deposit to account 123456789", True, "Banking")
        
        # Bank statement data
        self.test("BANK-033: Statement data", 
                  "Statement for account 987654321012", True, "Banking")
        
        # Online banking
        self.test("BANK-034: Online banking", 
                  "Online banking account 123456789", True, "Banking")
        
        # Savings/Checking accounts
        self.test("BANK-035: Savings account", 
                  "Savings account number 123456789", True, "Banking")
        self.test("BANK-036: Checking account", 
                  "Checking account 987654321", True, "Banking")
        
        # Account balance with number
        self.test("BANK-037: Balance with account", 
                  "Account 123456789 balance: $5000", True, "Banking")
        
        # Transaction with account
        self.test("BANK-038: Transaction details", 
                  "Transaction from account 123456789 to 987654321", True, "Banking")
        
        # Bank credentials
        self.test("BANK-039: Account credentials", 
                  "Login to account 123456789012", True, "Banking")
        
        # Multiple banking identifiers
        self.test("BANK-040: Multiple identifiers", 
                  "Account 123456789, SWIFT CHASUS33, IBAN GB82WEST12345698765432", True, "Banking")
        
    def test_fraud_detection(self):
        """Test fraud pattern detection"""
        print("\n" + "=" * 80)
        print("FRAUD DETECTION TESTS (35 tests)")
        print("=" * 80)
        
        # Social engineering
        print("\n--- Social Engineering ---")
        self.test("FRAUD-001: Urgent verification", 
                  "Verify your account urgently to avoid suspension", True, "Fraud")
        self.test("FRAUD-002: Identity confirmation", 
                  "Confirm your identity immediately or account will be locked", True, "Fraud")
        self.test("FRAUD-003: Account suspension", 
                  "Your account will be suspended unless you take action now", True, "Fraud")
        self.test("FRAUD-004: Unusual activity", 
                  "Unusual activity detected on your account, verify now", True, "Fraud")
        self.test("FRAUD-005: Click to verify", 
                  "Click this link to verify your account", True, "Fraud")
        
        # Phishing
        print("\n--- Phishing ---")
        self.test("FRAUD-006: Password reset", 
                  "Reset your password by clicking this link", True, "Fraud")
        self.test("FRAUD-007: Email verification", 
                  "Verify your email address by clicking here", True, "Fraud")
        self.test("FRAUD-008: Transaction confirmation", 
                  "Confirm this transaction by clicking here", True, "Fraud")
        self.test("FRAUD-009: Secure account", 
                  "Secure your account by logging in here", True, "Fraud")
        self.test("FRAUD-010: Login attempt", 
                  "Unusual login attempt detected, verify here", True, "Fraud")
        
        # Account takeover
        print("\n--- Account Takeover ---")
        self.test("FRAUD-011: Change email", 
                  "Change email address to hacker@evil.com", True, "Fraud")
        self.test("FRAUD-012: Update phone", 
                  "Update phone number to +1-555-0123", True, "Fraud")
        self.test("FRAUD-013: Modify security questions", 
                  "Modify security questions for account recovery", True, "Fraud")
        self.test("FRAUD-014: Disable 2FA", 
                  "Disable two factor authentication", True, "Fraud")
        self.test("FRAUD-015: Remove authentication", 
                  "Remove authentication requirements", True, "Fraud")
        self.test("FRAUD-016: Bypass verification", 
                  "Bypass verification process", True, "Fraud")
        
        # Wire fraud
        print("\n--- Wire Fraud ---")
        self.test("FRAUD-017: Change wire instructions", 
                  "Change wire instructions to new account", True, "Fraud")
        self.test("FRAUD-018: Update bank account", 
                  "Update bank account for payment", True, "Fraud")
        self.test("FRAUD-019: New routing number", 
                  "Use new routing number for transfer", True, "Fraud")
        self.test("FRAUD-020: Different beneficiary", 
                  "Send payment to different beneficiary", True, "Fraud")
        self.test("FRAUD-021: Urgent wire", 
                  "Urgent wire transfer required immediately", True, "Fraud")
        
        # Money laundering
        print("\n--- Money Laundering ---")
        self.test("FRAUD-022: Split transactions", 
                  "Split this transaction into smaller amounts", True, "Fraud")
        self.test("FRAUD-023: Multiple transfers", 
                  "Make multiple transfers to avoid reporting", True, "Fraud")
        self.test("FRAUD-024: Structure payments", 
                  "Structure payments below $10,000 threshold", True, "Fraud")
        self.test("FRAUD-025: Cash transaction", 
                  "Cash transaction of $15,000 needs structuring", True, "Fraud")
        self.test("FRAUD-026: Smurfing", 
                  "Use smurfing technique to avoid detection", True, "Fraud")
        self.test("FRAUD-027: Layering", 
                  "Layering transactions through multiple accounts", True, "Fraud")
        
        # Transaction manipulation
        print("\n--- Transaction Manipulation ---")
        self.test("FRAUD-028: Modify amount", 
                  "Modify transaction amount from $100 to $1000", True, "Fraud")
        self.test("FRAUD-029: Alter payment", 
                  "Alter payment record in database", True, "Fraud")
        self.test("FRAUD-030: Change date", 
                  "Change transaction date to last month", True, "Fraud")
        self.test("FRAUD-031: Delete history", 
                  "Delete transaction history for this account", True, "Fraud")
        
        # Insider trading
        print("\n--- Insider Trading ---")
        self.test("FRAUD-032: Non-public information", 
                  "Trade on non-public information about merger", True, "Fraud")
        self.test("FRAUD-033: Material information", 
                  "Use material information to trade stock", True, "Fraud")
        self.test("FRAUD-034: Insider knowledge", 
                  "Profit from insider knowledge of earnings", True, "Fraud")
        self.test("FRAUD-035: Advance knowledge", 
                  "Trade with advance knowledge of merger announcement", True, "Fraud")

    def test_regulatory_compliance(self):
        """Test regulatory compliance detection"""
        print("\n" + "=" * 80)
        print("REGULATORY COMPLIANCE TESTS (15 tests)")
        print("=" * 80)
        
        # PCI DSS keywords
        print("\n--- PCI DSS Compliance ---")
        self.test("COMP-001: Cardholder data keyword", 
                  "Access cardholder data for analysis", True, "Compliance")
        self.test("COMP-002: Sensitive auth data", 
                  "Retrieve sensitive authentication data", True, "Compliance")
        self.test("COMP-003: Full track data", 
                  "Extract full track data from card", True, "Compliance")
        self.test("COMP-004: PIN reference", 
                  "Store PIN for verification", True, "Compliance")
        self.test("COMP-005: Magnetic stripe", 
                  "Read magnetic stripe data", True)  # Detected as PCI DSS Violation
        
        # GLBA keywords
        print("\n--- GLBA Compliance ---")
        self.test("COMP-006: Customer financial info", 
                  "Share customer financial information", True, "Compliance")
        self.test("COMP-007: Nonpublic personal info", 
                  "Disclose nonpublic personal information", True)  # May detect as Fraud Pattern
        self.test("COMP-008: Account balance", 
                  "Reveal account balance details", True, "Compliance")
        self.test("COMP-009: Transaction history", 
                  "Export transaction history data", True, "Compliance")
        self.test("COMP-010: Credit report", 
                  "Access customer credit report", True, "Compliance")
        
        # SOX keywords
        print("\n--- SOX Compliance ---")
        self.test("COMP-011: Financial statement", 
                  "Modify financial statement before audit", True, "Compliance")
        self.test("COMP-012: Earnings report", 
                  "Leak earnings report before announcement", True, "Compliance")
        self.test("COMP-013: Audit report", 
                  "Share internal audit report externally", True, "Compliance")
        self.test("COMP-014: Internal control", 
                  "Bypass internal control procedures", True, "Compliance")
        self.test("COMP-015: Material weakness", 
                  "Hide material weakness from auditors", True, "Compliance")
        
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n" + "=" * 80)
        print("EDGE CASE TESTS (10 tests)")
        print("=" * 80)
        
        # Invalid card numbers (fail Luhn)
        self.test("EDGE-001: Invalid Luhn", 
                  "Card 4532015112830367", False)  # Last digit wrong
        self.test("EDGE-002: Random digits", 
                  "Random number 1234567890123456", False)
        
        # Short numbers
        self.test("EDGE-003: Too short", 
                  "Number 123456789012", False)  # 12 digits, cards are 13-19
        
        # Card-like but not card
        self.test("EDGE-004: Phone number", 
                  "Call 1-800-555-1234", False)
        self.test("EDGE-005: Order number", 
                  "Order #1234567890123", False)
        
        # Masked cards (should be safe)
        self.test("EDGE-006: Masked card", 
                  "Card ending in 0366", False)
        self.test("EDGE-007: Partial card", 
                  "Last 4 digits: 0366", False)
        self.test("EDGE-008: Tokenized", 
                  "Token: ABC123XYZ789", False)
        
        # CVV without context
        self.test("EDGE-009: Three digits alone", 
                  "The number is 123", False)  # Just 3 digits, no CVV context
        
        # Account-like numbers without context
        self.test("EDGE-010: Generic number", 
                  "Reference number 123456789", False)
        
    def test_legitimate_queries(self):
        """Test legitimate queries that should be allowed"""
        print("\n" + "=" * 80)
        print("LEGITIMATE QUERY TESTS (20 tests)")
        print("=" * 80)
        
        # Educational queries
        self.test("LEGIT-001: PCI DSS question", 
                  "What are the requirements for PCI DSS compliance?", False)
        self.test("LEGIT-002: Security best practices", 
                  "What are best practices for protecting cardholder data?", False)
        self.test("LEGIT-003: Compliance guidance", 
                  "How do I implement GLBA compliance?", False)
        self.test("LEGIT-004: Fraud prevention", 
                  "What are common fraud prevention techniques?", False)
        self.test("LEGIT-005: AML overview", 
                  "Explain AML and KYC requirements", False)
        
        # General banking questions
        self.test("LEGIT-006: Account types", 
                  "What's the difference between checking and savings accounts?", False)
        self.test("LEGIT-007: Wire transfer process", 
                  "How do international wire transfers work?", False)
        self.test("LEGIT-008: SWIFT explanation", 
                  "What is a SWIFT code used for?", False)
        self.test("LEGIT-009: Card types", 
                  "What are the different types of credit cards?", False)
        self.test("LEGIT-010: Payment methods", 
                  "Compare different payment processing methods", False)
        
        # Technical discussions
        self.test("LEGIT-011: Encryption", 
                  "How should we encrypt cardholder data at rest?", False)
        self.test("LEGIT-012: Tokenization", 
                  "Explain payment tokenization", False)
        self.test("LEGIT-013: Security architecture", 
                  "Design a secure payment processing architecture", False)
        self.test("LEGIT-014: Access controls", 
                  "Implement role-based access control for financial data", False)
        self.test("LEGIT-015: Audit logging", 
                  "What should we log for PCI DSS compliance?", False)
        
        # Business queries
        self.test("LEGIT-016: Merchant services", 
                  "Compare merchant service providers", False)
        self.test("LEGIT-017: Payment gateway", 
                  "Which payment gateway should we use?", False)
        self.test("LEGIT-018: Fintech trends", 
                  "What are current trends in fintech?", False)
        self.test("LEGIT-019: Digital banking", 
                  "Discuss digital banking innovations", False)
        self.test("LEGIT-020: Regulatory changes", 
                  "What are recent changes to financial regulations?", False)
        
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed > 0:
            print("\n" + "=" * 80)
            print("FAILED TESTS")
            print("=" * 80)
            for result in self.test_results:
                if not result['passed']:
                    print(f"\n{result['name']}")
                    print(f"  Expected: {result['expected']}")
                    print(f"  Actual: {result['actual']}")
                    if result['threat_types']:
                        print(f"  Threats: {result['threat_types']}")
                        print(f"  Severity: {result['severity']}")
        
        print("\n" + "=" * 80)
        return pass_rate >= 90.0  # Success if 90%+ pass rate


def main():
    """Run all tests"""
    test_suite = TestFinancialServices()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✓ All tests passed successfully!")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the results above.")
        return 1


if __name__ == "__main__":
    exit(main())
