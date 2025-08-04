from typing import Optional, Tuple

from ovos_bus_client.session import Session, SessionManager
from ovos_plugin_manager.templates.transformers import DialogTransformer
from ovos_utils.log import LOG

from ovos_dialog_normalizer_plugin.util import normalize


class DialogNormalizerTransformer(DialogTransformer):
    """OVOS Dialog Transformer plugin to normalize text for TTS engines:
    - Expands digits into words
    - Handles common abbreviations
    - Supports multiple languages
    """

    def __init__(self, name="ovos-dialog-normalizer-plugin", priority=5, config=None):
        super().__init__(name=name, priority=priority, config=config)

    def transform(self, dialog: str, context: Optional[dict] = None) -> Tuple[str, dict]:
        """Normalize dialog text."""
        context = context or {}
        sess = Session.deserialize(context["session"]) if "session" in context else SessionManager.get()
        original = dialog
        try:
            dialog = normalize(original, sess.lang)
            LOG.debug(f"normalized dialog: '{original}' -> '{dialog}'")
        except Exception as e:
            LOG.error(f"Failed to normalize dialog: {e}")

        return dialog, context


if __name__ == "__main__":
    # Silly example for demonstration purposes
    # 'I am Doctor Professor twelve thousand three hundred forty-five'
    print(DialogNormalizerTransformer().transform("I'm Dr. Prof. 12345 €"))
