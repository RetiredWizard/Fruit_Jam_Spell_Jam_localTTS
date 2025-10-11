KittenTTS/Kani-TTS engine for Fruit Jam Spell Jam. Install and run the kani-tts or KittenTTS AI server on your
local network following the instructions at: https://github.com/nineninesix-ai/kani-tts or 
https://learn.adafruit.com/speech-synthesis-on-raspberry-pi-with-kittentts/kittentts-setup

Then configure the server endpoint in launcher.conf.json, e.g.:
```json
  "spell_jam": {
      "tts_server_endpoint": "http://myserver.local:8000"
  }
```
