# JarvisLite

A complete, production-ready, AI-powered voice and chat assistant.

## Tech Stack
- Python 3.10+, FastAPI, Uvicorn
- SpeechRecognition, Pyttsx3, PyAudio
- OpenAI / Gemini API
- HTML, CSS, Vanilla JS

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Configure Environment
1. Clone or download this project.
2. Navigate to the project folder (`Jarvis AI` or wherever you placed the files).
3. Rename `.env.example` to `.env`.
4. Add your preferred API key (Gemini or OpenAI) in the `.env` file.
5. Set `AI_PROVIDER` in `.env` to either `gemini` or `openai`.

### 3. Install Dependencies
Open a terminal in the project directory and run:

```bat
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

> **Note on PyAudio**: If PyAudio fails to install on Windows, you may need to install Windows Build Tools or download a pre-compiled `.whl` file from [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it using `pip install <filename.whl>`. Alternatively, use `pipwin`:
> ```bat
> pip install pipwin
> pipwin install pyaudio
> ```

### 4. Running the Assistant
You can simply double-click the `run.bat` file in the main folder to:
1. Start the FastAPI backend server.
2. Automatically open the frontend UI in your default web browser.

Or manually:
1. Start backend: `cd backend` then `uvicorn main:app --reload`
2. Open `frontend/index.html` in your browser.

## Features
- **Voice & Text Chat**: Speak or type to interact with the assistant.
- **Smart Intent Routing**: Automatically decides if you are asking a general question (sent to AI) or giving a system command.
- **System Commands**: Can open websites (Google, YouTube, GitHub, VS Code), tell time, and search.
- **Self-Healing**: Robust error handling, retries, API timeouts, and fallback text-to-speech logic.
