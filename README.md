# speech-to-text

A simple, cross-platform tool to transcribe MP3 audio to text using OpenAI Whisper, with optional timestamps, offline model support, GPU acceleration when available, and a diagnostics mode. Available as both a command-line tool and a modern graphical user interface (GUI).

## Features

- Transcribes MP3 audio files to text
- **Modern GUI** with dark theme and multi-language support
- **GPU/CPU status indicator** showing real-time hardware acceleration status
- **Command-line interface** for automation and scripting
- Language handling:
  - Provide a Whisper language code (e.g., `en`, `fr`, `zh`), or
  - Omit it or use `auto` to auto-detect the language
- Optional timestamps per segment (`--timestamps`)
- Optional Chinese character conversion (`--chinese=simplified|traditional`)—only if detected language is Chinese; invalid values cause an error and exit
- Deterministic output format with file metadata and language info
- Uses a local Whisper model file (`./models/base.pt`) for offline use
- GPU acceleration with CUDA support; falls back to CPU automatically
- Diagnostics mode (`--diagnose`) to print environment info and exit
- List all supported Whisper languages (`--list-languages`)

## Requirements

- **Python 3.13+**
- **uv** package manager (recommended) or pip

## Installation

### Using uv (Recommended)

uv is a modern, fast Python package manager (10-100x faster than pip).

1) **Install uv**

```powershell
pip install uv
# Or: winget install astral-sh.uv
# Or: scoop install uv
```

2) **Clone and setup**

```bash
git clone https://github.com/alexandre-lecoq/speech-to-text.git
cd speech-to-text
uv sync  # Install all dependencies including PyTorch CUDA 13.0
```

3) **Download Whisper model**

```powershell
uv run speech_to_text.py --update-model
```
This tool expects a local model at `./models/base.pt`. Fetch it with:

This downloads the latest Whisper “base” model (requires internet) and saves it to `./models/base.pt` for offline use.

## Usage

### Graphical User Interface (GUI)

Launch the modern GUI:

```powershell
uv run speech_to_text.py --gui
# Or: python speech_to_text.py --gui
```

The GUI provides:
- **Modern dark theme**
- **Multi-language interface** (🇬🇧,🇫🇷,🇨🇳) with auto-detection
- **File browser** to select your MP3 audio file
- **Language selection** dropdown with auto-detect
- **Options** for timestamps and Chinese character conversion
- **Real-time progress** with elapsed time counter
- **GPU/CPU indicator** (🟢 GPU 😊 or 🔴 CPU 😐)
- **Result preview** displaying the transcription
- **One-click access** to open the generated file
- **Persistent settings** (remembers last directory)

### Command-Line Interface

Basic transcription (language auto-detected):

```powershell
uv run speech_to_text.py audio.mp3
# Or: python speech_to_text.py audio.mp3
```

Specify language explicitly (Whisper code):

```powershell
uv run speech_to_text.py audio.mp3 fr
# Examples: en (English), fr (French), zh (Chinese), auto (auto-detect)
```

Include timestamps per segment:

```powershell
uv run speech_to_text.py audio.mp3 --timestamps
uv run speech_to_text.py audio.mp3 en --timestamps
```

Convert Chinese output to Simplified or Traditional (only if detected language is Chinese):

```powershell
uv run speech_to_text.py audio.mp3 zh --chinese=simplified
uv run speech_to_text.py audio.mp3 zh --chinese=traditional
```

> **Note:** If you provide an invalid value for `--chinese` (anything other than `simplified` or `traditional`), the program will print an error and exit.

Update the local model file (requires internet):

```powershell
uv run speech_to_text.py --update-model
```

Print a diagnostics report and exit:

```powershell
uv run speech_to_text.py --diagnose
```

List all supported Whisper languages (code and name):

```powershell
uv run speech_to_text.py --list-languages
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

- Without `--timestamps` (default), content includes one segment per line for better readability.

## GPU Acceleration

- If a CUDA-enabled PyTorch is installed and your GPU/driver is compatible, the tool will automatically use `cuda`; otherwise it falls back to `cpu`.
- The selected device is printed at runtime and shown in the GUI status bar.
- To verify your environment, run the diagnostics:

```powershell
uv run speech_to_text.py --diagnose
```

This prints:
- Python/OS information
- `nvidia-smi` output (if available)
- `nvcc --version` (if available)
- PyTorch CUDA status and devices
- Whisper version
- Local model file status

## Notes

- Supported language codes include Whisper’s standard codes, e.g., `en`, `fr`, `zh`. Using `auto` or omitting the language enables auto-detection.
- The `--chinese` option only works if the detected language is Chinese (`zh`). If used with any other language, it is ignored with a warning. Invalid values for `--chinese` cause an error and exit.
- The `--list-languages` option prints all supported Whisper language codes and their names, then exits.
- The `--update-model` command requires internet connectivity. Normal transcription runs with the local `./models/base.pt` file.
- Windows is fully supported. The repository includes unit tests and sample audio files for validation.

## License

This project is open source and available under the MIT License.