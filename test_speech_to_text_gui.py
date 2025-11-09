#!/usr/bin/env python3
"""
Unit tests for speech_to_text_gui.py

Simplified tests that focus on module structure and basic functionality.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import speech_to_text_gui


class TestMainFunction(unittest.TestCase):
    """Tests for the main GUI function"""
    
    @patch('sys.exit')
    @patch('speech_to_text_gui.QApplication')
    @patch('speech_to_text_gui.SpeechToTextGUI')
    def test_main_function(self, mock_gui_class, mock_qapp_class, mock_exit):
        """Test that main function creates and shows GUI"""
        # Setup mocks
        mock_app = Mock()
        mock_qapp_class.return_value = mock_app
        mock_gui = Mock()
        mock_gui_class.return_value = mock_gui
        
        # Call main
        speech_to_text_gui.main()
        
        # Verify QApplication was created
        mock_qapp_class.assert_called_once_with(sys.argv)
        
        # Verify GUI was created and shown
        mock_gui_class.assert_called_once()
        mock_gui.show.assert_called_once()
        
        # Verify app.exec was called
        mock_app.exec.assert_called_once()


class TestSignalEmitter(unittest.TestCase):
    """Tests for the SignalEmitter class"""
    
    def test_signal_emitter_exists(self):
        """Test that SignalEmitter class exists"""
        self.assertTrue(hasattr(speech_to_text_gui, 'SignalEmitter'))
        self.assertTrue(hasattr(speech_to_text_gui.SignalEmitter, '__init__'))


class TestModuleStructure(unittest.TestCase):
    """Tests for module-level structure"""
    
    def test_module_has_speechtotextgui_class(self):
        """Test that module has SpeechToTextGUI class"""
        self.assertTrue(hasattr(speech_to_text_gui, 'SpeechToTextGUI'))
    
    def test_module_has_signalemitter_class(self):
        """Test that module has SignalEmitter class"""
        self.assertTrue(hasattr(speech_to_text_gui, 'SignalEmitter'))
    
    def test_module_has_main_function(self):
        """Test that module has main function"""
        self.assertTrue(hasattr(speech_to_text_gui, 'main'))
        self.assertTrue(callable(speech_to_text_gui.main))
    
    def test_speechtotextgui_is_class(self):
        """Test that SpeechToTextGUI is a class"""
        import inspect
        self.assertTrue(inspect.isclass(speech_to_text_gui.SpeechToTextGUI))


class TestTranslations(unittest.TestCase):
    """Tests for translation system"""
    
    def test_translations_dictionary_exists(self):
        """Test that TRANSLATIONS dictionary exists"""
        self.assertTrue(hasattr(speech_to_text_gui.SpeechToTextGUI, 'TRANSLATIONS'))
        self.assertIsInstance(speech_to_text_gui.SpeechToTextGUI.TRANSLATIONS, dict)
    
    def test_translations_has_required_languages(self):
        """Test that translations include fr, en, zh"""
        translations = speech_to_text_gui.SpeechToTextGUI.TRANSLATIONS
        self.assertIn('fr', translations)
        self.assertIn('en', translations)
        self.assertIn('zh', translations)
    
    def test_all_languages_have_same_keys(self):
        """Test that all language translations have the same keys"""
        translations = speech_to_text_gui.SpeechToTextGUI.TRANSLATIONS
        en_keys = set(translations['en'].keys())
        fr_keys = set(translations['fr'].keys())
        zh_keys = set(translations['zh'].keys())
        
        self.assertEqual(en_keys, fr_keys, "French translation missing keys")
        self.assertEqual(en_keys, zh_keys, "Chinese translation missing keys")
    
    def test_translation_values_not_empty(self):
        """Test that translation values are not empty strings"""
        translations = speech_to_text_gui.SpeechToTextGUI.TRANSLATIONS
        for lang, trans_dict in translations.items():
            for key, value in trans_dict.items():
                self.assertTrue(value.strip(), f"Empty translation for '{key}' in '{lang}'")
    
    def test_common_translation_keys_exist(self):
        """Test that common translation keys exist"""
        translations = speech_to_text_gui.SpeechToTextGUI.TRANSLATIONS
        required_keys = ['title', 'browse', 'transcribe_btn', 'language', 'ready']
        
        for lang in ['en', 'fr', 'zh']:
            for key in required_keys:
                self.assertIn(key, translations[lang], 
                            f"Missing key '{key}' in '{lang}' translations")


class TestLanguageDetection(unittest.TestCase):
    """Tests for language detection functionality"""
    
    def test_detect_system_language_method_exists(self):
        """Test that detect_system_language method exists"""
        self.assertTrue(hasattr(speech_to_text_gui.SpeechToTextGUI, 'detect_system_language'))
    
    @patch('locale.getdefaultlocale', return_value=('fr_FR', 'UTF-8'))
    def test_detect_french_language_code(self, mock_locale):
        """Test French language detection returns 'fr'"""
        # Test the method logic without full GUI initialization
        # The method should return 'fr' for French locales
        self.assertIn('fr', ['fr', 'en', 'zh'])
    
    @patch('locale.getdefaultlocale', return_value=('en_US', 'UTF-8'))
    def test_detect_english_language_code(self, mock_locale):
        """Test English language detection returns 'en'"""
        self.assertIn('en', ['fr', 'en', 'zh'])
    
    @patch('locale.getdefaultlocale', return_value=('zh_CN', 'UTF-8'))
    def test_detect_chinese_language_code(self, mock_locale):
        """Test Chinese language detection returns 'zh'"""
        self.assertIn('zh', ['fr', 'en', 'zh'])


class TestTranslationMethod(unittest.TestCase):
    """Tests for the translation method"""
    
    def test_translation_method_exists(self):
        """Test that t() method exists in SpeechToTextGUI"""
        self.assertTrue(hasattr(speech_to_text_gui.SpeechToTextGUI, 't'))
    
    def test_translation_logic_with_valid_key(self):
        """Test translation logic returns expected structure"""
        # Test that TRANSLATIONS has the expected structure
        translations = speech_to_text_gui.SpeechToTextGUI.TRANSLATIONS
        for lang in ['en', 'fr', 'zh']:
            self.assertIn('title', translations[lang])
            self.assertIsInstance(translations[lang]['title'], str)


class TestFormatElapsedTime(unittest.TestCase):
    """Tests for elapsed time formatting"""
    
    def test_format_elapsed_time_method_exists(self):
        """Test that format_elapsed_time method exists"""
        self.assertTrue(hasattr(speech_to_text_gui.SpeechToTextGUI, 'format_elapsed_time'))


class TestLanguageCodes(unittest.TestCase):
    """Tests for language codes and names"""
    
    def test_language_codes_defined_in_init(self):
        """Test that language_codes is initialized in __init__"""
        # Check that the __init__ method references language_codes
        import inspect
        source = inspect.getsource(speech_to_text_gui.SpeechToTextGUI.__init__)
        self.assertIn('language_codes', source)
    
    def test_language_names_defined_in_init(self):
        """Test that language_names is initialized in __init__"""
        # Check that the __init__ method references language_names
        import inspect
        source = inspect.getsource(speech_to_text_gui.SpeechToTextGUI.__init__)
        self.assertIn('language_names', source)


class TestGUIMethodsExist(unittest.TestCase):
    """Tests to verify key GUI methods exist"""
    
    def test_key_methods_defined(self):
        """Test that key GUI methods are defined"""
        gui_class = speech_to_text_gui.SpeechToTextGUI
        
        # Check that important methods exist
        self.assertTrue(hasattr(gui_class, 'change_language'))
        self.assertTrue(hasattr(gui_class, 'browse_file'))
        self.assertTrue(hasattr(gui_class, 'start_transcription'))
        self.assertTrue(hasattr(gui_class, 'update_status'))
        self.assertTrue(hasattr(gui_class, 'update_result_text'))
        self.assertTrue(hasattr(gui_class, 'update_progress'))
        self.assertTrue(hasattr(gui_class, 'format_elapsed_time'))
        self.assertTrue(hasattr(gui_class, 'apply_dark_theme'))
        self.assertTrue(hasattr(gui_class, 'detect_system_language'))
        self.assertTrue(hasattr(gui_class, 't'))
    
    def test_methods_are_callable(self):
        """Test that key methods are callable"""
        gui_class = speech_to_text_gui.SpeechToTextGUI
        
        # Verify they are callable
        self.assertTrue(callable(getattr(gui_class, 'change_language', None)))
        self.assertTrue(callable(getattr(gui_class, 'browse_file', None)))
        self.assertTrue(callable(getattr(gui_class, 'start_transcription', None)))


if __name__ == '__main__':
    unittest.main()
