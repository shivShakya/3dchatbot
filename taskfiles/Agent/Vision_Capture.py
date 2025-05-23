from langchain_huggingface import HuggingFaceEmbeddings
from typing import Annotated
import asyncio
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langchain_core.messages import HumanMessage
from taskfiles.Shared import State
from langgraph.types import Command
from langchain.tools import tool
from taskfiles.capture_bridge import broadcast_capture_request, image_futures
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
import os

google_api_key = os.getenv("GOOGLE_API_KEY")
llm_google = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=google_api_key, temperature=0.7)


@tool
def get_vision_info(state: State, config: RunnableConfig, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Triggers frontend to capture image and waits for response."""
    try:
        from chat import global_image_data
        
        print({"state" :  state})
        
        user_id = config.get("configurable", {}).get("user_id")
        
        print({'user_id' : user_id})
        if user_id not in global_image_data:
                     return Command(update={
                            "messages": [ToolMessage(
                                    content=f"Something is wrong. Cannot see you.",
                                    name="vision_capture",
                                    tool_call_id=tool_call_id)]
                     })
        
        image_data = global_image_data[user_id].get("image")

        message_url = HumanMessage(
           content=[
            {
                "type": "text",
                "text": state["messages"][-1].content or "Describe the image and do it in friendly way . such as complimenting.",
            },
            {"type": "image_url", "image_url": f"{image_data}"},
        ])
        
        if not image_data:
                    return Command(update={
                        "messages": [ToolMessage(
                            content=f"Something is wrong.I did not get image data . Cannot see you.",
                            name="vision_capture",
                            tool_call_id=tool_call_id)]
                    })
        

        result_url = llm_google.invoke([message_url])
        print(f"Response for URL image: {result_url.content}")

        return Command(update={
            "messages": [ToolMessage(
                content=f"{result_url.content}",
                name="vision_capture",
                tool_call_id=tool_call_id)]
        })
    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(
                content=f"Error: {str(e)}",
                name="vision_capture",
                tool_call_id=tool_call_id)]
        })
