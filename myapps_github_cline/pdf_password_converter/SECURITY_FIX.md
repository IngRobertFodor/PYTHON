# Security Fix: pypdf Infinite Loop Vulnerability

## Vulnerability Details

- Package: pypdf
- Severity: HIGH
- Type: Possible infinite loop / Denial of Service (DoS)
- Affected versions: pypdf < 5.1.0
- Fixed in: pypdf >= 5.1.0

## Description

A high-severity vulnerability exists in pypdf where processing PDF files
containing non-terminated inline images using ASCII85 or ASCIIHex filters
could cause an infinite loop, resulting in a Denial of Service (DoS).

An attacker crafting a malicious PDF and providing it as input to this
application would cause it to hang indefinitely (100% CPU, unresponsive).

## Impact on This Application

pdf_password_converter uses pypdf in converter.py for:
- PdfReader: reading PDF files before encryption
- PdfWriter: writing and encrypting PDF output files

A malicious PDF as input could trigger the infinite loop in encrypt_pdf().

## Fix Applied

File: requirements.txt
Before: pypdf>=6.14.2
After:  pypdf==6.14.2

Pinning to exact version 6.14.2 ensures:
1. Version is well above the patched threshold (5.1.0)
2. No accidental downgrade to a vulnerable version is possible
3. Reproducible and predictable builds
4. Vulnerability is permanently eliminated

## Verification

Run: pip show pypdf
Expected: Version: 6.14.2

## References

- GitHub Security Advisory: pypdf infinite loop (ASCII85 and ASCIIHex filter)
- Fixed in pypdf 5.1.0 release
- https://pypdf.readthedocs.io/en/stable/meta/changelog.html
