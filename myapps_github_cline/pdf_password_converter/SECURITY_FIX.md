# Security Fix: pypdf Vulnerabilities

## Latest Fix (Oct 2026)

- Package: pypdf
- Severity: HIGH
- CVEs: CVE-2026-102997, CVE-2026-102998, CVE-2026-102996, CVE-2026-102995, CVE-2026-102993
- Affected versions: pypdf < 6.18.1
- Fixed in: pypdf >= 6.18.1

### Fix Applied

File: requirements.txt
Before: pypdf==6.16.2
After:  pypdf~=6.18.1  (>=6.18.1, <6.19.0 -- allows patch updates within 6.18.x)

Source: GitHub Security Alert digest, week of Oct 7-Oct 14, 2026

### Additional Change (Python 3.14 Compatibility)

File: requirements.txt
Before: pyinstaller==6.11.1
After:  pyinstaller>=6.15.0

pyinstaller 6.11.1 does not support Python 3.14 (bundled WinPython version).
Constraint relaxed to >=6.15.0 which is the earliest version supporting Python 3.14.
This is a build tool only -- it does not affect the running application.

---

## Previous Fix (Aug 2026)

- Package: pypdf
- Severity: MODERATE
- CVEs: CVE-2026-71852, CVE-2026-71870
- Affected versions: pypdf < 6.15.0
- Fixed in: pypdf >= 6.15.0

### Fix Applied

File: requirements.txt
Before: pypdf==6.14.2
After:  pypdf==6.16.2 (latest stable at the time)

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
Current: pypdf~=6.18.1  (>=6.18.1, <6.19.0)

Using the pessimistic constraint ~=6.18.1 ensures:
1. All known CVEs (CVE-2026-102997, CVE-2026-102998, CVE-2026-102996,
   CVE-2026-102995, CVE-2026-102993) are patched -- all fixed in >= 6.18.1
2. All prior CVEs (CVE-2026-71852, CVE-2026-71870) remain patched
3. Version is well above the DoS patch threshold (5.1.0)
4. Patch-level updates within 6.18.x are allowed automatically
5. No accidental downgrade below 6.18.1 is possible

## Verification

Run: pip show pypdf
Expected: Version: 6.18.x  (any 6.18.x release, e.g. 6.18.1 or higher)

## References

- GitHub Security Alert digest: week of Oct 7-Oct 14, 2026
- CVEs: CVE-2026-102997, CVE-2026-102998, CVE-2026-102996, CVE-2026-102995, CVE-2026-102993
- GitHub Security Advisory: CVE-2026-71852, CVE-2026-71870
- GitHub Security Advisory: pypdf infinite loop (ASCII85 and ASCIIHex filter)
- https://pypdf.readthedocs.io/en/stable/meta/changelog.html