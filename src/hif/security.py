"""Fast, local, read-only security checks for AI-generated application code.

This is a heuristic pre-audit, not a substitute for a full SAST/DAST or human review.
It never executes project code and never reads secret-bearing .env files.
"""
from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".next", "coverage",
}
SOURCE_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".java", ".cs", ".go",
    ".php", ".rb", ".rs", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".xml", ".sh", ".ps1", ".sql", ".html",
}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 5000
DEFAULT_TIMEOUT_SECONDS = 8.0

_RULES: tuple[tuple[str, str, str, re.Pattern[str], str], ...] = (
    ("SEC001", "critical", "Private key material committed in source",
     re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
     "Remove the key from the repository, rotate/revoke it, and load secrets from a secret manager."),
    ("SEC002", "critical", "Hard-coded provider or cloud credential",
     re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*['\"][A-Za-z0-9_./+=:-]{12,}['\"]"),
     "Revoke and rotate the exposed credential; use environment injection or a managed secret store."),
    ("SEC003", "high", "Potential eval/exec code execution",
     re.compile(r"\b(?:eval|exec)\s*\("),
     "Remove dynamic evaluation or strictly parse/allowlist input; never evaluate untrusted text."),
    ("SEC004", "high", "Shell command built or invoked with shell=True",
     re.compile(r"\b(?:shell\s*=\s*True|os\.system\s*\(|subprocess\.(?:Popen|run|call)\([^\n]*shell\s*=\s*True)"),
     "Use argument arrays with shell=False, validate arguments and apply least-privilege execution."),
    ("SEC005", "high", "Unsafe pickle deserialization",
     re.compile(r"\bpickle\.(?:loads|load)\s*\("),
     "Do not deserialize untrusted pickle data; use a safe, schema-validated format."),
    ("SEC006", "high", "Potentially unsafe YAML loading",
     re.compile(r"\byaml\.load\s*\((?![^\n]*Loader\s*=\s*yaml\.SafeLoader)"),
     "Use yaml.safe_load and validate the resulting object against a strict schema."),
    ("SEC007", "high", "TLS certificate verification disabled",
     re.compile(r"(?i)(?:verify\s*=\s*False|CERT_NONE|check_hostname\s*=\s*False)"),
     "Enable certificate and hostname verification; install the correct CA bundle."),
    ("SEC008", "medium", "Weak cryptographic hash",
     re.compile(r"\bhashlib\.(?:md5|sha1)\s*\("),
     "Use SHA-256 or stronger for integrity; use Argon2id/bcrypt/scrypt for password hashing."),
    ("SEC009", "medium", "Debug mode enabled in application configuration",
     re.compile(r"(?i)\bDEBUG\s*=\s*(?:True|true|1)\b"),
     "Disable debug mode outside local development and ensure errors do not expose internals."),
    ("SEC010", "medium", "Wildcard CORS origin",
     re.compile(r"""(?i)(?:allow_origins\s*=\s*\[\s*['"]\*['"]|Access-Control-Allow-Origin['"]?\s*[:,=]\s*['"]\*['"])"""),
     "Restrict CORS to explicit trusted origins; do not combine wildcard origins with credentials."),
    ("SEC012", "high", "Potential SQL query built with string interpolation",
     re.compile(r"""(?i)\b(?:execute|executemany)\s*\(\s*(?:f['"]|['"][^'"]*['"]\s*%|['"][^'"]*['"]\.format\s*\()"""),
     "Use parameterized SQL statements and bind values separately; add injection regression tests."),
    ("SEC013", "high", "JWT signature verification may be disabled",
     re.compile(r"""(?i)jwt\.decode\s*\([^\n]*(?:verify_signature['"]?\s*:\s*False|verify\s*=\s*False)"""),
     "Require signature verification, an explicit algorithm allowlist, issuer and audience validation."),
    ("SEC014", "medium", "Cookie security attribute explicitly disabled",
     re.compile(r"""(?i)(?:httponly|secure)\s*=\s*False"""),
     "Enable HttpOnly and Secure where applicable; choose an intentional SameSite policy."),
    ("SEC015", "high", "Potential unsafe HTML injection sink",
     re.compile(r"""(?i)(?:dangerouslySetInnerHTML|\.innerHTML\s*=)"""),
     "Avoid injecting untrusted HTML; encode output or sanitize with a maintained allowlist sanitizer."),
)

@dataclass(frozen=True)
class SecurityFinding:
    rule_id: str
    severity: str
    title: str
    path: str
    line: int
    evidence: str
    owner_role: str
    recommendation: str

@dataclass(frozen=True)
class SecurityReport:
    root: str
    scanned_files: int
    skipped_files: int
    elapsed_ms: int
    findings: tuple[SecurityFinding, ...]

    def to_dict(self) -> dict:
        counts = {level: sum(f.severity == level for f in self.findings)
                  for level in ("critical", "high", "medium", "low")}
        return {
            "root": self.root,
            "scanned_files": self.scanned_files,
            "skipped_files": self.skipped_files,
            "elapsed_ms": self.elapsed_ms,
            "summary": counts,
            "risk": "critical" if counts["critical"] else "high" if counts["high"]
                    else "medium" if counts["medium"] else "low" if self.findings else "no_findings",
            "findings": [asdict(item) for item in self.findings],
            "action_plan": _action_plan(self.findings),
            "limitations": [
                "Heuristic static pre-audit only; not a complete SAST, DAST, dependency or cloud-configuration audit.",
                "Project code is read as text and never executed. .env and secret files are not opened.",
                "Findings require human validation; absence of findings is not proof of security.",
            ],
        }

def _action_plan(findings: tuple[SecurityFinding, ...]) -> list[dict[str, str]]:
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    priority_codes = {"critical": "P0", "high": "P1", "medium": "P2", "low": "P3"}
    plan = []
    seen: set[tuple[str, str, int]] = set()
    for item in sorted(findings, key=lambda x: (order.get(x.severity, 9), x.path, x.line)):
        key = (item.rule_id, item.path, item.line)
        if key in seen:
            continue
        seen.add(key)
        plan.append({
            "priority": priority_codes.get(item.severity, "P3"),
            "severity": item.severity,
            "step": f"{item.rule_id}: {item.title}",
            "location": f"{item.path}:{item.line}",
            "owner_role": item.owner_role,
            "action": item.recommendation,
            "verification": "Re-run the scan and add a regression/security test for the corrected behavior.",
        })
    if not plan:
        plan.append({
            "priority": "baseline",
            "step": "Run dependency and configuration audits",
            "action": "Review dependencies, lockfiles, cloud/IAM configuration, authentication, authorization and deployment secrets.",
            "verification": "Run the project's dependency scanner, tests and deployment security checks.",
        })
    return plan

def _owner_for_rule(rule_id: str) -> str:
    if rule_id in {"SEC001", "SEC002", "SEC007", "SEC011"}:
        return "devops_engineer"
    if rule_id in {"SEC009", "SEC010", "SEC014"}:
        return "platform_engineer"
    return "backend_developer"


def scan_project(root: str | Path, *, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
                 max_files: int = MAX_FILES) -> SecurityReport:
    base = Path(root).expanduser().resolve()
    if not base.exists() or not base.is_dir():
        raise ValueError(f"Project directory does not exist: {base}")
    started = time.monotonic()
    findings: list[SecurityFinding] = []
    scanned = skipped = 0

    # Report presence, but never open secret files.
    for secret_name in (".env", ".env.local", ".env.production"):
        if (base / secret_name).is_file():
            findings.append(SecurityFinding(
                "SEC011", "high", "Local secret file exists in project root",
                secret_name, 0, "File presence only; contents were not read.",
                "devops_engineer",
                "Ensure this file is gitignored, restrict filesystem permissions, and rotate any secret previously committed.",
            ))

    for path in base.rglob("*"):
        if time.monotonic() - started > timeout_seconds or scanned + skipped >= max_files:
            break
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.name.startswith(".env") or path.suffix.lower() not in SOURCE_SUFFIXES:
            skipped += 1
            continue
        try:
            if path.is_symlink() or path.stat().st_size > MAX_FILE_BYTES:
                skipped += 1
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            skipped += 1
            continue
        scanned += 1
        for line_number, line in enumerate(content.splitlines(), 1):
            for rule_id, severity, title, pattern, recommendation in _RULES:
                match = pattern.search(line)
                if not match:
                    continue
                evidence = line.strip()[:180]
                # Redact probable credential literals in evidence.
                evidence = re.sub(
                    r"""(?i)((?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*)['"][^'"]+['"]""",
                    r"\1'[REDACTED]'",
                    evidence,
                )
                findings.append(SecurityFinding(
                    rule_id, severity, title, relative.as_posix(), line_number,
                    evidence, _owner_for_rule(rule_id), recommendation,
                ))
    return SecurityReport(
        root=str(base), scanned_files=scanned, skipped_files=skipped,
        elapsed_ms=int((time.monotonic() - started) * 1000),
        findings=tuple(findings),
    )
