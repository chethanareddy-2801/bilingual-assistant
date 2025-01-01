import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import threading
import pygame
import google.cloud.texttospeech as tts
import google.generativeai as genai
from google.cloud import translate_v2 as translate
import os
import tempfile
from PIL import Image, ImageTk

class BilingualAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Hindi-Kannada Language Assistant")
        self.root.geometry("800x600")
        
        # Initialize Gemini for language processing
        genai.configure(api_key="YOUR_API_KEY_HERE")
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }
        )
        
        # Initialize Google Cloud clients
        self.translate_client = translate.Client.from_service_account_json("path/to/your/service-account.json")
        self.tts_client = tts.TextToSpeechClient.from_service_account_json("path/to/your/service-account.json")
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recording = False
        self.audio_data = None
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Language selection
        lang_frame = ttk.LabelFrame(main_frame, text="Select Language", padding="10")
        lang_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.language_var = tk.StringVar(value="hindi")
        ttk.Radiobutton(lang_frame, text="Hindi", variable=self.language_var, 
                       value="hindi").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(lang_frame, text="Kannada", variable=self.language_var, 
                       value="kannada").grid(row=0, column=1, padx=10)
        
        # Record and playback controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.record_button = ttk.Button(control_frame, text="Start Recording", 
                                      command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, padx=5)
        
        self.play_button = ttk.Button(control_frame, text="Play Translation", 
                                    command=self.play_translation, state="disabled")
        self.play_button.grid(row=0, column=1, padx=5)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Text display areas
        display_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        display_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Original speech
        ttk.Label(display_frame, text="Original Speech:").grid(row=0, column=0, sticky="w")
        self.original_text = tk.Text(display_frame, height=4, width=60)
        self.original_text.grid(row=1, column=0, pady=5)
        
        # Translation
        ttk.Label(display_frame, text="Translation:").grid(row=2, column=0, sticky="w")
        self.translated_text = tk.Text(display_frame, height=4, width=60)
        self.translated_text.grid(row=3, column=0, pady=5)
        
        # Corrections (if any)
        ttk.Label(display_frame, text="Corrections:").grid(row=4, column=0, sticky="w")
        self.corrections_text = tk.Text(display_frame, height=4, width=60)
        self.corrections_text.grid(row=5, column=0, pady=5)
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.record_button.configure(text="Stop Recording")
        self.status_var.set("Recording...")
        
        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.start()
    
    def stop_recording(self):
        self.recording = False
        self.record_button.configure(text="Start Recording")
        self.status_var.set("Processing...")
        
        # Process the recorded audio
        self.process_audio()
    
    def record_audio(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.recording:
                try:
                    audio = self.recognizer.listen(source, timeout=1)
                    self.audio_data = audio
                except sr.WaitTimeoutError:
                    continue
    
    def process_audio(self):
        try:
            # Convert speech to text
            source_lang = "hi-IN" if self.language_var.get() == "hindi" else "kn-IN"
            text = self.recognizer.recognize_google(self.audio_data, language=source_lang)
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(tk.END, text)
            
            # Translate the text
            target_lang = "kn" if self.language_var.get() == "hindi" else "hi"
            translation = self.translate_text(text, target_lang)
            self.translated_text.delete(1.0, tk.END)
            self.translated_text.insert(tk.END, translation)
            
            # Check for corrections
            corrections = self.check_corrections(text, self.language_var.get())
            self.corrections_text.delete(1.0, tk.END)
            self.corrections_text.insert(tk.END, corrections)
            
            # Generate TTS for translation
            self.generate_tts(translation, target_lang)
            
            self.status_var.set("Ready")
            self.play_button.configure(state="normal")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def translate_text(self, text, target_lang):
        result = self.translate_client.translate(
            text,
            target_language=target_lang
        )
        return result["translatedText"]
    
    def check_corrections(self, text, source_lang):
        prompt = f"""Check the following {source_lang} text for any grammatical or pronunciation errors and provide corrections if needed:
        {text}"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_tts(self, text, language):
        # Configure voice based on language
        if language == "hi":
            voice = tts.VoiceSelectionParams(
                language_code="hi-IN",
                name="hi-IN-Standard-A"
            )
        else:
            voice = tts.VoiceSelectionParams(
                language_code="kn-IN",
                name="kn-IN-Standard-A"
            )
        
        # Configure audio
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.MP3
        )
        
        # Generate speech
        synthesis_input = tts.SynthesisInput(text=text)
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save to temporary file
        self.temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        self.temp_audio_file.write(response.audio_content)
        self.temp_audio_file.close()
    
    def play_translation(self):
        pygame.mixer.music.load(self.temp_audio_file.name)
        pygame.mixer.music.play()
    
    def _del_(self):
        # Cleanup temporary files
        if hasattr(self, 'temp_audio_file'):
            os.unlink(self.temp_audio_file.name)

def main():
    root = tk.Tk()
    app = BilingualAssistant(root)
    root.mainloop()

if __name__ == "__main__":
    main()