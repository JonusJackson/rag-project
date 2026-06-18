from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from google import genai

app = FastAPI()

print("STARTING FILE")

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

print("API KEY VALUE:", api_key)

if not api_key:
    print("ERROR: GEMINI_API_KEY is missing.")
    sys.exit(1)

gemini_client = genai.Client(api_key=api_key)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test-gemini")
def test_gemini():

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in one sentence."
    )

    return {
        "response": response.text
    }