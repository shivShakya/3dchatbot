import os
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_groq import ChatGroq
from groq import Groq
from typing import Dict
import re
import json
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

# Initialize GROQ LLM
groq_api_key = os.getenv("GROQ_API")
client = Groq(api_key=groq_api_key)
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")
embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
    )

async def customize_conversation( chat_history_manager: Dict[str, Dict[str, list]] , unique_id: str, user_id: str , text: str ,assistant_name: str , company_name: str):
    try:
        print(unique_id)
        print({user_id})
        folder_path = f"./store/{unique_id}"

        if os.path.exists(folder_path):
            vectors = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
        else:
            return {"status": "failed", "answer": "Please provide your Id"}
        
        general_system_template = "<s>" + "You are " + assistant_name + ", the AI assistant of " + company_name + """. Your purpose is to engage in professional, 
        context-aware conversations strictly based on the provided company information.

        ----
        {context}
         ----

        - If a user asks something beyond the given context, give a blank response.
        - Keep responses professional, polite, and limited to **10-15 words**.
        - Greet users properly and maintain a formal tone.

        Determine if the user is addressing you explicitly:

        - **Always return `"is_talking_to_me": true"` if any of these conditions are met:**
        - The user's message includes `""" + assistant_name + """` or `""" + company_name + """`.
        - The question relates to `{context}`.
        - The message contains greetings, introductions, or AI-related questions (e.g., "hello," "who are you?").
        - The user is asking for information, clarification, or verification about company-related topics.
        - The user gives a command or directive that an AI would typically respond to.
        - The message includes acknowledgments, follow-ups, or corrections.
        - The message references AI-specific discussions like capabilities, intelligence, or chatbot nature.
        - **Only return `"is_talking_to_me": false"` if the message is clearly directed at another person or completely unrelated.**


        Provide your response in JSON format:
        {{
            "response": "Your reply here",
            "is_talking_to_me": true or false
        }}


        """ + "</s>"
       
        general_user_template = "Question:{question}"
        messages = [
             SystemMessagePromptTemplate.from_template(general_system_template),
             HumanMessagePromptTemplate.from_template(general_user_template),
        ]
        qa_prompt = ChatPromptTemplate.from_messages(messages)

        chat_history_user = chat_history_manager.get(user_id)
        
        qa = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever= vectors.as_retriever(),
                combine_docs_chain_kwargs={"prompt": qa_prompt}
        )

        response = qa({"question": text, "chat_history": chat_history_user["chat_history"]})
        print("Response:", response['answer'])
        response['answer'] = re.sub(r"<think>.*?</think>", "", response["answer"], flags=re.DOTALL).strip()
        print("Response:", response['answer'])
        cleaned_json = re.sub(r"```json|```", "", response["answer"]).strip()
        print(cleaned_json)
        data_dict = json.loads(cleaned_json)
        response_text = data_dict["response"]
        is_talking_to_me = data_dict["is_talking_to_me"]
        # Step 4: Print results
        print("Response:", response_text)
        print("Is Talking To Me:", is_talking_to_me)

        if is_talking_to_me:

            chat_history_user["chat_answers_history"].append(response_text)
            chat_history_user["user_prompt_history"].append(text)
            chat_history_user["chat_history"].append((text, response_text))

            return {"status": "success", "message": response_text}
        else:
            return {"status": "failed", "message": "Not talking to you"}


    except Exception as e:
        print(f"Error in conversation customization: {str(e)}")
        return {"status": "error", "message": str(e)}
   
   
async def test_call(text: str):
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "convert the text into hindi.",
        },
        {
            "role": "user",
            "content": text,
        }
    ],
    model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content
    
async def customize_conversation_test( text: str):
    try:
        folder_path = f"./store/515b8e1e-d6ff-491e-8715-54142f072a0f"

        if os.path.exists(folder_path):
            vectors = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
        else:
            return {"status": "failed", "answer": "Please provide your Id"}
        
        general_system_template = f"""
        You are karan AI assistant of VR AR MR Company and the context shared is the information about your company. 
        Your role is to have a professional conversation with users about the context only. 
        Say 'I don't have information' if something is asked out of the context. Provide responses in 10-15 words only. 
        Greet well, behave professionally, and think like a human.
        ----
        {{context}}
        ----
        """
        
        general_user_template = "Question:{question}"
        messages = [
             SystemMessagePromptTemplate.from_template(general_system_template),
             HumanMessagePromptTemplate.from_template(general_user_template),
        ]
        qa_prompt = ChatPromptTemplate.from_messages(messages)

        
        qa = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever= vectors.as_retriever(),
                combine_docs_chain_kwargs={"prompt": qa_prompt}
        )

        response = qa({"question": text, "chat_history": []})
        print({response['answer']})
        
        text =  await test_call(response['answer'])

        return {"status": "success", "message": text}

    except Exception as e:
        print(f"Error in conversation customization: {str(e)}")
        return {"status": "error", "message": str(e)}
    
