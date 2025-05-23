from typing import Dict
import uuid

from datetime import datetime, timedelta
from dateutil import parser
import json
import os
from pprint import pprint
import re
from typing import Dict, Annotated
import pytz
from typing_extensions import TypedDict
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI


from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from groq import Groq
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages





load_dotenv()
# node
from taskfiles.Agent.Appointment_Booking import book_event_by_time , cancel_event_by_time 
from taskfiles.Agent.Contact_Form import redirection_node, fillupTheContactPageDetails ,submitTheContactPageDetails
from taskfiles.Agent.Story_Retrival import retrieval_node , datetime_node
from taskfiles.Agent.Vision_Capture import get_vision_info
from langchain_tavily import TavilySearch
from taskfiles.Shared import State
#from langchain_anthropic import ChatAnthropic
#from langchain_google_genai import ChatGoogleGenerativeAI
# ========== Setup LLM and Embeddings ==========
groq_api_key = os.getenv("GROQ_API")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
github_open_ai = os.getenv("GITHUB_OPEN_AI")
open_router_api = os.getenv("OPEN_ROUTER_API")


print(google_api_key)

client = Groq(api_key=groq_api_key)
llm = ChatGroq(groq_api_key=groq_api_key, model_name="meta-llama/llama-4-maverick-17b-128e-instruct")
#llm_anthropic = ChatAnthropic(model='claude-3-opus-20240229', api_key=anthropic_api_key)
llm_google = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=google_api_key, temperature=0.7)
github_url = "https://models.github.ai/inference"
openRouter_url = "https://openrouter.ai/api/v1"
github_model = "openai/gpt-4o"
qwen_model = "qwen/qwen3-235b-a22b:free"
llmOpenAI = ChatOpenAI( base_url=openRouter_url,model= qwen_model, api_key=open_router_api)


tavily = TavilySearch(
    tavily_api_key = os.getenv("TAILVY_API"),
    max_results=5,
    topic="general",
)


# ========== Graph Setup ==========
tools = [get_vision_info, retrieval_node , datetime_node, book_event_by_time , cancel_event_by_time, redirection_node, fillupTheContactPageDetails , submitTheContactPageDetails , tavily ] #retrieval_node , datetime_node, book_event_by_time , cancel_event_by_time, redirection_node, fillupTheContactPageDetails , submitTheContactPageDetails, vision_capture
#tools.extend(tools_cal)

llm_with_tools = llm_google.bind_tools(tools=tools)

def chatbot(state: State) -> Dict:
    try:
        print("... A")
        response = llm_with_tools.invoke(state["messages"])
        print("... A 1")
    except Exception as e1:
        print("Primary model failed in chatbot node:", str(e1))
        try:
            print("... B")
            fallback1 = ChatOpenAI( base_url="https://models.github.ai/inference",model= "openai/gpt-4o-mini", api_key=github_open_ai).bind_tools(tools=tools)
            response = fallback1.invoke(state["messages"])
            print("... B 1") 
        except Exception as e2:
            print("Fallback 1 also failed:", str(e2))
            try:
                print("... C")
                fallback2 = ChatGroq(groq_api_key=groq_api_key, model_name="meta-llama/llama-4-scout-17b-16e-instruct").bind_tools(tools=tools)
                response = fallback2.invoke(state["messages"])
                print("... C 2") 
            except Exception as e3:
                try:
                      print("... D")
                      fallback3 = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192").bind_tools(tools=tools)
                      response = fallback3.invoke(state["messages"])
                      print("... D 1")
                except Exception as e4:
                       print("Fallback 3 also failed:", str(e3))
                raise RuntimeError("All LLM models failed in chatbot execution.")

    if hasattr(response, "content") and isinstance(response.content, str):
        if "<|python_start|>" in response.content or response.content.strip().startswith("<function="):
            print("Tool call was generated but not executed. Returning fallback message.")
            response = AIMessage(content="I'm not sure how to answer that at the moment. Please try again. Better is to reintialize.")


    redirection_info = state.get("redirection", "")
    name_info = state.get("name", "")
    email_info = state.get("email", "")
    contact_message_info = state.get("contact_message", "")
    contact_subject_info = state.get("contact_subject", "")
    submitting_details_info = state.get("submitting_details", False)
    
    print({submitting_details_info, redirection_info , name_info , email_info , contact_message_info , contact_subject_info})
    messages = [response]
    
    print({'messages': messages})
    if redirection_info:
        messages.append(AIMessage(content=response.content, additional_kwargs={"redirection": redirection_info}))
    
    if name_info and email_info and contact_message_info:
        messages.append(AIMessage(content=response.content, additional_kwargs={
            "name": name_info,
            "email": email_info,
            "contact_subject" : contact_subject_info,
            "contact_message": contact_message_info
        }))

    if submitting_details_info:
        messages.append(AIMessage(content=response.content, additional_kwargs={"submitting_details": True}))

    return {"messages": add_messages(state["messages"], messages)}


graphBuilder = StateGraph(State)
graphBuilder.add_node("chatbot", chatbot)
graphBuilder.add_edge(START, "chatbot")
graphBuilder.add_node("tools", ToolNode(tools=tools))
graphBuilder.add_conditional_edges("chatbot", tools_condition)
graphBuilder.add_edge("tools", "chatbot")
graphBuilder.add_edge("chatbot", END)



def authorize_function(
    id_param: str, 
    url_param: str, 
    user_id: str,
    db, 
    chat_history_manager: Dict[str, Dict[str, list]]
):
    try:
        print({"id_param": id_param})
        print({"url_param": url_param})

        memory = MemorySaver()
        graph = graphBuilder.compile(checkpointer=memory)

        userId_new = ""
        effective_user_id = user_id

        if not user_id:
            userId_new = str(uuid.uuid4())
            effective_user_id = userId_new
            chat_history_manager[effective_user_id] = {
                "memory": [memory],
                "graph": [graph],
            }

        docs = db.collection("user_data").where("id", "==", id_param).where("url", "==", url_param).stream()
        for doc in docs:
            data = doc.to_dict()
            return {
                "authorized": True,
                "id": data.get("id"),
                "user_id": effective_user_id
            }

        return {"authorized": False, "status_code": 401}

    except Exception as e:
        print(f"Error during authorization: {str(e)}")
        return {"error": str(e), "status_code": 500}
