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
  /// Supports various international and local phone number formats.
  List<String> _findPhoneNumbers(String text) {
    // Comprehensive regex patterns for phone numbers
    final List<RegExp> patterns = [
      // International format: +421 123 456 789, +1-234-567-8901
      RegExp(r'\+\d{1,3}[\s\-.]?\(?\d{1,4}\)?[\s\-.]?\d{1,4}[\s\-.]?\d{1,4}[\s\-.]?\d{0,4}'),

      // Numbers with country code without +: 00421 123 456 789
      RegExp(r'00\d{1,3}[\s\-.]?\d{1,4}[\s\-.]?\d{1,4}[\s\-.]?\d{1,4}'),

      // Local formats with area code in parentheses: (02) 1234 5678
      RegExp(r'\(\d{2,4}\)[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}'),

      // Standard formats: 0912 345 678, 0912-345-678, 0912.345.678
      RegExp(r'0\d{2,3}[\s\-.]?\d{3}[\s\-.]?\d{3,4}'),

      // Continuous digits (7-15 digits, possibly starting with +)
      RegExp(r'\+?\d{7,15}'),

      // US/CA format: 234-567-8901, (234) 567-8901
      RegExp(r'\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'),
    ];

    final Set<String> foundNumbers = {};

    for (final pattern in patterns) {
      final matches = pattern.allMatches(text);
      for (final match in matches) {
        String number = match.group(0) ?? '';
        number = number.trim();

        // Validate: must have at least 7 digits
        final digitsOnly = number.replaceAll(RegExp(r'[^\d]'), '');
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

  /// Check if a number is a duplicate of an already found number.
  /// Compares by stripping all non-digit characters.
  bool _isDuplicate(String number, Set<String> existingNumbers) {
    final normalizedNew = number.replaceAll(RegExp(r'[^\d+]'), '');

    for (final existing in existingNumbers) {
      final normalizedExisting = existing.replaceAll(RegExp(r'[^\d+]'), '');
      if (normalizedNew == normalizedExisting) {
        return true;
      }
      // Also check if one contains the other (e.g., with/without country code)
      if (normalizedNew.endsWith(normalizedExisting) ||
          normalizedExisting.endsWith(normalizedNew)) {
        if ((normalizedNew.length - normalizedExisting.length).abs() <= 3) {
          return true;
        }
      }
    }
    return false;
  }
}