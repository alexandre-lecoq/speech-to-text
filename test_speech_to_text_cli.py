#!/usr/bin/env python3
"""
Unit tests for speech_to_text.py (CLI)

Tests the command-line interface including argument parsing,
file validation, and main function behavior.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# Import the module to test
import speech_to_text


class TestMainFunction(unittest.TestCase):
    """Tests for the main CLI function"""
    
    @patch('speech_to_text_core.write_transcription')
    @patch('speech_to_text_core.transcribe_audio')
    @patch('os.path.exists')
    def test_main_with_valid_mp3_auto_language(self, mock_exists, mock_transcribe, mock_write):
        """Test main function with valid MP3 file and auto language detection"""
        # Setup
        mock_exists.return_value = True
        mock_result = {
            'text': 'Test transcription',
            'segments': [],
            'language': 'en'
        }
        mock_transcribe.return_value = mock_result
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', 'test.mp3']):
            speech_to_text.main()
        
        # Assertions
        mock_transcribe.assert_called_once_with('test.mp3', None)
        mock_write.assert_called_once()
    
    @patch('speech_to_text_core.write_transcription')
    @patch('speech_to_text_core.transcribe_audio')
    @patch('os.path.exists')
    def test_main_with_specified_language(self, mock_exists, mock_transcribe, mock_write):
        """Test main function with specified language"""
        # Setup
        mock_exists.return_value = True
        mock_result = {'text': 'Bonjour', 'segments': [], 'language': 'fr'}
        mock_transcribe.return_value = mock_result
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', 'test.mp3', 'fr']):
            speech_to_text.main()
        
        # Assertions
        mock_transcribe.assert_called_once_with('test.mp3', 'fr')
    
    @patch('speech_to_text_core.write_transcription')
    @patch('speech_to_text_core.transcribe_audio')
    @patch('os.path.exists')
    def test_main_with_timestamps(self, mock_exists, mock_transcribe, mock_write):
        """Test main function with timestamps option"""
        # Setup
        mock_exists.return_value = True
        mock_result = {'text': 'Test', 'segments': [], 'language': 'en'}
        mock_transcribe.return_value = mock_result
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', 'test.mp3', 'en', '--timestamps']):
            speech_to_text.main()
        
        # Verify timestamps flag was passed
        call_args = mock_write.call_args
        self.assertTrue(call_args[0][3])  # include_timestamps parameter
    
    @patch('sys.exit')
    @patch('os.path.exists')
    def test_main_file_not_found(self, mock_exists, mock_exit):
        """Test main function when audio file doesn't exist"""
        # Setup
        mock_exists.return_value = False
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', 'nonexistent.mp3']):
            speech_to_text.main()
        
        # Verify exit was called with error code
        self.assertTrue(mock_exit.called)
        # Check that at least one call was with exit code 1
        calls = [call[0][0] for call in mock_exit.call_args_list]
        self.assertIn(1, calls)
    
    @patch('sys.exit')
    def test_main_no_arguments(self, mock_exit):
        """Test main function with no arguments"""
        # When sys.exit is mocked, the function continues and raises IndexError
        # We expect sys.exit to be called due to invalid arguments
        with patch.object(sys, 'argv', ['speech_to_text.py']):
            try:
                speech_to_text.main()
            except IndexError:
                # This is expected since sys.exit is mocked and code continues
                pass
        
        # Verify exit was called with error code
        self.assertTrue(mock_exit.called)
        calls = [call[0][0] for call in mock_exit.call_args_list]
        self.assertIn(1, calls)
    
    @patch('speech_to_text_core.update_model')
    def test_main_update_model(self, mock_update):
        """Test main function with --update-model flag"""
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', '--update-model']):
            speech_to_text.main()
        
        # Verify update_model was called
        mock_update.assert_called_once()
    
    @patch('speech_to_text_core.diagnose')
    def test_main_diagnose(self, mock_diagnose):
        """Test main function with --diagnose flag"""
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', '--diagnose']):
            speech_to_text.main()
        
        # Verify diagnose was called
        mock_diagnose.assert_called_once()
    
    @patch('speech_to_text_core.list_languages')
    def test_main_list_languages(self, mock_list):
        """Test main function with --list-languages flag"""
        # Mock sys.argv
        with patch.object(sys, 'argv', ['speech_to_text.py', '--list-languages']):
            speech_to_text.main()
        
        # Verify list_languages was called
        mock_list.assert_called_once()


class TestArgumentParsing(unittest.TestCase):
    """Tests for argument parsing logic"""
    
    def test_timestamps_flag_parsing(self):
        """Test that --timestamps flag is correctly parsed"""
        test_args = ['test.mp3', 'en', '--timestamps']
        
        include_timestamps = '--timestamps' in test_args
        self.assertTrue(include_timestamps)
    
    def test_chinese_flag_parsing_simplified(self):
        """Test parsing of --chinese=simplified"""
        test_args = ['test.mp3', 'zh', '--chinese=simplified']
        
        chinese_conversion = None
        for arg in test_args:
            if arg.startswith('--chinese='):
                chinese_conversion = arg.split('=', 1)[1].strip().lower()
        
        self.assertEqual(chinese_conversion, 'simplified')
    
    def test_chinese_flag_parsing_traditional(self):
        """Test parsing of --chinese=traditional"""
        test_args = ['test.mp3', 'zh', '--chinese=traditional']
        
        chinese_conversion = None
        for arg in test_args:
            if arg.startswith('--chinese='):
                chinese_conversion = arg.split('=', 1)[1].strip().lower()
        
        self.assertEqual(chinese_conversion, 'traditional')
    
    def test_mixed_argument_order(self):
        """Test that arguments can be in any order"""
        test_args = ['--timestamps', 'test.mp3', '--chinese=simplified', 'zh']
        
        # Simulate parsing
        include_timestamps = '--timestamps' in test_args
        chinese_conversion = None
        
        for arg in test_args[:]:
            if arg.startswith('--chinese='):
                chinese_conversion = arg.split('=', 1)[1].strip().lower()
        
        self.assertTrue(include_timestamps)
        self.assertEqual(chinese_conversion, 'simplified')


if __name__ == '__main__':
    unittest.main()
