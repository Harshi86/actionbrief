import json
import os
from datetime import datetime

import streamlit as st
from openai import OpenAI


st.set_page_config(page_title="ActionBrief", page_icon="✳️", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.04em; }
    .stApp { background: #f6f5f1; }
    [data-testid="stSidebar"] { background: #17241f; }
    [data-testid="stSidebar"] * { color: #edf3e9; }
    .hero { padding: 1.4rem 0 1rem; }
    .eyebrow { color: #527361; font-size: .78rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .hero h1 { font-size: clamp(2.7rem, 6vw, 4.7rem); line-height: .98; margin: .45rem 0 .8rem; color: #17241f; }
    .hero p { color: #66736b; font-size: 1.08rem; max-width: 700px; }
    .pill { display: inline-block; padding: .3rem .65rem; background: #e3eee4; color: #345c46; border-radius: 999px; font-size: .75rem; font-weight: 700; }
    div[data-testid="stForm"] { background: white; padding: 1rem 1.1rem; border: 1px solid #e5e4dc; border-radius: 18px; }
    div.stButton > button[kind="primary"] { background: #d5f26b; color: #17241f; border: 0; border-radius: 11px; font-weight: 700; }
    div.stButton > button[kind="primary"]:hover { background: #c6e75b; color: #17241f; }
    .small-note { color: #7a827c; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_MODEL = "nvidia/Nemotron-3.5-Super-VL"


def get_server_settings() -> tuple[str, str]:
    """Read deployment credentials without passing them into a browser widget."""
    try:
        secret_key = st.secrets.get("NEBIUS_API_KEY", "")
        secret_model = st.secrets.get("NEBIUS_MODEL", "")
    except Exception:
        # Streamlit raises when no secrets.toml exists locally.
        secret_key = ""
        secret_model = ""

    return (
        secret_key or os.getenv("NEBIUS_API_KEY", ""),
        secret_model or os.getenv("NEBIUS_MODEL", ""),
    )


def make_client(api_key: str) -> OpenAI:
    return OpenAI(
        base_url="https://api.tokenfactory.nebius.com/v1/",
        api_key=api_key,
        timeout=90,
    )


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The model response did not contain a JSON object. Try again.")
    return json.loads(text[start : end + 1])


def analyze_notes(api_key: str, model: str, notes: str) -> dict:
    client = make_client(api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "You are ActionBrief, an accurate meeting-notes analyst. Extract only facts supported by the notes. Never invent owners or deadlines; use null when missing. Return only valid JSON with this schema: {\"title\": string, \"summary\": string, \"decisions\": [string], \"action_items\": [{\"task\": string, \"owner\": string|null, \"due\": string|null}], \"open_questions\": [string], \"next_meeting\": string|null}. Keep the summary concise. Distinguish a proposed plan from a confirmed decision.",
            },
            {"role": "user", "content": f"Extract a clear action brief from these meeting notes:\n\n{notes}"},
        ],
    )
    content = response.choices[0].message.content or ""
    return extract_json(content)


st.sidebar.markdown("## ✳️ ActionBrief")
st.sidebar.caption("From meeting notes to clear next steps")
st.sidebar.markdown("---")
st.sidebar.markdown("### Model connection")
server_api_key, server_model = get_server_settings()
if server_api_key:
    api_key = server_api_key
    model = server_model or DEFAULT_MODEL
    st.sidebar.success("Connected with a server-side API key")
    st.sidebar.caption(f"Model: `{model}`")
else:
    api_key = st.sidebar.text_input(
        "Nebius Token Factory API key",
        type="password",
        help="For local testing only. For a hosted app, configure NEBIUS_API_KEY in the host's server-side Secrets settings.",
    )
    model = st.sidebar.text_input(
        "Model ID",
        value=DEFAULT_MODEL,
        help="Use an NVIDIA open model ID enabled for your Token Factory account.",
    )
st.sidebar.markdown("---")
st.sidebar.caption("Your notes are sent to the selected model for processing. This demo does not save them to a database.")

st.markdown(
    """
    <div class="hero">
      <span class="eyebrow">A calmer way to close the meeting</span>
      <h1>Turn talk into<br>clear next steps.</h1>
      <p>Paste your meeting notes. Get the decisions, owners, and follow-ups in one clean brief.</p>
      <span class="pill">Powered by NVIDIA Nemotron on Nebius</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("notes_form"):
    col_title, col_hint = st.columns([3, 2])
    with col_title:
        st.subheader("Meeting notes")
    with col_hint:
        st.markdown("<p class='small-note' style='text-align:right;padding-top:1rem'>Paste rough notes or a transcript · 20,000 characters max</p>", unsafe_allow_html=True)
    notes = st.text_area(
        "Paste notes",
        height=245,
        placeholder="Paste a transcript, rough notes, or meeting chat here…",
        label_visibility="collapsed",
        max_chars=20000,
    )
    left, right = st.columns([1, 4])
    with left:
        submitted = st.form_submit_button("Create my brief →", type="primary", use_container_width=True)
    with right:
        st.caption("Be specific in the notes. ActionBrief will leave missing owners or dates blank rather than guess.")

if submitted:
    if not notes.strip():
        st.warning("Add some meeting notes first.")
    elif not api_key.strip():
        st.error("Add your Nebius Token Factory API key in the sidebar for local testing, or configure NEBIUS_API_KEY in the hosting provider's server-side Secrets settings.")
    elif not model.strip():
        st.error("Enter the model ID enabled for your Token Factory account.")
    else:
        with st.spinner("Turning the conversation into a brief…"):
            try:
                st.session_state["brief"] = analyze_notes(api_key.strip(), model.strip(), notes.strip())
                st.session_state["source_notes"] = notes.strip()
            except Exception as exc:
                st.error(f"Could not create the brief: {exc}")

brief = st.session_state.get("brief")
if brief:
    st.markdown("---")
    heading, meta = st.columns([3, 1])
    with heading:
        st.markdown(f"### {brief.get('title') or 'Meeting brief'}")
    with meta:
        st.caption(f"Created {datetime.now().strftime('%b %d, %Y · %I:%M %p')}")

    st.markdown("#### In a nutshell")
    st.write(brief.get("summary") or "No summary returned.")

    decisions = brief.get("decisions") or []
    questions = brief.get("open_questions") or []
    left, right = st.columns(2)
    with left:
        st.markdown("#### Decisions")
        if decisions:
            for decision in decisions:
                st.markdown(f"- {decision}")
        else:
            st.caption("No confirmed decisions identified.")
    with right:
        st.markdown("#### Open questions")
        if questions:
            for question in questions:
                st.markdown(f"- {question}")
        else:
            st.caption("No open questions identified.")

    st.markdown("#### Action items")
    actions = brief.get("action_items") or []
    if actions:
        st.dataframe(
            [
                {
                    "Next step": item.get("task", ""),
                    "Owner": item.get("owner") or "Unassigned",
                    "Due": item.get("due") or "No date set",
                }
                for item in actions
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No action items identified.")

    next_meeting = brief.get("next_meeting")
    if next_meeting:
        st.markdown(f"**Next meeting:** {next_meeting}")

    markdown_export = [
        f"# {brief.get('title') or 'Meeting brief'}",
        f"\n## Summary\n{brief.get('summary') or ''}",
        "\n## Decisions",
        *[f"- {item}" for item in decisions],
        "\n## Action items",
        *[
            f"- [ ] {item.get('task', '')} — {item.get('owner') or 'Unassigned'} — {item.get('due') or 'No date set'}"
            for item in actions
        ],
        "\n## Open questions",
        *[f"- {item}" for item in questions],
    ]
    st.download_button(
        "Download brief as Markdown",
        data="\n".join(markdown_export),
        file_name="actionbrief.md",
        mime="text/markdown",
    )
    with st.expander("See source notes"):
        st.write(st.session_state.get("source_notes", ""))

st.markdown("---")
st.markdown("<p class='small-note'>ActionBrief is an early demo. Review generated owners and dates before sharing.</p>", unsafe_allow_html=True)
