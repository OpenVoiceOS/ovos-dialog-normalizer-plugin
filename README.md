# OVOS Dialog Normalizer

a dialog transformer plugins for OpenVoiceOS

## Description

This plugin will prepare text for TTS, it will expand contractions and pronounce digits, ensuring the TTS engine pronounces words correctly

- "I'm" -> "I am"
- "Dr." -> "Doctor"
- "1" -> "one"

## Install

`pip install ovos-dialog-normalizer-plugin`


## Configuration

All you need to do is add a entry in your `mycroft.conf` under `"dialog_transformers"` to enable the plugin

```json
"dialog_transformers": {
    "ovos-dialog-normalizer-plugin": {}
}
```

## Contributing

Pull Requests welcome! 

- to support new languages translate the `.json` files in the `locale` folder
- to improve number handling please refer to [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser)
- to improve date/time handling please refer to [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)

## Credits

<img src="img.png" width="128"/>

> This plugin was funded by the Ministerio para la Transformación Digital y de la Función Pública and Plan de Recuperación, Transformación y Resiliencia - Funded by EU – NextGenerationEU within the framework of the project ILENIA with reference 2022/TL22/00215337
