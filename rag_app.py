print("STARTING FILE")

from dotenv import load_dotenv
import os
import sys

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API KEY VALUE:", api_key)

if not api_key:
    print("ERROR: GEMINI_API_KEY is missing.")
    sys.exit(1)

print("SUCCESS")