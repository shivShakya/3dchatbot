"""

class OutfitRequest(BaseModel):
    imageUrl: str
    textPrompt: str

@app.post("/proxy/outfit")
def proxy_outfit(req: OutfitRequest):
    url = 'https://api.lightxeditor.com/external/api/v1/outfit'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': lightx_api_key
    }
    payload = {
        "imageUrl": req.imageUrl,
        "textPrompt": req.textPrompt
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
class StatusRequest(BaseModel):
    orderId: str

STATUS_URL = "https://api.lightxeditor.com/external/api/v1/order-status"

@app.post("/proxy/status")
async def proxy_status(req: StatusRequest):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": lightx_api_key
    }
    print({'oid' : req.orderId})
    payload = {
        "orderId": req.orderId
    }

    response = requests.post(STATUS_URL, headers=headers, json=payload)
    result = response.json()
    image_url = result.get("body", {}).get("output", None) 
    print(image_url)
    
    return {
        "status_code": response.status_code,
        "data": result
    }
    
    
 
 
class ImageRequest(BaseModel):
    image_url: str
    background: str

@app.post("/proxy/remove-background")
def remove_background(request: ImageRequest):
    url = "https://api.lightxeditor.com/external/api/v1/remove-background"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": lightx_api_key
    }
    data = {
        "imageUrl": request.image_url,
        "background": ""
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print("remove_background_from_image response:", response.json())

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"LightX API error: {response.status_code} - {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   
   
 
  
   
def overlay_person_on_background_1(person_url: str, background_path: str, output_dir: str = "static", output_filename: str = "output.png", public_url_base: str = "http://127.0.0.1:8000/static"):
    # Ensure output directory exists
    print("overlay_person_on_background")
    os.makedirs(output_dir, exist_ok=True)
    
    # Download person image
    response = requests.get(person_url)
    if response.status_code != 200:
        raise Exception("Failed to download person image.")
    
    parsed_url = urlparse(person_url)
    person_filename = os.path.basename(parsed_url.path)
    person_path = f"/tmp/{person_filename}"
    
    with open(person_path, "wb") as f:
        f.write(response.content)

    # Build paths
    output_path = os.path.join(output_dir, output_filename)
    public_url = f"{public_url_base}/{output_filename}"

    # Run ffmpeg 
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", background_path,
        "-i", person_path,
        "-filter_complex",
        "[1:v]scale='if(gt(a\\,950/950)\\,950\\,-1)':'if(gt(a\\,950/950)\\,-1\\,950)',format=rgba[fg];[0:v][fg]overlay=(W-w)/2-110:(H-h)/2+80",
        "-frames:v", "1",
        "-pix_fmt", "rgba",
        output_path
    ]

    print("overlay_person_on_background 1")
    result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("overlay_person_on_background 2")
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr.decode())
        raise Exception("FFmpeg processing failed.")

    print(f"Image saved as {output_path}")
    return public_url


class StatusRequestBG(BaseModel):
    orderId: str
    background: str



@app.post("/proxy/statusBG")
async def proxy_status(req: StatusRequestBG):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": lightx_api_key
    }
    print({'oid' : req.orderId})
    payload = {
        "orderId": req.orderId
    }

    image_url = None
    result = None

    try:
        response = requests.post(STATUS_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if isinstance(result, dict):
            image_url = result.get("body", {}).get("output")
    except Exception as e:
        print(f"Error during status check: {e}")

    print(f"Image URL: {image_url}")
    print(f"Background: {req.background}")
    
    link = ""
    if image_url is not None:
      filename = f"output_img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
      link = overlay_person_on_background_1(
              image_url,
              f"./Background/{req.background}.jpg",
              output_dir="static",
              output_filename=filename
      )
    
    return {
        "status_code": response.status_code,
        "data": result,
        "result": link
    }
    
    
    
class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate-outfit/")
def generate_and_get_image(request: ImageRequest):
    api_key = os.getenv("PIAPI_API")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key is missing.")

    # Step 1: Create task
    create_url = "https://api.piapi.ai/api/v1/task"
    payload = {
        "model": "Qubico/flux1-schnell",
        "task_type": "txt2img",
        "input": {
            "prompt": request.prompt,
            "width": 1024,
            "height": 1024
        }
    }
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    print(f"[INFO] Sending task creation request to PiAPI...")
    try:
        response = requests.post(create_url, headers=headers, data=json.dumps(payload))
    except requests.RequestException as e:
        print(f"[ERROR] Task creation request failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to PiAPI.")

    print(f"[DEBUG] Task creation response: {response.status_code} {response.text}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    task_response = response.json()
    print(task_response)
    task_id = task_response.get("data", {}).get("task_id")
    if not task_id:
        print(f"[ERROR] No task_id returned in response: {task_response}")
        raise HTTPException(status_code=500, detail="No task_id returned from PiAPI.")

    print(f"[INFO] Task created. Task ID: {task_id}")

    # Step 2: Poll task status
    get_url = f"https://api.piapi.ai/api/v1/task/{task_id}"
    max_retries = 10
    delay = 4  # seconds

    for attempt in range(1, max_retries + 1):
        print(f"[INFO] Polling task status (attempt {attempt}/{max_retries})...")
        try:
           get_response = requests.get(get_url, headers=headers)
        except requests.RequestException as e:
           print(f"[ERROR] Failed to poll task: {e}")
           raise HTTPException(status_code=500, detail="Failed to poll task status from PiAPI.")

        print(f"[DEBUG] Poll response: {get_response.status_code} {get_response.text}")
        if get_response.status_code != 200:
           raise HTTPException(status_code=get_response.status_code, detail=get_response.text)

        result = get_response.json()
        task_data = result.get("data", {})
        status = task_data.get("status", "")

        if status == "completed":
            print("[INFO] Task completed successfully.")
            return task_data  # or return result if you need the outer structure
        elif status == "failed":
            print("[ERROR] Task failed.")
            raise HTTPException(status_code=500, detail="Image generation failed.")

        print(f"[INFO] Task still processing. Waiting {delay} seconds...")
        time.sleep(delay)

    print("[ERROR] Task did not complete in time.")
    raise HTTPException(status_code=504, detail="Image generation timed out after polling.")



class FashnRequest(BaseModel):
    model_image: str
    garment_image: str
    category: str = "one-pieces"

@app.post("/fashn-tryon/")
def run_fashn_tryon(data: FashnRequest):
    logger.debug("Received request with data: %s", data.dict())

    api_key = os.getenv("FASHN_API_KEY")
    if not api_key:
        logger.error("FASHN_API_KEY not found in environment variables.")
        raise HTTPException(status_code=500, detail="FASHN_API_KEY not set in environment.")

    base_url = "https://api.fashn.ai/v1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    input_data = {
        "model_image": data.model_image,
        "garment_image": data.garment_image,
        "category": data.category
    }

    logger.debug("Sending POST request to /run with input data: %s", input_data)
    try:
        response = requests.post(f"{base_url}/run", json=input_data, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception("Error sending request to /run endpoint")
        raise HTTPException(status_code=500, detail=f"Error triggering try-on: {e}")

    prediction_id = response.json().get("id")
    logger.debug("Received prediction ID: %s", prediction_id)

    if not prediction_id:
        logger.error("No prediction ID returned from API.")
        raise HTTPException(status_code=500, detail="Failed to get prediction ID.")

    # Polling loop
    for attempt in range(60):
        logger.debug("Polling status, attempt %d for ID %s", attempt + 1, prediction_id)
        try:
            status_response = requests.get(f"{base_url}/status/{prediction_id}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            logger.debug("Status response: %s", status_data)
        except requests.exceptions.RequestException as e:
            logger.exception("Error polling try-on status")
            raise HTTPException(status_code=500, detail=f"Error polling try-on status: {e}")

        status = status_data.get("status")
        if status == "completed":
            logger.info("Prediction completed successfully for ID %s", prediction_id)
            return {
                "message": "Prediction completed",
                "output": status_data.get("output"),
                "id": prediction_id
            }
        elif status in ["starting", "in_queue", "processing"]:
            time.sleep(3)
        else:
            error_message = status_data.get("error", {}).get("message", "Unknown error")
            logger.error("Prediction failed with error: %s", error_message)
            raise HTTPException(status_code=500, detail=f"Prediction failed: {error_message}")

    logger.warning("Prediction timeout for ID %s", prediction_id)
    raise HTTPException(status_code=408, detail="Prediction timeout.")




import random

from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from datetime import datetime
import shutil, os, random, time, requests, logging
import itertools

PUBLIC_KEYS = [
    "project_public_e4be42be8eacfdb3e50cb9ecfced09a5_LIDTRafaf5c978c3bf305f3b5f544eb55bec9",
    "project_public_b96ed56255eec1483cde8cd76e7a6804_qt7gG38c163adc280e672ec03b635bff395f9",
    "project_public_33632448032649e90482a08c335f2865_Fq0Bs0c6c4f0868639d7f353e64737046aa19",
    "project_public_a95baa8ae31eded06026f6eda6b2d46b_O2J96767af967edc52af3e9dea286ffb11eab"
]

key_cycle = itertools.cycle(PUBLIC_KEYS) 

logger = logging.getLogger("uvicorn.error")




def overlay_person_on_background(person_path: str, background_path: str, output_dir: str = "static", output_filename: str = "output.png", public_url_base: str = "http://127.0.0.1:8000/static"):
    print("overlay_person_on_background")
    
    os.makedirs(output_dir, exist_ok=True)

    # Build paths
    output_path = os.path.join(output_dir, output_filename)
    public_url = f"{public_url_base}/{output_filename}"

    # Run ffmpeg 
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", background_path,
        "-i", person_path,
        "-filter_complex",
        "[1:v]scale=280:-1,format=rgba[fg];[0:v][fg]overlay=x=(W-w)/2-180:y=(H-h)/2+80",
        "-frames:v", "1",
        "-pix_fmt", "rgba",
        output_path
    ]

    print("Running ffmpeg...")
    result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr.decode())
        raise Exception("FFmpeg processing failed.")

    print(f"Image saved as {output_path}")
    return public_url




import os
import requests
import base64
from PIL import Image
from io import BytesIO

def enhance_image(image_url, enhance_mode='fine/ultra', public_url_base="http://127.0.0.1:8000/static"):
    api_key = os.getenv("INHANCE_API")
    endpoint = 'https://platform.snapedit.app/api/image_enhancement/v1/enhance'

    headers = {
        'X-API-KEY': api_key,
        'X-ENHANCE-MODE': enhance_mode
    }

    local_path = image_url.replace(public_url_base, "static")

    with open(local_path, 'rb') as img_file:
        files = {
            'input_image': ('image.jpg', img_file)
        }

        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()
        data = response.json()

    if not data.get("output_images"):
        raise ValueError("No output image received from API.")

    base64_img = data["output_images"][0]
    image_data = base64.b64decode(base64_img)
    enhanced_image = Image.open(BytesIO(image_data))

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    folder = os.path.dirname(local_path)
    output_filename = f"output_img_{timestamp}.jpg"
    output_path = os.path.join(folder, output_filename)

    enhanced_image.save(output_path)
    relative_path = output_path.replace("static", "").replace("\\", "/").lstrip("/")
    public_url = f"{public_url_base}/{relative_path}"
    print({"Final Image saved as " : public_url})
    return {
        "output": public_url,
        "filename": output_filename,
        "saved_path": output_path
    }

@app.post("/fashn-tryon/")
async def run_fashn_tryon(
    model_image: UploadFile = File(None),
    image_url: str = Form(None),
    attire: str = Form(...),
    gender: str = Form(...),
    category: str = Form("one-piece"),
    background: str = Form(...),
):
    first_time = time.time()
    os.makedirs("uploads", exist_ok=True)
    if model_image:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        original_ext = os.path.splitext(model_image.filename)[1]  
        unique_filename = f"model_{timestamp}{original_ext}"
        file_path = f"uploads/{unique_filename}"

        with open(file_path, "wb") as f:
            shutil.copyfileobj(model_image.file, f)

        model_image_url = f"https://bingowhatsappcampaign.in/uploads/{unique_filename}"
    elif image_url:
        model_image_url = image_url
        print({'model': model_image_url})
    else:
        raise HTTPException(status_code=400, detail="Either model_image or image_url must be provided.")

    # Fetch API key from env
    api_key = os.getenv("FASHN_API_KEY")
    if not api_key:
        logger.error("FASHN_API_KEY not found in environment variables.")
        raise HTTPException(status_code=500, detail="FASHN_API_KEY not set in environment.")

    base_url = "https://api.fashn.ai/v1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    print({'gender': gender , 'atrie': attire})
    input_data = {
        "model_image": model_image_url,
        "garment_image": f"https://bingowhatsappcampaign.in/garments/{gender}/{attire}/1.png",
        "category": category,
        "mode": "quality"
    }

    logger.debug("Sending POST request to /run with input data: %s", input_data)
    try:
        response = requests.post(f"{base_url}/run", json=input_data, headers=headers)
        print(response)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception("Error sending request to /run endpoint")
        raise HTTPException(status_code=500, detail=f"Error triggering try-on: {e}")

    prediction_id = response.json().get("id")
    if not prediction_id:
        raise HTTPException(status_code=500, detail="Failed to get prediction ID.")

    path = ""
    for attempt in range(60):
       try:
          status_response = requests.get(f"{base_url}/status/{prediction_id}", headers=headers)
          status_response.raise_for_status()
          status_data = status_response.json()
       except requests.exceptions.RequestException as e:
          raise HTTPException(status_code=500, detail=f"Error polling try-on status: {e}")

       if status_data.get("status") == "completed":
           path = status_data.get("output")
           if isinstance(path, list): 
                path = path[0]
           
            return {
                "message": "Prediction completed",
                "output": status_data.get("output"),
                "id": prediction_id
            } 
           break  
       elif status_data.get("status") in ["starting", "in_queue", "processing"]:
           time.sleep(3)
       else:
          error_msg = status_data.get("error", {}).get("message", "Unknown error")
          raise HTTPException(status_code=500, detail=f"Prediction failed: {error_msg}")
    else:
       raise HTTPException(
           status_code=408,
           detail="Try-on prediction timed out after 3 minutes. Please try again later."
       )  
      
    public_key = next(key_cycle)
    logger.info(f"Using public key: {public_key}")

    # Step 2: Authenticate with iLovePDF
    logger.info("Authenticating with iLovePDF...")
    auth_res = requests.post("https://api.ilovepdf.com/v1/auth", json={"public_key": public_key})
    auth_res.raise_for_status()
    token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("Authentication successful.")

    # Step 3: Start task
    logger.info("Starting background removal task...")
    start_res = requests.get("https://api.ilovepdf.com/v1/start/removebackgroundimage", headers=headers)
    start_res.raise_for_status()
    task_data = start_res.json()
    server = task_data["server"]
    task = task_data["task"]
    logger.info(f"Task started: {task}")

    # Step 4: Upload image
    logger.info("Uploading image to iLovePDF server...")
    response = requests.get(path)
    filename = os.path.basename(urlparse(path).path)
    response.raise_for_status() 
    upload_res = requests.post(
         f"https://{server}/v1/upload",
         headers=headers,
         files={"file": ("filename.jpg", BytesIO(response.content))},
         data={"task": task}
    )
    upload_res.raise_for_status()
    server_filename = upload_res.json()["server_filename"]
    logger.info(f"Image uploaded. Server filename: {server_filename}")

    # Step 5: Process image
    logger.info("Requesting background removal process...")
    process_payload = {
        "task": task,
        "tool": "removebackgroundimage",
        "files": [{
             "server_filename": server_filename,
             "filename": filename
            }]
        }
    process_res = requests.post(
            f"https://{server}/v1/process",
            headers=headers,
            json=process_payload
    )
    process_res.raise_for_status()
    logger.info("Background removal processing initiated.")

    logger.info("Downloading processed image...")
    download_res = requests.get(f"https://{server}/v1/download/{task}", headers=headers)
    download_res.raise_for_status()

    processed_image_path = f"uploads/{filename.replace('.png', '_nobg.png')}"
    with open(processed_image_path, "wb") as out_file:
        out_file.write(download_res.content)
    logger.info(f"Processed image saved to: {processed_image_path}")

    trimmed_image_path = processed_image_path.replace(".png", "_trimmed.png")
    img = Image.open(processed_image_path)
    bbox = img.getbbox()
    trimmed = img.crop(bbox)
    trimmed.save(trimmed_image_path)
    logger.info(f"Trimmed image saved to: {trimmed_image_path}")
    last_time = time.time() - first_time
    print(f"Elapsed time: {last_time:.2f} seconds")
    if background:
        filename = f"output_img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
        background_image_path = f"./Background/{background}.jpg"
            
        if not os.path.exists(background_image_path):
            raise HTTPException(status_code=404, detail="Background image not found")

        logger.info(f"Merging with background: {background_image_path}")
        public_url = overlay_person_on_background(
            trimmed_image_path, background_image_path,
            output_dir="static", output_filename=filename
        )
        
        result = enhance_image(public_url)
        
        logger.info(f"Final image available at: {public_url}")
        return {"url": result["output"]}








@app.post("/remove-background")
async def remove_background(
    image_file: UploadFile = File(None),  # If the file is uploaded as a blob
    image_url: str = Form(None),  # If the image is passed as a URL
    background: str = Form(...),  # Background image filename (in /Background/ directory)
):
    try:    
        start_time = time.time()
        local_path = None
        processed_image_path = None
        
        print({"image_file" : image_file , "image_url" : image_url })
        # Case 1: If the image is uploaded as a file (Blob)
        if image_file:
            os.makedirs("uploads", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            ext = os.path.splitext(image_file.filename)[1]
            input_filename = f"input_{timestamp}{ext}"
            input_path = f"uploads/{input_filename}"

            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
                
            local_path = input_path
            logger.info(f"Image saved locally at: {local_path}")

            
            image_url = f"https://bingowhatsappcampaign.in/uploads/{input_filename}"
            logger.info(f"Image saved to: {image_url}")
            
        # Case 2: If the image is provided as a URL
        elif image_url:
            logger.info(f"Downloading image from URL: {image_url}")
            image_res = requests.get(image_url)
            if not image_res.ok:
                raise HTTPException(status_code=400, detail="Failed to download image from URL")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(image_res.content)
                local_path = tmp_file.name
            logger.info(f"Image downloaded to: {local_path}")

        # No need to download again, using local saved file directly
 
        public_key = next(key_cycle)
        logger.info(f"Using public key: {public_key}")

        # Step 2: Authenticate with iLovePDF
        logger.info("Authenticating with iLovePDF...")
        auth_res = requests.post("https://api.ilovepdf.com/v1/auth", json={"public_key": public_key})
        auth_res.raise_for_status()
        token = auth_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        logger.info("Authentication successful.")

        # Step 3: Start task
        logger.info("Starting background removal task...")
        start_res = requests.get("https://api.ilovepdf.com/v1/start/removebackgroundimage", headers=headers)
        start_res.raise_for_status()
        task_data = start_res.json()
        server = task_data["server"]
        task = task_data["task"]
        logger.info(f"Task started: {task}")

        # Step 4: Upload image
        logger.info("Uploading image to iLovePDF server...")
        with open(local_path, "rb") as f:
            upload_res = requests.post(
                f"https://{server}/v1/upload",
                headers=headers,
                files={"file": f},
                data={"task": task}
            )
        upload_res.raise_for_status()
        server_filename = upload_res.json()["server_filename"]
        logger.info(f"Image uploaded. Server filename: {server_filename}")

        # Step 5: Process image
        logger.info("Requesting background removal process...")
        process_payload = {
            "task": task,
            "tool": "removebackgroundimage",
            "files": [{
                "server_filename": server_filename,
                "filename": os.path.basename(local_path)
            }]
        }
        process_res = requests.post(
            f"https://{server}/v1/process",
            headers=headers,
            json=process_payload
        )
        process_res.raise_for_status()
        logger.info("Background removal processing initiated.")

        logger.info("Downloading processed image...")
        download_res = requests.get(f"https://{server}/v1/download/{task}", headers=headers)
        download_res.raise_for_status()

        processed_image_path = local_path.replace(".png", "_nobg.png")
        with open(processed_image_path, "wb") as out_file:
            out_file.write(download_res.content)
        logger.info(f"Processed image saved to: {processed_image_path}")

        trimmed_image_path = processed_image_path.replace(".png", "_trimmed.png")
        img = Image.open(processed_image_path)
        bbox = img.getbbox()
        trimmed = img.crop(bbox)
        trimmed.save(trimmed_image_path)
        logger.info(f"Trimmed image saved to: {trimmed_image_path}")

        if background:
            filename = f"output_img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
            background_image_path = f"./Background/{background}.jpg"
            
            if not os.path.exists(background_image_path):
                raise HTTPException(status_code=404, detail="Background image not found")

            logger.info(f"Merging with background: {background_image_path}")
            public_url = overlay_person_on_background(
                trimmed_image_path, background_image_path,
                output_dir="static", output_filename=filename
            )
            logger.info(f"Final image available at: {public_url}")
            
            #result = enhance_image(public_url)
            end_time = time.time() - start_time
            print({"Final time" : end_time})
            return {"url": public_url}

    except Exception as e:
        logger.exception("Error occurred during background removal process.")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        logger.info("Cleaning up temporary files...")
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            logger.info(f"Deleted temp file: {local_path}")
        if processed_image_path and os.path.exists(processed_image_path):
            os.remove(processed_image_path)
            logger.info(f"Deleted processed file: {processed_image_path}")

"""

