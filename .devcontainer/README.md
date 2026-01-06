# Codespaces Setup

This repository is configured to work with GitHub Codespaces.

## What's Included

- Python 3.11 environment
- All dependencies from `requirements.txt` installed automatically
- VS Code Python extensions pre-installed

## Important Notes

### GUI Application Limitation

**This application uses Tkinter for the GUI, which requires a display server.** Codespaces runs in a browser and doesn't have a native display, so the GUI won't work directly.

**Options:**
1. **Use X11 forwarding** (if supported by your Codespaces setup)
2. **Run locally** for full functionality (recommended)
3. **Convert to web-based UI** (future enhancement)

### PyAudio Installation

PyAudio requires system-level PortAudio installation. In Codespaces:

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
pip install pyaudio
```

Or the application will run without microphone features (with a warning message).

## Running the Application

**For full functionality, run locally:**
```bash
python quran_memorization_tool.py
```

**In Codespaces (for testing code only):**
The GUI won't display, but you can test the code logic and imports.

