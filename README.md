# RAG Project

This repository contains my Retrieval-Augmented Generation (RAG) project for the GenAI Secure Coding course.

This project will be built incrementally each week.


## Git Commands Used So Far

- git clone  
- git status  
- git add  
- git commit  
- git push

## Week 4 Updates:

-added .env, rag_app.py, requirements.txt
-installed fastapi uvicorn python-dotenv google-generativeai  / Dependencies
The rag_app.py is the main backend of the rag project, it makes uvicorn run some could say.
Questions: Honestly I'm not too sure about the connection between files, I'm not sure if I messed up somewhere but uvicorn is running it's just not really connecting with the .env. Than again it might and I'm just expecting a different result.

## Week 5 Updates:

Fixed the mess I made in week 4 and now the server actually works properly, /health responds well and the AI responds to the hardcoded prompt. Right now /test-gemini starts with @app.get("/test-gemini") which tells FastAPI that whenever someone visits /test-gemini to run the function below. It then runs the function which calls Gemini through FastAPI servers, chooses the model, and sends the prompt. Gemini makes it's respone and the SDK turns it into an object, stored at response=, which is then printed to give the result. How would memory even work though, would I have to store it locally? --- Commit 2: I realized that I leaked the API key in the past, so I fixed it. Also added an example file for the .env.

## Week 6 Updates:

Changed the /test-gemini function so that it had a multi-step flow. First it would create an outline for how photosynthesis happens, then it would use that outline to give a brief explanation. I had to make it give short and simple responses because it kept making them way too long and having strange breaks in between parts. The steps are seperated so that it can give adequate explanation to each part described in the outline. The only challenge was giving a good enough prompt to not break the localhost. 

## Week 7 Updates:

Added a new endpoint /query that includes user input, user validation, and AI response validation. Input validation exists so that users are not able to send harmful prompts to the AI that may lead to security risks. Output validation exists as to avoid errors with AI responses such as hallucinations or security risks. A second AI model is used to review responses to fix any mistakes the first might make, improve it's response, and add a safety/quality filter. The endpoint I made this week doesn't have anything as advanced as that, only touching on basic validations. Also changed some of the previous code, making it easier to read and having a clearer flow. Had to add prints in the new endpoint function because google kept having internal errors and the prints can show whether it's an internal bug or a service issue.