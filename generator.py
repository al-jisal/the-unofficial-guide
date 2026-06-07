"""Stage [5] Generation — Groq (llama-3.3-70b-versatile).

generate(query, n_results) retrieves the most relevant chunks and asks the LLM
to answer the student's question using only that context, citing sources.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retrieval import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You're the go-to assistant at Colby College when newly admitted students have questions concerning course selection.
Answer the students' question using only the context provided below. If the answer is not in the text, say so clearly
— do not guess or draw on outside knowledge. cite the documents answers are sourced from
"""

_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def build_user_prompt(query, chunks):
    """Construct the user message: retrieved chunks under Context, the
    student's question under Query. Each chunk is labelled with its source
    document so the model can cite it."""
    context = "\n\n".join(
        f"[{i}] (source: {c['source']})\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )
    return f"Context:\n{context}\n\nQuery:\n{query}"


def generate(query, n_results=3):
    """Retrieve context for `query` and generate a grounded, cited answer.

    Returns a dict: {"answer", "chunks"} where chunks are the retrieved
    sources used to ground the response.
    """
    chunks = retrieve(query, n_results=n_results)

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(query, chunks)},
        ],
    )

    return {"answer": response.choices[0].message.content, "chunks": chunks}


if __name__ == "__main__":
    sample_query = "If I took AP Computer Science, can I skip the intro CS courses?"
    result = generate(sample_query)

    print(f"Query: {sample_query}\n")
    print("Answer:")
    print(result["answer"])
    print("\nRetrieved sources:")
    for i, c in enumerate(result["chunks"], 1):
        print(f"  [{i}] {c['source']} (distance={c['distance']:.4f})")
