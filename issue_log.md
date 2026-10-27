# Static Code Analysis Issue Log

## 1. Overview & Tool Configuration

- **Target Source File**: `flight_reservation_system.py`
- **Environment**: Python 3.14.0 (Windows x86_64) isolated virtual environment (`.venv`)
- **Tools & Versions**:
  - Pylint: `4.1.3`
  - Bandit: `1.9.4`
  - Flake8: `7.4.1`

---

## 2. Comprehensive Issue Tracking Table

| Issue # | Tool | Original Line(s) | Finding Code & Severity | Explanation | Actual Fix Approach | Verification Result |
|---|---|---|---|---|---|---|
| 1 | Pylint | 15 | `W0102` (Warning) | Dangerous mutable default argument `baggage_tags=[]` shared across all function calls, leading to persistent state leakage between invocations. | Replaced default with `None` and initialized `baggage_tags = []` inside function body if `None`. | Resolved; Pylint W0102 no longer reported. Independent baggage tags across calls verified. |
| 2 | Pylint | 4, 36, 46, 68 | `W0611`, `W0612` (Warning) | Unused import `math` and unused variables (`airport_fee`, `base_fare`, loop key `f` in `items()`). Unused elements create clutter and dead code. | Removed `import math` and unused assignment `airport_fee`; iterated `.values()` in dictionary loop. `base_fare` evaluated safely in security fix. | Resolved; W0611 and W0612 warnings cleared. |
| 3 | Pylint | 1, 15, 27, 35, 45, 51, 55, 59, 66, 74 | `C0114`, `C0116`, `C0103` (Convention) | Missing module docstring, missing function docstrings, and non-conforming camelCase function names (`bookFlightSeat`, etc.). | Added descriptive PEP 257 docstrings for module and all functions; renamed functions to PEP 8 `snake_case`. | Resolved; docstring and naming conventions fully compliant. |
| 4 | Pylint | 60 | `R1732`, `W1514` (Refactor / Warning) | Manual file opening (`open()`) without context manager (`with`) and without explicit encoding leads to resource leakage and platform-dependent decoding bugs. | Wrapped file operations in `with open(filename, "w", encoding="utf-8") as manifest_file:`. | Resolved; guaranteed deterministic file descriptor release and UTF-8 encoding. |
| 5 | Bandit / Pylint | 47 | `B307` (Medium) / `W0123` (Warning) | Execution of arbitrary untrusted input via `eval(surcharge_expr)` introduces Remote Code Execution (RCE) / expression injection vulnerabilities. | Implemented safe AST evaluator using `ast.parse(mode='eval')` with an operator and variable whitelist (`base_fare`), completely rejecting unauthorized operations. | Resolved; Bandit B307 and Pylint W0123 cleared. Tested safe evaluation with 67.5 output. |
| 6 | Bandit | 63 | `B605` (High) | Starting a subshell process via `os.system("echo ... " + filename)` introduces shell command injection vulnerabilities if `filename` contains shell metacharacters. | Replaced shell invocation entirely with native, safe Python `print()` statement. | Resolved; Bandit B605 cleared. No subprocess or subshell spawned. |
| 7 | Bandit | 52 | `B324` (High) | Use of cryptographically weak and collision-prone MD5 hash algorithm (`hashlib.md5`) for passenger identity hashing. | Upgraded hashing algorithm to cryptographically secure SHA-256 (`hashlib.sha256`). | Resolved; Bandit B324 cleared. High-confidence hashing achieved. |
| 8 | Bandit | 56 | `B311` (Low) | Standard pseudo-random number generator (`random.randint`) is predictable and unsuitable for security/cryptographic credentials like boarding PINs. | Replaced `random` with cryptographically secure `secrets.randbelow(9000) + 1000`. | Resolved; Bandit B311 cleared. |
| 9 | Bandit / Pylint / Flake8 | 31 | `B110` (Low) / `W0702` (Warning) / `E722` (Error) | Bare `except:` with `pass` silently suppresses all exceptions, masking catastrophic errors, keyboard interrupts, and programming bugs. | Replaced bare except with explicit, specific exception `except KeyError:` matching dictionary access. | Resolved; B110, W0702, and E722 all cleared. |
| 10 | Bandit | 75 | `B105` (Low) | Hardcoded API secret token literal in source code leaks sensitive credentials into version control. | Retrieved API secret from environment via `os.environ.get("AIRLINE_API_SECRET", ...)` with safe fallback. | Resolved; Bandit B105 cleared. |
| 11 | Flake8 | 7, 8, 9, 23 | `E501` (Error) | Multiple lines exceeded PEP 8 maximum length of 79 characters. | Restructured dictionary literals and split long string interpolations across multiple lines. | Resolved; Flake8 E501 errors cleared. |
| 12 | Flake8 / Pylint | 87 | `W292`, `C0304` (Warning) | Missing final newline at end of file. | Added POSIX-compliant trailing newline `\n`. | Resolved; W292 and C0304 cleared. |

---

## 3. Reflection Section

### 3.1 What Was Found
Baseline static code analysis revealed a broad spectrum of defects spanning multiple layers:
1. **Security Vulnerabilities (Bandit)**: High-severity findings including shell command injection (`os.system` with string concatenation) and broken cryptographic algorithms (`hashlib.md5`). Medium-severity remote code execution through dynamic `eval()`, hardcoded credentials, weak pseudo-random generation for boarding passes (`random.randint`), and silent error swallowing (`except: pass`).
2. **Code Quality & Reliability Defects (Pylint)**: A classic mutable default argument bug (`baggage_tags=[]`) causing cross-call state leakage; unclosed file descriptors without context managers (`open()` without `with`); parameter shadowing (`def getFlightSummary(flights):`); unnecessary else branches; redundant comparisons (`== None`); and unused imports/variables.
3. **Style & PEP 8 Violations (Flake8)**: Multiple lines exceeding the 79-character limit, bare `except:` clauses, singleton comparisons with `==` rather than `is`, and missing final newlines.

### 3.2 What Was Fixed
- **Phase 1 (Code Quality)**: Standardized naming conventions to snake_case, supplied comprehensive module and function docstrings, fixed mutable default arguments to `None` initialization, enforced context management (`with open`) and explicit UTF-8 encoding for file I/O, removed dead code and unused variables, and cleaned up scope shadowing.
- **Phase 2 (Security)**: Replaced dangerous `eval()` with an AST whitelist parser supporting safe arithmetic; eliminated shell injection by replacing `os.system()` with native I/O; modernized cryptographic hashing to SHA-256; converted boarding PIN generation to `secrets`; caught specific exceptions (`KeyError`); and decoupled credentials using environment variable resolution.
- **Phase 3 (Style & Formatting)**: Reformatted all dictionary definitions and function arguments to adhere strictly to the 79-character PEP 8 ceiling, removed trailing whitespace, and ensured standard newline termination.

### 3.3 Limitations of Static Analysis
While static analysis tools are indispensable for automated quality gates, they possess notable limitations:
- **Semantic Intent**: Static analyzers cannot evaluate whether business requirements are accurately fulfilled. For instance, Bandit flags `eval()`, but cannot determine whether the business logic of baggage surcharge calculation is mathematically correct.
- **Dynamic Context**: Static tools evaluate code without execution context, often producing false positives or missing runtime-dependent issues (e.g., race conditions, network partition handling, external database state).
- **Tool Blindness**: Flake8 and Pylint cannot evaluate UI/UX quality, API responsiveness, or whether sample seed data in dictionaries meets real-world domain constraints.

### 3.4 Contribution to Software Quality & Security
Static code analysis contributes significantly across the Software Development Life Cycle (SDLC):
- **Shift-Left Quality & Security**: Detects critical vulnerabilities (injection, weak crypto, secret exposure) during coding before code ever merges or reaches staging/production.
- **Maintainability & Uniformity**: Standardizes formatting, naming, and docstrings across teams, drastically reducing cognitive overhead during peer code reviews.
- **Bug Prevention**: Catches elusive Python pitfalls (such as mutable default arguments and resource leaks) automatically, preventing production outages and subtle runtime bugs.
