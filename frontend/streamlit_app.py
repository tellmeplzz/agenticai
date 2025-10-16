"""Streamlit front-end for interacting with AgenticAI services."""

from __future__ import annotations

import base64
import json
from typing import Dict, List

import requests
import streamlit as st

BACKEND_URL = st.secrets.get("backend_url", "http://localhost:8000/api/chat")


def encode_file(file) -> Dict[str, str]:
    content = file.read()
    return {
        "name": file.name,
        "content_type": file.type,
        "data": base64.b64encode(content).decode("utf-8"),
    }


def render_sidebar() -> Dict[str, object]:
    st.sidebar.header("Agent configuration")
    agent_id = st.sidebar.selectbox("Agent", options=["ocr", "device_ops"], index=0)
    telemetry_raw = st.sidebar.text_area(
        "Telemetry JSON (device ops agent)",
        value=json.dumps({"temperature": "72C", "uptime": "48h"}, indent=2),
    )
    context: Dict[str, object] = {}
    if telemetry_raw:
        try:
            context["telemetry"] = json.loads(telemetry_raw)
        except json.JSONDecodeError:
            st.sidebar.warning("Invalid telemetry JSON; ignoring.")
    return {"agent_id": agent_id, "context": context}


def render_chat_interface(config: Dict[str, object]) -> None:
    st.title("AgenticAI Control Center")
    st.caption("Interact with OCR and device ops agents through a unified UI.")

    uploaded_files: List = st.file_uploader(
        "Upload documents for OCR agent", accept_multiple_files=True
    )

    user_message = st.text_input("Your message")
    if st.button("Send") and user_message:
        attachments = [encode_file(file) for file in uploaded_files] if uploaded_files else []
        payload = {
            "agent_id": config["agent_id"],
            "message": user_message,
            "context": config.get("context", {}),
            "attachments": attachments,
        }
        response = requests.post(BACKEND_URL, json=payload, timeout=60)
        if response.ok:
            data = response.json()
            st.markdown("### Agent response")
            st.write(data.get("response"))
            st.markdown("### Updated context")
            st.json(data.get("context"))
        else:
            st.error(f"Request failed: {response.status_code} {response.text}")


def main() -> None:
    config = render_sidebar()
    render_chat_interface(config)


if __name__ == "__main__":
    main()
