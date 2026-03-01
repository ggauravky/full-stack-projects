import sys
sys.path.append('backend')
from config import config
import google.generativeai as genai

print("AI_PROVIDER loaded:", config.AI_PROVIDER)
print("Key length:", len(config.GEMINI_API_KEY) if config.GEMINI_API_KEY else 0)

try:
    if config.GEMINI_API_KEY:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test. Reply with 'Success'.")
        print("API Response:", response.text)
    else:
        print("No GEMINI_API_KEY found.")
except Exception as e:
    import traceback
    traceback.print_exc()
