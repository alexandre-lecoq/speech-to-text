#!/usr/bin/env python3
"""
Speech to Text Command Line Tool

This tool converts MP3 audio files to text with timestamps.
It supports Chinese, French, and English languages.

Usage:
    python speech_to_text.py <mp3_file> [language] [--timestamps]
    python speech_to_text.py --update-model

Arguments:
    mp3_file: Path to the MP3 file to transcribe
    language: Optional Whisper language code or 'auto'.
              Codes: english=en, chinese=zh, french=fr, auto=auto
    --timestamps: Include timestamps in output (disabled by default)
    --update-model: Download the latest Whisper base model to ./models/base.pt (requires internet)

Example:
    python speech_to_text.py audio.mp3 en
    python speech_to_text.py audio.mp3 auto --timestamps
    python speech_to_text.py --update-model
"""

import sys
import os
import hashlib
import whisper
from datetime import timedelta


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
    print(f"Loading Whisper model from ./models/base.pt ...")
    model = whisper.load_model("./models/base.pt")
    
    print(f"Transcribing audio file: {audio_file}")
    print(f"Language: {language_code if language_code else 'auto-detect'}")
    
    kwargs = {"verbose": False}
    if language_code:
        kwargs["language"] = language_code
    
    result = model.transcribe(audio_file, **kwargs)
    
    # Print detected language if available
    # detected = result.get("language") if isinstance(result, dict) else None
    # if detected:
    #     print(f"Detected language: {detected}")
    
    return result


def write_transcription(result, output_file, audio_file, include_timestamps=False):
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
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])
                f.write(f"[{start_time} --> {end_time}]\n")
                f.write(f"{text}\n\n")
        else:
            # Use full text without timestamps (simpler and more efficient)
            f.write(result.get('text', '').strip())
            f.write('\n')


def update_model():
    """
    Download the latest Whisper base model and save to ./models/base.pt
    """
    print("Downloading latest Whisper base model (requires internet)...")
    import shutil
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

def main():
    """Main function to handle command line arguments and run transcription"""
    
    # Option: update model
    if len(sys.argv) == 2 and sys.argv[1] == "--update-model":
        update_model()
        return

    # Parse arguments
    args = sys.argv[1:]
    include_timestamps = False
    
    # Check for --timestamps flag
    if '--timestamps' in args:
        include_timestamps = True
        args.remove('--timestamps')
    
    # Check number of arguments: require at least the MP3 file, optional language
    if len(args) < 1 or len(args) > 2:
        print("Error: Invalid number of arguments")
        print("\nUsage: python speech_to_text.py <mp3_file> [language] [--timestamps]\n    python speech_to_text.py --update-model")
        print("\nArguments:")
        print("  mp3_file: Path to the MP3 file")
        print("  language: Optional Whisper language code or 'auto'")
        print("           Codes: english=en, chinese=zh, french=fr, auto=auto")
        print("  --timestamps: Include timestamps in output (disabled by default)")
        print("  --update-model: Download the latest Whisper base model to ./models/base.pt (requires internet)")
        print("\nExamples:")
        print("  python speech_to_text.py audio.mp3 en")
        print("  python speech_to_text.py audio.mp3 auto --timestamps")
        print("  python speech_to_text.py --update-model")
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
        write_transcription(result, output_file, audio_file, include_timestamps)

        print(f"\nTranscription completed successfully!")
        print(f"Output written to: {output_file}")

    except Exception as e:
        print(f"\nError during transcription: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
