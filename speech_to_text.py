#!/usr/bin/env python3
"""
Speech to Text Command Line Tool

This tool converts MP3 audio files to text with timestamps.
It supports Chinese, French, and English languages.

Usage:
    python speech_to_text.py <language> <mp3_file>

Arguments:
    language: The language spoken in the audio (chinese, french, or english)
    mp3_file: Path to the MP3 file to transcribe

Example:
    python speech_to_text.py english audio.mp3
"""

import sys
import os
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


def transcribe_audio(audio_file, language_code):
    """
    Transcribe audio file using Whisper model
    
    Args:
        audio_file: Path to the audio file
        language_code: Language code for the audio
    
    Returns:
        Transcription result with segments
    """
    print(f"Loading Whisper model...")
    model = whisper.load_model("base")
    
    print(f"Transcribing audio file: {audio_file}")
    print(f"Language: {language_code}")
    
    result = model.transcribe(audio_file, language=language_code, verbose=False)
    
    return result


def write_transcription(result, output_file):
    """
    Write transcription result to a text file with timestamps
    
    Args:
        result: Whisper transcription result
        output_file: Path to the output text file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Speech to Text Transcription\n")
        f.write("=" * 50 + "\n\n")
        
        for segment in result['segments']:
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"[{start_time} --> {end_time}]\n")
            f.write(f"{text}\n\n")
        
        f.write("=" * 50 + "\n")
        f.write("End of transcription\n")


def main():
    """Main function to handle command line arguments and run transcription"""
    
    # Check if correct number of arguments provided
    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments")
        print("\nUsage: python speech_to_text.py <language> <mp3_file>")
        print("\nArguments:")
        print("  language: chinese, french, or english")
        print("  mp3_file: Path to the MP3 file")
        print("\nExample:")
        print("  python speech_to_text.py english audio.mp3")
        sys.exit(1)
    
    language_input = sys.argv[1].lower()
    audio_file = sys.argv[2]
    
    # Map language names to Whisper language codes
    language_map = {
        'chinese': 'zh',
        'french': 'fr',
        'english': 'en'
    }
    
    # Validate language
    if language_input not in language_map:
        print(f"Error: Unsupported language '{language_input}'")
        print("Supported languages: chinese, french, english")
        sys.exit(1)
    
    language_code = language_map[language_input]
    
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
        write_transcription(result, output_file)
        
        print(f"\nTranscription completed successfully!")
        print(f"Output written to: {output_file}")
        
    except Exception as e:
        print(f"\nError during transcription: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
