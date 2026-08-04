# workflow.py
# -----------
# This file improves retrieval quality using multi-step AI workflows.
#
# The retrieval quality problem:
# The quality of a RAG answer depends heavily on what gets retrieved.
# And what gets retrieved depends on how similar the query embedding is
# to the document embeddings. If the user's query is vague or uses
# different vocabulary than the documents, retrieval suffers.
#
# Two solutions:
#
# 1. Query rewriting: Use an LLM to rewrite the user's question into a
#    version that will produce a better embedding for semantic search.
#    "tell me about that database thing" → "How do relational databases
#    store and query structured data using SQL?"
#
# 2. Query decomposition: Some questions are actually multiple questions.
#    Split them up and retrieve separately, then combine the results.
#    This is called "multi-hop retrieval."

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL
from embeddings import embed_text
from vector_store import query_similar

_client = genai.Client(api_key=GEMINI_API_KEY)


def rewrite_query(original_query, conversation_context=""):
    """
    Use Gemini to rewrite the user's query for better semantic search.

    Args:
        original_query:      The user's original question.
        conversation_context: Recent conversation history (helps resolve
                              pronouns like "it" or "that").

    Returns:
        A rewritten query string, or the original if rewriting fails.
    """
    # TODO (Week 15): Implement query rewriting using Gemini. (Done)
    try:
        if conversation_context:
            prompt = (
                f"Rewrite the following question to be more specific and technical, "
                f"suitable for semantic search. Context: {conversation_context}\n\n"
                f"Question: {original_query}"
            )
        else:
            prompt = (
                f"Rewrite the following question to be more specific and technical, "
                f"suitable for semantic search. Question: {original_query}"
            )

        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(temperature=0.1),
        )

        rewritten = response.text.strip()
        if rewritten and len(rewritten) < 500:
            return rewritten
        return original_query

    except Exception:
        return original_query

def decompose_query(query):
    """
    Break a complex multi-part question into simpler sub-questions.

    Args:
        query: A question that may contain multiple distinct topics.

    Returns:
        A list of sub-question strings (up to 3), or [query] if it's
        already simple or if decomposition fails.
    """
    # TODO (Week 15): Implement query decomposition using Gemini. (Done)
    try:
        prompt = (
            f"If this question covers multiple topics, split it into 2-3 simpler "
            f"sub-questions; otherwise return it as-is. Question: {query}"
        )
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(temperature=0.1),
        )
        sub_queries = response.text.strip().split("\n")
        sub_queries = [q.strip() for q in sub_queries if len(q.strip()) > 5]

        if not sub_queries:
            return [query]

        return sub_queries[:3]
    except Exception:
        return [query]

def multi_hop_retrieve(query, n_per_hop=2):
    """
    Retrieve documents for each sub-question and combine the results.

    Steps:
      1. Decompose the query into sub-questions
      2. Embed and search for each sub-question independently
      3. Combine results, removing duplicates

    Args:
        query:     The original complex query.
        n_per_hop: Documents to retrieve per sub-question.

    Returns:
        A deduplicated list of relevant document strings.
    """
    sub_queries = decompose_query(query)

    all_documents = []
    seen_documents = set()

    for sub_query in sub_queries:
        embedding = embed_text(sub_query)
        results = query_similar(embedding, n_per_hop)

        for doc in results["documents"][0]:
            if doc not in seen_documents:
                seen_documents.add(doc)
                all_documents.append(doc)

    return all_documents
