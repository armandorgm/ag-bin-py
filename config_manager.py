import os
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, env_filename="secrets.env"):
        load_dotenv(env_filename)
        self.api_key = os.getenv("API_KEY")
        self.secret = os.getenv("SECRET")

    def get_api_credentials(self):
        return self.api_key, self.secret