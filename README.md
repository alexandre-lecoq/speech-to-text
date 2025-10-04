# speech-to-text

A simple command-line tool for converting MP3 audio files to text with timestamps.

## Features

- Converts MP3 audio files to text transcriptions
- Supports multiple languages: Chinese, French, and English
- Outputs text with timestamps for each segment
- Uses OpenAI's Whisper model for accurate transcription

## Installation

1. Clone this repository:
```bash
git clone https://github.com/alexandre-lecoq/speech-to-text.git
cd speech-to-text
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Note: The first time you run the tool, it will download the Whisper model (approximately 140 MB).

## Usage

```bash
python speech_to_text.py <language> <mp3_file>
```

### Arguments

- `language`: The language spoken in the audio file
  - Supported values: `chinese`, `french`, `english`
- `mp3_file`: Path to the MP3 audio file you want to transcribe

### Examples

Transcribe an English audio file:
```bash
python speech_to_text.py english audio.mp3
```

Transcribe a French audio file:
```bash
python speech_to_text.py french presentation.mp3
```

Transcribe a Chinese audio file:
```bash
python speech_to_text.py chinese lecture.mp3
```

## Output

The tool generates a text file with the same name as the input file, with `_transcription.txt` appended. For example:
- Input: `audio.mp3`
- Output: `audio_transcription.txt`

The output file contains:
- Timestamps for each segment in format `[HH:MM:SS.mmm --> HH:MM:SS.mmm]`
- The transcribed text for each segment

Example output:
```
Speech to Text Transcription
==================================================

[00:00:00.000 --> 00:00:03.500]
Hello, welcome to this presentation.

[00:00:03.500 --> 00:00:07.200]
Today we will discuss speech recognition technology.

==================================================
End of transcription
```

## Requirements

- Python 3.7 or higher
- openai-whisper package (installed via requirements.txt)

## License

This project is open source and available under the MIT License.