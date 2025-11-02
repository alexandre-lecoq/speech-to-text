#!/usr/bin/env python3
"""
Speech to Text GUI Application (PySide6)

Graphical User Interface for the speech-to-text tool using PySide6.
Provides an easy-to-use, modern interface for transcribing MP3 audio files.
"""

import os
import threading
import time
import locale
import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QComboBox, QCheckBox,
    QTextEdit, QProgressBar, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QSettings
from PySide6.QtGui import QFont, QCursor, QIcon


class SignalEmitter(QObject):
    """Helper class to emit signals from worker thread"""
    status_update = Signal(str, str, float)
    text_update = Signal(str)
    progress_update = Signal(float)
    button_state = Signal(bool)
    transcription_complete = Signal()
    start_elapsed_timer = Signal()
    stop_elapsed_timer = Signal()


class SpeechToTextGUI(QMainWindow):
    # Translation dictionary
    TRANSLATIONS = {
        "fr": {
            "title": "Speech to Text - Transcription Audio",
            "window_title": "Speech to Text - Transcription Audio",
            "section1": "1. Sélectionner un fichier audio (MP3):",
            "browse": "Parcourir...",
            "no_file": "Aucun fichier sélectionné",
            "section2": "2. Options de transcription:",
            "language": "Langue:",
            "auto_detect": "Auto-detect",
            "timestamps": "Inclure les timestamps",
            "chinese_conversion": "Conversion chinoise:",
            "chinese_simplified": "Simplifié",
            "chinese_traditional": "Traditionnel",
            "section3": "3. Fichier de sortie:",
            "transcribe_btn": "🚀 Transcrire",
            "open_result_btn": "📄 Ouvrir le résultat",
            "preview": "Aperçu du résultat:",
            "tip": "💡 Astuce: Vous pouvez aussi utiliser l'outil en ligne de commande",
            "ready": "Prêt",
            "ready_to_transcribe": "Prêt à transcrire",
            "transcribing": "Transcription en cours depuis",
            "transcription_complete": "✓ Transcription terminée!\nFichier sauvegardé:",
            "error": "❌ Erreur:",
            "warning_title": "Attention",
            "select_file_warning": "Veuillez sélectionner un fichier audio",
            "error_title": "Erreur",
            "file_not_exist": "Le fichier sélectionné n'existe pas",
            "info_title": "Information",
            "no_transcription": "Aucun fichier de transcription disponible",
            "file_exists_warning": "⚠️ Le fichier existe déjà et sera écrasé lors de la transcription",
            "file_read_error": "Erreur lors de la lecture du fichier existant:",
            "file_coming": "Fichier à venir",
            "file_will_be_created": "Le fichier sera créé ici après la transcription:\n",
            "gui_language": "Langue:",
        },
        "en": {
            "title": "Speech to Text - Audio Transcription",
            "window_title": "Speech to Text - Audio Transcription",
            "section1": "1. Select an audio file (MP3):",
            "browse": "Browse...",
            "no_file": "No file selected",
            "section2": "2. Transcription options:",
            "language": "Language:",
            "auto_detect": "Auto-detect",
            "timestamps": "Include timestamps",
            "chinese_conversion": "Chinese conversion:",
            "chinese_simplified": "Simplified",
            "chinese_traditional": "Traditional",
            "section3": "3. Output file:",
            "transcribe_btn": "🚀 Transcribe",
            "open_result_btn": "📄 Open result",
            "preview": "Result preview:",
            "tip": "💡 Tip: You can also use the command-line tool",
            "ready": "Ready",
            "ready_to_transcribe": "Ready to transcribe",
            "transcribing": "Transcribing for",
            "transcription_complete": "✓ Transcription complete!\nFile saved:",
            "error": "❌ Error:",
            "warning_title": "Warning",
            "select_file_warning": "Please select an audio file",
            "error_title": "Error",
            "file_not_exist": "The selected file does not exist",
            "info_title": "Information",
            "no_transcription": "No transcription file available",
            "file_exists_warning": "⚠️ The file already exists and will be overwritten during transcription",
            "file_read_error": "Error reading existing file:",
            "file_coming": "Upcoming file",
            "file_will_be_created": "The file will be created here after transcription:\n",
            "gui_language": "Language:",
        },
        "zh": {
            "title": "语音转文字 - 音频转录",
            "window_title": "语音转文字 - 音频转录",
            "section1": "1. 选择音频文件（MP3）：",
            "browse": "浏览...",
            "no_file": "未选择文件",
            "section2": "2. 转录选项：",
            "language": "语言：",
            "auto_detect": "自动检测",
            "timestamps": "包含时间戳",
            "chinese_conversion": "中文转换：",
            "chinese_simplified": "简体",
            "chinese_traditional": "繁体",
            "section3": "3. 输出文件：",
            "transcribe_btn": "🚀 转录",
            "open_result_btn": "📄 打开结果",
            "preview": "结果预览：",
            "tip": "💡 提示：您也可以使用命令行工具",
            "ready": "就绪",
            "ready_to_transcribe": "准备转录",
            "transcribing": "转录进行中",
            "transcription_complete": "✓ 转录完成！\n文件已保存：",
            "error": "❌ 错误：",
            "warning_title": "警告",
            "select_file_warning": "请选择音频文件",
            "error_title": "错误",
            "file_not_exist": "选择的文件不存在",
            "info_title": "信息",
            "no_transcription": "没有可用的转录文件",
            "file_exists_warning": "⚠️ 文件已存在，转录时将被覆盖",
            "file_read_error": "读取现有文件时出错：",
            "file_coming": "即将创建文件",
            "file_will_be_created": "转录后将在此处创建文件：\n",
            "gui_language": "语言：",
        }
    }
    
    def __init__(self):
        super().__init__()
        
        # Preload heavy modules in background immediately (non-blocking)
        self.preload_modules_in_background()
        
        # Initialize settings to persist preferences across sessions
        self.settings = QSettings("SpeechToText", "SpeechToTextApp")
        
        # Detect system language
        self.current_language = self.detect_system_language()
        
        self.setWindowTitle(self.t("window_title"))
        
        # Set window icon
        try:
            self.setWindowIcon(QIcon('icon.ico'))
        except:
            pass  # Ignore if icon file is not found
        
        self.setMinimumSize(723, 1050)
        self.resize(1300, 1050)
        
        self.audio_file = ""
        self.output_file = ""
        self.is_processing = False
        self.start_time = None
        self.elapsed_timer_active = False
        self.gpu_status_label = None  # Reference to GPU status label for background update
        # Load last directory from settings
        self.last_directory = self.settings.value("last_directory", "")  # Remember last directory for file browser
        
        # Signal emitter for thread communication
        self.signals = SignalEmitter()
        self.signals.status_update.connect(self.update_status)
        self.signals.text_update.connect(self.update_result_text)
        self.signals.progress_update.connect(self.update_progress)
        self.signals.button_state.connect(self.set_transcribe_button_state)
        self.signals.transcription_complete.connect(self.load_and_display_transcription)
        self.signals.start_elapsed_timer.connect(self.start_elapsed_timer)
        self.signals.stop_elapsed_timer.connect(self.stop_elapsed_timer)
        
        # Timer for elapsed time updates
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)
        
        # Languages supported by Whisper - using language codes as keys
        self.language_codes = [
            None, "en", "fr", "zh", "es", "de", "it", "pt", "ru", "ja", "ko", "ar",
            "nl", "tr", "pl", "sv", "fi", "da", "no", "cs", "hu", "el", "ro", "vi",
            "th", "id", "ms", "he", "uk"
        ]
        
        # Translated language names for display
        self.language_names = {
            "en": [
                "Auto-detect", "English", "French", "Chinese", "Spanish", "German",
                "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Arabic",
                "Dutch", "Turkish", "Polish", "Swedish", "Finnish", "Danish",
                "Norwegian", "Czech", "Hungarian", "Greek", "Romanian", "Vietnamese",
                "Thai", "Indonesian", "Malay", "Hebrew", "Ukrainian"
            ],
            "fr": [
                "Détection automatique", "Anglais", "Français", "Chinois", "Espagnol", "Allemand",
                "Italien", "Portugais", "Russe", "Japonais", "Coréen", "Arabe",
                "Néerlandais", "Turc", "Polonais", "Suédois", "Finnois", "Danois",
                "Norvégien", "Tchèque", "Hongrois", "Grec", "Roumain", "Vietnamien",
                "Thaï", "Indonésien", "Malais", "Hébreu", "Ukrainien"
            ],
            "zh": [
                "自动检测", "英语", "法语", "中文", "西班牙语", "德语",
                "意大利语", "葡萄牙语", "俄语", "日语", "韩语", "阿拉伯语",
                "荷兰语", "土耳其语", "波兰语", "瑞典语", "芬兰语", "丹麦语",
                "挪威语", "捷克语", "匈牙利语", "希腊语", "罗马尼亚语", "越南语",
                "泰语", "印尼语", "马来语", "希伯来语", "乌克兰语"
            ]
        }
        
        self.create_widgets()
        self.apply_dark_theme()
        
        # Start GPU detection in background (non-blocking)
        self.detect_gpu_in_background()
    
    def detect_gpu_in_background(self):
        """Detect GPU availability in background thread (non-blocking). It makes the GUI more responsive on startup."""
        def detect_gpu():
            try:
                import torch
                if torch.cuda.is_available():
                    compute_text = "🟢 GPU 😀"
                    compute_tooltip = "Using CUDA GPU"
                else:
                    compute_text = "🔴 CPU 😐"
                    compute_tooltip = "Using CPU"
                
                # Update label from background thread
                if self.gpu_status_label:
                    self.gpu_status_label.setText(compute_text)
                    self.gpu_status_label.setToolTip(compute_tooltip)
            except Exception as e:
                if self.gpu_status_label:
                    self.gpu_status_label.setText("⚠️ GPU ?")
                    self.gpu_status_label.setToolTip(f"Detection error: {str(e)}")
        
        # Run detection in daemon thread (non-blocking)
        thread = threading.Thread(target=detect_gpu, daemon=True)
        thread.start()
    
    def preload_modules_in_background(self):
        """Preload heavy external modules in background to speed up later usage"""
        def preload():
            try:
                from speech_to_text_core import preload_external_modules
                preload_external_modules()
            except Exception as e:
                print(f"Warning: Failed to preload modules: {e}")
        
        # Run preloading in daemon thread (non-blocking)
        thread = threading.Thread(target=preload, daemon=True)
        thread.start()
    
    def detect_system_language(self):
        """Detect system language and return 'fr', 'en', or 'zh'"""
        try:
            system_locale = locale.getlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code == 'fr':
                    return 'fr'
                elif lang_code == 'zh':
                    return 'zh'
        except:
            pass
        return 'en'  # Default to English
    
    def t(self, key):
        """Get translated text for the current language"""
        return self.TRANSLATIONS[self.current_language].get(key, key)
    
    def change_language(self, lang_code):
        """Change the GUI language and update all text elements"""
        self.current_language = lang_code
        self.update_all_texts()
    
    def update_all_texts(self):
        """Update all text elements in the GUI with current language"""
        # Update window title
        self.setWindowTitle(self.t("window_title"))
        
        # Update all labels and buttons
        self.title_label.setText(f"🎤 {self.t('title')}")
        self.section1_label.setText(self.t("section1"))
        self.browse_button.setText(self.t("browse"))
        
        if not self.audio_file:
            self.file_path_label.setText(self.t("no_file"))
        
        self.section2_label.setText(self.t("section2"))
        self.lang_label.setText(self.t("language"))
        self.section3_label.setText(self.t("section3"))
        self.transcribe_button.setText(self.t("transcribe_btn"))
        self.open_button.setText(self.t("open_result_btn"))
        self.preview_label.setText(self.t("preview"))
        self.tip_label.setText(self.t("tip"))
        self.timestamps_check.setText(self.t("timestamps"))
        self.chinese_check.setText(self.t("chinese_conversion"))
        self.gui_lang_label.setText(self.t("gui_language"))
        
        # Update language combo box with translated "Auto-detect"
        self.update_language_combo()
        
        # Update Chinese conversion combo box items
        current_index = self.chinese_combo.currentIndex()
        self.chinese_combo.clear()
        self.chinese_combo.addItems([self.t("chinese_simplified"), self.t("chinese_traditional")])
        self.chinese_combo.setCurrentIndex(current_index)
        
        # Update status if it shows "Ready"
        current_status = self.status_label.text()
        if current_status in ["Prêt", "Ready", "就绪", "Prêt à transcrire", "Ready to transcribe", "准备转录"]:
            if self.audio_file:
                self.status_label.setText(self.t("ready_to_transcribe"))
            else:
                self.status_label.setText(self.t("ready"))
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
            }
            QPushButton {
                background-color: #1f6aa5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2986cc;
            }
            QPushButton:pressed {
                background-color: #165d8f;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #808080;
            }
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
                selection-background-color: #1f6aa5;
            }
            QCheckBox {
                background-color: transparent;
                color: white;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #1f6aa5;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #1f6aa5;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
            QProgressBar {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #1f6aa5;
                border-radius: 5px;
            }
        """)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header frame with title and language selector
        header_layout = QHBoxLayout()
        
        # Title on the left
        self.title_label = QLabel(f"🎤 {self.t('title')}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Language selector on the right
        self.gui_lang_label = QLabel(self.t("gui_language"))
        header_layout.addWidget(self.gui_lang_label)
        
        self.gui_language_combo = QComboBox()
        self.gui_language_combo.addItems(["🇫🇷 Français", "🇬🇧 English", "🇨🇳 简体中文"])
        lang_display = {
            "fr": "🇫🇷 Français",
            "en": "🇬🇧 English",
            "zh": "🇨🇳 简体中文"
        }
        self.gui_language_combo.setCurrentText(lang_display[self.current_language])
        self.gui_language_combo.currentTextChanged.connect(self.on_gui_language_change)
        self.gui_language_combo.setFixedWidth(140)
        header_layout.addWidget(self.gui_language_combo)
        
        main_layout.addLayout(header_layout)
        
        # Section 1: File selection
        file_frame = QFrame()
        file_layout = QVBoxLayout(file_frame)
        
        self.section1_label = QLabel(self.t("section1"))
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        self.section1_label.setFont(section_font)
        file_layout.addWidget(self.section1_label)
        
        self.browse_button = QPushButton(self.t("browse"))
        self.browse_button.setFixedWidth(120)
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        
        self.file_path_label = QLabel(self.t("no_file"))
        self.file_path_label.setStyleSheet("color: gray;")
        file_layout.addWidget(self.file_path_label)
        
        main_layout.addWidget(file_frame)
        
        # Section 2: Options
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        
        self.section2_label = QLabel(self.t("section2"))
        self.section2_label.setFont(section_font)
        options_layout.addWidget(self.section2_label)
        
        # Language selection
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel(self.t("language"))
        self.lang_label.setFixedWidth(100)
        lang_layout.addWidget(self.lang_label)
        
        self.language_combo = QComboBox()
        # Populate language combo with translated "Auto-detect" and other languages
        self.update_language_combo()
        self.language_combo.setFixedWidth(200)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        
        options_layout.addLayout(lang_layout)
        
        # Timestamps checkbox
        self.timestamps_check = QCheckBox(self.t("timestamps"))
        options_layout.addWidget(self.timestamps_check)
        
        # Chinese conversion
        chinese_layout = QHBoxLayout()
        self.chinese_check = QCheckBox(self.t("chinese_conversion"))
        self.chinese_check.stateChanged.connect(self.update_chinese_options)
        chinese_layout.addWidget(self.chinese_check)
        
        self.chinese_combo = QComboBox()
        self.chinese_combo.addItems([self.t("chinese_simplified"), self.t("chinese_traditional")])
        self.chinese_combo.setFixedWidth(150)
        self.chinese_combo.setEnabled(False)
        chinese_layout.addWidget(self.chinese_combo)
        chinese_layout.addStretch()
        
        options_layout.addLayout(chinese_layout)
        
        main_layout.addWidget(options_frame)
        
        # Section 3: Output
        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)
        
        self.section3_label = QLabel(self.t("section3"))
        self.section3_label.setFont(section_font)
        output_layout.addWidget(self.section3_label)
        
        self.output_path_label = QLabel("")
        self.output_path_label.setStyleSheet("color: #3B8ED0;")
        self.output_path_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.output_path_label.mousePressEvent = lambda e: self.open_file_location()
        output_layout.addWidget(self.output_path_label)
        
        main_layout.addWidget(output_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.transcribe_button = QPushButton(self.t("transcribe_btn"))
        self.transcribe_button.setFixedSize(180, 40)
        button_font = QFont()
        button_font.setPointSize(11)
        button_font.setBold(True)
        self.transcribe_button.setFont(button_font)
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.transcribe_button.setEnabled(False)
        button_layout.addWidget(self.transcribe_button)
        
        self.open_button = QPushButton(self.t("open_result_btn"))
        self.open_button.setFixedSize(180, 40)
        self.open_button.setFont(button_font)
        self.open_button.clicked.connect(self.open_output_file)
        button_layout.addWidget(self.open_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(400)
        self.progress_bar.setValue(0)
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        main_layout.addLayout(progress_layout)
        
        # Status label
        self.status_label = QLabel(self.t("ready"))
        self.status_label.setStyleSheet("color: lightgreen;")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Result preview
        preview_frame = QFrame()
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_label = QLabel(self.t("preview"))
        self.preview_label.setFont(section_font)
        preview_layout.addWidget(self.preview_label)
        
        self.result_text = QTextEdit()
        self.result_text.setMinimumHeight(120)
        preview_layout.addWidget(self.result_text)
        
        main_layout.addWidget(preview_frame, 1)
        
        # Bottom bar with copyright, tip, and compute info
        bottom_layout = QHBoxLayout()
        
        # Copyright on the left
        copyright_label = QLabel("© 2025 Alexandre")
        copyright_label.setStyleSheet("color: #666666;")
        copyright_label.setAlignment(Qt.AlignLeft)
        copyright_font = QFont()
        copyright_font.setPointSize(8)
        copyright_label.setFont(copyright_font)
        bottom_layout.addWidget(copyright_label)
        
        # Tip in the center
        self.tip_label = QLabel(self.t("tip"))
        self.tip_label.setStyleSheet("color: gray;")
        self.tip_label.setAlignment(Qt.AlignCenter)
        tip_font = QFont()
        tip_font.setPointSize(9)
        self.tip_label.setFont(tip_font)
        bottom_layout.addWidget(self.tip_label, 1)
        
        # GPU indicator on the right (initial state while detecting)
        self.gpu_status_label = QLabel("⚪ GPU ?")
        self.gpu_status_label.setStyleSheet("color: #888888;")
        self.gpu_status_label.setAlignment(Qt.AlignRight)
        self.gpu_status_label.setToolTip("Detecting...")
        compute_font = QFont()
        compute_font.setPointSize(9)
        self.gpu_status_label.setFont(compute_font)
        bottom_layout.addWidget(self.gpu_status_label)
        
        main_layout.addLayout(bottom_layout)

    def on_gui_language_change(self, choice):
        """Handle GUI language change from combobox"""
        lang_map = {
            "🇫🇷 Français": "fr",
            "🇬🇧 English": "en",
            "🇨🇳 简体中文": "zh"
        }
        lang_code = lang_map.get(choice, "en")
        self.change_language(lang_code)
    
    def update_language_combo(self):
        """Update the language combo box with translated language names and preserve selection"""
        # Remember current selection by index
        current_index = self.language_combo.currentIndex()
        if current_index < 0:
            current_index = 0  # Default to first item (Auto-detect)
        
        # Clear and rebuild the list with translated names
        self.language_combo.clear()
        self.language_combo.addItems(self.language_names[self.current_language])
        
        # Restore selection by index
        if current_index < self.language_combo.count():
            self.language_combo.setCurrentIndex(current_index)
    
    def browse_file(self):
        """Open file dialog to select MP3 file"""
        # Use last directory if available, otherwise empty string (current directory)
        start_dir = self.last_directory if self.last_directory else ""
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select audio file",
            start_dir,
            "MP3 Files (*.mp3);;All Files (*.*)"
        )
        
        if filename:
            self.audio_file = filename
            self.file_path_label.setText(filename)
            self.file_path_label.setStyleSheet("color: white;")
            
            # Remember the directory for next time and save to settings
            self.last_directory = os.path.dirname(filename)
            self.settings.setValue("last_directory", self.last_directory)
            
            # Auto-generate output filename
            base_name = os.path.splitext(filename)[0]
            self.output_file = f"{base_name}_transcription.txt"
            
            # Update output path label
            self.output_path_label.setText(self.output_file)
            
            # Check if output file already exists
            if os.path.exists(self.output_file):
                self.show_existing_file_warning()
            else:
                self.result_text.clear()
                self.status_label.setText(self.t("ready_to_transcribe"))
                self.status_label.setStyleSheet("color: lightgreen;")
            
            # Enable transcribe button
            self.transcribe_button.setEnabled(True)
    
    def update_chinese_options(self):
        """Enable/disable Chinese conversion options"""
        self.chinese_combo.setEnabled(self.chinese_check.isChecked())
    
    def show_existing_file_warning(self):
        """Display warning and preview for existing transcription file"""
        # Update status with warning
        self.status_label.setText(self.t("file_exists_warning"))
        self.status_label.setStyleSheet("color: orange;")
        
        # Load and display existing file content in preview
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Skip header to show actual transcription in preview
                lines = content.split('\n')
                # Find where the actual transcription starts
                start_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("=" * 80) and i > 5:  # Skip first header
                        start_idx = i + 2
                        break
                
                # Get transcription content
                transcription_lines = lines[start_idx:]
                preview_text = '\n'.join(transcription_lines)
                
                preview = preview_text[:1000] + ("..." if len(preview_text) > 1000 else "")
                self.result_text.setPlainText(preview)
        except Exception as e:
            self.result_text.setPlainText(f"{self.t('file_read_error')} {str(e)}")
    
    def load_and_display_transcription(self):
        """Load and display the transcription file in preview"""
        if not os.path.exists(self.output_file):
            return
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Skip header to show actual transcription in preview
                lines = content.split('\n')
                # Find where the actual transcription starts
                start_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("=" * 80) and i > 5:  # Skip first header
                        start_idx = i + 2
                        break
                
                # Get transcription content
                transcription_lines = lines[start_idx:]
                preview_text = '\n'.join(transcription_lines)
                preview = preview_text[:1000] + ("..." if len(preview_text) > 1000 else "")
                self.result_text.setPlainText(preview)
        except Exception as e:
            self.result_text.setPlainText(f"{self.t('file_read_error')} {str(e)}")
    
    def start_transcription(self):
        """Start transcription process"""
        if not self.audio_file:
            QMessageBox.warning(self, self.t("warning_title"), self.t("select_file_warning"))
            return
        
        if not os.path.exists(self.audio_file):
            QMessageBox.critical(self, self.t("error_title"), self.t("file_not_exist"))
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.result_text.clear()
        
        # Run transcription in separate thread to keep UI responsive
        thread = threading.Thread(target=self.transcribe_thread)
        thread.daemon = True
        thread.start()
    
    def transcribe_thread(self):
        """Run transcription in a separate thread"""
        try:
            # Start elapsed time tracking
            self.start_time = time.time()
            self.elapsed_timer_active = True
            
            # Update UI and start timer
            self.signals.button_state.emit(False)
            self.signals.start_elapsed_timer.emit()  # Signal to start timer in main thread
            
            # Get options
            language_index = self.language_combo.currentIndex()
            # Get the language code from the index
            if language_index >= 0 and language_index < len(self.language_codes):
                language_code = self.language_codes[language_index]
            else:
                language_code = None  # Default to auto-detect
            include_timestamps = self.timestamps_check.isChecked()
            
            chinese_conversion = None
            if self.chinese_check.isChecked():
                chinese_type = self.chinese_combo.currentText()
                # Check against all possible translations
                if chinese_type in [self.t("chinese_simplified"), "Simplified", "Simplifié", "简体"]:
                    chinese_conversion = "simplified"
                else:
                    chinese_conversion = "traditional"

            # Import transcription functions here to avoid blocking UI            
            from speech_to_text_core import transcribe_audio, write_transcription

            # Transcribe
            self.signals.progress_update.emit(0.5)
            result = transcribe_audio(self.audio_file, language_code)
            
            # Write output
            self.signals.progress_update.emit(0.8)
            write_transcription(result, self.output_file, self.audio_file, 
                              include_timestamps, chinese_conversion)
            
            # Stop elapsed timer
            self.elapsed_timer_active = False
            self.signals.stop_elapsed_timer.emit()  # Signal to stop timer in main thread
            
            # Success
            self.signals.progress_update.emit(1.0)
            success_msg = f"{self.t('transcription_complete')} {os.path.basename(self.output_file)}"
            self.signals.status_update.emit(success_msg, "lightgreen", 1.0)
            
            # Display result preview - refresh with new content
            self.signals.transcription_complete.emit()
            
        except Exception as e:
            # Stop elapsed timer on error
            self.elapsed_timer_active = False
            self.signals.stop_elapsed_timer.emit()  # Signal to stop timer in main thread
            
            error_msg = f"{self.t('error')} {str(e)}"
            self.signals.status_update.emit(error_msg, "red", 0.0)
            self.signals.progress_update.emit(0.0)
        
        finally:
            self.is_processing = False
            self.start_time = None
            self.signals.button_state.emit(True)
    
    def update_status(self, message, color, progress):
        """Update status label and progress bar"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")
        if progress > 0:
            self.progress_bar.setValue(int(progress * 100))
    
    def update_result_text(self, text):
        """Update result text widget"""
        self.result_text.setPlainText(text)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(int(value * 100))
    
    def set_transcribe_button_state(self, enabled):
        """Set transcribe button enabled state"""
        self.transcribe_button.setEnabled(enabled)
    
    def format_elapsed_time(self, seconds):
        """Format elapsed time in a readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def update_elapsed_time(self):
        """Update the elapsed time display during transcription"""
        if not self.elapsed_timer_active or not self.start_time:
            return
        
        elapsed = time.time() - self.start_time
        elapsed_str = self.format_elapsed_time(elapsed)
        message = f"{self.t('transcribing')} {elapsed_str}..."
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: lightblue;")
    
    def start_elapsed_timer(self):
        """Start the elapsed time timer (must be called from main thread)"""
        self.elapsed_timer.start(1000)  # Update every second
    
    def stop_elapsed_timer(self):
        """Stop the elapsed time timer (must be called from main thread)"""
        self.elapsed_timer.stop()
    
    def open_output_file(self):
        """Open the output file in default text editor"""
        if os.path.exists(self.output_file):
            if os.name == 'nt':  # Windows
                os.startfile(self.output_file)
            elif os.name == 'posix':  # macOS/Linux
                import platform
                if platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{self.output_file}"')
                else:  # Linux
                    os.system(f'xdg-open "{self.output_file}"')
        else:
            QMessageBox.information(self, self.t("info_title"), self.t("no_transcription"))
    
    def open_file_location(self):
        """Open file explorer and select the output file"""
        if not self.output_file:
            return
        
        if os.path.exists(self.output_file):
            # Open explorer and select the file
            if os.name == 'nt':  # Windows
                os.system(f'explorer /select,"{os.path.abspath(self.output_file)}"')
            elif os.name == 'posix':  # macOS/Linux
                import platform
                if platform.system() == 'Darwin':  # macOS
                    os.system(f'open -R "{self.output_file}"')
                else:  # Linux
                    # Open the directory containing the file
                    directory = os.path.dirname(os.path.abspath(self.output_file))
                    os.system(f'xdg-open "{directory}"')
        else:
            # File doesn't exist yet, show the path that will be created
            QMessageBox.information(
                self, 
                self.t("file_coming"), 
                f"{self.t('file_will_be_created')}{self.output_file}"
            )


def main():
    """Launch the GUI application"""
    app = QApplication(sys.argv)
    window = SpeechToTextGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
