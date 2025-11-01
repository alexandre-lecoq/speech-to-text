#!/usr/bin/env python3
"""
Speech to Text Command Line Interface

This module provides the command-line interface for the speech-to-text tool.
It handles argument parsing and user interaction for CLI usage.

Usage:
    python speech_to_text_cli.py <mp3_file> [language] [--timestamps] [--chinese=simplified|traditional]
    python speech_to_text_cli.py --update-model
    python speech_to_text_cli.py --diagnose
    python speech_to_text_cli.py --list-languages

Arguments:
    mp3_file: Path to the MP3 file to transcribe
    language: Optional Whisper language code or 'auto'.
              Codes: english=en, chinese=zh, french=fr, auto=auto

    --timestamps: Include timestamps in output (disabled by default)
    --chinese=simplified|traditional: Convert Chinese output to Simplified or Traditional (only if language is zh)
    --update-model: Download the latest Whisper base model to ./models/base.pt (requires internet)
    --diagnose: Print GPU/CUDA/PyTorch/Whisper/model diagnostics and exit
    --list-languages: Print all supported Whisper language codes and names

Example:
    python speech_to_text_cli.py audio.mp3 en
    python speech_to_text_cli.py audio.mp3 auto --timestamps
    python speech_to_text_cli.py --update-model
    python speech_to_text_cli.py --diagnose
"""

import sys
import os
from speech_to_text_core import transcribe_audio, write_transcription, diagnose, update_model, list_languages


def main():
    """Main function to handle command line arguments and run transcription"""
    
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
        print("\nUsage: python speech_to_text_cli.py <mp3_file> [language] [--timestamps] [--chinese=simplified|traditional]")
        print("       python speech_to_text_cli.py --update-model")
        print("       python speech_to_text_cli.py --diagnose")
        print("       python speech_to_text_cli.py --list-languages")
        print("\nArguments:")
        print("  mp3_file: Path to the MP3 file")
        print("  language: Optional Whisper language code or 'auto'")
        print("           Codes: english=en, chinese=zh, french=fr, auto=auto")
        print("  --timestamps: Include timestamps in output (disabled by default)")
        print("  --chinese=simplified|traditional: Convert Chinese output to Simplified or Traditional (only if language is zh)")
        print("  --update-model: Download the latest Whisper base model to ./models/base.pt (requires internet)")
        print("  --diagnose: Print GPU/CUDA/PyTorch/Whisper/model diagnostics and exit")
        print("  --list-languages: Print all supported Whisper language codes and names")
        print("\nExamples:")
        print("  python speech_to_text_cli.py audio.mp3 zh --chinese=simplified")
        print("  python speech_to_text_cli.py audio.mp3 zh --chinese=traditional --timestamps")
        print("  python speech_to_text_cli.py audio.mp3 en")
        print("  python speech_to_text_cli.py audio.mp3 auto --timestamps")
        print("  python speech_to_text_cli.py --update-model")
        print("  python speech_to_text_cli.py --list-languages")
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
