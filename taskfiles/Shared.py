# ========== State Definition ==========
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Literal, Annotated
from typing import List

class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class State(TypedDict):
    messages: Annotated[List[Message], add_messages]
    name: str
    email: str
    user_id : str
    vector_id: str
    booking_time_date: str
    cancel_time_date: str
    redirection: str
    contact_subject: str
    contact_message: str
    submitting_details: bool
