#!/usr/bin/env python3
"""
Unit tests for speech_to_text.py

Tests the command-line argument parsing and validation logic.
"""

import sys
import os
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
        """Test that script exits with error when no arguments provided"""
        with patch.object(sys, 'argv', ['speech_to_text.py']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text.main()
            self.assertEqual(cm.exception.code, 1)
    
    def test_one_argument(self):
        """Test that script exits with error when only one argument provided"""
        with patch.object(sys, 'argv', ['speech_to_text.py', 'english']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text.main()
            self.assertEqual(cm.exception.code, 1)
    
    def test_unsupported_language(self):
        """Test that script exits with error for unsupported language"""
        with patch.object(sys, 'argv', ['speech_to_text.py', 'spanish', 'test.mp3']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text.main()
            self.assertEqual(cm.exception.code, 1)
    
    def test_nonexistent_file(self):
        """Test that script exits with error when file doesn't exist"""
        with patch.object(sys, 'argv', ['speech_to_text.py', 'english', 'nonexistent.mp3']):
            with self.assertRaises(SystemExit) as cm:
                speech_to_text.main()
            self.assertEqual(cm.exception.code, 1)
    
    def test_non_mp3_file(self):
        """Test that script exits with error for non-MP3 files"""
        # Create a temporary non-MP3 file
        test_file = '/tmp/test_audio.wav'
        with open(test_file, 'w') as f:
            f.write('test')
        
        try:
            with patch.object(sys, 'argv', ['speech_to_text.py', 'english', test_file]):
                with self.assertRaises(SystemExit) as cm:
                    speech_to_text.main()
                self.assertEqual(cm.exception.code, 1)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


class TestLanguageMapping(unittest.TestCase):
    """Test language code mapping"""
    
    def test_supported_languages(self):
        """Test that all required languages are supported"""
        # Test with valid arguments but mock the transcription part
        test_file = '/tmp/test_audio.mp3'
        with open(test_file, 'w') as f:
            f.write('test')
        
        try:
            # Mock the transcribe_audio and write_transcription functions
            with patch('speech_to_text.transcribe_audio') as mock_transcribe:
                with patch('speech_to_text.write_transcription') as mock_write:
                    mock_transcribe.return_value = {'segments': []}
                    
                    # Test Chinese
                    with patch.object(sys, 'argv', ['speech_to_text.py', 'chinese', test_file]):
                        speech_to_text.main()
                    
                    # Test French
                    with patch.object(sys, 'argv', ['speech_to_text.py', 'french', test_file]):
                        speech_to_text.main()
                    
                    # Test English
                    with patch.object(sys, 'argv', ['speech_to_text.py', 'english', test_file]):
                        speech_to_text.main()
                    
                    # Verify transcribe_audio was called 3 times
                    self.assertEqual(mock_transcribe.call_count, 3)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
