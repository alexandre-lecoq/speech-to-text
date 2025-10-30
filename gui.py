#!/usr/bin/env python3
"""
Speech to Text GUI Application

Graphical User Interface for the speech-to-text tool using CustomTkinter.
Provides an easy-to-use, modern interface for transcribing MP3 audio files.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from speech_to_text import transcribe_audio, write_transcription


class SpeechToTextGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text - Transcription Audio")
        self.root.geometry("1300x900")
        
        # Set minimum window size
        self.root.minsize(723, 784)
        
        # Set theme
        ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        self.audio_file = ""
        self.output_file = ""
        self.is_processing = False
        
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
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🎤 Speech to Text - Transcription Audio",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Section 1: File selection
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=10)
        
        section1_label = ctk.CTkLabel(
            file_frame,
            text="1. Sélectionner un fichier audio (MP3):",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        section1_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        file_select_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_select_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            file_select_frame,
            text="Parcourir...",
            command=self.browse_file,
            width=120
        )
        self.browse_button.pack(side="left", padx=(0, 10))
        
        self.file_path_label = ctk.CTkLabel(
            file_select_frame,
            text="Aucun fichier sélectionné",
            text_color="gray",
            anchor="w"
        )
        self.file_path_label.pack(side="left", fill="x", expand=True)
        
        # Section 2: Options
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        section2_label = ctk.CTkLabel(
            options_frame,
            text="2. Options de transcription:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        section2_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Language selection
        lang_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lang_frame, text="Langue:", width=100, anchor="w").pack(side="left")
        self.language_var = ctk.StringVar(value="Auto-detect")
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
            text="Inclure les timestamps",
            variable=self.timestamps_var
        )
        self.timestamps_check.pack(pady=5, padx=10, anchor="w")
        
        # Chinese conversion
        chinese_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        chinese_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.chinese_var = ctk.BooleanVar(value=False)
        self.chinese_check = ctk.CTkCheckBox(
            chinese_frame,
            text="Conversion chinoise:",
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
        
        section3_label = ctk.CTkLabel(
            output_frame,
            text="3. Fichier de sortie:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        section3_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.output_path_label = ctk.CTkLabel(
            output_frame,
            text="",
            text_color="gray",
            anchor="w"
        )
        self.output_path_label.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        self.transcribe_button = ctk.CTkButton(
            button_frame,
            text="🚀 Transcrire",
            command=self.start_transcription,
            state="disabled",
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.transcribe_button.pack(side="left", padx=5)
        
        self.open_button = ctk.CTkButton(
            button_frame,
            text="📄 Ouvrir le résultat",
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
            text="Prêt",
            text_color="lightgreen",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        # Result preview
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, pady=10)
        
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Aperçu du résultat:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        preview_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.result_text = ctk.CTkTextbox(preview_frame, wrap="word", height=120)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Tip
        tip_label = ctk.CTkLabel(
            main_frame,
            text="💡 Astuce: Vous pouvez aussi utiliser l'outil en ligne de commande",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
        tip_label.pack(pady=(10, 0))
    
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
            self.output_path_label.configure(text=self.output_file, text_color="white")
            
            # Check if output file already exists
            if os.path.exists(self.output_file):
                self.show_existing_file_warning()
            else:
                self.result_text.delete("1.0", "end")
                self.status_label.configure(text="Prêt à transcrire", text_color="lightgreen")
            
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
        warning_msg = f"⚠️ Le fichier existe déjà et sera écrasé lors de la transcription"
        self.status_label.configure(text=warning_msg, text_color="orange")
        
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
            self.update_result_text(f"Erreur lors de la lecture du fichier existant: {str(e)}")
    
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
            self.update_result_text(f"Erreur lors de la lecture du fichier: {str(e)}")
    
    def start_transcription(self):
        """Start transcription process"""
        if not self.audio_file:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier audio")
            return
        
        if not os.path.exists(self.audio_file):
            messagebox.showerror("Erreur", "Le fichier sélectionné n'existe pas")
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
            # Update UI
            self.root.after(0, self.update_status, "Transcription en cours...", "lightblue", 0.3)
            self.root.after(0, lambda: self.transcribe_button.configure(state="disabled"))
            
            # Get options
            language_name = self.language_var.get()
            language_code = self.languages[language_name]
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
            
            # Success
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self.root.after(0, lambda: self.progress_label.configure(text="100%"))
            self.root.after(0, lambda: self.progress_details.configure(text="Terminé!"))
            success_msg = f"✓ Transcription terminée!\nFichier sauvegardé: {os.path.basename(self.output_file)}"
            self.root.after(0, self.update_status, success_msg, "lightgreen", 1.0)
            
            # Display result preview - refresh with new content
            self.root.after(0, self.load_and_display_transcription)
            
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            self.root.after(0, self.update_status, error_msg, "red", 0.0)
            self.root.after(0, lambda: self.progress_bar.set(0))
        
        finally:
            self.is_processing = False
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
    
    def open_output_file(self):
        """Open the output file in default text editor"""
        if os.path.exists(self.output_file):
            os.startfile(self.output_file)
        else:
            messagebox.showinfo("Information", "Aucun fichier de transcription disponible")


def launch_gui():
    """Launch the GUI application"""
    root = ctk.CTk()
    app = SpeechToTextGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
