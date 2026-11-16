import text2spoken
from ovos_bus_client.session import Session, SessionManager
from ovos_plugin_manager.templates.transformers import DialogTransformer
from ovos_utils.log import LOG


class DialogNormalizerTransformer(DialogTransformer):
    """OVOS Dialog Transformer plugin that rewrites written forms into spoken words.

    text2spoken reads numbers, dates, times, money, units, symbols and
    abbreviations in the language of the session.
    """

    def __init__(self, name="ovos-dialog-normalizer-plugin", priority=5, config=None):
        super().__init__(name=name, priority=priority, config=config)

    def transform(self, dialog: str, context: dict | None = None) -> tuple[str, dict]:
        """Read the written forms of the dialog in the language of the session.

        On a text2spoken failure the dialog stays as it was given.
        """
        context = context or {}
        sess = Session.deserialize(context["session"]) if "session" in context else SessionManager.get()
        try:
            spoken = text2spoken.normalize(dialog, sess.lang)
        except Exception as e:
            LOG.warning(f"text2spoken failed to read dialog '{dialog}' ({sess.lang}): {e}")
            return dialog, context
        LOG.debug(f"normalized dialog: '{dialog}' -> '{spoken}'")
        return spoken, context


if __name__ == "__main__":
    # 'I'm Doctor Prof. twelve thousand three hundred forty-five euros'
    print(DialogNormalizerTransformer().transform("I'm Dr. Prof. 12345 €"))
