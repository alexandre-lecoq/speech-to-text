#!/usr/bin/env python3
"""
Speech to Text Core Library

This module provides the core functionality for converting MP3 audio files to text
with timestamps. It supports Chinese, French, and English languages.

This is a library module meant to be imported by CLI and GUI applications.
For command-line usage, use speech_to_text.py
For graphical interface, use speech_to_text_gui.py
"""


import sys
import os
import hashlib
from datetime import timedelta
import platform
import subprocess
import shutil

def preload_external_modules():
    """Preload external modules to avoid import issues later."""
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


def transcribe_audio(audio_file, language_code=None, progress_callback=None):
    """
    Transcribe audio file using Whisper model
    
    Args:
        audio_file: Path to the audio file
        language_code: Language code for the audio. If None, auto-detect.
        progress_callback: Optional callback(current, total, percentage) for progress updates
    
    Returns:
        Transcription result with segments
    """
    # Check for GPU availability
    import torch
    import whisper
    
    # Monkey-patch tqdm si callback fourni
    original_tqdm = None
    if progress_callback:
        import tqdm
        original_tqdm = tqdm.tqdm
        
        class CallbackTqdm(original_tqdm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._callback = progress_callback
                
            def update(self, n=1):
                super().update(n)
                # Appeler le callback avec la progression actuelle
                if self._callback and self.total:
                    percentage = (self.n / self.total) * 100
                    self._callback(self.n, self.total, percentage)
        
        # Remplacer temporairement tqdm
        tqdm.tqdm = CallbackTqdm
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        print(f"Loading Whisper model from ./models/base.pt ...")
        model = whisper.load_model("./models/base.pt", device=device)
        print(f"Transcribing audio file: {audio_file}")
        print(f"Language: {language_code if language_code else 'auto-detect'}")
        
        # Préparer le prompt initial avec le nom de fichier nettoyé
        import re
        filename_only = os.path.splitext(os.path.basename(audio_file))[0]
        # Nettoyer: remplacer underscores/tirets par espaces, supprimer caractères spéciaux
        cleaned_name = re.sub(r'[_-]+', ' ', filename_only)
        cleaned_name = re.sub(r'[^\w\s]', ' ', cleaned_name)
        cleaned_name = ' '.join(cleaned_name.split())  # Normaliser les espaces
        print(f"Initial prompt: {cleaned_name}")
        
        kwargs = {"verbose": False}  # False pour activer tqdm
        if language_code:
            kwargs["language"] = language_code
        if cleaned_name:
            kwargs["initial_prompt"] = cleaned_name
        
        result = model.transcribe(audio_file, **kwargs)
        return result
        
    finally:
        # Restaurer tqdm original
        if original_tqdm is not None:
            import tqdm
            tqdm.tqdm = original_tqdm


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
            from opencc import OpenCC
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
        import torch
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
        import whisper
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
    import whisper
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
    import whisper
    langs = whisper.tokenizer.LANGUAGES
    print("Supported Whisper languages:")
    for code, name in sorted(langs.items()):
        print(f"{code}: {name}")
    sys.exit(0)

