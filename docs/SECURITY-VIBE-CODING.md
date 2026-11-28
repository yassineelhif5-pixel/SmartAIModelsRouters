# HIF Application Security Review for Vibe-Coded Software

**Purpose:** provide a fast, repeatable security pre-audit for applications created or modified with AI coding assistants.

HIF treats generated code as untrusted until reviewed. The security workflow is designed to produce actionable findings and a remediation plan, not merely a score.

## 1. Fast local pre-audit

The built-in scanner is local, read-only and does not execute project code.

```bash
hif security scan .
hif security scan . --json
```

Windows PowerShell:

```powershell
hif security scan .
hif security scan . --json
```

The scanner:
- scans supported source/configuration files with bounded file count, file size and runtime;
- skips common generated/dependency folders such as .git, virtual environments, node_modules, build and dist;
- does not open .env files or print secret values;
- checks for common high-risk patterns such as private-key material, hard-coded credentials, eval/exec, shell=True, unsafe pickle/YAML loading, disabled TLS verification, weak hashes, debug mode and wildcard CORS;
- returns file/line evidence, severity, a remediation recommendation and a verification step.

The scanner uses deterministic rules and is intentionally lightweight. It does not run the target application, install packages, contact external services, perform exploit attempts or change files.

## 2. Risk levels and response policy

| Severity | Examples | Required response |
|---|---|---|
| Critical | Private key material or exposed high-impact credentials | Stop release, rotate/revoke the credential, remove it from repository history where necessary, verify secret-store usage |
| High | Dynamic code execution, shell injection exposure, unsafe deserialization, disabled TLS validation | Fix before release; add a regression test and verify the exploit path is closed |
| Medium | Weak cryptographic primitive, debug enabled, wildcard CORS | Prioritize before production; document any accepted risk |
| Low / informational | Hardening and configuration gaps | Add to the technical-debt and release-hardening plan |

A scanner finding is evidence of a pattern, not proof of exploitability. A clean scan is not proof that the application is secure.

## 3. HIF security pipeline

For an AI-generated or vibe-coded application, HIF should follow these stages:

1. **Scope and architecture discovery:** identify entry points, trust boundaries, data flows, roles, tenants, APIs, storage, deployment and sensitive data.
2. **Fast deterministic scan:** run the local HIF scanner and collect dependency/configuration manifests.
3. **Threat modeling:** identify assets, threat actors, abuse cases, attack surfaces and likely impact. Consider STRIDE or an equivalent method.
4. **Application Security Reviewer:** inspect authentication, authorization, tenant isolation, injection, SSRF, file upload/download, path traversal, secrets, session handling, cryptography, logging and error handling.
5. **Dependency and supply-chain review:** inspect lockfiles, known vulnerabilities, unmaintained packages, provenance and license policy.
6. **Verification:** add regression tests, run unit/integration tests, static analysis and safe dynamic tests in a non-production environment.
7. **Prioritized remediation plan:** return findings with severity, evidence, affected component, business impact, exact corrective action, owner role, effort estimate, dependency and verification criteria.
8. **Release gate:** block release on unresolved critical/high findings unless an authorized security owner explicitly accepts a documented risk. Never auto-deploy a fix.

The Root Orchestrator owns the final security posture recommendation. The Assistant Architect checks design-level risks; the Infrastructure Architect checks network, identity, secrets, hosting, observability and deployment controls.

## 4. Recommended external checks

The built-in HIF scanner is not a replacement for specialist tools. Add the appropriate tools to CI or an isolated audit environment:

| Area | Suggested tool | Purpose |
|---|---|---|
| Python dependencies | pip-audit | Known vulnerabilities in installed/project dependencies |
| JavaScript dependencies | npm audit | Known package vulnerabilities |
| Multi-language SAST | Semgrep or CodeQL | Data-flow and code-pattern analysis |
| Secret detection | Gitleaks | Secrets committed to source history |
| Container images | Trivy | Image, OS package and dependency vulnerabilities |
| Infrastructure as Code | Checkov | Cloud/IaC misconfiguration checks |
| Web application | OWASP ZAP | Controlled DAST against a test deployment |

Run scanners with least privilege, pinned versions and bounded resource limits. Do not run active DAST against production without explicit authorization and a defined test window.

## 5. Minimum review checklist for AI-generated applications

### Identity and authorization
- Server-side authorization is enforced for every sensitive action.
- Role checks are not trusted solely to frontend state.
- Tenant IDs are derived from authenticated identity and cannot be changed to access another tenant.
- Admin and service credentials are least-privilege and rotated.

### Data and APIs
- Input validation uses explicit schemas and allowlists.
- SQL/NoSQL queries are parameterized.
- File uploads enforce size, type, storage isolation and malware scanning where required.
- SSRF, path traversal, insecure redirects and unsafe deserialization are considered.
- Rate limits and request-size limits protect expensive endpoints.

### Secrets and cryptography
- No secrets in source, logs, test fixtures, build output or browser bundles.
- TLS certificate validation is enabled.
- Passwords use a suitable password-hashing function.
- Encryption keys have a managed lifecycle.

### Runtime and operations
- Debug mode is disabled in production.
- CORS is limited to known origins.
- Security headers, audit events, alerting and redaction are configured.
- Backups are protected and restoration is tested.
- Dependencies are locked and scanned.
- CI runs tests and security checks before merge/release.

## 6. Output format expected from HIF

Every security review should produce:
- executive risk summary and scope;
- findings grouped by severity, with path/line or component evidence;
- false-positive/unknown items requiring human validation;
- prioritized action plan (P0/P1/P2/P3);
- exact technical remediation and regression test;
- owner role and dependencies;
- acceptance criteria and retest result;
- explicit limitations and residual risks.

Do not state "secure", "compliant" or "penetration-tested" solely because the heuristic scan completed.

## 7. Current implementation boundary

Implemented in this HIF branch:
- bounded read-only local source scanner;
- secret-safe handling of .env files (presence can be reported; contents are never read);
- rule IDs, severity and structured recommendations;
- JSON and terminal CLI output;
- asynchronous invocation through HIF's bounded I/O thread pool;
- security as a first-class task type and model-routing preference.

Not yet implemented by this scanner:
- full AST/data-flow SAST;
- dependency CVE database lookups;
- Git history secret scanning;
- authenticated DAST, fuzzing or penetration testing;
- automatic code modification or patching;
- enforceable CI/release policy gates.

These require dedicated tools, integration work and explicit authorization.
