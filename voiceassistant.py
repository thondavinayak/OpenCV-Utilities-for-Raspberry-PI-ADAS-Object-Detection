import sys
import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

# Predefined data
phone_numbers = {"Aron": "1234567890", "Cassey": "9999988888", "Kumar": "6543277777"}
bank_account_numbers = {"Aron": "123456789", "George": "99993333999"}

class VoiceThread(QThread):
    text_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.r = sr.Recognizer()
        self.is_listening = True
        
    def run(self):
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    self.status_signal.emit("Adjusting for ambient noise...")
                    self.r.adjust_for_ambient_noise(source)
                    self.status_signal.emit("Listening... Ask now...")
                    audioin = self.r.listen(source)
                    
                self.status_signal.emit("Processing...")
                my_text = self.r.recognize_google(audioin)
                my_text = my_text.lower()
                self.text_signal.emit(f"You said: {my_text}")
                
                # Process the command
                response = self.process_command(my_text)
                self.text_signal.emit(f"Assistant: {response}")
                self.speak(response)
                
            except sr.UnknownValueError:
                self.status_signal.emit("Could not understand audio")
            except sr.RequestError as e:
                self.status_signal.emit(f"Error with speech recognition: {e}")
            except Exception as e:
                self.status_signal.emit(f"Error: {str(e)}")
    
    def process_command(self, my_text):
        # Ask to play song
        if 'play' in my_text:
            my_text = my_text.replace('play', '')
            pywhatkit.playonyt(my_text)
            return f'playing {my_text}'
        
        # Ask date
        elif 'date' in my_text:
            today = datetime.date.today()
            return str(today)
        
        # Ask time
        elif 'time' in my_text:
            timenow = datetime.datetime.now().strftime('%H:%M')
            return timenow
        
        # Ask details about any person
        elif "who is" in my_text:
            person = my_text.replace('who is', '')
            try:
                info = wikipedia.summary(person, sentences=1)
                return info
            except:
                return "Sorry, I couldn't find information about that person."
        
        # Ask phone numbers
        elif "phone number" in my_text:
            names = list(phone_numbers)
            for name in names:
                if name in my_text:
                    return f"{name}'s phone number is {phone_numbers[name]}"
            return "I don't have a phone number for that person."
        
        # Ask personal bank account numbers
        elif "account number" in my_text:
            banks = list(bank_account_numbers)
            for bank in banks:
                if bank in my_text:
                    return f"{bank} bank account number is {bank_account_numbers[bank]}"
            return "I don't have a bank account number for that bank."
        
        # If not recognized
        else:
            return "Please ask a correct question"
    
    def speak(self, text):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
    
    def stop(self):
        self.is_listening = False
        self.wait()

class VoiceAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Voice Assistant")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 15px; background-color: #2c3e50; color: white;")
        layout.addWidget(title)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 11))
        layout.addWidget(self.output_text)
        
        # Status bar
        self.status_label = QLabel("Ready to start...")
        self.status_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Listening")
        self.start_button.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 10px; }")
        self.start_button.clicked.connect(self.start_listening)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 10px; }")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Initialize voice thread
        self.voice_thread = None
        
        # Add some initial text
        self.output_text.append("Welcome to Voice Assistant!")
        self.output_text.append("You can ask me to:")
        self.output_text.append(" - Play songs (e.g., 'play Pink Floyd Best Hits')")
        self.output_text.append(" - Tell you the date or time")
        self.output_text.append(" - Look up information (e.g., 'who is Marie Curie')")
        self.output_text.append(" - Provide phone numbers (e.g., 'what is Aron's phone number')")
        self.output_text.append(" - Provide bank account numbers (e.g., 'what is Kumar's bank account number')")
        self.output_text.append("")
        
    def start_listening(self):
        self.output_text.append("Starting voice assistant...")
        self.status_label.setText("Starting...")
        
        self.voice_thread = VoiceThread()
        self.voice_thread.text_signal.connect(self.update_text)
        self.voice_thread.status_signal.connect(self.update_status)
        self.voice_thread.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
    
    def stop_listening(self):
        if self.voice_thread:
            self.output_text.append("Stopping voice assistant...")
            self.voice_thread.stop()
            self.voice_thread = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Stopped")
    
    def update_text(self, text):
        self.output_text.append(text)
    
    def update_status(self, status):
        self.status_label.setText(status)
    
    def closeEvent(self, event):
        if self.voice_thread:
            self.voice_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = VoiceAssistantApp()
    window.show()
    
    sys.exit(app.exec_())