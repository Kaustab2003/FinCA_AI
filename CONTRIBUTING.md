# Contributing to FinCA AI 🤝

First off, thank you for considering contributing to FinCA AI! It's people like you that make FinCA AI such a great tool for the Indian finance community.

## 🌟 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## 🚀 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, browser)

**Example:**
```markdown
**Title:** Tax calculator shows incorrect deduction for 80C

**Description:** When entering 80C deduction > ₹1.5L, the calculator accepts it instead of capping at ₹1.5L

**Steps to Reproduce:**
1. Go to Tax Calculator
2. Enter income: ₹10,00,000
3. Enter 80C deduction: ₹2,00,000
4. Click Calculate

**Expected:** Deduction should be capped at ₹1.5L
**Actual:** Accepts ₹2L without validation
```

### Suggesting Enhancements 💡

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear and descriptive title**
- **Detailed explanation** of the proposed feature
- **Use case**: Why is this useful?
- **Mockups or examples** (if applicable)

**Example:**
```markdown
**Title:** Add FD Calculator

**Description:** Users want to compare FD returns across banks

**Use Case:** Users with lump sum amounts want to see which bank FD gives best returns

**Suggested Implementation:**
- Input: Amount, Tenure, Interest Rate
- Output: Maturity amount, Total interest
- Compare: Top 5 bank FD rates
```

### Pull Requests 🔧

1. **Fork the repository**
2. **Create a branch**:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Make your changes**
4. **Add tests** (if applicable)
5. **Update documentation** (README, docstrings)
6. **Commit with clear message**:
   ```bash
   git commit -m "feat: Add FD calculator with bank comparison"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/AmazingFeature
   ```
8. **Open a Pull Request**

## 📝 Coding Guidelines

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Good ✅
def calculate_tax(income: float, regime: str) -> dict:
    """
    Calculate income tax for FY 2024-25.
    
    Args:
        income: Annual income in rupees
        regime: 'old' or 'new' tax regime
    
    Returns:
        dict: Tax breakdown with final_tax amount
    """
    if regime == "old":
        return _calculate_old_regime(income)
    return _calculate_new_regime(income)

# Bad ❌
def calc_tax(inc, reg):  # No types, unclear names
    if reg == "old":
        return old_calc(inc)
    return new_calc(inc)
```

### Code Organization

```
src/
├── agents/          # AI agent logic
├── services/        # Business logic
├── ui/             # Streamlit interfaces
├── utils/          # Helper functions
└── config/         # Configuration
```

### Commit Message Format

Use conventional commits:

```
feat: Add feature
fix: Fix bug
docs: Update documentation
style: Code formatting
refactor: Code restructuring
test: Add tests
chore: Maintenance tasks
```

**Examples:**
```bash
feat: Add mutual fund SIP calculator
fix: Tax calculator rounding error for ₹7L income
docs: Update README with Groq setup instructions
style: Format code with black
refactor: Extract EMI calculation to utils
test: Add tests for tax deduction validation
chore: Update dependencies
```

## 🧪 Testing

Before submitting a PR, ensure:

```bash
# Run tests
pytest tests/

# Check code style
black src/
flake8 src/

# Type checking
mypy src/
```

## 📚 Documentation

- Add docstrings to all functions
- Update README.md for new features
- Add code comments for complex logic
- Update .env.example if adding new config

## 🎯 Priority Areas

We especially welcome contributions in:

1. **Indian Financial Context**
   - More accurate tax calculations
   - Additional investment options (PPF, EPF, NPS)
   - Regional language support

2. **AI Improvements**
   - Better prompt engineering
   - More specialized agents
   - Context-aware responses

3. **UI/UX Enhancements**
   - Better visualizations
   - Mobile responsiveness
   - Accessibility improvements

4. **Performance**
   - Query optimization
   - Caching strategies
   - Load time improvements

## 🐛 Good First Issues

Look for issues labeled `good-first-issue` - these are great for newcomers!

## 💬 Questions?

- Open a GitHub Discussion
- Join our Discord (coming soon)
- Email: contribute@finca-ai.com

## 🙏 Thank You!

Your contributions make FinCA AI better for everyone in the Indian finance community!

---

**Made with ❤️ in India 🇮🇳**
