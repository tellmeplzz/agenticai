"""Streamlit front-end for interacting with AgenticAI services."""

from __future__ import annotations

import base64
import json
from typing import Dict, List

import requests
import streamlit as st

BACKEND_URL = st.secrets.get("backend_url", "http://localhost:8000/api/chat")


def _init_session_state() -> None:
    st.session_state.setdefault("conversation", [])
    st.session_state.setdefault("server_context", {})


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
    clear = st.sidebar.button("Clear conversation")
    if clear:
        st.session_state["conversation"] = []
        st.session_state["server_context"] = {}
    return {"agent_id": agent_id, "context": context}


def _send_request(payload: Dict[str, object]) -> Dict[str, object] | None:
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=60)
    except requests.RequestException as exc:  # pragma: no cover - interactive UI
        st.error(f"Failed to contact backend: {exc}")
        return None

    if not response.ok:
        st.error(f"Request failed: {response.status_code} {response.text}")
        return None

    return response.json()


def render_chat_interface(config: Dict[str, object]) -> None:
    st.title("AgenticAI Control Center")
    st.caption("Interact with OCR and device ops agents through a unified UI.")

    uploaded_files: List = st.file_uploader(
        "Upload documents for OCR agent", accept_multiple_files=True
    )

    user_message = st.text_input("Your message")
    send_clicked = st.button("Send")

    if send_clicked and user_message:
        attachments = [encode_file(file) for file in uploaded_files] if uploaded_files else []
        context = dict(st.session_state.get("server_context", {}))
        context.update(config.get("context", {}))
        payload = {
            "agent_id": config["agent_id"],
            "message": user_message,
            "context": context,
            "attachments": attachments,
        }
        data = _send_request(payload)
        if data:
            server_context = data.get("context", {})
            history = server_context.get("conversation_history", [])
            if isinstance(history, list) and history:
                st.session_state["conversation"] = history
            else:
                st.session_state["conversation"].append(
                    {
                        "role": "user",
                        "message": user_message,
                        "attachments": [att["name"] for att in attachments],
                    }
                )
                st.session_state["conversation"].append(
                    {
                        "role": "agent",
                        "message": data.get("response", ""),
                        "context": server_context,
                    }
                )
            st.session_state["server_context"] = server_context

    if st.session_state["conversation"]:
        st.markdown("### Conversation history")
        for entry in st.session_state["conversation"]:
            if entry["role"] == "user":
                st.markdown(f"**You:** {entry['message']}")
                if entry.get("attachments"):
                    st.caption("Attachments: " + ", ".join(entry["attachments"]))
            else:
                st.markdown(f"**Agent:** {entry['message']}")
                agent_context = entry.get("context")
                if agent_context:
                    st.json(agent_context)


def main() -> None:
    _init_session_state()
    config = render_sidebar()
    render_chat_interface(config)


if __name__ == "__main__":
    main()
