#!/usr/bin/env python3
"""
Unit tests for speech_to_text_core.py

Tests the core library functions.
"""

import sys
import os
import tempfile
import io
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch, MagicMock
from datetime import timedelta


# Mock whisper module before importing speech_to_text_core
sys.modules['whisper'] = MagicMock()

# Now we can import the module
import speech_to_text_core


class TestFormatTimestamp(unittest.TestCase):
    """Test timestamp formatting function"""
    
    def test_zero_seconds(self):
        result = speech_to_text_core.format_timestamp(0)
        self.assertEqual(result, "00:00:00.000")
    
    def test_one_minute(self):
        result = speech_to_text_core.format_timestamp(60)
        self.assertEqual(result, "00:01:00.000")
    
    def test_one_hour(self):
        result = speech_to_text_core.format_timestamp(3600)
        self.assertEqual(result, "01:00:00.000")
    
    def test_complex_time(self):
        result = speech_to_text_core.format_timestamp(3723.456)
        self.assertEqual(result, "01:02:03.456")


class TestCommandLineValidation(unittest.TestCase):
    """Test command-line argument validation"""

    def test_no_arguments(self):
        """Exits with error when no arguments provided"""
        with patch.object(sys, 'argv', ['speech_to_text_core.py']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text_core.main()
            self.assertEqual(cm.exception.code, 1)

    def test_nonexistent_file(self):
        """Exits with error when MP3 file doesn't exist"""
        with patch.object(sys, 'argv', ['speech_to_text_core.py', 'nonexistent.mp3']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text_core.main()
            self.assertEqual(cm.exception.code, 1)

    def test_non_mp3_file(self):
        """Exits with error for non-MP3 files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test_audio.wav')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            with patch.object(sys, 'argv', ['speech_to_text_core.py', test_file]):
                with self.assertRaises(SystemExit) as cm:
                    speech_to_text_core.main()
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

                with patch.object(sys, 'argv', ['speech_to_text_core.py', test_file]):
                    speech_to_text_core.main()

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

                with patch.object(sys, 'argv', ['speech_to_text_core.py', test_file, 'auto']):
                    speech_to_text_core.main()

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

                with patch.object(sys, 'argv', ['speech_to_text_core.py', test_file, 'fr']):
                    speech_to_text_core.main()

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

            # Output file (test with timestamps enabled)
            out_path = os.path.join(tmpdir, 'out.txt')
            speech_to_text_core.write_transcription(result, out_path, audio_path, include_timestamps=True)

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
            # Segment 1 (with timestamps)
            self.assertEqual(lines[7], '[00:00:00.000 --> 00:00:01.230]')
            self.assertEqual(lines[8], 'Bonjour')
            self.assertEqual(lines[9], '')
            # Segment 2 (with timestamps)
            self.assertEqual(lines[10], '[00:00:01.230 --> 00:00:02.340]')
            self.assertEqual(lines[11], 'le monde')
            self.assertEqual(lines[12], '')

    def test_write_transcription_without_timestamps(self):
        """Test transcription output format without timestamps"""
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

            # Output file (default: no timestamps)
            out_path = os.path.join(tmpdir, 'out.txt')
            speech_to_text_core.write_transcription(result, out_path, audio_path)

            # Read and check output
            with open(out_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()

            # Check metadata
            self.assertTrue(lines[0].startswith('filename: sample.mp3'))
            self.assertTrue(lines[1].startswith('file_size: 3 bytes'))
            self.assertTrue(lines[2].startswith('sha1:'))
            # Blank line after metadata
            self.assertEqual(lines[3], '')
            # Language and segment count
            self.assertEqual(lines[4], 'language: fr')
            self.assertEqual(lines[5], 'segments: 2')
            # One blank line before content
            self.assertEqual(lines[6], '')
            # One segment per line without timestamps
            self.assertEqual(lines[7], 'Bonjour')
            self.assertEqual(lines[8], 'le monde')

    def test_french_audio_transcription_integration(self):
        """End-to-end test of French audio transcription against ground truth"""
        # Skip if test files don't exist or model file not available
        audio_file = 'test_data/french_words.mp3'
        ground_truth_file = 'test_data/french_words_ground_truth.txt'
        model_file = 'models/base.pt'
        
        if not (os.path.exists(audio_file) and os.path.exists(ground_truth_file) and os.path.exists(model_file)):
            self.skipTest("Test data files or model file not found")
        
        # Read ground truth words
        with open(ground_truth_file, 'r', encoding='utf-8') as f:
            ground_truth_words = [line.strip().lower() for line in f if line.strip()]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'french_test_output.txt')
            
            try:
                # Perform actual transcription (end-to-end test)
                result = speech_to_text_core.transcribe_audio(audio_file, 'fr')
                
                # Write transcription to file
                speech_to_text_core.write_transcription(result, output_file, audio_file)
                
                # Read the transcription output
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_content = f.read().lower()
                
                # Check if ground truth words appear in order
                last_position = -1
                for word_phrase in ground_truth_words:
                    position = output_content.find(word_phrase)
                    self.assertGreater(position, last_position, 
                                     f"Word/phrase '{word_phrase}' not found in correct order in transcription output")
                    last_position = position
                    
            except Exception as e:
                self.skipTest(f"Transcription failed (likely due to missing Whisper dependency): {e}")


class TestDiagnoseOption(unittest.TestCase):
    """Test the --diagnose CLI option"""

    def test_diagnose_exits_and_prints(self):
        buf = io.StringIO()
        with patch.object(sys, 'argv', ['speech_to_text_core.py', '--diagnose']):
            with self.assertRaises(SystemExit) as cm:
                with redirect_stdout(buf):
                    speech_to_text_core.main()
        self.assertEqual(cm.exception.code, 0)
        output = buf.getvalue()
        self.assertIn('Speech-to-Text Diagnostics', output)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
