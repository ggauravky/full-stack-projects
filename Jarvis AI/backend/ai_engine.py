import logging
import google.generativeai as genai
from openai import OpenAI
from config import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        """Initialize the AI engine with the configured provider."""
        self.provider = config.AI_PROVIDER
        self.openai_client = None
        
        try:
            if self.provider == "gemini":
                if config.GEMINI_API_KEY:
                    genai.configure(api_key=config.GEMINI_API_KEY)
                    self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                else:
                    logger.warning("Gemini initialized but API key is missing.")
            else:
                if config.OPENAI_API_KEY:
                    self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
                else:
                    logger.warning("OpenAI initialized but API key is missing.")
        except Exception as e:
            logger.error(f"Error initializing AI fallback to error handlers later: {e}")

    def get_ai_response(self, text: str, retries: int = 2) -> str:
        """Call the AI API with automatic retries."""
        for attempt in range(retries):
            try:
                if self.provider == "gemini":
                    return self._call_gemini(text)
                else:
                    return self._call_openai(text)
            except Exception as e:
                logger.error(f"AI Engine failure [Attempt {attempt + 1}/{retries}]: {e}")
                if attempt == retries - 1:
                    return "I'm having trouble connecting to my AI brain right now. Please check my API key or connection."
        
        return "Sorry, I could not process that request."

    def _call_gemini(self, text: str) -> str:
        """Helper to call Gemini."""
        if not config.GEMINI_API_KEY:
            return "My Gemini API key is missing from the configuration."
            
        system_instruction = f"You are a helpful and concise voice assistant named {config.ASSISTANT_NAME}. Keep answers relatively short so they can be spoken clearly."
        # Using a prepended instruction since flash model might not support explicit system_instruction param depending on sdk version
        prompt = f"System Instruction: {system_instruction}\nUser: {text}"
        
        response = self.gemini_model.generate_content(prompt)
        return response.text.strip()

    def _call_openai(self, text: str) -> str:
        """Helper to call OpenAI."""
        if not config.OPENAI_API_KEY or not self.openai_client:
            return "My OpenAI API key is missing from the configuration."
            
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful and concise voice assistant named {config.ASSISTANT_NAME}. Keep answers relatively short so they can be spoken clearly."},
                {"role": "user", "content": text}
            ],
            max_tokens=150,
            timeout=10.0
        )
        return response.choices[0].message.content.strip()
