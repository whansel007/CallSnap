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
- Windows OS
- Python 3.10+ recommended
- Bundled Vosk model (default: `models/vosk-model-small-en-us-0.15/`)
- Audio loopback support via `soundcard`
- Python dependencies: `numpy<2.0`, `SoundCard==0.4.5`, `vosk==0.3.45`, `pywin32`, `keyboard==0.13.5`
- Virtual Audio Device ([Voicemeeter Banana](https://vb-audio.com/Voicemeeter/banana.htm))
  ⚠ IMPORTANT TO BE ABLE TO ISOLATE THE ZOOM AUDIO AND STILL HEAR ALL AUDIOS ⚠
  Watch this [video](https://www.youtube.com/watch?v=XD9sWOjITYU) to understand Voicemeeter Banana

## Setup
0) Install Voicemeeter Banana and Setup Default
  - Open `Change System Sounds` and select `Playback` and click on `Voicemeeter Input` then `Set as Default Device`
  - Open VoiceMeeter and select A1 Hardware to the hardware device you use to hear
  - Open Zoom and select `Voicemeeter AUX Input` as Speaker
1) Create and activate a virtual environment:
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
2) Install dependencies:
   - `pip install -r requirements.txt`
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
