import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Internal imports
from config import config
from intent_router import IntentRouter
from ai_engine import AIEngine
from command_handler import CommandHandler
from speech_engine import SpeechEngine
from tts_engine import TTSEngine

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title=f"{config.ASSISTANT_NAME} API")

# Setup CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
ai_engine = AIEngine()
command_handler = CommandHandler()
intent_router = IntentRouter(ai_engine=ai_engine, command_handler=command_handler)
speech_engine = SpeechEngine()
tts_engine = TTSEngine()

# Models
class ChatRequest(BaseModel):
    text: str

class ResponseModel(BaseModel):
    status: str
    response: str
    source: str  # e.g., 'ai' or 'command'
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Startup self-check."""
    logger.info(f"Starting {config.ASSISTANT_NAME} Backend")
    config.validate()
    logger.info("Initializing background TTS engine")
    # TTS engine init check
    tts_engine.speak(f"System initialized. Good to go.", block=False)
    
@app.get("/health")
def health_check():
    """Health check endpoint to ensure server is running smoothly."""
    return {"status": "ok", "assistant": config.ASSISTANT_NAME}

@app.get("/favicon.ico", status_code=204)
def favicon():
    """Dummy favicon endpoint to prevent 404 errors."""
    return {}

@app.post("/chat", response_model=ResponseModel)
def chat_endpoint(request: ChatRequest):
    """Handles text input and routes it accordingly."""
    try:
        user_text = request.text.strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="Empty request text.")
            
        logger.info(f"User input: {user_text}")
        
        # Route intent
        result = intent_router.route_intent(user_text)
        
        # Optionally speak response in background (if configured to speak all responses)
        tts_engine.speak(result["response"], block=False)

        return ResponseModel(
            status="success",
            response=result["response"],
            source=result["source"]
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ResponseModel(
            status="error",
            response="I encountered an internal error processing your request.",
            source="system",
            error=str(e)
        )

@app.post("/voice", response_model=ResponseModel)
def voice_endpoint():
    """Listens for voice, converts to text, and routes it."""
    try:
        logger.info("Listening for voice input...")
        text = speech_engine.listen()
        
        if not text:
            return ResponseModel(
                status="success",
                response="I couldn't hear you properly. Please try again.",
                source="system"
            )
            
        logger.info(f"Recognized Voice: {text}")
        
        # Route recognized text
        result = intent_router.route_intent(text)
        
        # Speak the response
        tts_engine.speak(result["response"], block=False)
        
        return ResponseModel(
            status="success",
            response=result["response"],
            source=result["source"]
        )
    except Exception as e:
        logger.error(f"Error in voice endpoint: {e}")
        return ResponseModel(
            status="error",
            response="Voice processing failed.",
            source="system",
            error=str(e)
        )
