#!/usr/bin/env python3
"""
Unit tests for speech_to_text.py

Tests the command-line argument parsing and validation logic.
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import timedelta


# Mock whisper module before importing speech_to_text
sys.modules['whisper'] = MagicMock()

# Now we can import the module
import speech_to_text


class TestFormatTimestamp(unittest.TestCase):
    """Test timestamp formatting function"""
    
    def test_zero_seconds(self):
        result = speech_to_text.format_timestamp(0)
        self.assertEqual(result, "00:00:00.000")
    
    def test_one_minute(self):
        result = speech_to_text.format_timestamp(60)
        self.assertEqual(result, "00:01:00.000")
    
    def test_one_hour(self):
        result = speech_to_text.format_timestamp(3600)
        self.assertEqual(result, "01:00:00.000")
    
    def test_complex_time(self):
        result = speech_to_text.format_timestamp(3723.456)
        self.assertEqual(result, "01:02:03.456")


class TestCommandLineValidation(unittest.TestCase):
    """Test command-line argument validation"""

    def test_no_arguments(self):
        """Exits with error when no arguments provided"""
        with patch.object(sys, 'argv', ['speech_to_text.py']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text.main()
            self.assertEqual(cm.exception.code, 1)

    def test_nonexistent_file(self):
        """Exits with error when MP3 file doesn't exist"""
        with patch.object(sys, 'argv', ['speech_to_text.py', 'nonexistent.mp3']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text.main()
            self.assertEqual(cm.exception.code, 1)

    def test_non_mp3_file(self):
        """Exits with error for non-MP3 files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test_audio.wav')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            with patch.object(sys, 'argv', ['speech_to_text.py', test_file]):
                with self.assertRaises(SystemExit) as cm:
                    speech_to_text.main()
                self.assertEqual(cm.exception.code, 1)


class TestLanguageArgument(unittest.TestCase):
    """Test language argument handling: <mp3_file> [language]"""

    def test_auto_detection_when_missing_language(self):
        """With only MP3 argument, language should be auto-detected (None passed)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test_audio.mp3')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            with patch('speech_to_text.transcribe_audio') as mock_transcribe, \
                 patch('speech_to_text.write_transcription') as mock_write:
                mock_transcribe.return_value = {'segments': []}

                with patch.object(sys, 'argv', ['speech_to_text.py', test_file]):
                    speech_to_text.main()

                # language_code should be None for auto-detection
                args, kwargs = mock_transcribe.call_args
                self.assertEqual(args[0], test_file)
                self.assertIsNone(args[1])

    def test_auto_detection_when_language_auto(self):
        """With 'auto' language arg, pass None to transcribe for detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test_audio.mp3')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            with patch('speech_to_text.transcribe_audio') as mock_transcribe, \
                 patch('speech_to_text.write_transcription') as mock_write:
                mock_transcribe.return_value = {'segments': []}

                with patch.object(sys, 'argv', ['speech_to_text.py', test_file, 'auto']):
                    speech_to_text.main()

                args, kwargs = mock_transcribe.call_args
                self.assertEqual(args[0], test_file)
                self.assertIsNone(args[1])

    def test_specific_language_code_passed(self):
        """When language provided (e.g., fr), pass it through to transcribe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test_audio.mp3')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            with patch('speech_to_text.transcribe_audio') as mock_transcribe, \
                 patch('speech_to_text.write_transcription') as mock_write:
                mock_transcribe.return_value = {'segments': []}

                with patch.object(sys, 'argv', ['speech_to_text.py', test_file, 'fr']):
                    speech_to_text.main()

                args, kwargs = mock_transcribe.call_args
                self.assertEqual(args[0], test_file)
                self.assertEqual(args[1], 'fr')




class TestTranscriptionOutput(unittest.TestCase):
    """Test output file format from write_transcription"""

    def test_write_transcription_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy mp3 file
            audio_path = os.path.join(tmpdir, 'sample.mp3')
            with open(audio_path, 'wb') as f:
                f.write(b'abc')

            # Prepare a mock result
            result = {
                'language': 'fr',
                'segments': [
                    {'start': 0.0, 'end': 1.23, 'text': 'Bonjour'},
                    {'start': 1.23, 'end': 2.34, 'text': 'le monde'}
                ]
            }

            # Output file
            out_path = os.path.join(tmpdir, 'out.txt')
            speech_to_text.write_transcription(result, out_path, audio_path)

            # Read and check output
            with open(out_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()

            # Check metadata
            self.assertTrue(lines[0].startswith('filename: sample.mp3'))
            self.assertTrue(lines[1].startswith('file_size: 3 bytes'))
            self.assertTrue(lines[2].startswith('sha1:'))
            # Blank line after metadata
            self.assertEqual(lines[3], '')
            # Language and segment count
            self.assertEqual(lines[4], 'language: fr')
            self.assertEqual(lines[5], 'segments: 2')
            # One blank line before segments
            self.assertEqual(lines[6], '')
            # Segment 1
            self.assertEqual(lines[7], '[00:00:00.000 --> 00:00:01.230]')
            self.assertEqual(lines[8], 'Bonjour')
            self.assertEqual(lines[9], '')
            # Segment 2
            self.assertEqual(lines[10], '[00:00:01.230 --> 00:00:02.340]')
            self.assertEqual(lines[11], 'le monde')
            self.assertEqual(lines[12], '')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
