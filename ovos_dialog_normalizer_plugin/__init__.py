import json
import re
from functools import cache
from pathlib import Path

import text2spoken
from ovos_bus_client.session import Session, SessionManager
from ovos_number_parser import pronounce_number
from ovos_plugin_manager.templates.transformers import DialogTransformer
from ovos_utils.log import LOG
from unicode_rbnf import FormatPurpose, RbnfEngine

LOCALE = Path(__file__).parent / "locale"


@cache
def _locale_table(lang: str, name: str) -> dict[str, str]:
    path = LOCALE / lang / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


@cache
def text2spoken_reads(lang: str) -> bool:
    """True when text2spoken has a language file for `lang`.

    A language with no file gets the text2spoken core language, which reads
    only cardinals and lexicon entries, so it stays on the legacy path.
    """
    try:
        forms = text2spoken.supports(lang).forms
    except text2spoken.Text2SpokenError:
        return False
    return bool(forms - {text2spoken.Form.LEXICON, text2spoken.Form.CARDINAL})


def expand_contractions(dialog: str, lang: str) -> str:
    contractions = _locale_table(lang.split("-")[0], "contractions")
    if not contractions:
        return dialog
    return re.sub(r"\S+", lambda word: contractions.get(word.group(), word.group()), dialog)


class DialogNormalizerTransformer(DialogTransformer):
    """OVOS Dialog Transformer plugin to normalize text for TTS engines.

    text2spoken reads numbers, dates, times, money, units, symbols and
    abbreviations in every language it has a language file for. Other
    languages keep the legacy digit and title expansion.
    """

    def __init__(self, name="ovos-dialog-normalizer-plugin", priority=5, config=None):
        super().__init__(name=name, priority=priority, config=config)

    def transform(self, dialog: str, context: dict | None = None) -> tuple[str, dict]:
        """Normalize dialog text in the language of the session."""
        context = context or {}
        sess = Session.deserialize(context["session"]) if "session" in context else SessionManager.get()
        if text2spoken_reads(sess.lang):
            return self.read_with_text2spoken(dialog, sess.lang), context
        return self.legacy_normalize(dialog, sess.lang), context

    @staticmethod
    def read_with_text2spoken(dialog: str, lang: str) -> str:
        """Expand contractions, then read written forms with text2spoken.

        On a text2spoken failure the dialog stays as it was given.
        """
        try:
            spoken = text2spoken.normalize(expand_contractions(dialog, lang), lang)
        except Exception as e:
            LOG.warning(f"text2spoken failed to read dialog '{dialog}' ({lang}): {e}")
            return dialog
        LOG.debug(f"normalized dialog: '{dialog}' -> '{spoken}'")
        return spoken

    @staticmethod
    def legacy_normalize(dialog: str, full_lang: str) -> str:
        """Digit, title and contraction expansion for languages text2spoken does not read."""
        lang = full_lang.split("-")[0]
        contractions = _locale_table(lang, "contractions")
        titles = _locale_table(lang, "titles")

        original = dialog
        try:
            rbnf_engine = RbnfEngine.for_language(lang)
        except Exception:  # doesnt support lang
            rbnf_engine = None

        # substitute ' €' by 'euros' and 'someword€' by 'someword euros'
        dialog = re.sub(r"(\w+)\s*€", r"\1 euros", dialog)

        try:
            if lang == "gl":
                # substitute ' ºC' by 'graos centígrados' and 'somewordºC' by 'someword graos centígrados'
                dialog = re.sub(r"(\w+)\s*ºC", r"\1 graos centígrados", dialog)

            words = dialog.split()
            for idx, word in enumerate(words):

                if word in contractions:
                    words[idx] = contractions[word]
                    continue

                if word in titles:
                    words[idx] = titles[word]
                    continue

                if word.isdigit():
                    try:
                        words[idx] = pronounce_number(int(word), lang=full_lang)
                    except Exception as e:
                        LOG.error(f"ovos-number-parser failed to pronounce number: {word} - ({e})")

                # NOTE: pronounce_digit may return the digit itself again for some languages (upstream bug)
                # we recheck if isdigit() to handle this
                if rbnf_engine and words[idx].isdigit():
                    # fallback to unicode RBNF
                    try:
                        words[idx] = rbnf_engine.format_number(word, FormatPurpose.CARDINAL).text
                    except Exception as e:
                        LOG.error(f"unicode-rbnf failed to pronounce number: {word} - ({e})")

            dialog = " ".join(words)

            LOG.debug(f"normalized dialog: '{original}' -> '{dialog}'")
        except Exception as e:
            LOG.error(f"Failed to normalize dialog: {e}")

        return dialog


if __name__ == "__main__":
    # 'I am Doctor Prof. twelve thousand three hundred forty-five euros'
    print(DialogNormalizerTransformer().transform("I'm Dr. Prof. 12345 €"))
