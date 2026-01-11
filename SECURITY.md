# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v0.5.x  | :white_check_mark: |
| < 0.5.0 | :x:                |

## Reporting a Vulnerability

Please do **NOT** open a public issue if you discover a security vulnerability.

Instead, please email the maintainers directly or use the GitHub Private Vulnerability Reporting feature if enabled.

We will acknowledge your report within 48 hours.

## Branch Protection Policy

To ensure code stability and security, the `master` branch is protected:

- **Require Pull Request**: Direct pushes to main are disabled.
- **Require Status Checks**: CI (tests/lint) must pass before merging.
- **Require Reviews**: At least one approval from a Code Owner (@Gijsja) is required.
- **No Force Pushes**: History is immutable.

To apply these rules, run: `./scripts/protect_branch.sh`
