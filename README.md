KittenTTS/Kani-TTS engine for the [Fruit Jam Spell Jam](https://learn.adafruit.com/spell-jam-app-on-fruit-jam/overview) app  

Install and run the kani-tts or KittenTTS AI server on your
local network following the instructions at: https://github.com/nineninesix-ai/kani-tts or 
https://learn.adafruit.com/speech-synthesis-on-raspberry-pi-with-kittentts/kittentts-setup

for KittenTTS you will need to install three additional pip packages into the KittenTTS virtual environment
before running the `server.py` script:
```
source venv/bin/activate
pip install uvicorn scipy fastapi
```

Then configure the server endpoint in launcher.conf.json on the Fruit Jam, e.g.:
```json
  "spell_jam": {
      "tts_server_endpoint": "http://myserver.local:8000"
  }
```
