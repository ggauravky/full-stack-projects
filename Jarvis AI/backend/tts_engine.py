import pyttsx3
import threading
import logging
from config import config

logger = logging.getLogger(__name__)

class TTSEngine:
    """Handles Text-To-Speech (TTS) functionality."""
    
    def __init__(self):
        self.engine = None
        self.lock = threading.Lock()
        
        try:
            self._init_engine()
        except Exception as e:
            logger.error(f"Failed to initialize TTS Engine: {e}")

    def _init_engine(self):
        """Initializes pyttsx3 engine and sets properties like voice and rate."""
        self.engine = pyttsx3.init()
        # Set Speech Rate
        self.engine.setProperty('rate', config.SPEECH_RATE)
        
        # Try to select a female voice (often Zira on Windows)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str, block: bool = False):
        """
        Speaks the given text.
        If block is False, the speech happens in a background thread so it doesn't freeze the app.
        """
        if not text or not self.engine:
            return
            
        def _say():
            with self.lock:
                try:
                    # re-init to avoid thread COM errors in windows
                    engine = pyttsx3.init()
                    engine.setProperty('rate', config.SPEECH_RATE)
                    
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if "female" in voice.name.lower() or "zira" in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break
                    
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    logger.error(f"Error during speech generation: {e}")

        if block:
            _say()
        else:
            thread = threading.Thread(target=_say, daemon=True)
            thread.start()
