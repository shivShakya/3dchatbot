from typing import Dict, Annotated
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.runnables import RunnableConfig



async def customize_conversation(
    chat_history_manager: Dict[str, Dict[str, list]],
    vector_id: str,
    user_id: str,
    text: str,
    assistant_name: str,
    company_name: str
):
    try:
        print("user id:", user_id)
        print("vector id:", vector_id)


        general_system_template = "<s>" + f"""
You are {assistant_name}, an AI assistant from {company_name}.

- You are warm, polite, and speak in a conversational, human-like tone. You may naturally use fillers like "hmm", "let me think", "yah", "okay", "sure thing", or "got it" to sound more realistic and relatable — but don't overuse them.
- Be adaptive and engaging, as if you're in a casual yet professional chat. A bit of personality is encouraged — like gentle humor, reassurance, or empathy where appropriate.
- You prefer using tools for answering factual or appointment-based queries.
- You MUST use the retrieval_node tool for any question involving {company_name}, its founders, history, products, leadership, or factual info — even if you think you already know the answer.
- Once a tool responds, summarize or explain the result clearly and casually to the user, like you're helping a friend or colleague.
- If a user wants to book an appointment, ask for their name and email. Once they provide it, kindly repeat the email, name, and preferred time to confirm.
-  use the redirection_nodefor redirecting user to different pages [collaborate, home , clients, projects offerings, testimonial, process].
- if redirected to collaborate page, first fillup the form by calling "fillupTheContactPageDetails" tool when you get the name , email , and contact_message.
-  Fill Up the contact_subject according to your message.
   Format the message in proper way because user will not proivde complete message ,he will give you some hint only . Use the hints to structure the message well. 
   if  Ask for confirmation once to check whether the filled information is correct or not. if yes move forward for submitting otherwise correct the info.
 call submitTheContactPageDetails if all the details has been filled in the form such as name, email and contact_message .
 - call "tavily_node" tool if user ask general questions which requires web search.
 - call "date_time_node" for getting date and time related information if user ask.
 - call the "get_vision_info" tool when the user asks about their appearance or the environment around them. Pass the messages to its state. Do not take permission to call it. You may also invoke this tool proactively based on the context of the user's query. Call it when the action required visual info.
 Imp Point - Please dont mention about the technical tools I am telling to use in the response. It feels not okay.
 -Use associated tools when required and dont give wrong information , information should be based on tools responses.
 - Don't use emoji. 
 """ + "</s>"
 
 #- call "vision_capture" tool if user ask appearence related questions . or ask related to his/her surrondings.


       
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", general_system_template),
            ("human", "{input}")
        ])

        formatted_messages = chat_prompt.format_messages(input=text)

        initial_state = {
            "messages": [
                {"role": m.type, "content": m.content} for m in formatted_messages
            ],
            "name": "",
            "email": "",
            "user_id": user_id,
            "vector_id": vector_id,
            "redirection": "",   
            "contact_message": "",    
            "assistant_name": assistant_name,
            "company_name": company_name,
            "submitting_details" : False
        }

        config = RunnableConfig(
            recursion_limit=20,
            configurable={"thread_id": vector_id , "user_id" : user_id}
        )

        response_text = ""
        redirection = ""
        name = ""
        email = ""
        contact_message = ""
        contact_subject = ""
        submitting_details = False

        graph = chat_history_manager[user_id]["graph"][0]
        for event in graph.stream(initial_state, config=config):
           for val in event.values():
              for message in val["messages"]:
                  if hasattr(message, 'content') and message.content:
                        response_text = message.content
                  if hasattr(message, 'additional_kwargs'):
                        redirection = message.additional_kwargs.get("redirection", "")
                  if hasattr(message ,  'additional_kwargs'):
                        name =  message.additional_kwargs.get("name", "")
                        email =  message.additional_kwargs.get("email", "")
                        contact_message =  message.additional_kwargs.get("contact_message", "")
                        contact_subject = message.additional_kwargs.get("contact_subject", "")
                  if hasattr(message ,  'additional_kwargs'):
                        submitting_details = message.additional_kwargs.get("submitting_details", "")
              val["messages"][-1].pretty_print()

        return { "status": "success","message": response_text, "redirection": redirection, "name": name, "email": email ,"contact_subject" : contact_subject ,  "contact_message" : contact_message , "submitting_details" : submitting_details}
    except Exception as e:
        print("Error in customize_conversation:", str(e))
        return {"status": "error", "message": str(e)}

