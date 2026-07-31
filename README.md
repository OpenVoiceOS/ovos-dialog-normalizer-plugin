# OVOS Dialog Normalizer

A dialog transformer plugin for OpenVoiceOS (OVOS).

This plugin prepares text for a text-to-speech (TTS) engine. It expands contractions and converts digits to words, so the TTS engine pronounces the text correctly. It supports multiple languages.

Examples:

- "I'm" -> "I am"
- "Dr." -> "Doctor"
- "1" -> "one"

## Install

```bash
pip install ovos-dialog-normalizer-plugin
```

## Configuration

Add an entry under `"dialog_transformers"` in your `mycroft.conf` to enable the plugin.

```json
"dialog_transformers": {
    "ovos-dialog-normalizer-plugin": {}
}
```

## Related projects

- [OpenVoiceOS/ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser): number-to-word conversion used by this plugin. To improve number handling, contribute there.
- [OpenVoiceOS/ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager): defines the `DialogTransformer` base class this plugin implements.

## Contributing

Pull requests are welcome. Adding new expansions is straightforward. To improve number handling, see [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser).

## Credits

[TigreGotico](https://tigregotico.pt) developed this plugin for OpenVoiceOS under the [ILENIA](https://proyectoilenia.es) project.

<img src="img.png" width="128"/>

> This plugin was funded by the Ministerio para la Transformación Digital y de la Función Pública and Plan de Recuperación, Transformación y Resiliencia. It was funded by the EU, NextGenerationEU, within the framework of the project [ILENIA](https://proyectoilenia.es), reference 2022/TL22/00215337.
