from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict, Annotated
from datetime import datetime, timedelta
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from taskfiles.Shared import State
from langgraph.types import Command
from langchain.tools import tool
import os

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False},
)

# ==========Retrive Data from story ==========
@tool
def retrieval_node(
    state: State,
    tool_call_id: Annotated[str, InjectedToolCallId],
    query: str = ""  
) -> Command:
    """Tool to retrieve documents from FAISS vector store based on input query."""
    try:
        print({"state" : state})
        print({"vector id": state.get("vector_id", "N/A")})
        folder_path = "./store/" + "515b8e1e-d6ff-491e-8715-54142f072a0f"

        if not os.path.exists(folder_path):
            return Command(update={
                "messages": [ToolMessage(
                    content="❌ Please provide your ID.",
                    name="retrieval_node",
                    tool_call_id=tool_call_id)]
            })

        # Load vector store
        vectors = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vectors.as_retriever(search_kwargs={"k": 3})

        try:
            user_message = state.get("messages", [{}])[0].get("content", "")
        except Exception:
            user_message = ""

        # If state message empty, use query
        if not user_message:
            user_message = query

        if not user_message:
            return Command(update={
                "messages": [ToolMessage(
                    content="No user input found to retrieve information.",
                    name="retrieval_node",
                    tool_call_id=tool_call_id)]
            })

        # Run retrieval
        retrieved_docs = retriever.invoke(user_message)
        limited_content = "\n\n".join(doc.page_content[:300] for doc in retrieved_docs)

        return Command(update={
            "messages": [ToolMessage(
                content=limited_content or "No relevant information found.",
                name="retrieval_node",
                tool_call_id=tool_call_id)]
        })

    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(
                content=f" Error: {str(e)}",
                name="retrieval_node",
                tool_call_id=tool_call_id)]
        })


# ==========Date Time Fetch==========
@tool
def datetime_node(state: State, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Tool to get the current date and time."""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return Command(update={
            "messages": [ToolMessage(
                content=current_time,
                name="datetime_node",
                tool_call_id=tool_call_id)]
        })
    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(
                content=f"❌ Error: {str(e)}",
                name="datetime_node",
                tool_call_id=tool_call_id)]
        })
