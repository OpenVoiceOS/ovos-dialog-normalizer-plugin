"""The plugin reads written forms through text2spoken and keeps the legacy path for other languages."""
import re
from unittest import mock

import pytest
import text2spoken
from ovos_bus_client.session import Session, SessionManager

from ovos_dialog_normalizer_plugin import DialogNormalizerTransformer

# Each sentence holds a number, a date or a time, money or a unit.
SERVED = {
    "en-US": ["The meeting starts at 14:30 on 12/03/2024.",
              "The ticket costs $25.50 and the bag weighs 3 kg.",
              "I walked 5 km in 45 minutes.",
              "We have 1234 users and 3 servers.",
              "Pay 10 € before 9:15 tomorrow."],
    "en-GB": ["The train leaves at 07:45 on 01/02/2025.",
              "A pint costs £4.20 today.",
              "It is 20 °C outside."],
    "pt-PT": ["O Dr. Silva pagou 2,50 € às 14:30.",
              "A reunião é a 12/03/2024 às 9h15.",
              "Corri 10 km e bebi 2 litros de água.",
              "Comprei 3 casas por 250 €.",
              "A temperatura chegou aos 35 °C."],
    "pt-BR": ["O ingresso custa R$ 30,00 e começa às 20:00.",
              "Tenho 16 anos e peso 60 kg."],
    "es-ES": ["Son las 14:30 y cuesta 3 €.",
              "La reunión es el 12/03/2024.",
              "El Sr. García recorrió 15 km.",
              "Tengo 21 años y 2 hermanos.",
              "El paquete pesa 5 kg y cuesta 12,50 €."],
    "de-DE": ["Es ist 14:30 Uhr.",
              "Dr. Müller zahlt 5 € für 2 kg Äpfel.",
              "Der Termin ist am 12.03.2024.",
              "Wir fuhren 120 km in 2 Stunden.",
              "Das kostet 19,99 €."],
    "eu-ES": ["Bilera 14:30ean da.",
              "Liburuak 15 € balio du.",
              "2024ko martxoaren 12an etorri zen.",
              "10 km korrika egin nituen.",
              "3 etxe ditut."],
    "ru-RU": ["Встреча в 14:30.",
              "Билет стоит 500 рублей.",
              "Я прошёл 5 км.",
              "У меня 3 книги.",
              "Это было 12.03.2024."],
    "ar-SA": ["الساعة 14:30 الآن.",
              "اشتريت 3 كتب.",
              "المسافة 10 كم.",
              "السعر 50 دولار.",
              "عندي 25 سنة."],
}
SERVED_ROWS = [(lang, text) for lang, texts in SERVED.items() for text in texts]

# Readings checked by hand against the grammar of each language.
GOLD = [
    ("pt-PT", "O Dr. Silva pagou 2,50 € às 14:30.",
     "O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta."),
    ("pt-BR", "Tenho 16 anos.", "Tenho dezesseis anos."),
    ("pt-PT", "Tenho 16 anos.", "Tenho dezasseis anos."),
    ("en-US", "I walked 5 km.", "I walked five kilometers."),
    ("es-ES", "Cuesta 3 €.", "Cuesta tres euros."),
    ("de-DE", "Es ist 14:30 Uhr.", "Es ist vierzehn Uhr dreißig."),
]

# The output of dev a0c561d. text2spoken has no language file for these languages.
# When it gains one, the language moves to SERVED.
UNSERVED_DEV_OUTPUT = [
    ("gl-ES", "Fai 25 ºC en Vigo.", "Fai vinte e cinco graos centígrados en Vigo."),
    ("gl-ES", "O Dr. Pérez ten 3 fillos.", "O Doutor Pérez ten tres fillos."),
    ("gl-ES", "Custa 15€ e chega ás 14:30.", "Custa quince euros e chega ás 14:30."),
    ("gl-ES", "A Sra. López ten 42 anos.", "A Señora López ten corenta e dous anos."),
    ("it-IT", "Il Dott.ssa Rossi ha 3 gatti.", "Il Dottoressa Rossi ha tre gatti."),
    ("it-IT", "Costa 20 € al giorno.", "Costa venti euros al giorno."),
    ("it-IT", "Il Sig. Bianchi ha 45 anni.", "Il Signore Bianchi ha quarantacinque anni."),
    ("nl-NL", "Dhr. Jansen heeft 2 katten.", "De Heer Jansen heeft twee katten."),
    ("nl-NL", "Het kost 15 € per dag.", "Het kost vijftien euros per dag."),
    ("nl-NL", "Mevr. de Vries is 60 jaar.", "Mevrouw de Vries is zestig jaar."),
    ("ca-ES", "El Sr. Puig té 3 fills.", "El Senyor Puig té tres fills."),
    ("ca-ES", "Costa 12 € per persona.", "Costa dotze euros per persona."),
    ("ca-ES", "La Sra. Vila té 50 anys.", "La Senyora Vila té cinquanta anys."),
    ("fr-FR", "M. Dupont a 3 enfants.", "Monsieur Dupont a trois enfants."),
    ("fr-FR", "Cela coûte 25 € par jour.", "Cela coûte vingt-cinq euros par jour."),
    ("fr-FR", "Mme Martin a 40 ans.", "Madame Martin a quarante ans."),
]


@pytest.fixture(scope="module")
def plugin():
    return DialogNormalizerTransformer()


def transform(plugin, text, lang):
    context = {"session": Session("test", lang=lang).serialize()}
    out, returned = plugin.transform(text, context)
    assert returned is context
    return out


@pytest.mark.parametrize("lang,text", SERVED_ROWS)
def test_served_language_reads_through_text2spoken(plugin, lang, text):
    expected = text2spoken.normalize(text, lang)
    assert not re.search(r"\d", expected), f"text2spoken leaves a digit in {expected!r}"
    assert transform(plugin, text, lang) == expected


def test_every_served_language_has_five_sentences():
    per_language = {}
    for lang, texts in SERVED.items():
        code = lang.split("-")[0]
        per_language[code] = per_language.get(code, 0) + len(texts)
    assert per_language == {"en": 8, "pt": 7, "es": 5, "de": 5, "eu": 5, "ru": 5, "ar": 5}


@pytest.mark.parametrize("lang,text,expected", GOLD)
def test_hand_checked_readings(plugin, lang, text, expected):
    assert transform(plugin, text, lang) == expected


@pytest.mark.parametrize("lang,text,expected", UNSERVED_DEV_OUTPUT)
def test_unserved_language_keeps_dev_output(plugin, lang, text, expected):
    assert transform(plugin, text, lang) == expected


def test_full_session_tag_reaches_text2spoken(plugin):
    text = "We met on 12/03/2024."
    with mock.patch("text2spoken.normalize", wraps=text2spoken.normalize) as normalize:
        us = transform(plugin, text, "en-US")
        gb = transform(plugin, text, "en-GB")
    assert [c.args[1] for c in normalize.call_args_list] == ["en-US", "en-GB"]
    assert us == "We met on December third twenty twenty-four."
    assert gb == "We met on the twelfth of March twenty twenty-four."


def test_english_contractions_expand_before_text2spoken(plugin):
    text = "I'm sure it's 5 km and we can't walk 12 km."
    expected = text2spoken.normalize("I am sure it is 5 km and we can not walk 12 km.", "en-US")
    assert transform(plugin, text, "en-US") == expected
    assert expected == "I am sure it is five kilometers and we can not walk twelve kilometers."


def test_text2spoken_failure_leaves_dialog_unchanged(plugin):
    text = "O Dr. Silva pagou 2,50 € às 14:30."
    with mock.patch("text2spoken.normalize", side_effect=RuntimeError("broken reader")), \
            mock.patch("ovos_dialog_normalizer_plugin.LOG") as log:
        out = transform(plugin, text, "pt-PT")
    assert out == text
    log.warning.assert_called_once()
    message = log.warning.call_args.args[0]
    assert "broken reader" in message and "pt-PT" in message


def test_no_session_in_context_uses_default_session(plugin):
    lang = SessionManager.get().lang
    out, context = plugin.transform("I walked 5 km.")
    assert context == {}
    assert out == text2spoken.normalize("I walked 5 km.", lang)
