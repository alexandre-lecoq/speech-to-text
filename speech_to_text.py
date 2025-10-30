#!/usr/bin/env python3
"""
Speech to Text Command Line Tool

This tool converts MP3 audio files to text with timestamps.
It supports Chinese, French, and English languages.


Usage:
    python speech_to_text.py <mp3_file> [language] [--timestamps] [--chinese=simplified|traditional]
    python speech_to_text.py --gui
    python speech_to_text.py --guipyside6
    python speech_to_text.py --update-model
    python speech_to_text.py --diagnose
    python speech_to_text.py --list-languages

Arguments:
    mp3_file: Path to the MP3 file to transcribe
    language: Optional Whisper language code or 'auto'.
              Codes: english=en, chinese=zh, french=fr, auto=auto

    --gui: Launch the graphical user interface (CustomTkinter)
    --guipyside6: Launch the graphical user interface (PySide6)
    --timestamps: Include timestamps in output (disabled by default)
    --chinese=simplified|traditional: Convert Chinese output to Simplified or Traditional (only if language is zh)
    --update-model: Download the latest Whisper base model to ./models/base.pt (requires internet)
    --diagnose: Print GPU/CUDA/PyTorch/Whisper/model diagnostics and exit
    --list-languages: Print all supported Whisper language codes and names

Example:
    python speech_to_text.py --gui
    python speech_to_text.py --guipyside6
    python speech_to_text.py audio.mp3 en
    python speech_to_text.py audio.mp3 auto --timestamps
    python speech_to_text.py --update-model
    python speech_to_text.py --diagnose
"""


import sys
import os
import hashlib
from datetime import timedelta
import platform
import subprocess
import shutil
import torch
import whisper
from opencc import OpenCC


def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS.mmm format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def transcribe_audio(audio_file, language_code=None):
    """
    Transcribe audio file using Whisper model
    
    Args:
        audio_file: Path to the audio file
    language_code: Language code for the audio. If None, auto-detect.
    
    Returns:
        Transcription result with segments
    """
    # Check for GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print(f"Loading Whisper model from ./models/base.pt ...")
    model = whisper.load_model("./models/base.pt", device=device)
    print(f"Transcribing audio file: {audio_file}")
    print(f"Language: {language_code if language_code else 'auto-detect'}")
    kwargs = {"verbose": False}
    if language_code:
        kwargs["language"] = language_code
    result = model.transcribe(audio_file, **kwargs)
    return result


def write_transcription(result, output_file, audio_file, include_timestamps=False, chinese_conversion=None):
    """
    Write transcription result to a text file
    
    Args:
        result: Whisper transcription result
        output_file: Path to the output text file
        audio_file: Path to the original input audio file (for metadata)
        include_timestamps: Whether to include timestamps in output (default: False)
    """
    # Compute file metadata
    filename = os.path.basename(audio_file)
    try:
        file_size = os.path.getsize(audio_file)
    except OSError:
        file_size = 0

    # SHA1 of file (streaming)
    sha1 = hashlib.sha1()
    try:
        with open(audio_file, 'rb') as af:
            for chunk in iter(lambda: af.read(8192), b''):
                sha1.update(chunk)
        file_sha1 = sha1.hexdigest()
    except OSError:
        file_sha1 = ""

    # Chinese conversion setup
    cc = None
    detected_lang = result.get('language')
    if chinese_conversion:
        if detected_lang == 'zh':
            print(f"Converting Chinese output to: {chinese_conversion}")
            cc = OpenCC('t2s' if chinese_conversion == 'simplified' else 's2t')
        else:
            print("Warning: --chinese option ignored (language is not Chinese)")

    with open(output_file, 'w', encoding='utf-8') as f:
        # File metadata
        f.write(f"filename: {filename}\n")
        f.write(f"file_size: {file_size} bytes\n")
        f.write(f"sha1: {file_sha1}\n\n")

        # Language and segment count
        f.write(f"language: {result.get('language')}\n")
        f.write(f"segments: {len(result.get('segments', []))}\n\n")

        # Content
        if include_timestamps:
            # Use segments with timestamps
            for segment in result['segments']:
                text = segment['text'].strip()
                if cc:
                    text = cc.convert(text)
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])
                f.write(f"[{start_time} --> {end_time}]\n")
                f.write(f"{text}\n\n")
        else:
            # No timestamps: write one segment per line (improves readability)
            for segment in result.get('segments', []):
                text = str(segment.get('text', '')).strip()
                if cc:
                    text = cc.convert(text)
                if text:
                    f.write(text + "\n")


def diagnose():
    """Print a diagnostics report about GPU/driver/CUDA/PyTorch/Whisper and exit."""
    print("=== Speech-to-Text Diagnostics ===")
    # Python and OS
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")

    # NVIDIA driver via nvidia-smi
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("\n[nvidia-smi]\n" + result.stdout.strip())
        else:
            print("\n[nvidia-smi] Not available or returned error")
    except Exception as e:
        print(f"\n[nvidia-smi] Not available: {e}")

    # nvcc version
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("\n[nvcc --version]\n" + result.stdout.strip())
        else:
            print("\n[nvcc] Not available or returned error")
    except Exception as e:
        print(f"\n[nvcc] Not available: {e}")

    try:
        print("\n[PyTorch]")
        print(f"  Version: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        print(f"  CUDA runtime: {torch.version.cuda}")
        print(f"  cuDNN enabled: {torch.backends.cudnn.enabled}")
        if torch.cuda.is_available():
            print(f"  Device count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                name = torch.cuda.get_device_name(i)
                cap = torch.cuda.get_device_capability(i)
                print(f"  GPU {i}: {name} (SM {cap[0]}.{cap[1]})")
    except Exception as e:
        print(f"\n[PyTorch] Not available: {e}")

    # Whisper
    try:
        print("\n[Whisper]")
        print(f"  Version: {whisper.__version__ if hasattr(whisper, '__version__') else 'unknown'}")
    except Exception as e:
        print(f"\n[Whisper] Not available: {e}")

    # Model file
    model_path = os.path.abspath(os.path.join(".", "models", "base.pt"))
    print("\n[Model file]")
    if os.path.exists(model_path):
        try:
            size = os.path.getsize(model_path)
            print(f"  Found: {model_path}")
            print(f"  Size: {size} bytes")
        except Exception as e:
            print(f"  Found but could not stat: {model_path} ({e})")
    else:
        print(f"  Not found: {model_path}")

    # Exit after diagnostics
    sys.exit(0)


def update_model():
    """
    Download the latest Whisper base model and save to ./models/base.pt
    """
    print("Downloading latest Whisper base model (requires internet)...")
    model = whisper.load_model("base")
    # Find the cached model file
    cache_dir = os.path.expanduser(os.getenv("WHISPER_CACHE", "~/.cache/whisper"))
    cache_path = os.path.join(cache_dir, "base.pt")
    if not os.path.exists(cache_path):
        print(f"Error: Could not find downloaded model at {cache_path}")
        sys.exit(1)
    # Ensure models directory exists
    os.makedirs("./models", exist_ok=True)
    shutil.copy2(cache_path, "./models/base.pt")
    print("Model updated: ./models/base.pt")

def list_languages():
    """Print all supported Whisper language codes and names, then exit."""
    langs = whisper.tokenizer.LANGUAGES
    print("Supported Whisper languages:")
    for code, name in sorted(langs.items()):
        print(f"{code}: {name}")
    sys.exit(0)

def main():
    """Main function to handle command line arguments and run transcription"""
    
    # Option: GUI (CustomTkinter)
    if len(sys.argv) == 2 and sys.argv[1] == "--gui":
        from gui import launch_gui
        launch_gui()
        return
    # Option: GUI (PySide6)
    if len(sys.argv) == 2 and sys.argv[1] == "--guipyside6":
        from gui_pyside6 import launch_gui
        launch_gui()
        return
    # Option: update model
    if len(sys.argv) == 2 and sys.argv[1] == "--update-model":
        update_model()
        return
    # Option: diagnose
    if len(sys.argv) == 2 and sys.argv[1] == "--diagnose":
        diagnose()
        return
    # Option: list languages
    if len(sys.argv) == 2 and sys.argv[1] == "--list-languages":
        list_languages()
        return

    # Parse arguments
    args = sys.argv[1:]
    include_timestamps = False
    chinese_conversion = None
    
    # Check for --timestamps flag
    if '--timestamps' in args:
        include_timestamps = True
        args.remove('--timestamps')
    # Check for --chinese flag
    for arg in args[:]:
        if arg.startswith('--chinese='):
            val = arg.split('=', 1)[1].strip().lower()
            if val in ('simplified', 'traditional'):
                chinese_conversion = val
            else:
                print("Error: --chinese must be 'simplified' or 'traditional'")
                sys.exit(1)
            args.remove(arg)
    
    # Check number of arguments: require at least the MP3 file, optional language
    if len(args) < 1 or len(args) > 2:
        print("Error: Invalid number of arguments")
        print("\nUsage: python speech_to_text.py <mp3_file> [language] [--timestamps] [--chinese=simplified|traditional]\n    python speech_to_text.py --gui\n    python speech_to_text.py --guipyside6\n    python speech_to_text.py --update-model\n    python speech_to_text.py --diagnose\n    python speech_to_text.py --list-languages")
        print("\nArguments:")
        print("  mp3_file: Path to the MP3 file")
        print("  language: Optional Whisper language code or 'auto'")
        print("           Codes: english=en, chinese=zh, french=fr, auto=auto")
        print("  --timestamps: Include timestamps in output (disabled by default)")
        print("  --chinese=simplified|traditional: Convert Chinese output to Simplified or Traditional (only if language is zh)")
        print("  --gui: Launch the graphical user interface (CustomTkinter)")
        print("  --guipyside6: Launch the graphical user interface (PySide6)")
        print("  --update-model: Download the latest Whisper base model to ./models/base.pt (requires internet)")
        print("  --diagnose: Print GPU/CUDA/PyTorch/Whisper/model diagnostics and exit")
        print("  --list-languages: Print all supported Whisper language codes and names")
        print("\nExamples:")
        print("  python speech_to_text.py audio.mp3 zh --chinese=simplified")
        print("  python speech_to_text.py audio.mp3 zh --chinese=traditional --timestamps")
        print("  python speech_to_text.py audio.mp3 en")
        print("  python speech_to_text.py audio.mp3 auto --timestamps")
        print("  python speech_to_text.py --gui")
        print("  python speech_to_text.py --guipyside6")
        print("  python speech_to_text.py --update-model")
        print("  python speech_to_text.py --list-languages")
        sys.exit(1)

    audio_file = args[0]
    language_input = args[1].lower() if len(args) == 2 else 'auto'

    # Determine language code: None for auto-detect, else pass through
    language_code = None if language_input == 'auto' else language_input

    # Validate audio file exists
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found")
        sys.exit(1)

    # Validate file extension
    if not audio_file.lower().endswith('.mp3'):
        print(f"Error: File '{audio_file}' is not an MP3 file")
        print("Only MP3 files are supported")
        sys.exit(1)

    # Generate output file name
    base_name = os.path.splitext(audio_file)[0]
    output_file = f"{base_name}_transcription.txt"

    try:
        # Transcribe audio
        result = transcribe_audio(audio_file, language_code)
        # Write transcription to file
        write_transcription(result, output_file, audio_file, include_timestamps, chinese_conversion)

        print(f"\nTranscription completed successfully!")
        print(f"Output written to: {output_file}")
    except Exception as e:
        print(f"\nError during transcription: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
