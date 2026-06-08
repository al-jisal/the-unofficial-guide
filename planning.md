# Project 1 Planning: The Unofficial Guide

---

## Domain

Incoming Freshmen Course Selection Experience

This is a knowledge base of upperclassmen's experiences with their freshman year course selection period: 
the good and the bad. Unlike official sites that state only facts, this knowledge base captures the hustle
of students and the strategies they found helpful. It is, however, scattered across different platforms like Reddit, so it's important that this project centralizes it.

---

## Documents


| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Quora | What are some of the best courses to take for freshman year? | [Link to source](https://www.quora.com/Colby-College-What-are-some-of-the-best-courses-to-take-for-freshman-year) |
| 2 | Reddit | If I have 32 credits heading into my freshman year, does that mean I could graduate a year early? | [Link to source](https://www.reddit.com/r/Colby/comments/15auahz/if_i_have_32_credits_heading_into_my_freshman/ ) |
| 3 | Reddit | Any I interesting course recommendation for Math and CS? | [Link to source](https://www.reddit.com/r/Colby/comments/n4v3ml/choosing_courses_for_freshman_year/) |
| 4 | Reddit | Tips to Prepare for Freshman Year | [Link to source](https://www.reddit.com/r/Colby/comments/13r76l1/tips_to_prepare_for_freshman_year/) |
| 5 | Reddit | Would 5 courses (20 credit) be too much for first semester? | [Link to source](https://www.reddit.com/r/Colby/comments/14cs293/would_5_courses_20_credit_be_too_much_for_first/) |
| 6 | Reddit | Understanding Course Requirement | [Link to source](https://www.reddit.com/r/Colby/comments/1df2kua/help_understanding_the_course_taking_requirments/) |
| 7 | Reddit | Questions about first-year advising | [Link to source](https://www.reddit.com/r/Colby/comments/1dah8fs/questions_about_firstyear_advising/) |
| 8 | Colby | Diversity and Distribution Areas Requirements | [Link to source](https://www.colby.edu/academics/first-year-advising/colbys-liberal-arts-curriculum/) |
| 9 | Colby | Advicing: what to expect and how to prepare | [Link to source](https://www.colby.edu/academics/first-year-advising/advising-what-to-expect-and-how-to-prepare/) |
| 10 | Colby | Advice from Departments | [Link to resource](https://www.colby.edu/academics/first-year-advising/advice-from-departments/) |

---

## Chunking Strategy

Paragraph-based splitting. The documents texts are stepped through in paragraphs, as a result
there is no overlap between chunks.

**Chunk size:**
Paragraph-level chunking (variable size; averages ~85 tokens, most paragraphs 3–6 sentences)

**Overlap:**
No overlap

**Reasoning:**
In the document, each paragraph expresses a complete thought, responding to a specific question
The paragraphs are of moderate sizes (3 - 6 sentences), resulting in a chunk size of about 85 tokens on average

---

## Retrieval Approach

**Embedding model:**
all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**
3
Top 3 most relevant chunks result in less noise in generated responses

**Production tradeoff reflection:**
In production, a more complex model (e.g. OpenAI's `text-embedding-3-large`) would produce more accurate results
However, that would come at a cost and add latency from network calls

---

## Evaluation Plan


| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Do I have to take a language class in my freshman year? | Yes, all freshmen are required to take three semesters of a language. Students that speak a foreign language can test out |
| 2 | Which distribution requirements must be completed in my freshman year | First-year students are required to take a writing-intensive course (W1) and should begin work on their foreign language requirement. |
| 3 | What are the easiest classes at Colby? | Logic 1, CS152, MA130, EC133, SP125, MA274  |
| 4 | If I took AP Computer Science, can I skip the intro CS courses? | Yes — with a high enough AP CS score you can place out of CS151/152 and go straight to CS231. No certificate is needed; you email the CS department chair and complete a quick placement test. |
| 5 | Why do students recommend signing up for 5 classes and then dropping to 4? | Because Colby has a really long drop period, so students register for 5 classes and drop down to 4 if the workload feels too heavy. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Retrieval of chunks which are unrelated to students questions

2. System responding confidently but wrongly to students questions

---

## Architecture

```
Student query
    │
    ▼
[1] Document Ingestion             ──► Rule book text is chunked and stored once at startup
    │
    ▼
[2] Chunking                       ──► recursive chunking: paragraph-based
    │
    ▼
[3] Embedding + Vector Store       ──► all-MiniLM-L6-v2 + chromaDB
    │
    ▼
[4] Retrieval                      ──► chromaDB
    │
    ▼
[5] Generation                     ──► Groq( llama-3.3-70b-versatile )
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
```
I'll ask claude to write the following functions in a file named ingest.py:

load_documents() -> loads all .txt files from the documents folder. it returns a list of dictionaries, where each dictionary corresponds to each .txt file. Each dictionary has the following keys: "filename" and "text"

chunk_documents(text, filename) -> chunks `text` using my Chunking Strategy section. it returns a list of dictionaries each with keys: "text"(the chunk text) and chunk_id(a unique identifier, e.g `filename`_1)
```

**Milestone 4 — Embedding and retrieval:**

```
I'll instruct claude that using the Embedding + vector store from the Architecture section in the plannin.md, implement the following functions in a file called retrieval.py:

embed_store(chunks) -> embeds each chunk using all-MiniLM-L6-v2 model, stores the text and the chunk id in a chromaDB

retrieve.py(query, n_results) -> retrieves n_results relevant chunks for the user's query, returns a list of dicts, each with the text and the distance (the similarity score (lower = more similar for cosine))
```

**Milestone 5 — Generation and interface:**
```
I'll ask cluade to implement the following using part 5 of the architecture in generator.py:

generate a response to the student's query using groq. Use the string below as the system input
"""
You're the go-to assistant at Colby College when newly admitted students have questions concerning course selection.
Answer the students' question using only the context provided below. If the answer is not in the text, say so clearly
— do not guess or draw on outside knowledge. cite the documents answers are sourced from
""" 

For the user input, construct it following the instructions below:
"""
Context:
    add the retrieved chunks under this section
Query:
    add the student's question under this section
"""
```
