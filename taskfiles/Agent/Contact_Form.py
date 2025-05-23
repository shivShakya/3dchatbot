from taskfiles.Shared import State
from langgraph.types import Command
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from datetime import datetime, timedelta
from langchain.tools import tool
from typing import Dict
from typing_extensions import TypedDict, Literal, Annotated
import re

# ========== Contact Page Redirection and Form FIlling ==========

@tool
def redirection_node(
    state: State,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Redirect to contact page."""

    return Command(
        update={
            "redirection": state["redirection"],
            "messages": [
                ToolMessage(
                    content=f"""You have been redirected to the {state["redirection"]}.(if redirected to collaborate page) Please provide your name, email, and message you want to convey.""",
                    name="redirection_node",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )
     

@tool
def fillupTheContactPageDetails(
    state: State,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Filling Up contact form details."""

    name = state.get("name", "").strip()
    email = state.get("email", "").strip()
    message = state.get("contact_message", "").strip()
    subject = state.get("contact_subject","").strip()

    EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(EMAIL_REGEX, email):
        return Command(update={
            "messages": [
                ToolMessage(
                    content="The email you provided doesn't look valid. Could you double-check and re-enter it?",
                    name="fillupTheContactPageDetails",
                    tool_call_id=tool_call_id
                )
            ]
        })

    if name and email and message and subject:
        return Command(update={
            "name": name,
            "email": email,
            "contact_subject": subject,
            "contact_message": message,
            "messages": [
                ToolMessage(
                    content=f"Your form has been filled.Check if anything is wrong .ask me to correct.(Name: {name}, Email: {email})",
                    name="fillupTheContactPageDetails",
                    tool_call_id=tool_call_id
                )
            ]
        })

    missing = []
    if not name:
        missing.append("name")
    if not email:
        missing.append("email")
    if not message:
        missing.append("message")
    if not subject:
        missing.append("subject")

    return Command(update={
        "messages": [
            ToolMessage(
                content=f"Missing info: {', '.join(missing)}. Please provide it so I can fill up the form.",
                name="fillupTheContactPageDetails",
                tool_call_id=tool_call_id
            )
        ]
    })

#submitTheContactPageDetails
@tool
def submitTheContactPageDetails(
    state: State,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
        """Submitting contact form details."""
        return Command(
        update={
            "submitting_details": True,
            "messages": [
                ToolMessage(
                    content="Your form has successfully submitted. ",
                    name="submitTheContactPageDetails",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )
