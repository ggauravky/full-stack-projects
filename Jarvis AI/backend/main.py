import logging
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sse_starlette.sse import EventSourceResponse
import asyncio
import io
import PIL.Image

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
command_handler = CommandHandler()
ai_engine = AIEngine(command_handler=command_handler)
intent_router = IntentRouter(ai_engine=ai_engine, command_handler=command_handler)
speech_engine = SpeechEngine()
tts_engine = TTSEngine()

# Models
class ChatRequest(BaseModel):
    text: str

# Global Event Queue for SSE
main_loop = None
event_queue = asyncio.Queue()

async def event_generator():
    """Generator that yields Server-Sent Events to the connected client."""
    while True:
        # Wait for a new message to be placed in the queue
        message = await event_queue.get()
        yield message

class ResponseModel(BaseModel):
    status: str
    response: str
    source: str  # e.g., 'ai' or 'command'
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Startup self-check."""
    global main_loop
    main_loop = asyncio.get_running_loop()
    
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

@app.get("/events")
async def sse_events():
    """SSE endpoint for pushing asynchronous AI responses to the frontend."""
    return EventSourceResponse(event_generator())

def process_chat_background(user_text: str):
    """Background task to fetch response and push to SSE queue."""
    try:
        # Route intent
        result = intent_router.route_intent(user_text)
        
        # Speak the response
        tts_engine.speak(result["response"], block=False)
        
        # Send payload to frontend via SSE
        import json
        payload = {
            "status": "success",
            "response": result["response"],
            "source": result["source"]
        }
        asyncio.run_coroutine_threadsafe(event_queue.put(json.dumps(payload)), loop=main_loop)
    except Exception as e:
        logger.error(f"Error in background chat: {e}")
        error_payload = {
            "status": "error",
            "response": "I encountered an internal error processing your request in the background.",
            "source": "system",
            "error": str(e)
        }
        asyncio.run_coroutine_threadsafe(event_queue.put(json.dumps(error_payload)), loop=main_loop)

@app.post("/chat")
def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """Accepts text and offloads the processing to a background task."""
    """Handles text input and routes it accordingly."""
    try:
        user_text = request.text.strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="Empty request text.")
            
        logger.info(f"User input received: {user_text}")
        
        # Offload to background Task
        background_tasks.add_task(process_chat_background, user_text)

        # Immediately return acceptance so the UI doesn't freeze
        return {"status": "accepted", "message": "Working on it..."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def process_voice_background(recognized_text: str):
    """Background task to handle verified voice text and push to SSE."""
    try:
        # Route recognized text
        result = intent_router.route_intent(recognized_text)
        
        # Speak the response
        tts_engine.speak(result["response"], block=False)
        
        # Send payload
        import json
        payload = {
            "status": "success",
            "response": result["response"],
            "source": result["source"]
        }
        asyncio.run_coroutine_threadsafe(event_queue.put(json.dumps(payload)), loop=main_loop)
    except Exception as e:
        logger.error(f"Error in background voice processing: {e}")
        error_payload = {
            "status": "error",
            "response": "Voice processing failed.",
            "source": "system",
            "error": str(e)
        }
        asyncio.run_coroutine_threadsafe(event_queue.put(json.dumps(error_payload)), loop=main_loop)

@app.post("/voice")
def voice_endpoint(background_tasks: BackgroundTasks):
    """Listens for voice synchronously, then offloads AI gen to background."""
    """Listens for voice, converts to text, and routes it."""
    try:
        logger.info("Listening for voice input...")
        # Speech engine is synchronous and blocking
        text = speech_engine.listen()
        
        if not text:
            return {"status": "error", "message": "I couldn't hear you properly. Please try again."}
            
        logger.info(f"Recognized Voice: {text}")
        
        # Offload AI to background so we don't block
        background_tasks.add_task(process_voice_background, text)
        
        return {"status": "accepted", "message": "Working on it...", "recognized_text": text}
    except Exception as e:
        logger.error(f"Error accepting voice endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def process_vision_background(pil_img, prompt_text: str):
    """Background task to handle vision API calls."""
    try:
        # Pass directly to AI Engine vision capabilities
        result_text = ai_engine.get_vision_response(pil_img, prompt_text)
        
        # Speak response
        tts_engine.speak(result_text, block=False)
        
        import json
        payload = {
            "status": "success",
            "response": result_text,
            "source": "ai"
        }
        asyncio.run_coroutine_threadsafe(event_queue.put(json.dumps(payload)), loop=main_loop)
    except Exception as e:
        logger.error(f"Error in vision background: {e}")
        error_payload = {
            "status": "error",
            "response": "I couldn't process that image.",
            "source": "system",
            "error": str(e)
        }
        asyncio.run_coroutine_threadsafe(event_queue.put(json.dumps(error_payload)), loop=main_loop)

@app.post("/vision")
async def vision_endpoint(background_tasks: BackgroundTasks, image: UploadFile = File(...), text: Optional[str] = Form(None)):
    """Handles an image upload along with an optional query."""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File uploaded is not an image.")
            
        logger.info(f"Received Vision Request. Image: {image.filename}, Text: {text}")
        
        # Read the image file into memory
        contents = await image.read()
        pil_img = PIL.Image.open(io.BytesIO(contents))
        
        # Determine the prompt
        prompt_text = text if text else "Describe this image."
        
        # Offload logic to background
        background_tasks.add_task(process_vision_background, pil_img, prompt_text)
        
        return {"status": "accepted", "message": "Analyzing image..."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting vision endpoint request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
