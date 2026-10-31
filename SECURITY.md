# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in sitepulse, please report it by:

1. **Do not** open a public issue
2. Email the maintainer or use GitHub's private vulnerability reporting feature
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue promptly.

## Security Considerations

- sitepulse makes outbound HTTP requests to audit target websites
- Always audit sites you own or have permission to scan
- Be aware that aggressive scanning may trigger WAF/rate limits
- No authentication credentials are stored or transmitted