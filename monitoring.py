# monitoring.py
# -------------
# This file monitors the quality of our RAG app's responses.
#
# What is hallucination?
# Even when we give an LLM context documents, it sometimes generates
# information that isn't actually in those documents. It "fills in the gaps"
# with plausible-sounding but unverified facts. This is called hallucination.
#
# How do we detect it?
# We use a technique called "LLM-as-judge": we send the answer AND the
# source documents back to Gemini and ask it to evaluate whether the answer
# is actually supported by the context. This is a common pattern in
# production RAG systems.

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)


def check_hallucination(answer, context_docs):
    """
    Ask Gemini to evaluate whether the generated answer is grounded in
    the source documents that were retrieved.

    Args:
        answer:       The answer our app generated.
        context_docs: The documents we retrieved and used as context.

    Returns:
        A dictionary with:
          - "verdict":     "GROUNDED", "PARTIAL", or "HALLUCINATED"
          - "is_grounded": True if verdict is GROUNDED, False otherwise
          - "warning":     A warning string to show the user (empty if grounded)
    """
    # TODO (Week 13): Implement LLM-as-judge hallucination detection. (Done)
    try:
        context = "\n\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(context_docs)])

        prompt = f"""You are evaluating whether an AI-generated answer is grounded in the provided source documents.

        SOURCE DOCUMENTS:
        {context}

        GENERATED ANSWER:
        {answer}

        Your task: decide if the answer is fully supported by the source documents.

        Respond with exactly one word:
        - GROUNDED: every claim in the answer is supported by the source documents.
        - PARTIAL: some claims are supported, but the answer also includes information not found in the sources.
        - HALLUCINATED: the answer contains claims that are unsupported by, or contradict, the source documents.

        Respond with only one word: GROUNDED, PARTIAL, or HALLUCINATED."""

        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.0},
        )

        verdict = response.text.strip().upper()

        validate_verdicts = ["GROUNDED", "PARTIAL", "HALLUCINATED"]
        if verdict not in validate_verdicts:
            verdict = "PARTIAL"

        warning = {
            "GROUNDED": "",
            "PARTIAL": "Note: This answer may include some information beyond the provided sources.",
            "HALLUCINATED": "Warning: This answer may contain information not found in the source documents.",
        }
        return {
            "verdict": verdict,
            "is_grounded": verdict == "GROUNDED",
            "warning": warning[verdict],
        }

    except Exception:
        return {"verdict": "UNKNOWN", "is_grounded": True, "warning": ""}

def calculate_confidence(distances):
    print("distances:", distances)
    """
    Convert ChromaDB similarity distances into a 0–1 confidence score.

    Args:
        distances: A list of L2 distance values from ChromaDB.
                   0.0 = identical vectors, 2.0 = completely different.

    Returns:
        A float between 0.0 (not confident) and 1.0 (very confident).
    """
    # TODO (Week 13): Implement the confidence score calculation. (Done)

    if not distances:
        return 0.0
    avg_distance = sum(distances) / len(distances)
    confidence = max(0.0, 1.0 - (avg_distance / 2.0))
    return round(confidence, 2)
