import datetime
import json
import os
import re
import string
from datetime import date

from ovos_date_parser import nice_time, nice_date
from ovos_number_parser import pronounce_number, pronounce_fraction
from ovos_number_parser.util import is_numeric
from ovos_utils.log import LOG
from unicode_rbnf import RbnfEngine, FormatPurpose

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "locale")


# --- Locale Data Management Class ---
class LocaleDataManager:
    """
    A helper class to lazy-load and cache locale-specific data from JSON files.
    The data is not hardcoded and will be loaded from a 'locale' directory
    containing language-specific JSON files on first use.
    """

    def __init__(self):
        """Initializes an empty cache for locale data."""
        self.cache = {}

    def _load_data(self, lang_code: str, file_name: str) -> dict:
        """Loads a single JSON file and caches it."""
        file_path = os.path.join(RESOURCES_DIR, lang_code, f"{file_name}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cache.setdefault(lang_code, {})[file_name] = data
                return data
        except FileNotFoundError:
            LOG.debug(f"Locale file not found: {file_path}. Using empty dictionary.")
            self.cache.setdefault(lang_code, {})[file_name] = {}
            return {}
        except json.JSONDecodeError as e:
            LOG.error(f"Error decoding JSON from {file_path}: {e}")
            self.cache.setdefault(lang_code, {})[file_name] = {}
            return {}

    def get_data(self, lang_code: str, file_name: str) -> dict:
        """Retrieves data for a given language and file, using the cache."""
        if lang_code in self.cache and file_name in self.cache[lang_code]:
            return self.cache[lang_code][file_name]
        return self._load_data(lang_code, file_name)

    def get_contractions(self, lang_code: str) -> dict:
        return self.get_data(lang_code, "contractions")

    def get_units(self, lang_code: str) -> dict:
        return self.get_data(lang_code, "units")

    def get_titles(self, lang_code: str) -> dict:
        return self.get_data(lang_code, "titles")


# Instantiate the manager to be used by the normalization functions
locale_data_manager = LocaleDataManager()


def _get_number_separators(full_lang: str) -> tuple[str, str]:
    """
    Return the decimal and thousands separators appropriate for the specified language.
    
    Parameters:
        full_lang (str): The full language code (e.g., "en-US", "pt-BR").
    
    Returns:
        tuple[str, str]: A tuple containing the decimal separator and thousands separator for the language.
    """
    lang_code = full_lang.split("-")[0]
    decimal_separator = '.'
    thousands_separator = ','
    # TODO This logic can also be moved to a JSON file
    if lang_code in ["pt", "es", "fr", "de"]:
        decimal_separator = ','
        thousands_separator = '.'
    return decimal_separator, thousands_separator


def _normalize_number_word(word: str, full_lang: str, rbnf_engine) -> str:
    """
    Normalizes a word representing a number or fraction, converting it to its spoken form according to locale conventions.
    
    Handles locale-specific decimal and thousands separators, expands fractions, and uses available pronunciation engines to generate the spoken equivalent. If normalization fails, returns the original word.
    """
    cleaned_word = word.rstrip(string.punctuation)

    # Handle fractions like '3/3'
    if is_fraction(cleaned_word):
        try:
            return pronounce_fraction(cleaned_word, full_lang) + word[len(cleaned_word):]
        except Exception as e:
            LOG.error(f"ovos-number-parser failed to pronounce fraction: {word} - ({e})")
            return word

    # Handle numbers with locale-specific separators
    decimal_separator, thousands_separator = _get_number_separators(full_lang)
    temp_cleaned_word = cleaned_word

    # Check if the word contains a thousands separator followed by digits and a decimal separator
    # This is a specific check for formats like '123.456,78'
    has_thousands_and_decimal = (
            thousands_separator in temp_cleaned_word and
            decimal_separator in temp_cleaned_word and
            temp_cleaned_word.index(thousands_separator) < temp_cleaned_word.index(decimal_separator)
    )

    if has_thousands_and_decimal:
        temp_cleaned_word = temp_cleaned_word.replace(thousands_separator, "")
        temp_cleaned_word = temp_cleaned_word.replace(decimal_separator, ".")
    elif decimal_separator in temp_cleaned_word and is_numeric(temp_cleaned_word.replace(decimal_separator, ".", 1)):
        # Handle cases like '1,2' -> '1.2'
        temp_cleaned_word = temp_cleaned_word.replace(decimal_separator, ".")
    elif thousands_separator in temp_cleaned_word and is_numeric(temp_cleaned_word.replace(thousands_separator, "", 1)):
        # Handle cases like '1.234' -> '1234'
        temp_cleaned_word = temp_cleaned_word.replace(thousands_separator, "")

    # Check if the word is a valid number after processing
    if is_numeric(temp_cleaned_word):
        try:
            num = float(temp_cleaned_word) if "." in temp_cleaned_word else int(temp_cleaned_word)
            return pronounce_number(num, lang=full_lang) + word[len(cleaned_word):]
        except Exception as e:
            LOG.error(f"ovos-number-parser failed to pronounce number: {word} - ({e})")
            return word

    elif rbnf_engine and cleaned_word.isdigit():
        try:
            pronounced_number = rbnf_engine.format_number(cleaned_word, FormatPurpose.CARDINAL).text
            return pronounced_number + word[len(cleaned_word):]
        except Exception as e:
            LOG.error(f"unicode-rbnf failed to pronounce number: {word} - ({e})")
            return word

    return word


# --- Date and Time Pronunciation ---
def pronounce_date(date_obj: date, full_lang: str) -> str:
    """
    Return the spoken form of a date object in the specified language.
    
    Parameters:
        date_obj (date): The date to be pronounced.
        full_lang (str): The language code for pronunciation.
    
    Returns:
        str: The spoken representation of the date.
    """
    return nice_date(date_obj, full_lang)


def pronounce_time(time_string: str, full_lang: str) -> str:
    """
    Convert a time string in "HHhMM" format to its spoken form in the specified language.
    
    If parsing fails, returns the input string with "h" replaced by a space.
    """
    try:
        hours, mins = time_string.split("h")
        time_obj = datetime.time(int(hours), int(mins))
        # Use nice_time from ovos-date-parser
        return nice_time(time_obj, full_lang, speech=True, use_24hour=True, use_ampm=False)
    except Exception as e:
        LOG.warning(f"Failed to parse time string '{time_string}': {e}")
        return time_string.replace("h", " ")


def _normalize_dates_and_times(text: str, full_lang: str, date_format: str = "DMY") -> str:
    """
    Normalizes dates and times in a text string, converting them to their spoken equivalents for the specified language.
    
    This function identifies and processes time expressions (e.g., "15h01") and date patterns (e.g., "DD/MM/YYYY", "YYYY/MM/DD") using regular expressions. It handles locale-specific formats, expands ambiguous years, and replaces recognized dates and times with their pronounced forms suitable for text-to-speech. For English, it also separates and expands "am"/"pm" time markers.
    
    Parameters:
        text (str): The input text containing dates and times to normalize.
        full_lang (str): The language code specifying the locale for normalization.
        date_format (str, optional): The expected date format ("DMY" or "MDY"). Defaults to "DMY".
    
    Returns:
        str: The text with dates and times replaced by their spoken equivalents.
    """
    lang_code = full_lang.split("-")[0]
    # Pre-process with regex to handle English am/pm times
    if lang_code == "en":
        text = re.sub(r"(?i)(\d+)(am|pm)", r"\1 \2", text)
        # Handle the pronunciation for TTS
        text = text.replace("am", "A M").replace("pm", "P M")

    # Normalize times like "15h01" to words
    time_pattern = re.compile(r"(\d{1,2})h(\d{2})", re.IGNORECASE)

    def replace_time(match):
        """
        Replaces a matched time string with its spoken equivalent in the specified language.
        
        Parameters:
        	match: A regex match object containing the time string to be pronounced.
        
        Returns:
        	A string with the time expressed in spoken form for the target language.
        """
        time_str = match.group(0)
        return pronounce_time(time_str, full_lang)

    text = time_pattern.sub(replace_time, text)

    # Find dates like "DD/MM/YYYY" or "YYYY/MM/DD"
    date_pattern = re.compile(r"(\d{1,4})[/-](\d{1,2})[/-](\d{1,4})")

    match = date_pattern.search(text)

    if match:
        # Get the three parts of the date string
        part1_str, part2_str, part3_str = match.groups()
        p1, p2, p3 = int(part1_str), int(part2_str), int(part3_str)

        # Initialize month, day, and year
        month, day, year = None, None, None

        # Determine year first based on length (4 digits)
        if len(part1_str) == 4:
            year, rest_parts = p1, [p2, p3]
        elif len(part3_str) == 4:
            year, rest_parts = p3, [p1, p2]
        else:
            # If no 4-digit year, it's ambiguous, assume a 2-digit year.
            # We'll assume the last part is the year based on common patterns.
            year = p3
            # Expand 2-digit year to 4-digit year
            if year < 100:
                # Assume years 00-29 are 2000-2029, 30-99 are 1930-1999
                year = 2000 + year if year < 30 else 1900 + year
            rest_parts = [p1, p2]

        # From the remaining parts, try to determine day and month
        if day is None and any(p > 12 and len(str(p)) == 2 for p in rest_parts):
            # If a two-digit number is > 12, it's a day
            day_candidate = next((p for p in rest_parts if p > 12), None)
            if day_candidate:
                day = day_candidate
                rest_parts.remove(day_candidate)
                month = rest_parts[0]

        # Fallback to date_format if day/month are still ambiguous
        if day is None or month is None:
            if date_format.lower() == "mdy":
                month, day = rest_parts[0], rest_parts[1]
            else:  # default to DD/MM/YY
                day, month = rest_parts[0], rest_parts[1]

        try:
            date_obj = date(year, month, day)
            pronounced_date_str = pronounce_date(date_obj, full_lang)
            text = text.replace(match.group(0), pronounced_date_str)
        except (ValueError, IndexError) as e:
            LOG.warning(f"Could not parse date from '{match.group(0)}': {e}")

    return text


def _normalize_word_hyphen_digit(text: str) -> str:
    """
    Replaces occurrences of a word followed by a hyphen and digits with the word and number separated by a space.
    
    For example, transforms 'sub-23' into 'sub 23'.
    """
    # Regex to find a word (\w+) followed by a hyphen and a digit (\d+)
    pattern = re.compile(r"(\w+)-(\d+)")
    text = pattern.sub(r"\1 \2", text)
    return text


def _normalize_units(text: str, full_lang: str) -> str:
    """
    Expands and pronounces units attached to numbers in the text according to the specified language.
    
    This function detects numbers followed by unit symbols or abbreviations (e.g., "50kg", "100€"), converts the number to its spoken form, and replaces the unit with its full word equivalent based on language-specific mappings. Handles both symbolic (non-alphanumeric) and alphanumeric units, accounting for locale-specific decimal and thousands separators.
    
    Returns:
        str: The text with numbers and units normalized to their spoken forms.
    """
    text = text.replace("º", "°")  # these characters look the same... but...
    lang_code = full_lang.split("-")[0]
    units_data = locale_data_manager.get_units(lang_code)

    if units_data:
        # Determine number separators for the language
        decimal_separator, thousands_separator = _get_number_separators(full_lang)

        # Separate units into symbolic and alphanumeric
        symbolic_units = {k: v for k, v in units_data.items() if not k.isalnum()}
        alphanumeric_units = {k: v for k, v in units_data.items() if k.isalnum()}

        # Create regex pattern for symbolic units and replace them first
        sorted_symbolic = sorted(symbolic_units.keys(), key=len, reverse=True)
        symbolic_pattern_str = "|".join(re.escape(unit) for unit in sorted_symbolic)
        if symbolic_pattern_str:
            # Pattern to match numbers with optional thousands and decimal separators
            number_pattern_str = rf"(\d+[{re.escape(thousands_separator)}]?\d*[{re.escape(decimal_separator)}]?\d*)"
            symbolic_pattern = re.compile(number_pattern_str + r"\s*(" + symbolic_pattern_str + r")", re.IGNORECASE)

            def replace_symbolic(match):
                """
                Replaces a matched symbolic unit expression with its spoken number and unit word equivalent.
                
                The function is intended for use as a regex replacement callback, converting patterns like "50%" or "1.5€" into their spoken forms (e.g., "fifty percent" or "one point five euros") according to the specified language. If pronunciation fails, returns the original matched string.
                """
                number = match.group(1)
                # Remove thousands separator and replace decimal separator for parsing
                if thousands_separator in number and decimal_separator in number:
                    number = number.replace(thousands_separator, "").replace(decimal_separator, ".")
                elif decimal_separator != "." and decimal_separator in number:
                    number = number.replace(decimal_separator, ".")
                unit_symbol = match.group(2)
                unit_word = symbolic_units[unit_symbol]
                try:
                    return f"{pronounce_number(float(number) if '.' in number else int(number), full_lang)} {unit_word}"
                except Exception as e:
                    LOG.error(f"Failed to pronounce number with unit: {number}{unit_symbol} - ({e})")
                    return match.group(0)

            text = symbolic_pattern.sub(replace_symbolic, text)

        # Create regex pattern for alphanumeric units and replace them next
        sorted_alphanumeric = sorted(alphanumeric_units.keys(), key=len, reverse=True)
        alphanumeric_pattern_str = "|".join(re.escape(unit) for unit in sorted_alphanumeric)
        if alphanumeric_pattern_str:
            number_pattern_str = rf"(\d+[{re.escape(thousands_separator)}]?\d*[{re.escape(decimal_separator)}]?\d*)"
            alphanumeric_pattern = re.compile(number_pattern_str + r"\s*(" + alphanumeric_pattern_str + r")\b",
                                              re.IGNORECASE)

            def replace_alphanumeric(match):
                """
                Replaces a matched alphanumeric unit expression with its spoken number and full unit name.
                
                Parameters:
                	match: A regex match object containing a number and an alphanumeric unit symbol.
                
                Returns:
                	A string with the number pronounced in the specified language followed by the expanded unit name.
                """
                number = match.group(1)
                # Remove thousands separator and replace decimal separator for parsing
                if thousands_separator in number and decimal_separator in number:
                    number = number.replace(thousands_separator, "").replace(decimal_separator, ".")
                elif decimal_separator != "." and decimal_separator in number:
                    number = number.replace(decimal_separator, ".")
                unit_symbol = match.group(2)
                unit_word = alphanumeric_units[unit_symbol]
                return f"{pronounce_number(float(number) if '.' in number else int(number), full_lang)} {unit_word}"

            text = alphanumeric_pattern.sub(replace_alphanumeric, text)
    return text


def _normalize_word(word: str, full_lang: str, rbnf_engine) -> str:
    """
    Normalizes a single word by expanding contractions, titles, or pronouncing numbers and fractions.
    
    If the word matches a known contraction or title in the specified language, it is expanded to its full form. If the word represents a number or fraction, it is converted to its spoken equivalent. Returns the original word if no normalization applies.
    """
    lang_code = full_lang.split("-")[0]
    contractions = locale_data_manager.get_contractions(lang_code)
    titles = locale_data_manager.get_titles(lang_code)

    if word in contractions:
        return contractions[word]

    if word in titles:
        return titles[word]

    # Delegate number parsing to the new helper function
    normalized_number = _normalize_number_word(word, full_lang, rbnf_engine)
    if normalized_number != word:
        return normalized_number

    return word


def is_fraction(word: str) -> bool:
    """
    Determine if the input string represents a numeric fraction in the form 'n1/n2'.
    
    Returns:
        bool: True if the string is a fraction with two integer components separated by '/', otherwise False.
    """
    if "/" in word:
        parts = word.split("/")
        if len(parts) == 2:
            n1, n2 = parts
            return n1.isdigit() and n2.isdigit()
    return False


def normalize(text: str, lang: str) -> str:
    """
    Normalize a text string for spoken output by expanding contractions, titles, numbers, units, fractions, dates, and times according to the specified language.
    
    Parameters:
        text (str): The input text to normalize.
        lang (str): The language code (e.g., "en-US", "pt-PT") used for locale-specific normalization.
    
    Returns:
        str: The normalized text with contractions expanded, numbers and units pronounced, and dates and times converted to spoken form.
    """
    full_lang = lang
    lang_code = full_lang.split("-")[0]
    dialog = text

    # Step 1: Handle dates and times with ovos-date-parser
    date_format = "MDY" if full_lang.lower() == "en-us" else "DMY"
    dialog = _normalize_dates_and_times(dialog, full_lang, date_format)

    # Step 2: Normalize words with hyphens and digits
    dialog = _normalize_word_hyphen_digit(dialog)

    # Step 3: Expand units attached to numbers
    dialog = _normalize_units(dialog, full_lang)

    # Step 4: Normalize word-by-word
    words = dialog.split()
    rbnf_engine = None
    try:
        rbnf_engine = RbnfEngine.for_language(lang_code)
    except (ValueError, KeyError) as e:
        LOG.debug(f"RBNF engine not available for language '{lang_code}': {e}")

    normalized_words = [_normalize_word(word, full_lang, rbnf_engine) for word in words]
    dialog = " ".join(normalized_words)

    return dialog


if __name__ == "__main__":
    # --- Example usage for demonstration purposes ---

    # General normalization examples
    print("General English example: " + normalize('I\'m Dr. Prof. 3/3 0.5% of 12345€, 5ft, and 10kg', 'en'))
    print(
        f"Word Salad Portuguese (Dr. Prof. 3/3 0,5% de 12345€, 5m, e 10kg): {normalize('Dr. Prof. 3/3 0,5% de 12345€, 5m, e 10kg', 'pt')}")
    print(
        f"Word Salad Portuguese (Dr. Prof. 3/3 0.5% de 12345€, 5m, e 10kg): {normalize('Dr. Prof. 3/3 0.5% de 12345€, 5m, e 10kg', 'pt')}")

    # Portuguese examples with comma decimal separator
    print("\n--- Portuguese Decimal Separator Examples ---")
    print(
        f"Original: 'A coima aplicada é de 1,2 milhões de euros.' Normalized: '{normalize('A coima aplicada é de 1,2 milhões de euros.', 'pt')}'")
    print(
        f"Original: 'Agora, tem 1,88 metros e muito para contar.' Normalized: '{normalize('Agora, tem 1,88 metros e muito para contar.', 'pt')}'")
    print(
        f"Original: 'Ainda temos 1,7 milhões de pobres!' Normalized: '{normalize('Ainda temos 1,7 milhões de pobres!', 'pt')}'")
    print(f"Original: 'O lucro foi de 123.456,78€.' Normalized: '{normalize('O lucro foi de 123.456,78€.', 'pt')}'")
    print(f"Normalized: '{normalize('O lucro foi de 123.456,78€.', 'pt-PT')}'")

    # English dates and times
    print("\n--- English Date & Time Examples ---")
    print(f"English date (MDY format): {normalize('The date is 08/03/2025', 'en-US')}")
    print(f"English ambiguous date (MDY assumed): {normalize('The report is due 15/05/2025', 'en-US')}")
    print(f"English date with dashes: {normalize('The event is on 11-04-2025', 'en-US')}")
    print(f"English AM/PM time: {normalize('The meeting is at 10am', 'en-US')}")
    print(f"English military time: {normalize('The party is at 19h30', 'en-US')}")
    print(f"English month name: {normalize('The report is due 15 May 2025', 'en-US')}")

    # Portuguese dates and times
    print("\n--- Portuguese Date & Time Examples ---")
    print(f"Portuguese date (A data é 03/08/2025): {normalize('A data é 03/08/2025', 'pt')}")
    print(
        f"Portuguese ambiguous date (O relatório é para 15/05/2025): {normalize('O relatório é para 15/05/2025', 'pt')}")
    print(
        f"Portuguese date with dashes (O evento é no dia 25-10-2024): {normalize('O evento é no dia 25-10-2024', 'pt')}")
    print(f"Portuguese military time (O encontro é às 14h30): {normalize('O encontro é às 14h30', 'pt')}")

    # Other examples
    print(f"\n--- Other Examples ---")
    print(f"English fraction: {normalize('The fraction is 1/2', 'en')}")
    print(f"English plural fraction: {normalize('There are 3/4 of a cup', 'en')}")
    print(f"Spanish example with units: {normalize('The temperature is 25ºC', 'es')}")
    print(f"Portuguese with punctuation: {normalize('12345€, 5m e 10kg', 'pt')}")
    print(
        f"Portuguese word-digit: {normalize('Esta temporada leva oito jogos ao serviço da equipa sub-23 leonina.', 'pt')}")
