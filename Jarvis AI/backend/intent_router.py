import logging
from typing import Dict, Any
from ai_engine import AIEngine
from command_handler import CommandHandler

logger = logging.getLogger(__name__)

class IntentRouter:
    """Routes incoming text to either the OS Command Handler or the AI Engine."""
    
    def __init__(self, ai_engine: AIEngine, command_handler: CommandHandler):
        self.ai_engine = ai_engine
        self.command_handler = command_handler
        
        # Define keywords that trigger a local command instead of AI
        self.command_keywords = [
            "open youtube",
            "open google",
            "open github",
            "open vs code",
            "tell time",
            "time",
            "tell date",
            "date",
            "search"
        ]

    def route_intent(self, text: str) -> Dict[str, Any]:
        """
        Determines the intent of the text.
        Returns a dictionary with 'response' and 'source' ('command' or 'ai').
        """
        text_lower = text.lower().strip()
        
        # 1. Check for command intention
        matched_cmd = None
        for cmd in self.command_keywords:
            if text_lower.startswith(cmd) or cmd == text_lower:
                matched_cmd = cmd
                break
            # Allow "google search <query>" or just "search <query>"
            if "search" in text_lower and text_lower.startswith(("google search", "search")):
                matched_cmd = "search"
                break
                
        if matched_cmd:
            logger.info(f"Intent routed to Command Handler (Trigger: {matched_cmd})")
            response = self.command_handler.execute_command(matched_cmd, text_lower)
            return {"response": response, "source": "command"}

        # 2. Fallback to AI intention
        logger.info("Intent routed to AI Engine")
        # Ensure it doesn't block FastAPI thread if it was async, but we are using sync requests wrapped in thread logic or directly
        response = self.ai_engine.get_ai_response(text)
        return {"response": response, "source": "ai"}
