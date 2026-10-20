"""Streamlit entry point: shows the Berliner Luft dashboard (app/index.html)."""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

APP = Path(__file__).parent / "app"


def build_page(html_path: Path, data_path: Path) -> str:
    """Return the dashboard HTML with the data built in.

    Streamlit shows the page in a frame that cannot load files next to it,
    so the JSON is placed in the page as window.BERLIN_DATA.

    Args:
        html_path: Path to app/index.html.
        data_path: Path to app/berlin_2025.json.

    Returns:
        The page as one HTML string.
    """
    html = html_path.read_text(encoding="utf-8")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    script = f"<script>window.BERLIN_DATA = {json.dumps(data, separators=(',', ':'))};</script>"
    return html.replace("<script>", script + "\n<script>", 1)


st.set_page_config(page_title="Berliner Luft · Data 2025", layout="wide")
# Remove Streamlit's own page padding so the dashboard uses the full width
st.markdown("<style>.block-container{padding:0 0.5rem;max-width:100%;}header{visibility:hidden;}</style>",
            unsafe_allow_html=True)
components.html(build_page(APP / "index.html", APP / "berlin_2025.json"), height=2300, scrolling=True)