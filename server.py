"""FastAPI server for Kani/Kitten TTS with streaming support"""

import sys
import io
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write as wav_write

try:
    from audio import LLMAudioPlayer, StreamingAudioWriter
    from generation import TTSGenerator
    from nemo.utils.nemo_logging import Logger
except ImportError:
    try:
        from kittentts import KittenTTS
    except ImportError:
        pass

kitten = 'KittenTTS' in globals()  # Check if KittenTTS is available
kani = 'TTSGenerator' in globals()
espeak = False

if len(sys.argv) > 1:
    if sys.argv[1].upper() == "KITTEN":
        kitten = True
        kani = False
        espeak = False
    elif sys.argv[1].upper() == "KANI":
        kani = True
        kitten = False
        espeak = False
    elif sys.argv[1].upper() == "ESPEAK":
        espeak = True
        kitten = False
        kani = False

if kitten:
    app = FastAPI(title="Kitten TTS API", version="1.0.1")
elif kani:
    nemo_logger = Logger()
    nemo_logger.remove_stream_handlers()
    app = FastAPI(title="Kani TTS API", version="1.0.1")
else:
    app = FastAPI(title="eSpeak TTS API", version="1.0.1")

# Add CORS middleware to allow client.html to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
generator = None
player = None


class TTSRequest(BaseModel):
    text: str
    temperature: Optional[float] = 0.6
    max_tokens: Optional[int] = 1200
    top_p: Optional[float] = 0.95
    chunk_size: Optional[int] = 25
    lookback_frames: Optional[int] = 15

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global generator, player, kitten, espeak, kani
    print("Initializing TTS models...")
    if kitten:
        kani = False
        print('kitten')
        generator = KittenTTS("KittenML/kitten-tts-nano-0.2")
    elif kani:
        print('kani')
        generator = TTSGenerator()
        player = LLMAudioPlayer(generator.tokenizer)
    else:
        command = ["espeak","--version"]
        try:
            result = subprocess.run(command)
            generator = True
            espeak = True
            print('espeak')
        except:
            espeak = False
            pass

    if generator is not None and (kitten or (player is not None) or espeak):
        print("TTS models initialized successfully!")


@app.get("/health")
async def health_check():
    """Check if server is ready"""
    return {
        "status": "healthy",
        "tts_initialized": generator is not None and (kitten or (player is not None) or espeak)
    }


@app.post("/tts")
async def generate_speech(request: TTSRequest):
    """Generate complete audio file (non-streaming)"""
    if not generator:
        raise HTTPException(status_code=503, detail="TTS models not initialized")
    if not kitten and not player and not espeak:
        raise HTTPException(status_code=503, detail="Audio player not initialized")

    try:
        # Create audio writer
        if kani:
            audio_writer = StreamingAudioWriter(
                player,
                output_file=None,  # We won't write to file
                sample_rate=22050,
                chunk_size=request.chunk_size,
                lookback_frames=request.lookback_frames
            )
            audio_writer.start()

            # Generate speech
            result = generator.generate(
                request.text,
                audio_writer,
                max_tokens=request.max_tokens
            )

            # Finalize and get audio
            audio_writer.finalize()

            if not audio_writer.audio_chunks:
                raise HTTPException(status_code=500, detail="No audio generated")

            # Concatenate all chunks
            full_audio = np.concatenate(audio_writer.audio_chunks)
        elif kitten:
            # For KittenTTS, generate directly

            # remove Kani voice prefix
            # Kitten appears to cut out early, so pad with "Done" at end
            full_audio = generator.generate(
                request.text[request.text.find(":")+2:]+"     Done", voice='expr-voice-2-f')

        elif espeak:
            # espeak sometimes misses the first character so pad start with spaces
            command = ["espeak", "--stdout", "    "+request.text[request.text.find(":")+2:]]
            result = subprocess.run(command, capture_output=True)
            full_audio = result.stdout

            # 2. Treat the bytes like a file and read the numerical data
            # io.BytesIO(wav_bytes) allows scipy to "read" the data without saving to disk
            samplerate, audio_int16 = wavfile.read(io.BytesIO(full_audio))

        if not espeak:
            # Convert float32 audio (-1.0 to 1.0) to 16-bit PCM
            audio_int16 = np.clip(full_audio, -1.0, 1.0)
            audio_int16 = (audio_int16 * 32767).astype(np.int16)

        # Write as 16-bit WAV
        wav_buffer = io.BytesIO()
        wav_write(wav_buffer, 24000, audio_int16)
        wav_buffer.seek(0)

        # Convert to WAV bytes
        #wav_buffer = io.BytesIO()
        #wav_write(wav_buffer, 22050, full_audio)
        #wav_buffer.seek(0)

        return Response(
            content=wav_buffer.read(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Kani TTS API",
        "version": "1.0.0",
        "endpoints": {
            "/tts": "POST - Generate complete audio",
            "/health": "GET - Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Kani TTS Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
