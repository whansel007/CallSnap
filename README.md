# CallSnap
Catch your name in the noise and snap back to the call.

CallSnap listens to your meeting audio, detects when your name is spoken, and minimizes other windows so you can jump back in. It uses offline speech-to-text (Vosk) and a simple Tkinter UI to keep setup quick.

## Features
- Name detection from speaker output (loopback audio)
- Quick "Minimize All Apps" action from the main window
- Live partial transcription and a log of finalized speech
- Per-device selection for Zoom-only or app-specific routing
- Offline model support (no cloud dependency)

## Requirements
- Windows
- Python 3.10+ recommended
- Bundled Vosk model (default: `models/vosk-model-small-en-us-0.15/`)
- Audio loopback support via `soundcard`
- Virtual Audio Device (Voicemeeter Banana)

## Setup
1) Create and activate a virtual environment:
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
2) Install dependencies:
   - `pip install numpy soundcard vosk`
3) Use the bundled Vosk model under `models/` (or point the UI to a different model path).

## Usage
- Launch the main window:
  - `python main.py`
- Launch the name detector directly:
  - `python name_detector.py`
- Choose your audio device in the Settings panel:
  - For Zoom-only capture, route Zoom to its own output device and select that device here.

## Tips
- Match the sample rate to your device (common: 48000).
- If the default device keeps resetting, pick a specific output device instead.
