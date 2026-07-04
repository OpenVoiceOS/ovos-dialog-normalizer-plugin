import unittest

from ovos_dialog_normalizer_plugin.util import normalize, is_fraction


class TestIsFraction(unittest.TestCase):
    def test_valid_fraction(self):
        self.assertTrue(is_fraction("1/2"))
        self.assertTrue(is_fraction("10/100"))

    def test_invalid_fraction(self):
        self.assertFalse(is_fraction("1/2/3"))
        self.assertFalse(is_fraction("a/b"))
        self.assertFalse(is_fraction("12"))
        self.assertFalse(is_fraction("1.5"))


class TestNormalizeEnglish(unittest.TestCase):
    def test_titles_expanded(self):
        self.assertEqual(
            normalize("I am Dr. Prof. 12345", "en-US"),
            "I am Doctor Professor twelve thousand, three hundred and forty five",
        )

    def test_am_pm_only_on_clock(self):
        # "am" attached to a number is expanded, unrelated "am" is preserved
        self.assertEqual(normalize("The meeting is at 10am", "en-US"),
                         "The meeting is at ten A M")
        self.assertIn("I am", normalize("I am here", "en-US"))

    def test_units(self):
        self.assertEqual(normalize("The temperature is 25kg", "en"),
                         "The temperature is twenty five kilograms")

    def test_percent(self):
        self.assertEqual(normalize("It grew 50%", "en"),
                         "It grew fifty per cent")


class TestNormalizePortuguese(unittest.TestCase):
    def test_units_and_number(self):
        self.assertEqual(normalize("10kg", "pt"), "dez quilogramas")

    def test_word_hyphen_digit(self):
        # "sub-23" -> "sub 23" -> number expanded
        result = normalize("equipa sub-23", "pt")
        self.assertNotIn("-", result)
        self.assertIn("vinte e três", result)


class TestTransformerPlugin(unittest.TestCase):
    def test_transform_returns_tuple(self):
        from ovos_dialog_normalizer_plugin import DialogNormalizerTransformer
        plugin = DialogNormalizerTransformer()
        out, ctx = plugin.transform("I am Dr. Prof. 12345",
                                    {"session": {"session_id": "test", "lang": "en-US"}})
        self.assertEqual(
            out,
            "I am Doctor Professor twelve thousand, three hundred and forty five",
        )
        self.assertIsInstance(ctx, dict)

    def test_transform_no_context(self):
        from ovos_dialog_normalizer_plugin import DialogNormalizerTransformer
        plugin = DialogNormalizerTransformer()
        out, ctx = plugin.transform("hello world")
        self.assertIsInstance(out, str)


if __name__ == "__main__":
    unittest.main()
