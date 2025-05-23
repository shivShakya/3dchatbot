from io import BytesIO
import os
import random
import shutil
import subprocess
import tempfile
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, File, UploadFile , Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from fastapi import UploadFile, File , HTTPException, Query
from fastapi.staticfiles import StaticFiles
import requests  
from datetime import datetime

from taskfiles.authorization import authorize_function
from taskfiles.rag import initialize_vectors_function
#from taskfiles.llm import  customize_conversation_test
from taskfiles.agent import customize_conversation
from taskfiles.capture_bridge import broadcast_capture_request, register_client, unregister_client, resolve_image
from taskfiles.firebase import db
from taskfiles.tts import useElavenlabsVoice
from urllib.parse import urlparse
from pathlib import Path
import json
import logging
import itertools
from PIL import Image


import requests
import base64
from PIL import Image
from io import BytesIO
import os



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()
chat_history_manager = {}
global_image_data = {} 



lightx_api_key = os.getenv("LIGHTX_API_KEY")

app = FastAPI()
app.mount("/public", StaticFiles(directory="public"), name="public")
app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("public/index.html", "r") as f:
        return f.read()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuthorizeRequest(BaseModel):
    id: str  
    url: str
    user_id: str

@app.post("/authorize")
async def authorize(request: AuthorizeRequest):
    print("Received request:", request.dict())
    response = authorize_function(
        id_param=request.id, 
        url_param=request.url,
        user_id=request.user_id,
        db=db, 
        chat_history_manager=chat_history_manager
    )
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    elif response.get("authorized") is False:
        raise HTTPException(status_code=401, detail="Authorization failed")
    return response


@app.post("/initialize-vectors")
async def initialize_vectors(
    file: UploadFile = File(...),
    web_url: str = Form(...)
):
    file_data = await file.read()
    result = initialize_vectors_function(file_data, file.filename, web_url)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return JSONResponse(content=result)

@app.post("/getVoice")
async def get_voice(
    request: Request,
    transcript: str = Form(...),
    vector_id: str = Form(...),
    user_id: str = Form(...),
    assistant_name: str = Form(...),
    company_name: str = Form(...),
):
    try:
        if await request.is_disconnected():
            raise HTTPException(status_code=499, detail="Client disconnected")

        if not vector_id:
            return {"status": "failed", "message": "Vector ID is required"}
        print({"vector": vector_id})
        print({"text": transcript})
        

        if transcript:
           startTime = time.time()
           response = await customize_conversation(
               chat_history_manager,
               vector_id,
               user_id,
               transcript ,
               assistant_name,
               company_name,
            )
        else:
            response = { "status": "success","message": "I am sorry ? what you are trying to say?", "redirection": "", "name": "", "email": "" ,"contact_subject" : "" ,  "contact_message" : "" , "submitting_details" : ""}
        print({"response" : response})
        if response["status"] != "success":
             response = { "status": "success","message": "Something went wrong I think . Please click the microphone button to reintialize conversation.", "redirection": "", "name": "", "email": "" ,"contact_subject" : "" ,  "contact_message" : "" , "submitting_details" : ""}
        
        print({'Response Timing' , time.time()-startTime})

        if not response.get("message"):
             response["message"] = "Sorry, can you repeat?"
        audioDetails = useElavenlabsVoice(response) #.dict()
        #nUagRYBWb90CoyEXd8zt   HSdLdxNgP1KF3yQK3IkB 
        print(type(audioDetails))
        audioDetails["redirection"] = response.get("redirection", "")
        audioDetails["name"] = response.get("name", "")
        audioDetails["email"] = response.get("email", "")
        audioDetails["contact_message"] = response.get("contact_message", "")
        audioDetails["contact_subject"] = response.get("contact_subject", "")
        audioDetails["submitting_details"] = response.get("submitting_details", False)
        return audioDetails 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")



@app.get("/removeUserId")
async def remove(user_id: str):
    try:
        if user_id in chat_history_manager:
            del chat_history_manager[user_id]
            return JSONResponse(content={"message": f"User {user_id} removed successfully."})
        else:
            return JSONResponse(content={"error": f"User {user_id} not found."}, status_code=404)
    except Exception as e:
        print(f"Error while removing user_id {user_id}: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)



@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle WebSocket connections and broadcast image capture requests."""
    await ws.accept()
    user_id = ws.query_params.get("user_id")
    print({'user_Id' : user_id })
    
    register_client(ws)

    try:
        await broadcast_capture_request(user_id)

        while True:
            data = await ws.receive_json()
            if data.get("type") == "image":
                image_data = data.get("image")
                #print(f"Received image from {user_id}: {image_data}")
                if user_id not in global_image_data:
                    global_image_data[user_id] = {}

                global_image_data[user_id]["image"] = image_data
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected.")
    except Exception as e:
        print(f"Error during WebSocket communication: {str(e)}")
    finally:
        unregister_client(ws)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat:app", host="0.0.0.0", port=8000, reload=True)
