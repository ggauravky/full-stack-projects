import os
import webbrowser
import datetime
import logging
import wikipedia
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CommandHandler:
    """Executes local system and internet commands safely."""
    
    def __init__(self):
        # Known commands mapping
        self.commands = {
            "open youtube": self.open_youtube,
            "open google": self.open_google,
            "open github": self.open_github,
            "open vs code": self.open_vscode,
            "time": self.tell_time,
            "tell time": self.tell_time,
            "date": self.tell_date,
            "tell date": self.tell_date,
            "open notepad": self.open_notepad,
            "open calculator": self.open_calculator,
            "tell me a joke": self.tell_joke,
            "joke": self.tell_joke
        }

    def execute_command(self, cmd_key: str, full_text: str) -> str:
        """Executes the mapped command."""
        try:
            logger.info(f"Executing command: {cmd_key}")
            
            # Special case for search
            if "search" in full_text and "google search" not in self.commands:
                # Basic search extraction
                query = full_text.split("search")[-1].strip()
                return self.search_google(query)
                
            # Special case for wikipedia
            if "wikipedia" in full_text:
                query = full_text.replace("wikipedia", "").strip()
                return self.search_wikipedia(query)
                
            # Special case for weather
            if "weather in" in full_text or "weather for" in full_text:
                city = full_text.split("in")[-1].strip() if "in" in full_text else full_text.split("for")[-1].strip()
                return self.get_weather(city)

            # Standard commands
            if cmd_key in self.commands:
                return self.commands[cmd_key]()
            
            return "Command recognized but not implemented."
        except Exception as e:
            logger.error(f"Error executing command '{cmd_key}': {e}")
            return f"I tried to execute '{cmd_key}', but encountered an error."

    def open_youtube(self) -> str:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube for you, sir."

    def open_google(self) -> str:
        webbrowser.open("https://www.google.com")
        return "Opening Google right away."

    def open_github(self) -> str:
        webbrowser.open("https://github.com")
        return "Opening GitHub now."

    def open_vscode(self) -> str:
        try:
            os.system("code")
            return "Opening Visual Studio Code."
        except Exception:
            return "I couldn't find VS Code in your system path."

    def tell_time(self) -> str:
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip('0')
        return f"The time is {time_str}."

    def tell_date(self) -> str:
        now = datetime.datetime.now()
        date_str = now.strftime("%B %d, %Y")
        return f"Today's date is {date_str}."

    def search_google(self, query: str) -> str:
        if not query:
            return "What would you like me to search for?"
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for {query}."

    def search_wikipedia(self, query: str) -> str:
        if not query:
            return "What would you like me to search Wikipedia for?"
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return "There are multiple results for this. Can you be more specific?"
        except Exception:
            return f"I couldn't find any Wikipedia article for '{query}'."

    def get_weather(self, city: str) -> str:
        if not city:
            return "For which city do you want the weather?"
        try:
            # wttr.in is a free API that doesn't need a key
            response = requests.get(f"https://wttr.in/{city}?format=%C+%t")
            if response.status_code == 200:
                return f"The current weather in {city} is {response.text}."
            return "I couldn't fetch the weather right now."
        except Exception:
            return "I'm having trouble connecting to the weather service."

    def open_notepad(self) -> str:
        try:
            os.system("notepad")
            return "Opening Notepad."
        except Exception:
            return "I couldn't find Notepad."

    def open_calculator(self) -> str:
        try:
            os.system("calc")
            return "Opening Calculator."
        except Exception:
            return "I couldn't find Calculator."

    def tell_joke(self) -> str:
        try:
            # Using Official Joke API
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            if response.status_code == 200:
                data = response.json()
                return f"{data['setup']} ... {data['punchline']}"
        except Exception:
            pass
        return "Why do programmers prefer dark mode? Because light attracts bugs!"

    def scrape_website(self, url: str) -> str:
        """Fetches the website URL and parses out the readable text content, removing all HTML."""
        if not url:
            return "Please provide a valid URL to scrape."
            
        try:
            # Add user-agent to bypass basic anti-scraping
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.extract()
                    
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                
                # Truncate to reasonable length for LLM context window limits
                if len(text) > 15000:
                     logger.warning(f"Scraped text truncated from {len(text)} to 15000 characters.")
                     text = text[:15000] + "... [Content Truncated due to length]"
                     
                return text
            return f"I couldn't access that website. Server returned status: {response.status_code}"
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return f"I encountered an error trying to read that website: {str(e)}"
