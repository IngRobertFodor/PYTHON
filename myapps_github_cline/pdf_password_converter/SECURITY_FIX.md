# Security Fix: pypdf Vulnerabilities

## Latest Fix (Aug 2026)

- Package: pypdf
- Severity: MODERATE
- CVEs: CVE-2026-71852, CVE-2026-71870
- Affected versions: pypdf < 6.15.0
- Fixed in: pypdf >= 6.15.0

### Fix Applied

File: requirements.txt
Before: pypdf==6.14.2
After:  pypdf==6.15.0

---

## Previous Fix (Infinite Loop Vulnerability)

- Package: pypdf
- Severity: HIGH
- Type: Possible infinite loop / Denial of Service (DoS)
- Affected versions: pypdf < 5.1.0
- Fixed in: pypdf >= 5.1.0

### Description

A high-severity vulnerability exists in pypdf where processing PDF files
containing non-terminated inline images using ASCII85 or ASCIIHex filters
could cause an infinite loop, resulting in a Denial of Service (DoS).

An attacker crafting a malicious PDF and providing it as input to this
application would cause it to hang indefinitely (100% CPU, unresponsive).

### Impact on This Application

pdf_password_converter uses pypdf in converter.py for:
- PdfReader: reading PDF files before encryption
- PdfWriter: writing and encrypting PDF output files

A malicious PDF as input could trigger the infinite loop in encrypt_pdf().

---

## Current Version Status

File: requirements.txt
Current: pypdf==6.15.0

Pinning to exact version 6.15.0 ensures:
1. All known CVEs (CVE-2026-71852, CVE-2026-71870) are patched
2. Version is well above the DoS patch threshold (5.1.0)
3. No accidental downgrade to a vulnerable version is possible
4. Reproducible and predictable builds

## Verification

Run: pip show pypdf
Expected: Version: 6.15.0

## References

- GitHub Security Advisory: CVE-2026-71852, CVE-2026-71870
- GitHub Security Advisory: pypdf infinite loop (ASCII85 and ASCIIHex filter)
- Fixed in pypdf 6.15.0 release
- https://pypdf.readthedocs.io/en/stable/meta/changelog.html
