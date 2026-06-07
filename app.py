"""Query interface — wires the Gradio UI to the RAG pipeline.

Student question -> generator.generate() (retrieve + grounded Groq answer)
-> answer + the source documents it was grounded in.

Styled with Colby College's official brand colors:
    Colby Blue  #002169  (primary)
    Bright Blue #5D8EE5  (accent)
    Blue Black  #1A2D38
    Colby Gray  #9EA9B0
"""

import html as _html

import gradio as gr

from generator import generate

# --- Colby brand palette -------------------------------------------------
COLBY_BLUE = "#002169"
BRIGHT_BLUE = "#5D8EE5"
BLUE_BLACK = "#1A2D38"
COLBY_GRAY = "#9EA9B0"

# A Gradio theme seeded with Colby Blue so primary controls inherit the brand.
theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#e6ebf3",
        c100="#c0cce0",
        c200="#94a8cb",
        c300="#6783b5",
        c400="#33599e",
        c500=COLBY_BLUE,
        c600="#001d5c",
        c700="#00184d",
        c800="#00133d",
        c900="#000d2b",
        c950="#00081c",
    ),
    secondary_hue=gr.themes.Color(
        c50="#eef4fc",
        c100="#d6e3f8",
        c200="#b3ccf2",
        c300="#8fb3ec",
        c400="#5D8EE5",
        c500=BRIGHT_BLUE,
        c600="#3f6fc4",
        c700="#3357a0",
        c800="#28457e",
        c900="#1f3560",
        c950="#142340",
    ),
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
)

CSS = f"""
.gradio-container {{
    background: #f4f7fb !important;
}}
/* Branded header banner */
#colby-header {{
    background: linear-gradient(135deg, {COLBY_BLUE} 0%, {BRIGHT_BLUE} 100%);
    color: #ffffff;
    padding: 28px 32px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0, 33, 105, 0.25);
}}
#colby-header h1 {{
    margin: 0 0 6px 0;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
}}
#colby-header p {{
    margin: 0;
    font-size: 1rem;
    opacity: 0.92;
    color: #eaf1ff;
}}
/* Primary "Ask" button */
#ask-btn {{
    background: {COLBY_BLUE} !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border-radius: 10px !important;
    transition: background 0.15s ease, transform 0.05s ease;
}}
#ask-btn:hover {{
    background: {BRIGHT_BLUE} !important;
}}
#ask-btn:active {{
    transform: translateY(1px);
}}
/* Conversation area — fills the page so the input sits at the bottom */
#chat-area {{
    min-height: 52vh;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 8px 4px 16px 4px;
}}
.chat-empty {{
    margin: auto;
    color: {COLBY_GRAY};
    font-size: 1rem;
    text-align: center;
}}
/* User's query — right-aligned bubble in Colby Blue */
.user-msg {{
    align-self: flex-end;
    max-width: 78%;
    background: {COLBY_BLUE};
    color: #ffffff;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    box-shadow: 0 2px 8px rgba(0, 33, 105, 0.18);
    line-height: 1.5;
}}
/* Generated response — left-aligned bubble with a faint Bright Blue tint */
.bot-msg {{
    align-self: flex-start;
    max-width: 82%;
    background: rgba(93, 142, 229, 0.15);
    color: {BLUE_BLACK};
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    box-shadow: 0 2px 8px rgba(93, 142, 229, 0.18);
    line-height: 1.65;
    font-size: 1.02rem;
}}
/* Processing indicator — animated dots in the response bubble's spot */
.bot-msg.processing {{
    display: flex;
    gap: 7px;
    align-items: center;
    width: fit-content;
}}
.bot-msg.processing .dot {{
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: {COLBY_BLUE};
    opacity: 0.35;
    animation: colby-blink 1.2s infinite ease-in-out;
}}
.bot-msg.processing .dot:nth-child(2) {{ animation-delay: 0.2s; }}
.bot-msg.processing .dot:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes colby-blink {{
    0%, 80%, 100% {{ opacity: 0.3; transform: translateY(0); }}
    40% {{ opacity: 1; transform: translateY(-3px); }}
}}
/* Sources note under each response */
.bot-sources {{
    align-self: flex-start;
    max-width: 82%;
    margin-top: -6px;
    padding: 0 6px;
    color: {COLBY_GRAY};
    font-size: 0.82rem;
    border-left: 3px solid {BRIGHT_BLUE};
    padding-left: 10px;
}}
/* Input row pinned to the bottom */
#input-row {{
    align-items: stretch;
    margin-top: 8px;
}}
#question-box span[data-testid="block-info"],
.gradio-container label span {{
    color: {COLBY_BLUE} !important;
    font-weight: 700 !important;
}}
#colby-footer {{
    text-align: center;
    color: {COLBY_GRAY};
    font-size: 0.85rem;
    margin-top: 18px;
}}
"""


EMPTY_STATE = (
    '<div id="chat-area"><div class="chat-empty">'
    "Ask a question below to get started 🐴</div></div>"
)


def _fmt(text):
    """Escape user/model text and preserve line breaks for HTML rendering."""
    return _html.escape(text).replace("\n", "<br>")


# Animated three-dot indicator shown where the response will appear.
PROCESSING_BUBBLE = (
    '<div class="bot-msg processing">'
    '<span class="dot"></span><span class="dot"></span><span class="dot"></span>'
    "</div>"
)


def render_chat(history, pending_question=None):
    """Render the conversation: each query right-aligned, each response
    left-aligned beneath it, with its sources. If `pending_question` is given,
    it is shown immediately with a processing indicator where the response
    will land."""
    if not history and pending_question is None:
        return EMPTY_STATE
    bubbles = []
    for turn in history:
        bubbles.append(f'<div class="user-msg">{_fmt(turn["question"])}</div>')
        bubbles.append(f'<div class="bot-msg">{_fmt(turn["answer"])}</div>')
        if turn["sources"]:
            bubbles.append(
                f'<div class="bot-sources">Retrieved from: '
                f'{_html.escape(turn["sources"])}</div>'
            )
    if pending_question is not None:
        bubbles.append(f'<div class="user-msg">{_fmt(pending_question)}</div>')
        bubbles.append(PROCESSING_BUBBLE)
    return f'<div id="chat-area">{"".join(bubbles)}</div>'


def handle_query(question, history):
    history = history or []
    if not question or not question.strip():
        yield render_chat(history), history, ""
        return

    # Step 1 — immediately echo the query and show the processing indicator
    # where the response will appear. State is unchanged; input is cleared.
    yield render_chat(history, pending_question=question), history, ""

    # Step 2 — generate the grounded answer.
    result = generate(question)

    # De-duplicate source files (a query often pulls several chunks from the
    # same document) while preserving retrieval order.
    seen = set()
    sources = []
    for chunk in result["chunks"]:
        if chunk["source"] not in seen:
            seen.add(chunk["source"])
            sources.append(chunk["source"])

    history = history + [
        {
            "question": question,
            "answer": result["answer"],
            "sources": ", ".join(sources),
        }
    ]
    yield render_chat(history), history, ""


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.HTML(
        """
        <div id="colby-header">
            <h1>🐴 The Unofficial Guide</h1>
            <p>Ask about freshman course selection at Colby — answers are grounded
            in upperclassmen's experiences and official guidance.</p>
        </div>
        """
    )
    # Conversation area at the top — grows to fill the page.
    chat = gr.HTML(EMPTY_STATE)
    history = gr.State([])

    # Input pinned to the bottom of the page.
    with gr.Row(elem_id="input-row"):
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. Should I take four classes my first semester?",
            elem_id="question-box",
            scale=5,
            container=False,
        )
        btn = gr.Button("Ask", elem_id="ask-btn", scale=1)

    gr.HTML(
        '<div id="colby-footer">Powered by upperclassmen wisdom · Go Mules!</div>'
    )

    btn.click(handle_query, inputs=[inp, history], outputs=[chat, history, inp])
    inp.submit(handle_query, inputs=[inp, history], outputs=[chat, history, inp])

if __name__ == "__main__":
    demo.launch(inbrowser=True, theme=theme, css=CSS)
