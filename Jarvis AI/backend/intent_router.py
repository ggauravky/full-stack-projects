import logging
from typing import Dict, Any
from ai_engine import AIEngine
from command_handler import CommandHandler

logger = logging.getLogger(__name__)

class IntentRouter:
    """Routes incoming text to either fast OS commands or the Advanced AI Agent."""
    
    def __init__(self, ai_engine: AIEngine, command_handler: CommandHandler):
        self.ai_engine = ai_engine
        self.command_handler = command_handler
        
        # FAST-TRACK OS COMMANDS ONLY.
        # We removed weather, wikpedia, time etc., because Gemini Native Tools handle them autonomously now.
        # We only keep commands that do localized PC actions that don't need AI context generation.
        self.os_fast_commands = [
            "open youtube",
            "open google",
            "open github",
            "open vs code",
            "open notepad",
            "open calculator"
        ]

    def route_intent(self, text: str) -> Dict[str, Any]:
        """
        Determines the intent of the text.
        Returns a dictionary with 'response' and 'source' ('command' or 'ai').
        """
        text_lower = text.lower().strip()
        
        # 1. Check for FAST OS Actions
        matched_cmd = None
        for cmd in self.os_fast_commands:
            if text_lower.startswith(cmd) or cmd == text_lower:
                matched_cmd = cmd
                break
                
        if matched_cmd:
            logger.info(f"Intent fast-tracked to OS Handler (Trigger: {matched_cmd})")
            response = self.command_handler.execute_command(matched_cmd, text_lower)
            return {"response": response, "source": "command"}

        # 2. Forward to Autonomous AI Agent
        # The AI Engine now has memory and native tools. 
        # If the user asks for the weather, the AI Engine will autonomously trigger the get_weather() Python function!
        logger.info("Intent forwarded to Autonomous AI Agent")
        response = self.ai_engine.get_ai_response(text)
        return {"response": response, "source": "ai"}
