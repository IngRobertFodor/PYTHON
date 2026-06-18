import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

class OcrService {
  /// Extracts phone numbers from an image file path using Google ML Kit OCR.
  /// Returns a list of unique phone numbers found in the image.
  Future<List<String>> extractPhoneNumbers(String imagePath) async {
    final textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);

    try {
      final inputImage = InputImage.fromFilePath(imagePath);
      final RecognizedText recognizedText =
          await textRecognizer.processImage(inputImage);

      final String fullText = recognizedText.text;

      // Extract phone numbers from the recognized text
      final List<String> phoneNumbers = _findPhoneNumbers(fullText);

      return phoneNumbers;
    } finally {
      textRecognizer.close();
    }
  }

  /// Finds all phone number patterns in the given text.
  /// Supports international formats from all regions:
  /// EU (SK, CZ, DE, AT, HU, PL, FR, GB, IT, ES, NL, BE, CH, SE, NO, DK, FI, RU, UA)
  /// Americas (USA/CA, MX, BR, AR)
  /// Asia-Pacific (CN, JP, KR, IN, AU)
  List<String> _findPhoneNumbers(String text) {
    // Comprehensive regex patterns for worldwide phone numbers
    final List<RegExp> patterns = [
      // === INTERNATIONAL FORMATS ===

      // +XXX followed by 7-12 digits with separators (spaces, dashes, dots)
      // Covers: +421 2 20608080, +49 30 12345678, +33 1 23456789, +1 212 555 1234
      RegExp(r'\+\d{1,3}[\s\-.]?\d{1,5}[\s\-.]?\d{1,5}[\s\-.]?\d{1,5}[\s\-.]?\d{0,5}[\s\-.]?\d{0,4}'),

      // 00XXX format (alternative to +): 00421 2 20608080, 0049 30 12345678
      RegExp(r'00\d{1,3}[\s\-.]?\d{1,5}[\s\-.]?\d{1,5}[\s\-.]?\d{1,5}[\s\-.]?\d{0,5}'),

      // === USA/CANADA NANP FORMAT ===

      // (XXX) XXX-XXXX or (XXX) XXX XXXX
      RegExp(r'\(\d{3}\)[\s\-.]?\d{3}[\s\-.]?\d{4}'),

      // XXX-XXX-XXXX (without parentheses)
      RegExp(r'(?<!\d)\d{3}[\-\.]\d{3}[\-\.]\d{4}(?!\d)'),

      // === EUROPEAN LOCAL FORMATS ===

      // Local with leading 0: 0912 345 678, 02 20608080, 030 12345678
      // Covers SK, DE, AT, GB, FR, NL, BE, CH, FI, SE, JP, AU
      RegExp(r'0\d{1,4}[\s\-.]?\d{2,8}[\s\-.]?\d{0,6}[\s\-.]?\d{0,4}'),

      // Local with area code in parentheses: (02) 2060 8080, (030) 12345678
      RegExp(r'\(\d{2,5}\)[\s\-.]?\d{2,8}[\s\-.]?\d{0,6}[\s\-.]?\d{0,4}'),

      // === SPECIAL REGIONAL FORMATS ===

      // Hungary: 06 XX XXX XXXX (06 prefix instead of 0)
      RegExp(r'06[\s\-.]?\d{1,2}[\s\-.]?\d{3}[\s\-.]?\d{3,4}'),

      // Russia: 8 XXX XXX-XX-XX (8 prefix for domestic calls)
      RegExp(r'8[\s\-.]?\d{3}[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}'),

      // Brazil: (XX) XXXXX-XXXX (11 digit mobile with 9 prefix)
      RegExp(r'\(\d{2}\)[\s\-.]?\d{4,5}[\s\-.]?\d{4}'),

      // === CONTINUOUS DIGITS FALLBACK ===

      // 7-15 continuous digits (possibly starting with +)
      // Last resort – catches anything that looks like a phone number
      RegExp(r'(?<!\d)\+?\d{7,15}(?!\d)'),
    ];

    final Set<String> foundNumbers = {};

    for (final pattern in patterns) {
      final matches = pattern.allMatches(text);
      for (final match in matches) {
        String number = match.group(0) ?? '';
        number = number.trim();

        // Normalize the number for validation
        String normalized = _normalizeNumber(number);

        // Validate: must have at least 7 digits and max 15 (ITU E.164 standard)
        final digitsOnly = normalized.replaceAll(RegExp(r'[^\d]'), '');
        if (digitsOnly.length >= 7 && digitsOnly.length <= 15) {
          // Avoid duplicates (normalized check)
          if (!_isDuplicate(number, foundNumbers)) {
            foundNumbers.add(number);
          }
        }
      }
    }

    return foundNumbers.toList();
  }

  /// Normalizes a phone number for consistent comparison.
  /// - Converts 00XXX to +XXX
  /// - Trims whitespace
  String _normalizeNumber(String number) {
    String normalized = number.trim();

    // Convert 00 prefix to + (international format)
    if (normalized.startsWith('00') && !normalized.startsWith('000')) {
      normalized = '+${normalized.substring(2)}';
    }

    return normalized;
  }

  /// Check if a number is a duplicate of an already found number.
  /// Compares by stripping all non-digit characters (except leading +).
  bool _isDuplicate(String number, Set<String> existingNumbers) {
    final normalizedNew = _normalizeNumber(number).replaceAll(RegExp(r'[^\d+]'), '');

    for (final existing in existingNumbers) {
      final normalizedExisting = _normalizeNumber(existing).replaceAll(RegExp(r'[^\d+]'), '');

      // Exact match
      if (normalizedNew == normalizedExisting) {
        return true;
      }

      // One contains the other (e.g., local vs international format)
      // +421912345678 contains 0912345678 (without leading 0)
      final digitsNew = normalizedNew.replaceAll('+', '');
      final digitsExisting = normalizedExisting.replaceAll('+', '');

      if (digitsNew.endsWith(digitsExisting) ||
          digitsExisting.endsWith(digitsNew)) {
        // Allow difference of up to 4 digits (country code length)
        if ((digitsNew.length - digitsExisting.length).abs() <= 4) {
          return true;
        }
      }
    }
    return false;
  }
}