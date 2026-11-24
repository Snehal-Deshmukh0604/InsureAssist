
import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found. Check your .env file.")

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"


def test_gemini():
    response = client.models.generate_content(
        model=MODEL,
        contents="Introduce yourself as the AI assistant for an insurance claim processing system."
    )

    return response.text


if __name__ == "__main__":
    print("\n--- GEMINI CONNECTION TEST ---")
    print(test_gemini())
