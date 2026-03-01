import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Try finding .env one directory up if running from within backend folder
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

class Config:
    """Application configuration and environment variables."""
    # AI Provider Settings
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Assistant settings
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "JarvisLite")
    SPEECH_RATE = int(os.getenv("SPEECH_RATE", "175"))

    @classmethod
    def validate(cls):
        """Validate critical configuration elements."""
        if cls.AI_PROVIDER not in ("gemini", "openai"):
            print(f"Warning: Invalid AI_PROVIDER '{cls.AI_PROVIDER}'. Falling back to 'gemini'.")
            cls.AI_PROVIDER = "gemini"

        if cls.AI_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY is not set.")
        elif cls.AI_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY is not set.")

config = Config()
