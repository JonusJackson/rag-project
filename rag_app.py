from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from google import genai
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()

class QueryRequest(BaseModel):
    question: str 

def validate_user_input(text: str):
    if text is None or text.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Question is too short")

    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Question is too long")

def validate_model_output(text: str):
    if text is None or text.strip() == "":
        raise HTTPException(status_code=500, detail="AI returned an empty response")

    if len(text) < 10:
        raise HTTPException(status_code=500, detail="AI response is too short")

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY is missing.")
    sys.exit(1)
else:
    print("API KEY VALID")
    print("Starting Server...")

gemini_client = genai.Client(api_key=api_key)

def review_model_output(original_answer: str):
    review_prompt = f"""
You are reviewing an AI-generated response.

Your job:
- If the response meets the criteria below, improve it.
- Otherwise, return it unchanged.

Criteria:
- The response is unclear, incomplete, or poorly written (compared to an 8th grade reading level).

AI response to review:
{original_answer}
"""

    review_response = gemini_client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=review_prompt
    )
    return review_response.text

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test-gemini")
def test_gemini():

    step1_response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Create a short, very simple, and direct outline for photosynthesis."
    )

    outline = step1_response.text

    step2_response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Create a short, easily understandable paragraph about photosynthesis based on the following outline: {outline}"
    )

    instructions = step2_response.text

    return {
        "instructions": instructions
    }

@app.post("/query")
def query_ai(request: QueryRequest):
    validate_user_input(request.question)

    primary_response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=request.question
    )
    print("CALLING AI MODEL")
    #This print is to check if the validation works
    raw_answer = primary_response.text
    print("PRIMARY MODEL COMPLETE")
    validate_model_output(raw_answer)
    print("STARTING REVIEW")

    reviewed_answer = review_model_output(raw_answer)
    validate_model_output(reviewed_answer)

    return {
        "question": request.question,
        "answer": reviewed_answer
    }