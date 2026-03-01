import os
import webbrowser
import datetime
import logging

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
            "tell date": self.tell_date
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
