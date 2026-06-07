# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Incoming freshmen course selection experience at Colby College. This is a knowledge base of
upperclassmen's experiences with their freshman year course selection period — the good and the
bad. Unlike official sites that state only facts, this knowledge base captures the hustle of
students and the strategies they found helpful. That knowledge is scattered across different
platforms like Reddit, so this project centralizes it.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Quora — What are some of the best courses to take for freshman year? | Q&A forum thread | [Link to source](https://www.quora.com/Colby-College-What-are-some-of-the-best-courses-to-take-for-freshman-year) |
| 2 | Reddit r/Colby — If I have 32 credits heading into my freshman year, does that mean I could graduate a year early? | Forum thread | [Link to source](https://www.reddit.com/r/Colby/comments/15auahz/if_i_have_32_credits_heading_into_my_freshman/) |
| 3 | Reddit r/Colby — Any interesting course recommendation for Math and CS? | Forum thread | [Link to source](https://www.reddit.com/r/Colby/comments/n4v3ml/choosing_courses_for_freshman_year/) |
| 4 | Reddit r/Colby — Tips to Prepare for Freshman Year | Forum thread | [Link to source](https://www.reddit.com/r/Colby/comments/13r76l1/tips_to_prepare_for_freshman_year/) |
| 5 | Reddit r/Colby — Would 5 courses (20 credit) be too much for first semester? | Forum thread | [Link to source](https://www.reddit.com/r/Colby/comments/14cs293/would_5_courses_20_credit_be_too_much_for_first/) |
| 6 | Reddit r/Colby — Understanding Course Requirement | Forum thread | [Link to source](https://www.reddit.com/r/Colby/comments/1df2kua/help_understanding_the_course_taking_requirments/) |
| 7 | Reddit r/Colby — Questions about first-year advising | Forum thread | [Link to source](https://www.reddit.com/r/Colby/comments/1dah8fs/questions_about_firstyear_advising/) |
| 8 | Colby — Diversity and Distribution Areas Requirements | Official page | [Link to source](https://www.colby.edu/academics/first-year-advising/colbys-liberal-arts-curriculum/) |
| 9 | Colby — Advising: what to expect and how to prepare | Official page | [Link to source](https://www.colby.edu/academics/first-year-advising/advising-what-to-expect-and-how-to-prepare/) |
| 10 | Colby — Advice from Departments | Official page | [Link to source](https://www.colby.edu/academics/first-year-advising/advice-from-departments/) |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
Paragraph-level chunking (~100 tokens). The document text is stepped through paragraph by paragraph.

**Overlap:**
No overlap.

**Why these choices fit your documents:**
In the documents, each paragraph expresses a complete thought, responding to a specific question.
The paragraphs are of moderate size (3–6 sentences), resulting in a chunk size of about 100 tokens.
Because each paragraph already stands as a self-contained unit, no overlap is needed between chunks.

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2 via sentence-transformers. Top-k retrieval is set to 3, since the top 3 most
relevant chunks result in less noise in generated responses.

**Production tradeoff reflection:**
In production, a more complex model (e.g. OpenAI's `text-embedding-3-large`) would produce more
accurate results. However, that would come at a cost and add latency from network calls.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The model receives this system message, which constrains it to the retrieved context and forbids
outside knowledge:

> You're the go-to assistant at Colby College when newly admitted students have questions concerning
> course selection. Answer the students' question using only the context provided below. If the answer
> is not in the text, say so clearly — do not guess or draw on outside knowledge. cite the documents
> answers are sourced from

The grounding is reinforced structurally by the user message, which is built in a fixed
`Context:` / `Query:` shape. Each retrieved chunk is inserted under `Context:` and the student's
question under `Query:`, so the model always sees the evidence and the question as separate, clearly
delimited blocks:

```
Context:
[1] (source: reddit_thread_1.txt)
<chunk text>

[2] (source: colby.txt)
<chunk text>

Query:
<student question>
```

Only the top-k=3 chunks are passed, so low-relevance retrieval results never reach the model. In
practice this works: when the answer is genuinely absent from the retrieved chunks (e.g. the easiest-
classes list), the model says the information is not available rather than fabricating one.

**How source attribution is surfaced in the response:**
Each chunk is labelled `[n] (source: <filename>)` in the context, so the model cites the originating
document inline in its answer (e.g. "(source: reddit_thread_1.txt)"). The source travels with each
chunk because `retrieve()` returns a `source` field (stored as ChromaDB metadata at ingest time). The
Gradio interface also renders a separate "Retrieved from" panel listing the de-duplicated source
documents used to ground the response.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Do I have to take a language class in my freshman year? | Yes, all freshmen are required to take three semesters of a language. Students that speak a foreign language can test out. | Correctly reported the 3-semester language requirement and the test-out option, but hedged on the freshman-year timing — said the context only states it must be done before graduation. | Relevant | Partially accurate |
| 2 | Which distribution requirements must be completed in my freshman year | First-year students are required to take a writing-intensive course (W1) and should begin work on their foreign language requirement. | Said no distribution requirements must be completed in freshman year, citing a student chunk that requirements just need finishing before graduation. Missed the W1 / foreign-language first-year requirement. | Partially relevant | Inaccurate |
| 3 | What are the easiest classes at Colby? | Logic 1, CS152, MA130, EC133, SP125, MA274 | Said the easiest classes are not stated in the context — it retrieved the matching *question* ("What are the easiest classes you've taken at Colby?") but not the *answer* paragraph listing the courses. | Partially relevant | Inaccurate |
| 4 | If I took AP Computer Science, can I skip the intro CS courses? | Yes — with a high enough AP CS score you can place out of CS151/152 and go straight to CS231. No certificate needed; email the CS chair and complete a quick placement test. | Correctly answered yes, you can likely place out of CS151/152 with AP CS, citing reddit_thread_1.txt. Did not surface the CS231 / email-the-chair / placement-test details. | Relevant | Accurate |
| 5 | Why do students recommend signing up for 5 classes and then dropping to 4? | Because Colby has a really long drop period, so students register for 5 classes and drop down to 4 if the workload feels too heavy. | Surfaced the correct reasoning (try 5, drop if too heavy) from the right chunks, but framed it cautiously as "not explicitly stated" and under-emphasized the long drop period as the reason. | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"What are the easiest classes at Colby?" (test question 3). Expected answer: Logic 1, CS152, MA130,
EC133, SP125, MA274.

**What the system returned:**
The system said the easiest classes are not stated in the provided context. Its top retrieval was a
near-perfect match (cosine distance 0.039) — but the chunk it matched was the *question*
"What are the easiest classes you've taken at Colby?", not the reply that actually lists the courses.
With no answer text in the context, the model correctly refused to guess and reported the
information as unavailable.

**Root cause (tied to a specific pipeline stage):**
Chunking (Stage 2). The corpus stores a forum question and its answer as two separate paragraphs, and
the paragraph-based, zero-overlap strategy splits them into two independent chunks. The question
paragraph ("What are the easiest classes...") embeds almost identically to the user's query, so it
dominates retrieval, while the answer paragraph (the list of courses) embeds differently and never
enters the top-k=3. Retrieval then returns the half of the conversation that restates the question
and omits the half that answers it — so generation had no grounding to work from. The grounding
itself behaved correctly; the failure is upstream, in how the document was divided.

**What you would change to fix it:**
Make a chunk carry both the question and its answer instead of splitting them. Options, roughly in
order of effort: (1) preprocess the Reddit/Quora dumps so each question is merged with the reply
paragraph(s) beneath it into a single chunk; (2) add a small inter-paragraph overlap so a chunk
includes the start of the following paragraph; or (3) retrieve a larger top-k and include the
neighboring chunk (by `chunk_id` index) of each hit, so an answer paragraph is pulled in alongside
its matched question. Option (1) targets this failure most directly given the clear question/answer
structure of these sources.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
