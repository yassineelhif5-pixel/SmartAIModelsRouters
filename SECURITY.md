# Security policy

## Reporting a vulnerability

Please do not open a public issue for a security problem. Report it privately with
GitHub's **"Report a vulnerability"** button in the repository's Security tab
(private vulnerability reporting).

Include the affected version, a description, steps to reproduce and the impact you observed.
We acknowledge reports within 5 business days and agree on a disclosure date with you.

## Supported versions

| Version | Supported |
| --- | --- |
| 0.4.x | Yes |
| < 0.4 | No |

## Scope

The runtime, the gateway, the provider adapters, the spend guard and the installer scripts are
in scope. The `hif security scan` command is a heuristic pre-audit: a missed finding in a
scanned project is not a vulnerability in HIF. Security design notes are in
[docs/SECURITY.md](docs/SECURITY.md).
