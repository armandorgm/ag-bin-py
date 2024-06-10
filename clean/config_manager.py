import os
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, env_filename="secrets.env"):
        load_dotenv(env_filename)
        self.api_key = os.getenv("API_KEY")
        self.secret = os.getenv("SECRET")
        self.api_test_key = os.getenv("TEST_API_KEY")
        self.api_test_secret = os.getenv("TEST_SECRET")

    def get_api_credentials(self):
        return self.api_key, self.secret
    
    def get_api_test_credentials(self):
        return self.api_test_key, self.api_test_secret
