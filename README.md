# Quran Memorization Practice Tool

A Python GUI application for practicing Quran recitation with real-time speech recognition and feedback.

## Features

- Voice-activated surah selection
- Real-time speech recognition and transcription
- Automatic comparison with correct text
- Visual and audio feedback
- Automatic progression through all ayahs
- Similarity scoring (80% threshold)

## Requirements

- Python 3.7+
- Microphone access
- Internet connection (for Google Speech Recognition API)

## Installation

### Option 1: GitHub Codespaces (Recommended)

1. Click the green "Code" button on GitHub
2. Select "Codespaces" tab
3. Click "Create codespace on main"
4. Wait for the environment to set up (dependencies install automatically)
5. Run: `python quran_memorization_tool.py`

**Note:** For microphone support in Codespaces, run:
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Option 2: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/ahmadafzalt/Quran-memorisation-tool.git
cd Quran-memorisation-tool
```

2. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install PyAudio (for microphone support):
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# Windows
pip install pyaudio
```

## Usage

1. Ensure `quran.csv` exists with columns: `surah`, `ayah`, `text`

2. Run the application:
```bash
python quran_memorization_tool.py
```

3. Click "Start Listening for Surah" and say the surah name

4. Recite each ayah as it appears

5. Get real-time feedback on your recitation

## CSV File Format

```csv
surah,ayah,text
1,1,بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
1,2,الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
```

## License

MIT License
