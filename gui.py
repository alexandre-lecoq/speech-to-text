#!/usr/bin/env python3
"""
Speech to Text GUI Application

Graphical User Interface for the speech-to-text tool using CustomTkinter.
Provides an easy-to-use, modern interface for transcribing MP3 audio files.
"""

import os
import threading
import time
import locale
import customtkinter as ctk
from tkinter import filedialog, messagebox
from speech_to_text import transcribe_audio, write_transcription


class SpeechToTextGUI:
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
    
    def __init__(self, root):
        self.root = root
        
        # Detect system language
        self.current_language = self.detect_system_language()
        
        self.root.title(self.t("window_title"))
        self.root.geometry("1300x900")
        
        # Set minimum window size
        self.root.minsize(723, 784)
        
        # Set theme
        ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        self.audio_file = ""
        self.output_file = ""
        self.is_processing = False
        self.start_time = None
        self.elapsed_timer_active = False
        
        # Languages supported by Whisper
        self.languages = {
            "Auto-detect": None,
            "English": "en",
            "French": "fr",
            "Chinese": "zh",
            "Spanish": "es",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Dutch": "nl",
            "Turkish": "tr",
            "Polish": "pl",
            "Swedish": "sv",
            "Finnish": "fi",
            "Danish": "da",
            "Norwegian": "no",
            "Czech": "cs",
            "Hungarian": "hu",
            "Greek": "el",
            "Romanian": "ro",
            "Vietnamese": "vi",
            "Thai": "th",
            "Indonesian": "id",
            "Malay": "ms",
            "Hebrew": "he",
            "Ukrainian": "uk",
        }
        
        self.create_widgets()
    
    def detect_system_language(self):
        """Detect system language and return 'fr', 'en', or 'zh'"""
        try:
            system_locale = locale.getdefaultlocale()[0]
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
        self.root.title(self.t("window_title"))
        
        # Update all labels and buttons
        self.title_label.configure(text=f"🎤 {self.t('title')}")
        self.section1_label.configure(text=self.t("section1"))
        self.browse_button.configure(text=self.t("browse"))
        
        if not self.audio_file:
            self.file_path_label.configure(text=self.t("no_file"))
        
        self.section2_label.configure(text=self.t("section2"))
        self.lang_label.configure(text=self.t("language"))
        self.section3_label.configure(text=self.t("section3"))
        self.transcribe_button.configure(text=self.t("transcribe_btn"))
        self.open_button.configure(text=self.t("open_result_btn"))
        self.preview_label.configure(text=self.t("preview"))
        self.tip_label.configure(text=self.t("tip"))
        self.timestamps_check.configure(text=self.t("timestamps"))
        self.chinese_check.configure(text=self.t("chinese_conversion"))
        self.gui_lang_label.configure(text=self.t("gui_language"))
        
        # Update language combo with translated "Auto-detect"
        current_whisper_lang = self.language_var.get()
        if current_whisper_lang == "Auto-detect":
            self.language_var.set(self.t("auto_detect"))
        
        # Update status if it shows "Ready"
        current_status = self.status_label.cget("text")
        if current_status in ["Prêt", "Ready", "就绪", "Prêt à transcrire", "Ready to transcribe", "准备转录"]:
            if self.audio_file:
                self.status_label.configure(text=self.t("ready_to_transcribe"))
            else:
                self.status_label.configure(text=self.t("ready"))
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header frame with title and language selector
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title on the left
        self.title_label = ctk.CTkLabel(
            header_frame, 
            text=f"🎤 {self.t('title')}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left")
        
        # Language selector on the right
        gui_lang_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        gui_lang_frame.pack(side="right")
        
        self.gui_lang_label = ctk.CTkLabel(
            gui_lang_frame,
            text=self.t("gui_language"),
            font=ctk.CTkFont(size=11)
        )
        self.gui_lang_label.pack(side="left", padx=(0, 5))
        
        # Determine initial language display value
        lang_display = {
            "fr": "Français",
            "en": "English",
            "zh": "简体中文"
        }
        
        self.gui_language_var = ctk.StringVar(value=lang_display[self.current_language])
        self.gui_language_combo = ctk.CTkComboBox(
            gui_lang_frame,
            values=["Français", "English", "简体中文"],
            variable=self.gui_language_var,
            width=120,
            state="readonly",
            command=self.on_gui_language_change
        )
        self.gui_language_combo.pack(side="left")
        
        # Section 1: File selection
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=10)
        
        self.section1_label = ctk.CTkLabel(
            file_frame,
            text=self.t("section1"),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.section1_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.browse_button = ctk.CTkButton(
            file_frame,
            text=self.t("browse"),
            command=self.browse_file,
            width=120
        )
        self.browse_button.pack(padx=10, pady=(0, 5), anchor="w")
        
        self.file_path_label = ctk.CTkLabel(
            file_frame,
            text=self.t("no_file"),
            text_color="gray",
            anchor="w"
        )
        self.file_path_label.pack(padx=10, pady=(0, 10), anchor="w", fill="x")
        
        # Section 2: Options
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        self.section2_label = ctk.CTkLabel(
            options_frame,
            text=self.t("section2"),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.section2_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Language selection
        lang_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        self.lang_label = ctk.CTkLabel(lang_frame, text=self.t("language"), width=100, anchor="w")
        self.lang_label.pack(side="left")
        self.language_var = ctk.StringVar(value=self.t("auto_detect"))
        self.language_combo = ctk.CTkComboBox(
            lang_frame,
            values=list(self.languages.keys()),
            variable=self.language_var,
            width=200,
            state="readonly"
        )
        self.language_combo.pack(side="left", padx=10)
        
        # Timestamps checkbox
        self.timestamps_var = ctk.BooleanVar(value=False)
        self.timestamps_check = ctk.CTkCheckBox(
            options_frame,
            text=self.t("timestamps"),
            variable=self.timestamps_var
        )
        self.timestamps_check.pack(pady=5, padx=10, anchor="w")
        
        # Chinese conversion
        chinese_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        chinese_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.chinese_var = ctk.BooleanVar(value=False)
        self.chinese_check = ctk.CTkCheckBox(
            chinese_frame,
            text=self.t("chinese_conversion"),
            variable=self.chinese_var,
            command=self.update_chinese_options
        )
        self.chinese_check.pack(side="left")
        
        self.chinese_type_var = ctk.StringVar(value="Simplified")
        self.chinese_combo = ctk.CTkComboBox(
            chinese_frame,
            values=["Simplified", "Traditional"],
            variable=self.chinese_type_var,
            width=150,
            state="disabled"
        )
        self.chinese_combo.pack(side="left", padx=10)
        
        # Section 3: Output
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="x", pady=10)
        
        self.section3_label = ctk.CTkLabel(
            output_frame,
            text=self.t("section3"),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.section3_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.output_path_label = ctk.CTkLabel(
            output_frame,
            text="",
            text_color="gray",
            anchor="w",
            cursor="hand2"  # Change cursor to hand on hover
        )
        self.output_path_label.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Bind click event to open file location
        self.output_path_label.bind("<Button-1>", lambda e: self.open_file_location())
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        self.transcribe_button = ctk.CTkButton(
            button_frame,
            text=self.t("transcribe_btn"),
            command=self.start_transcription,
            state="disabled",
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.transcribe_button.pack(side="left", padx=5)
        
        self.open_button = ctk.CTkButton(
            button_frame,
            text=self.t("open_result_btn"),
            command=self.open_output_file,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.open_button.pack(side="left", padx=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text=self.t("ready"),
            text_color="lightgreen",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        # Result preview
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, pady=10)
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text=self.t("preview"),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.preview_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.result_text = ctk.CTkTextbox(preview_frame, wrap="word", height=120)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Tip
        self.tip_label = ctk.CTkLabel(
            main_frame,
            text=self.t("tip"),
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
        self.tip_label.pack(pady=(10, 0))
    
    def on_gui_language_change(self, choice):
        """Handle GUI language change from combobox"""
        lang_map = {
            "Français": "fr",
            "English": "en",
            "简体中文": "zh"
        }
        lang_code = lang_map.get(choice, "en")
        self.change_language(lang_code)
    
    def browse_file(self):
        """Open file dialog to select MP3 file"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier audio",
            filetypes=[("Fichiers MP3", "*.mp3"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            self.audio_file = filename
            self.file_path_label.configure(text=filename, text_color="white")
            
            # Auto-generate output filename
            base_name = os.path.splitext(filename)[0]
            self.output_file = f"{base_name}_transcription.txt"
            
            # Update output path label with clickable styling
            self.output_path_label.configure(
                text=self.output_file, 
                text_color="#3B8ED0"  # Blue color to indicate it's clickable
            )
            
            # Check if output file already exists
            if os.path.exists(self.output_file):
                self.show_existing_file_warning()
            else:
                self.result_text.delete("1.0", "end")
                self.status_label.configure(text=self.t("ready_to_transcribe"), text_color="lightgreen")
            
            # Enable transcribe button
            self.transcribe_button.configure(state="normal")
    
    def update_chinese_options(self):
        """Enable/disable Chinese conversion options"""
        if self.chinese_var.get():
            self.chinese_combo.configure(state="readonly")
        else:
            self.chinese_combo.configure(state="disabled")
    
    def show_existing_file_warning(self):
        """Display warning and preview for existing transcription file"""
        # Update status with warning
        self.status_label.configure(text=self.t("file_exists_warning"), text_color="orange")
        
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
                self.update_result_text(preview)
        except Exception as e:
            self.update_result_text(f"{self.t('file_read_error')} {str(e)}")
    
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
                self.update_result_text(preview)
        except Exception as e:
            self.update_result_text(f"{self.t('file_read_error')} {str(e)}")
    
    def start_transcription(self):
        """Start transcription process"""
        if not self.audio_file:
            messagebox.showwarning(self.t("warning_title"), self.t("select_file_warning"))
            return
        
        if not os.path.exists(self.audio_file):
            messagebox.showerror(self.t("error_title"), self.t("file_not_exist"))
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.result_text.delete("1.0", "end")
        
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
            self.root.after(0, self.update_elapsed_time)
            self.root.after(0, lambda: self.transcribe_button.configure(state="disabled"))
            
            # Get options
            language_name = self.language_var.get()
            # Handle translated "Auto-detect"
            if language_name == self.t("auto_detect"):
                language_code = None
            else:
                language_code = self.languages.get(language_name, None)
            include_timestamps = self.timestamps_var.get()
            
            chinese_conversion = None
            if self.chinese_var.get():
                chinese_type = self.chinese_type_var.get()
                chinese_conversion = "simplified" if chinese_type == "Simplified" else "traditional"
            
            # Transcribe
            self.root.after(0, lambda: self.progress_bar.set(0.5))
            result = transcribe_audio(self.audio_file, language_code)
            
            # Write output
            self.root.after(0, lambda: self.progress_bar.set(0.8))
            write_transcription(result, self.output_file, self.audio_file, 
                              include_timestamps, chinese_conversion)
            
            # Stop elapsed timer
            self.elapsed_timer_active = False
            
            # Success
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            success_msg = f"{self.t('transcription_complete')} {os.path.basename(self.output_file)}"
            self.root.after(0, self.update_status, success_msg, "lightgreen", 1.0)
            
            # Display result preview - refresh with new content
            self.root.after(0, self.load_and_display_transcription)
            
        except Exception as e:
            # Stop elapsed timer on error
            self.elapsed_timer_active = False
            
            error_msg = f"{self.t('error')} {str(e)}"
            self.root.after(0, self.update_status, error_msg, "red", 0.0)
            self.root.after(0, lambda: self.progress_bar.set(0))
        
        finally:
            self.is_processing = False
            self.start_time = None
            self.root.after(0, lambda: self.transcribe_button.configure(state="normal"))
    
    def update_status(self, message, color, progress):
        """Update status label and progress bar"""
        self.status_label.configure(text=message, text_color=color)
        if progress > 0:
            self.progress_bar.set(progress)
    
    def update_result_text(self, text):
        """Update result text widget"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
    
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
        self.status_label.configure(text=message, text_color="lightblue")
        
        # Schedule next update in 1 second
        if self.elapsed_timer_active:
            self.root.after(1000, self.update_elapsed_time)
    
    def open_output_file(self):
        """Open the output file in default text editor"""
        if os.path.exists(self.output_file):
            os.startfile(self.output_file)
        else:
            messagebox.showinfo(self.t("info_title"), self.t("no_transcription"))
    
    def open_file_location(self):
        """Open file explorer and select the output file"""
        if not self.output_file:
            return
        
        if os.path.exists(self.output_file):
            # Open explorer and select the file (Windows)
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
            messagebox.showinfo(
                self.t("file_coming"), 
                f"{self.t('file_will_be_created')}{self.output_file}"
            )


def launch_gui():
    """Launch the GUI application"""
    root = ctk.CTk()
    app = SpeechToTextGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
