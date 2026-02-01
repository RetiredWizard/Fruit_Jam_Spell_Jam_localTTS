**This update to the Fruit Jam Spell Jam app is described in an [Adafruit Playground Note](https://adafruit-playground.com/u/retiredwizard/pages/your-own-tts-engine-for-the-fruit-jam-spell-jam-app)**

## Overview

The [Spell Jam](https://learn.adafruit.com/spell-jam-app-on-fruit-jam/overview) app on the [Fruit Jam](https://www.adafruit.com/product/6200) is a twist on a classic electronic toy. Check out the [Spell Jam learn guide](https://learn.adafruit.com/spell-jam-app-on-fruit-jam/overview) to lean all about it.

By default, Spell Jam uses the Amazon Polly Text-to-Speech (TTS) service to create audio from the entered text. While Amazon's service can be used for free during a trial period, it does require an AWS account.

If you'd prefer not to create an Amazon AWS account, you can instead run a local TTS server on your home network using open-source models like [KittenTTS](https://github.com/KittenML/KittenTTS), [Kani-TTS](https://github.com/nineninesix-ai/kani-tts) or [eSpeak](https://espeak.sourceforge.net/).

## Installing a Text-to-Speech Model

Two TTS AI models that have been tested with the Spell Jam local backend:

- [KittenTTS](https://github.com/KittenML/KittenTTS) - lightweight, will run on a Raspberry Pi 4/5  
- [Kani-TTS](https://github.com/nineninesix-ai/kani-tts)  - newer, but may require an Nvidia GPU.

Legacy software TTS application:

- [eSpeak](https://espeak.sourceforge.net/) - Initially released in 2006, a free and open-source compact, speech synthesizer.

**Before installing any of the TTS systems, create and/or activate a dedicated Python virtual environment.**
```
python3 -m venv venv
source venv/bin/activate
```
Then, you'll need to install three additional dependencies:  
```
pip install uvicorn scipy fastapi numpy pydantic
```

### eSpeak

To install the eSpeak software type the following commands:

```
sudo apt update
sudo apt install espeak
```

### KittenTTS

To install KittenTTS follow the instructions outlined in the [Speech Synthesis On Raspberry Pi with KittenTTS](https://learn.adafruit.com/speech-synthesis-on-raspberry-pi-with-kittentts/kittentts-setup) Learn Guide.

### Kani-TTS

To install Kani-TTS, follow the "setup" instructions from the Kani-TTS [GitHub project page](https://github.com/nineninesix-ai/kani-tts).

## Running the Local TTS Server

Once the TTS model has been installed, download the server script ([server.py](https://github.com/RetiredWizard/Fruit_Jam_Spell_Jam_localTTS/blob/main/server.py)) from this repository. Then activate your virtual environment and start the server.
```
source venv/bin/activate
python server.py
```
Your TTS server will now be running on port 8000.  

**NOTE: If your server is running a local firewall, you may need to add a firewall rule to allow TCP traffic to port 8000 from devices on your local network!!!**  

For *ufw* on linux:  
```
sudo ufw allow from 192.168.0.0/16 to any port 8000 proto tcp
```

## Configuring Spell Jam to use the local server

There are three steps to configuring Spell Jam to use a local TTS server:

1. **Copy the local TTS file**

Download [tts_local.py](https://github.com/RetiredWizard/Fruit_Jam_Spell_Jam_localTTS/blob/main/tts_local.py) from this repository and place it in:  

`CIRCUITPY/apps/Fruit_Jam_Spell_jam` on your Fruit Jam

2. **Edit the app code**

Open `CIRCUITPY/apps/Fruit_Jam_Spell_Jam/code.py`,  
comment out the AWS line and uncomment the local TTS line:  
```py
# from tts_aws import WordFetcherTTS
from tts_local import WordFetcherTTS
```
3. **Update the configuration file**

Edit `launcher.conf.json` on your Fruit Jam to include the TTS server endpoint:  
```json
{
    "spell_jam": {
        "tts_server_endpoint": "http://raspberrypi.local:8000",
    },
}
```
