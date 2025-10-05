# speech-to-text

A simple, cross-platform command-line tool to transcribe MP3 audio to text using OpenAI Whisper, with optional timestamps, offline model support, GPU acceleration when available, and a diagnostics mode.

## Features

- Transcribes MP3 audio files to text
- Language handling:
  - Provide a Whisper language code (e.g., `en`, `fr`, `zh`), or
  - Omit it or use `auto` to auto-detect the language
  - Optional timestamps per segment (`--timestamps`)
  - Optional Chinese character conversion (`--chinese=simplified|traditional`)—only if detected language is Chinese; invalid values cause an error and exit
  - Deterministic output format with file metadata and language info
  - Uses a local Whisper model file (`./models/base.pt`) for offline use
  - GPU acceleration if a CUDA-enabled PyTorch is available; falls back to CPU
  - Diagnostics mode (`--diagnose`) to print environment info and exit
  - List all supported Whisper languages (`--list-languages`)

## Requirements

- Python 3.8+
- Dependencies from `requirements.txt` (installs Whisper)
  - PyTorch is required by Whisper and will be installed (CPU by default). For GPU acceleration, install a CUDA-enabled PyTorch build separately following the instructions on pytorch.org.

## Installation

1) Clone this repository

```bash
git clone https://github.com/alexandre-lecoq/speech-to-text.git
cd speech-to-text
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Obtain the Whisper base model file (one-time)

This tool expects a local model at `./models/base.pt`. Fetch it with:

```bash
python speech_to_text.py --update-model
```

This downloads the latest Whisper “base” model (requires internet) and saves it to `./models/base.pt` for offline use.

## Usage

Basic transcription (language auto-detected):

```bash
python speech_to_text.py <mp3_file>
```

Specify language explicitly (Whisper code):

```bash
python speech_to_text.py <mp3_file> <language>
# Examples: en (English), fr (French), zh (Chinese), auto (auto-detect)
```

Include timestamps per segment:

```bash
python speech_to_text.py <mp3_file> [language] --timestamps
```

Convert Chinese output to Simplified or Traditional (only if detected language is Chinese):

```bash
python speech_to_text.py <mp3_file> [language] --chinese=simplified
python speech_to_text.py <mp3_file> [language] --chinese=traditional
```

> **Note:** If you provide an invalid value for `--chinese` (anything other than `simplified` or `traditional`), the program will print an error and exit.

Update the local model file (requires internet):

```bash
python speech_to_text.py --update-model
```

Print a diagnostics report and exit:

```bash
python speech_to_text.py --diagnose
```

List all supported Whisper languages (code and name):

```bash
python speech_to_text.py --list-languages
```

## Output

The tool writes a text file alongside your MP3, named `<basename>_transcription.txt`. The format is:

```
filename: <file name>
file_size: <size in bytes> bytes
sha1: <sha1 of input file>

language: <whisper_language_code>
segments: <number_of_segments>

<content>
```

- When `--timestamps` is used, content is a list of segments:

```
[HH:MM:SS.mmm --> HH:MM:SS.mmm]
<segment text>

[...]
```

- Without `--timestamps` (default), content is the full transcription text from Whisper (`result['text']`). Whisper may include newlines depending on the audio.

## GPU acceleration (optional)

- If a CUDA-enabled PyTorch is installed and your GPU/driver is compatible, the tool will automatically use `cuda`; otherwise it will fall back to `cpu`. The selected device is printed at runtime.
- To verify your environment, run the diagnostics:

```bash
python speech_to_text.py --diagnose
```

This prints Python/OS info, `nvidia-smi` (if available), `nvcc --version` (if available), PyTorch CUDA status and devices, Whisper version, and whether the local model file is present.

## Notes

- Supported language codes include Whisper’s standard codes, e.g., `en`, `fr`, `zh`. Using `auto` or omitting the language enables auto-detection.
- The `--chinese` option only works if the detected language is Chinese (`zh`). If used with any other language, it is ignored with a warning. Invalid values for `--chinese` cause an error and exit.
- The `--list-languages` option prints all supported Whisper language codes and their names, then exits.
- The `--update-model` command requires internet connectivity. Normal transcription runs with the local `./models/base.pt` file.
- Windows is supported. The repository includes unit tests and a small French audio sample for end-to-end validation.

## License

This project is open source and available under the MIT License.