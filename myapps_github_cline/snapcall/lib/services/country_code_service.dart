/// Country Code Service for SnapCall
/// Handles detection of local numbers and automatic country code addition.
/// Supports 50+ countries with region-specific rules.

class CountryInfo {
  final String code; // ISO 3166-1 alpha-2 (e.g. "SK")
  final String name; // English name
  final String dialCode; // International prefix (e.g. "+421")
  final String flag; // Emoji flag
  final String localPrefix; // What local numbers start with (e.g. "0")
  final bool keepPrefixInternational; // Italy exception: keep 0 in international format

  const CountryInfo({
    required this.code,
    required this.name,
    required this.dialCode,
    required this.flag,
    this.localPrefix = '0',
    this.keepPrefixInternational = false,
  });
}

class CountryCodeService {
  // Session state - remembered during app session only
  CountryInfo? _selectedCountry;
  List<CountryInfo> _recentCountries = [];

  /// Currently selected country for this session
  CountryInfo? get selectedCountry => _selectedCountry;

  /// Recently used countries (session only)
  List<CountryInfo> get recentCountries => _recentCountries;

  /// Set country for this session
  void setCountry(CountryInfo country) {
    _selectedCountry = country;
    // Add to recent if not already there
    _recentCountries.removeWhere((c) => c.code == country.code);
    _recentCountries.insert(0, country);
    if (_recentCountries.length > 5) {
      _recentCountries = _recentCountries.sublist(0, 5);
    }
  }

  /// Detect if a phone number is local (missing international prefix)
  bool isLocalNumber(String number) {
    final cleaned = number.replaceAll(RegExp(r'[\s\-.\(\)]'), '');
    // Already international
    if (cleaned.startsWith('+')) return false;
    if (cleaned.startsWith('00') && cleaned.length > 6) return false;
    return true;
  }

  /// Add country code to a local number based on selected country
  /// Returns the number with country code, or original if already international
  String addCountryCode(String number, CountryInfo country) {
    if (!isLocalNumber(number)) return number;

    final cleaned = number.replaceAll(RegExp(r'[\s\-.\(\)]'), '');

    // Apply country-specific rules
    switch (country.code) {
      // === STRIP "0" COUNTRIES ===
      // Most of Europe, Asia, Australia
      case 'SK':
      case 'DE':
      case 'AT':
      case 'GB':
      case 'FR':
      case 'NL':
      case 'BE':
      case 'CH':
      case 'FI':
      case 'SE':
      case 'UA':
      case 'AU':
      case 'JP':
      case 'KR':
      case 'PT':
      case 'IE':
      case 'GR':
      case 'RO':
      case 'BG':
      case 'HR':
      case 'SI':
      case 'RS':
      case 'NZ':
      case 'ZA':
      case 'TR':
        if (cleaned.startsWith('0')) {
          return '${country.dialCode} ${cleaned.substring(1)}';
        }
        return '${country.dialCode} $cleaned';

      // === ITALY - SPECIAL: Keep 0 in international format ===
      case 'IT':
        // Italian numbers keep the leading 0 even in international format
        // +39 06 1234 5678 (not +39 6 1234 5678)
        return '${country.dialCode} $cleaned';

      // === HUNGARY - Strip "06" ===
      case 'HU':
        if (cleaned.startsWith('06')) {
          return '${country.dialCode} ${cleaned.substring(2)}';
        }
        return '${country.dialCode} $cleaned';

      // === RUSSIA - Strip "8" ===
      case 'RU':
        if (cleaned.startsWith('8') && cleaned.length >= 10) {
          return '${country.dialCode} ${cleaned.substring(1)}';
        }
        return '${country.dialCode} $cleaned';

      // === NO-STRIP COUNTRIES (no leading 0 in local format) ===
      // CZ, PL, NO, DK, ES, IN, US/CA, MX, BR, AR, CN
      case 'CZ':
      case 'PL':
      case 'NO':
      case 'DK':
      case 'ES':
      case 'IN':
      case 'US':
      case 'CA':
      case 'MX':
      case 'BR':
      case 'AR':
      case 'CN':
        return '${country.dialCode} $cleaned';

      // Default: try strip 0 if starts with 0, otherwise just prepend code
      default:
        if (cleaned.startsWith('0')) {
          return '${country.dialCode} ${cleaned.substring(1)}';
        }
        return '${country.dialCode} $cleaned';
    }
  }

  /// Full list of supported countries (50+)
  static const List<CountryInfo> allCountries = [
    // Europe
    CountryInfo(code: 'SK', name: 'Slovakia', dialCode: '+421', flag: '🇸🇰'),
    CountryInfo(code: 'CZ', name: 'Czech Republic', dialCode: '+420', flag: '🇨🇿', localPrefix: ''),
    CountryInfo(code: 'DE', name: 'Germany', dialCode: '+49', flag: '🇩🇪'),
    CountryInfo(code: 'AT', name: 'Austria', dialCode: '+43', flag: '🇦🇹'),
    CountryInfo(code: 'HU', name: 'Hungary', dialCode: '+36', flag: '🇭🇺', localPrefix: '06'),
    CountryInfo(code: 'PL', name: 'Poland', dialCode: '+48', flag: '🇵🇱', localPrefix: ''),
    CountryInfo(code: 'FR', name: 'France', dialCode: '+33', flag: '🇫🇷'),
    CountryInfo(code: 'GB', name: 'United Kingdom', dialCode: '+44', flag: '🇬🇧'),
    CountryInfo(code: 'IT', name: 'Italy', dialCode: '+39', flag: '🇮🇹', keepPrefixInternational: true),
    CountryInfo(code: 'ES', name: 'Spain', dialCode: '+34', flag: '🇪🇸', localPrefix: ''),
    CountryInfo(code: 'NL', name: 'Netherlands', dialCode: '+31', flag: '🇳🇱'),
    CountryInfo(code: 'BE', name: 'Belgium', dialCode: '+32', flag: '🇧🇪'),
    CountryInfo(code: 'CH', name: 'Switzerland', dialCode: '+41', flag: '🇨🇭'),
    CountryInfo(code: 'SE', name: 'Sweden', dialCode: '+46', flag: '🇸🇪'),
    CountryInfo(code: 'NO', name: 'Norway', dialCode: '+47', flag: '🇳🇴', localPrefix: ''),
    CountryInfo(code: 'DK', name: 'Denmark', dialCode: '+45', flag: '🇩🇰', localPrefix: ''),
    CountryInfo(code: 'FI', name: 'Finland', dialCode: '+358', flag: '🇫🇮'),
    CountryInfo(code: 'PT', name: 'Portugal', dialCode: '+351', flag: '🇵🇹'),
    CountryInfo(code: 'IE', name: 'Ireland', dialCode: '+353', flag: '🇮🇪'),
    CountryInfo(code: 'GR', name: 'Greece', dialCode: '+30', flag: '🇬🇷'),
    CountryInfo(code: 'RO', name: 'Romania', dialCode: '+40', flag: '🇷🇴'),
    CountryInfo(code: 'BG', name: 'Bulgaria', dialCode: '+359', flag: '🇧🇬'),
    CountryInfo(code: 'HR', name: 'Croatia', dialCode: '+385', flag: '🇭🇷'),
    CountryInfo(code: 'SI', name: 'Slovenia', dialCode: '+386', flag: '🇸🇮'),
    CountryInfo(code: 'RS', name: 'Serbia', dialCode: '+381', flag: '🇷🇸'),
    CountryInfo(code: 'UA', name: 'Ukraine', dialCode: '+380', flag: '🇺🇦'),
    CountryInfo(code: 'RU', name: 'Russia', dialCode: '+7', flag: '🇷🇺', localPrefix: '8'),
    CountryInfo(code: 'TR', name: 'Turkey', dialCode: '+90', flag: '🇹🇷'),

    // Americas
    CountryInfo(code: 'US', name: 'United States', dialCode: '+1', flag: '🇺🇸', localPrefix: ''),
    CountryInfo(code: 'CA', name: 'Canada', dialCode: '+1', flag: '🇨🇦', localPrefix: ''),
    CountryInfo(code: 'MX', name: 'Mexico', dialCode: '+52', flag: '🇲🇽', localPrefix: ''),
    CountryInfo(code: 'BR', name: 'Brazil', dialCode: '+55', flag: '🇧🇷', localPrefix: ''),
    CountryInfo(code: 'AR', name: 'Argentina', dialCode: '+54', flag: '🇦🇷', localPrefix: ''),

    // Asia-Pacific
    CountryInfo(code: 'CN', name: 'China', dialCode: '+86', flag: '🇨🇳', localPrefix: ''),
    CountryInfo(code: 'JP', name: 'Japan', dialCode: '+81', flag: '🇯🇵'),
    CountryInfo(code: 'KR', name: 'South Korea', dialCode: '+82', flag: '🇰🇷'),
    CountryInfo(code: 'IN', name: 'India', dialCode: '+91', flag: '🇮🇳', localPrefix: ''),
    CountryInfo(code: 'AU', name: 'Australia', dialCode: '+61', flag: '🇦🇺'),
    CountryInfo(code: 'NZ', name: 'New Zealand', dialCode: '+64', flag: '🇳🇿'),

    // Middle East & Africa
    CountryInfo(code: 'AE', name: 'UAE', dialCode: '+971', flag: '🇦🇪'),
    CountryInfo(code: 'SA', name: 'Saudi Arabia', dialCode: '+966', flag: '🇸🇦'),
    CountryInfo(code: 'IL', name: 'Israel', dialCode: '+972', flag: '🇮🇱'),
    CountryInfo(code: 'EG', name: 'Egypt', dialCode: '+20', flag: '🇪🇬'),
    CountryInfo(code: 'ZA', name: 'South Africa', dialCode: '+27', flag: '🇿🇦'),
    CountryInfo(code: 'NG', name: 'Nigeria', dialCode: '+234', flag: '🇳🇬'),
    CountryInfo(code: 'KE', name: 'Kenya', dialCode: '+254', flag: '🇰🇪'),

    // Southeast Asia
    CountryInfo(code: 'TH', name: 'Thailand', dialCode: '+66', flag: '🇹🇭'),
    CountryInfo(code: 'VN', name: 'Vietnam', dialCode: '+84', flag: '🇻🇳'),
    CountryInfo(code: 'PH', name: 'Philippines', dialCode: '+63', flag: '🇵🇭'),
    CountryInfo(code: 'ID', name: 'Indonesia', dialCode: '+62', flag: '🇮🇩'),
    CountryInfo(code: 'MY', name: 'Malaysia', dialCode: '+60', flag: '🇲🇾'),
    CountryInfo(code: 'SG', name: 'Singapore', dialCode: '+65', flag: '🇸🇬', localPrefix: ''),
  ];

  /// Search countries by name or code
  static List<CountryInfo> search(String query) {
    final q = query.toLowerCase();
    return allCountries.where((c) =>
      c.name.toLowerCase().contains(q) ||
      c.code.toLowerCase().contains(q) ||
      c.dialCode.contains(q)
    ).toList();
  }

  /// Get country by ISO code
  static CountryInfo? getByCode(String code) {
    try {
      return allCountries.firstWhere((c) => c.code == code.toUpperCase());
    } catch (_) {
      return null;
    }
  }
}