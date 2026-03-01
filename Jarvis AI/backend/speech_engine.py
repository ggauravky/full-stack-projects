import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)

class SpeechEngine:
    """Handles speech-to-text functionality using the microphone."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust recognizer sensitivity
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def listen(self, timeout=5, phrase_time_limit=10) -> str:
        """
        Listens to the microphone and returns recognized text.
        Handles missing microphone, timeouts, and unrecognized speech.
        """
        try:
            with sr.Microphone() as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Listening...")
                
                # Listen with timeout (if nobody speaks) and phase limit (max speaking time)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                logger.info("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                return text

        except sr.WaitTimeoutError:
            logger.warning("Listening timed out. No speech detected.")
            return ""
        except sr.UnknownValueError:
            logger.warning("Could not understand the audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return "Sorry, my speech recognition service is currently unavailable."
        except OSError as e:
            # Often triggered if PyAudio is missing, or no mic is plugged in
            logger.error(f"Microphone access error: {e}")
            return "I could not access your microphone. Please check your audio settings or PyAudio installation."
        except Exception as e:
            logger.error(f"Unexpected speech error: {e}")
            return "An unexpected error occurred while listening to your voice."
