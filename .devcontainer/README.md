# Codespaces Setup

This repository is configured to work with GitHub Codespaces.

## What's Included

- Python 3.11 environment
- All dependencies from `requirements.txt` installed automatically
- VS Code Python extensions pre-installed

## Note About PyAudio

PyAudio requires system-level PortAudio installation. In Codespaces, you may need to:

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
pip install pyaudio
```

Or the application will run without microphone features (with a warning message).

## Running the Application

Once the Codespace is ready:

```bash
python quran_memorization_tool.py
```

The GUI will open in the Codespace. You can use port forwarding to access it.

