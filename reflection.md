# Lab 5: Static Code Analysis — Reflection

## 1. What was found by the static analysis tools?
The baseline analysis of `flight_reservation_system.py` using Pylint, Bandit, and Flake8 revealed multiple categories of software defects:
- **Pylint (initial score: 4.00/10)**: Identified critical code quality flaws including a dangerous mutable default argument (`baggage_tags=[]`) that leaks state across invocations; unmanaged file resources lacking a `with` context manager and explicit UTF-8 encoding; non-PEP 8 camelCase naming; outer-scope variable shadowing; redundant conditional checks (`== None`); and unused variables (`airport_fee`, `base_fare`) and imports (`math`).
- **Bandit (6 issues: 2 High, 1 Medium, 3 Low)**: Uncovered serious security vulnerabilities:
  1. `B605` (High): Command injection through `os.system()` with string concatenation.
  2. `B324` (High): Weak MD5 hashing for passenger identification.
  3. `B307` (Medium): Dangerous dynamic execution via `eval()`.
  4. `B311` (Low): Predictable standard pseudo-random number generator (`random.randint`) for boarding PINs.
  5. `B105` (Low): Hardcoded API secret token in source code.
  6. `B110` (Low): Silent exception suppression via bare `except: pass`.
- **Flake8 (10 findings)**: Flagged formatting violations such as lines exceeding 79 characters (`E501`), bare `except` (`E722`), singleton comparisons with `== None` (`E711`), and missing trailing newline (`W292`).

---

## 2. What was fixed and what approach was taken?
All actionable findings across all three tools were systematically fixed across three targeted phases:
1. **Code Quality (Pylint)**:
   - Fixed mutable default argument by setting default to `None` and initializing inside the function.
   - Refactored file operations to use `with open(...)` with explicit `encoding="utf-8"`.
   - Renamed functions to standard Python `snake_case` and added comprehensive docstrings.
   - Removed unused imports (`math`) and unused variables (`airport_fee`), and avoided scope shadowing in loop parameters.
2. **Security (Bandit)**:
   - Replaced `eval()` with a safe Abstract Syntax Tree (AST) parser that only evaluates whitelisted arithmetic operators (`+`, `-`, `*`, `/`) and allowed variables (`base_fare`), preventing arbitrary code execution.
   - Upgraded MD5 passenger hashing to SHA-256 (`hashlib.sha256`).
   - Replaced predictable `random.randint` with cryptographically secure `secrets.randbelow(9000) + 1000`.
   - Replaced `os.system()` shell execution with standard Python `print()`, eliminating command injection risk.
   - Retrieved API secrets from environment variables (`os.environ.get`) rather than hardcoding literals.
   - Replaced bare `except:` with explicit `except KeyError:` to prevent masking unexpected exceptions.
3. **Style & Formatting (Flake8)**:
   - Reformatted lines exceeding 79 characters, splitting dictionary literals and string messages.
   - Ensured clean POSIX newline termination at the end of the file.

---

## 3. What are the limitations of static code analysis?
Static code analysis is powerful but has distinct operational boundaries:
- **Absence of Business Logic Verification**: Static analyzers verify syntactic structure, rules, and known vulnerable patterns, but cannot verify whether the domain logic is correct (e.g., whether the baggage fee percentage aligns with airline policy).
- **Inability to Test Dynamic Runtime Behavior**: Static analyzers do not execute the software in production environments. Concurrency races, network outages, deadlocks, database query performance, and external API latency cannot be diagnosed statically.
- **Potential for False Positives and False Negatives**: Complex metaprogramming, dynamic attributes, or safe domain-specific constructs may trigger false positive warnings, while novel or deeply contextual vulnerabilities may be missed completely.

---

## 4. How does static analysis contribute to overall code quality and maintainability?
- **Automated Quality Gates & Continuous Integration**: Integrating static analyzers into CI/CD pipelines ensures that regressions in security, style, and quality are caught immediately at commit/pull request time.
- **Early Vulnerability Mitigation (Shift-Left Security)**: Addressing security risks (such as command injection, hardcoded secrets, and unsafe deserialization/evaluation) during local development drastically lowers remediation costs compared to post-deployment patching.
- **Enhanced Team Productivity & Readability**: Uniform PEP 8 formatting and clean docstrings minimize cognitive friction across development teams and facilitate seamless onboarding and refactoring.
