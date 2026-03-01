import logging
import google.generativeai as genai
from openai import OpenAI
from config import config
from command_handler import CommandHandler

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, command_handler: CommandHandler = None):
        """Initialize the AI engine with the configured provider and memory."""
        self.provider = config.AI_PROVIDER
        self.openai_client = None
        self.chat_session = None
        
        try:
            if self.provider == "gemini":
                if config.GEMINI_API_KEY:
                    genai.configure(api_key=config.GEMINI_API_KEY)
                    
                    # Define the tools we want to give to Gemini
                    tools = []
                    if command_handler:
                        tools = [
                            command_handler.search_wikipedia,
                            command_handler.get_weather,
                            command_handler.search_google,
                            command_handler.tell_time,
                            command_handler.tell_date,
                            command_handler.tell_joke,
                            command_handler.scrape_website
                        ]
                    
                    # System Instructions
                    system_instruction = f"You are a helpful and concise voice assistant named {config.ASSISTANT_NAME}. You have access to tools. Use them if the user asks for weather, time, wikipedia summaries, or to search google. You also have a scrape_website tool to read articles if the user provides a link. Keep answers relatively short so they can be spoken clearly."
                    
                    self.gemini_model = genai.GenerativeModel(
                        model_name='gemini-2.5-flash',
                        tools=tools,
                        system_instruction=system_instruction
                    )
                    
                    # Initialize conversation memory for Gemini
                    self.chat_session = self.gemini_model.start_chat(enable_automatic_function_calling=True)
                else:
                    logger.warning("Gemini initialized but API key is missing.")
            else:
                if config.OPENAI_API_KEY:
                    self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
                    # Initialize a basic memory buffer for OpenAI
                    self.openai_memory = [
                         {"role": "system", "content": f"You are a helpful and concise voice assistant named {config.ASSISTANT_NAME}. Keep answers relatively short so they can be spoken clearly."}
                    ]
                else:
                    logger.warning("OpenAI initialized but API key is missing.")
        except Exception as e:
            logger.error(f"Error initializing AI fallback to error handlers later: {e}")

    def get_ai_response(self, text: str, retries: int = 2) -> str:
        """Call the AI API with automatic retries and conversational memory."""
        for attempt in range(retries):
            try:
                if self.provider == "gemini":
                    return self._call_gemini(text)
                else:
                    return self._call_openai(text)
            except Exception as e:
                error_str = str(e)
                logger.error(f"AI Engine failure [Attempt {attempt + 1}/{retries}]: {error_str}")
                
                # Check for rate-limiting
                if "429" in error_str or "quota" in error_str.lower():
                    # Stop retrying if we hit a hard quota limit
                    return "My AI quota limit has been reached. You have exceeded the free tier requests. Please wait a moment and try again."
                    
                if attempt == retries - 1:
                    return "I'm having trouble connecting to my AI brain right now. Please check my API key or connection."
        
        return "Sorry, I could not process that request."

    def _call_gemini(self, text: str) -> str:
        """Helper to call Gemini using the stateful chat session."""
        if not config.GEMINI_API_KEY or not self.chat_session:
            return "My Gemini API key is missing from the configuration."
        
        # Send message to the session (which handles tool calls automatically via enable_automatic_function_calling)
        response = self.chat_session.send_message(text)
        return response.text.strip()

    def _call_openai(self, text: str) -> str:
        """Helper to call OpenAI with manual memory buffer."""
        if not config.OPENAI_API_KEY or not self.openai_client:
            return "My OpenAI API key is missing from the configuration."
            
        self.openai_memory.append({"role": "user", "content": text})
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.openai_memory,
            max_tokens=250,
            timeout=15.0
        )
        
        ai_reply = response.choices[0].message.content.strip()
        self.openai_memory.append({"role": "assistant", "content": ai_reply})
        
        # Prevent memory explosion
        if len(self.openai_memory) > 15:
            # Keep system prompt, drop oldest pair
            self.openai_memory = [self.openai_memory[0]] + self.openai_memory[3:]
            
        return ai_reply

    def get_vision_response(self, image, text: str = "Describe this image.") -> str:
        """Process an image and text prompt using Gemini Vision capabilities."""
        if self.provider != "gemini":
            return "Vision capabilities are currently only supported with Gemini."
            
        if not config.GEMINI_API_KEY:
            return "My Gemini API key is missing from the configuration."
            
        try:
            # We use the generic generate_content since vision isn't natively stateful in the same way 
            # across all SDK versions, but passing it directly works beautifully.
            response = self.gemini_model.generate_content([image, text])
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error in Vision API: {error_str}")
            if "429" in error_str or "quota" in error_str.lower():
                return "My AI quota limit has been reached. Please wait a moment and try again."
            return "I encountered an error trying to see that image."
