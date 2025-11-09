#!/usr/bin/env python3
"""
Unit tests for speech_to_text_core.py

Tests the core functionality including transcription, timestamp formatting,
file writing, and diagnostic functions.
"""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import sys
import tempfile
from datetime import timedelta

# Import the module to test
import speech_to_text_core


class TestFormatTimestamp(unittest.TestCase):
    """Tests for the format_timestamp function"""
    
    def test_format_timestamp_zero(self):
        """Test formatting of zero seconds"""
        result = speech_to_text_core.format_timestamp(0)
        self.assertEqual(result, "00:00:00.000")
    
    def test_format_timestamp_seconds_only(self):
        """Test formatting with only seconds"""
        result = speech_to_text_core.format_timestamp(45.123)
        self.assertEqual(result, "00:00:45.123")
    
    def test_format_timestamp_minutes_and_seconds(self):
        """Test formatting with minutes and seconds"""
        result = speech_to_text_core.format_timestamp(125.456)
        self.assertEqual(result, "00:02:05.456")
    
    def test_format_timestamp_hours_minutes_seconds(self):
        """Test formatting with hours, minutes and seconds"""
        result = speech_to_text_core.format_timestamp(3725.789)
        self.assertEqual(result, "01:02:05.789")
    
    def test_format_timestamp_milliseconds_precision(self):
        """Test that milliseconds are properly formatted"""
        result = speech_to_text_core.format_timestamp(1.001)
        self.assertEqual(result, "00:00:01.001")


class TestTranscribeAudio(unittest.TestCase):
    """Tests for the transcribe_audio function"""
    
    def test_transcribe_audio_requires_torch_and_whisper(self):
        """Test that transcribe_audio requires torch and whisper modules"""
        # This test verifies the function exists and has correct signature
        import inspect
        sig = inspect.signature(speech_to_text_core.transcribe_audio)
        params = list(sig.parameters.keys())
        
        self.assertIn('audio_file', params)
        self.assertIn('language_code', params)
        self.assertIn('progress_callback', params)


class TestWriteTranscription(unittest.TestCase):
    """Tests for the write_transcription function"""
    
    def setUp(self):
        """Create a temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.close()
        self.output_file = self.temp_file.name
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.output_file):
            os.unlink(self.output_file)
    
    def test_write_transcription_without_timestamps(self):
        """Test writing transcription without timestamps"""
        result = {
            'language': 'en',
            'segments': [
                {'text': ' Hello world', 'start': 0.0, 'end': 1.0},
                {'text': ' This is a test', 'start': 1.0, 'end': 2.0}
            ]
        }
        
        # Create a real audio file for testing
        audio_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mp3')
        audio_file.write('test data')
        audio_file.close()
        
        try:
            speech_to_text_core.write_transcription(
                result, self.output_file, audio_file.name, include_timestamps=False
            )
            
            # Read the output file
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Assertions
            self.assertIn('language: en', content)
            self.assertIn('segments: 2', content)
            self.assertIn('Hello world', content)
            self.assertIn('This is a test', content)
            self.assertNotIn('[00:00:00', content)  # No timestamps
        finally:
            os.unlink(audio_file.name)
    
    def test_write_transcription_with_timestamps(self):
        """Test writing transcription with timestamps"""
        result = {
            'language': 'fr',
            'segments': [
                {'text': ' Bonjour', 'start': 0.0, 'end': 1.5},
                {'text': ' Comment allez-vous', 'start': 1.5, 'end': 3.0}
            ]
        }
        
        audio_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mp3')
        audio_file.write('test data')
        audio_file.close()
        
        try:
            speech_to_text_core.write_transcription(
                result, self.output_file, audio_file.name, include_timestamps=True
            )
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Assertions
            self.assertIn('[00:00:00.000 --> 00:00:01.500]', content)
            self.assertIn('[00:00:01.500 --> 00:00:03.000]', content)
            self.assertIn('Bonjour', content)
        finally:
            os.unlink(audio_file.name)
    
    def test_write_transcription_metadata(self):
        """Test that file metadata is written correctly"""
        result = {
            'language': 'en',
            'segments': []
        }
        
        audio_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mp3')
        audio_file.write('test data')
        audio_file.close()
        
        try:
            speech_to_text_core.write_transcription(
                result, self.output_file, audio_file.name
            )
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check metadata
            self.assertIn('filename:', content)
            self.assertIn('file_size:', content)
            self.assertIn('sha1:', content)
            self.assertIn('.mp3', content)
        finally:
            os.unlink(audio_file.name)
    
    def test_write_transcription_chinese_without_conversion(self):
        """Test that Chinese text can be written without conversion"""
        result = {
            'language': 'zh',
            'segments': [
                {'text': '你好', 'start': 0.0, 'end': 1.0}
            ]
        }
        
        audio_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mp3')
        audio_file.write('test data')
        audio_file.close()
        
        try:
            speech_to_text_core.write_transcription(
                result, self.output_file, audio_file.name, 
                include_timestamps=False, chinese_conversion=None
            )
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify text is written as-is
            self.assertIn('你好', content)
        finally:
            os.unlink(audio_file.name)


class TestDiagnose(unittest.TestCase):
    """Tests for the diagnose function"""
    
    @patch('sys.exit')
    def test_diagnose_function_exits(self, mock_exit):
        """Test diagnose function calls sys.exit"""
        # Just verify the function attempts to call sys.exit
        speech_to_text_core.diagnose()
        
        # Verify exit was called
        mock_exit.assert_called_once_with(0)


class TestUpdateModel(unittest.TestCase):
    """Tests for the update_model function"""
    
    def test_update_model_function_signature(self):
        """Test that update_model function exists and has correct signature"""
        import inspect
        sig = inspect.signature(speech_to_text_core.update_model)
        params = list(sig.parameters.keys())
        
        # update_model takes no parameters
        self.assertEqual(len(params), 0)


class TestListLanguages(unittest.TestCase):
    """Tests for the list_languages function"""
    
    @patch('sys.exit')
    def test_list_languages_exits(self, mock_exit):
        """Test listing of supported languages"""
        # Capture stdout
        from io import StringIO
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            # Call function
            speech_to_text_core.list_languages()
            
            # Get output
            output = captured_output.getvalue()
            
            # Check that something was printed
            self.assertGreater(len(output), 0)
            mock_exit.assert_called_once_with(0)
        finally:
            sys.stdout = old_stdout


class TestPreloadExternalModules(unittest.TestCase):
    """Tests for the preload_external_modules function"""
    
    def test_preload_external_modules_signature(self):
        """Test that preload_external_modules function exists"""
        import inspect
        sig = inspect.signature(speech_to_text_core.preload_external_modules)
        params = list(sig.parameters.keys())
        
        # Function takes no parameters
        self.assertEqual(len(params), 0)


if __name__ == '__main__':
    unittest.main()
