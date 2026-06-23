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

      // Pre-process text for better number detection
      final String processedText = _preProcessText(fullText);

      // Extract phone numbers from the processed text
      final List<String> phoneNumbers = _findPhoneNumbers(processedText);

      return phoneNumbers;
    } finally {
      textRecognizer.close();
    }
  }

  /// Pre-processes OCR text to fix common issues:
  /// 1. Join multi-line numbers (e.g. "+421 2\n20608080")
  /// 2. Fix common OCR character substitutions (O→0, l→1, etc.)
  String _preProcessText(String text) {
    String processed = text;

    // Replace newlines with spaces when surrounded by digits/phone chars
    // This helps with numbers split across lines
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)\n(\d)'),
      (m) => '${m.group(1)} ${m.group(2)}',
    );

    // Fix common OCR substitutions in digit contexts
    // Only fix when character is surrounded by digits (to avoid false positives)
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)[Oo](\d)'),
      (m) => '${m.group(1)}0${m.group(2)}',
    );
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)[lI](\d)'),
      (m) => '${m.group(1)}1${m.group(2)}',
    );
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)[Bb](\d)'),
      (m) => '${m.group(1)}8${m.group(2)}',
    );
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)[Ss](\d)'),
      (m) => '${m.group(1)}5${m.group(2)}',
    );
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)[Zz](\d)'),
      (m) => '${m.group(1)}2${m.group(2)}',
    );
    processed = processed.replaceAllMapped(
      RegExp(r'(\d)[Gg](\d)'),
      (m) => '${m.group(1)}6${m.group(2)}',
    );

    return processed;
  }

  /// Finds all phone number patterns in the given text.
  /// Supports international formats from all regions worldwide.
  List<String> _findPhoneNumbers(String text) {
    final List<RegExp> patterns = [
      // === INTERNATIONAL FORMATS ===

      // +XXX with up to 12 digits after, separated by spaces/dashes/dots
      // Handles: +421 2 20608080, +49 30 12345678, +1 212 555 1234
      RegExp(r'\+\d{1,3}[\s\-.]?\d{1,8}[\s\-.]?\d{0,8}[\s\-.]?\d{0,8}'),

      // 00XXX format: 00421 2 20608080, 0049 30 12345678
      RegExp(r'00\d{1,3}[\s\-.]?\d{1,8}[\s\-.]?\d{0,8}[\s\-.]?\d{0,8}'),

      // === USA/CANADA NANP FORMAT ===

      // (XXX) XXX-XXXX
      RegExp(r'\(\d{3}\)[\s\-.]?\d{3}[\s\-.]?\d{4}'),

      // XXX-XXX-XXXX (without parentheses)
      RegExp(r'(?<!\d)\d{3}[\-\.]\d{3}[\-\.]\d{4}(?!\d)'),

      // === LOCAL FORMATS ===

      // Local with leading 0: 0912 345 678, 02 20608080, 0850 166 000
      RegExp(r'0\d{1,4}[\s\-.]?\d{2,8}[\s\-.]?\d{0,8}'),

      // Local with area code in parentheses: (02) 20608080
      RegExp(r'\(\d{2,5}\)[\s\-.]?\d{2,8}[\s\-.]?\d{0,8}'),

      // === SPECIAL REGIONAL FORMATS ===

      // Hungary: 06 XX XXX XXXX
      RegExp(r'06[\s\-.]?\d{1,2}[\s\-.]?\d{3}[\s\-.]?\d{3,4}'),

      // Russia: 8 XXX XXX-XX-XX
      RegExp(r'8[\s\-.]?\d{3}[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}'),

      // Brazil: (XX) XXXXX-XXXX
      RegExp(r'\(\d{2}\)[\s\-.]?\d{4,5}[\s\-.]?\d{4}'),

      // === FALLBACK ===

      // 7-15 continuous digits (must start with digit or +)
      RegExp(r'(?<!\d)\+?\d{7,15}(?!\d)'),
    ];

    final Set<String> foundNumbers = {};

    for (final pattern in patterns) {
      final matches = pattern.allMatches(text);
      for (final match in matches) {
        String number = match.group(0) ?? '';
        number = number.trim();

        // Remove trailing whitespace/separators
        number = number.replaceAll(RegExp(r'[\s\-.]$'), '');

        // Normalize for validation
        String normalized = _normalizeNumber(number);

        // Validate: must have at least 7 digits (ITU E.164) and max 15
        final digitsOnly = normalized.replaceAll(RegExp(r'[^\d]'), '');
        if (digitsOnly.length >= 7 && digitsOnly.length <= 15) {
          // Additional validation: reject fake numbers
          if (_isValidPhoneNumber(digitsOnly)) {
            if (!_isDuplicate(number, foundNumbers)) {
              foundNumbers.add(number);
            }
          }
        }
      }
    }

    return foundNumbers.toList();
  }

  /// Validates that a number looks like a real phone number.
  /// Rejects repeated digits (0000000, 1111111) and other invalid patterns.
  bool _isValidPhoneNumber(String digitsOnly) {
    // Reject if all digits are the same (e.g., 0000000, 1111111)
    if (digitsOnly.split('').toSet().length == 1) {
      return false;
    }

    // Reject if it's only zeros with maybe one other digit
    final zeroCount = digitsOnly.split('').where((c) => c == '0').length;
    if (zeroCount >= digitsOnly.length - 1 && digitsOnly.length < 9) {
      return false;
    }

    return true;
  }

  /// Normalizes a phone number.
  /// - Converts 00XXX to +XXX (international format)
  String _normalizeNumber(String number) {
    String normalized = number.trim();
    if (normalized.startsWith('00') && !normalized.startsWith('000')) {
      normalized = '+${normalized.substring(2)}';
    }
    return normalized;
  }

  /// Check if a number is a duplicate.
  bool _isDuplicate(String number, Set<String> existingNumbers) {
    final normalizedNew = _normalizeNumber(number).replaceAll(RegExp(r'[^\d+]'), '');

    for (final existing in existingNumbers) {
      final normalizedExisting = _normalizeNumber(existing).replaceAll(RegExp(r'[^\d+]'), '');

      if (normalizedNew == normalizedExisting) return true;

      final digitsNew = normalizedNew.replaceAll('+', '');
      final digitsExisting = normalizedExisting.replaceAll('+', '');

      if (digitsNew.endsWith(digitsExisting) ||
          digitsExisting.endsWith(digitsNew)) {
        if ((digitsNew.length - digitsExisting.length).abs() <= 4) {
          return true;
        }
      }
    }
    return false;
  }
}