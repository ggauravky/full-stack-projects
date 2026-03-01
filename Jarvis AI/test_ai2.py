import sys
sys.path.append('backend')
from config import config
import google.generativeai as genai

genai.configure(api_key=config.GEMINI_API_KEY)
with open('models.txt', 'w') as f:
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(m.name + '\n')
    except Exception as e:
        f.write("Error: " + str(e))
