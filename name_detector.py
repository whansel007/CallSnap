# Detect when a target name is spoken on a specific output device (e.g., Zoom).
# Requirements:
#   pip install vosk soundcard numpy
#   Download a Vosk model and point MODEL_PATH to it.
#
# Tip for "only Zoom audio":
#   Route Zoom's output to a dedicated device (e.g., VB-Audio Virtual Cable),
#   then set DEVICE_KEYWORD to that device's name.

import json
import time

import numpy as np
import soundcard as sc
from vosk import KaldiRecognizer, Model

# === Settings (edit these) ===
TARGET_NAME = "alex"
MODEL_PATH = "models/vosk-model-small-en-us-0.15"
DEVICE_KEYWORD = "CABLE"  # Substring of output device name, or None for default.
SAMPLE_RATE = 16000
BLOCK_SIZE = 4096
COOLDOWN_SECONDS = 5.0


def find_loopback_microphone(device_keyword):
    speakers = sc.all_speakers()
    if device_keyword:
        keyword = device_keyword.lower()
        for spk in speakers:
            if keyword in spk.name.lower():
                return sc.get_microphone(spk.name, include_loopback=True)
        available = ", ".join(s.name for s in speakers)
        raise RuntimeError(
            f"No speaker device matched '{device_keyword}'. Available: {available}"
        )
    default_speaker = sc.default_speaker()
    return sc.get_microphone(default_speaker.name, include_loopback=True)


def name_in_text(target: str, text: str) -> bool:
    target = target.strip().lower()
    text = text.strip().lower()
    if not target or not text:
        return False
    return target in text


def main():
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    mic = find_loopback_microphone(DEVICE_KEYWORD)
    last_hit = 0.0

    print(
        "Listening... press Ctrl+C to stop. "
        f"Device='{mic.name}', target='{TARGET_NAME}'."
    )

    with mic.recorder(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=BLOCK_SIZE,
    ) as recorder:
        while True:
            data = recorder.record(BLOCK_SIZE)
            data16 = (data * 32767).astype(np.int16)

            if recognizer.AcceptWaveform(data16.tobytes()):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
            else:
                partial = json.loads(recognizer.PartialResult())
                text = partial.get("partial", "")

            if name_in_text(TARGET_NAME, text):
                now = time.time()
                if now - last_hit >= COOLDOWN_SECONDS:
                    last_hit = now
                    print(f"Detected name '{TARGET_NAME}' in: {text}")


if __name__ == "__main__":
    main()
