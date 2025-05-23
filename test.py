import requests

def upscale_image(image_path: str, upscale_factor: int = 8, output_format: str = "JPG") -> bytes:
    url = "https://api.picsart.io/tools/1.0/upscale"
    api_key = "eyJraWQiOiI5NzIxYmUzNi1iMjcwLTQ5ZDUtOTc1Ni05ZDU5N2M4NmIwNTEiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhdXRoLXNlcnZpY2UtMGY1MDM5NjktOTU1ZC00YWI3LTkwZmItZjQyZGUwNTYxNDNhIiwiYXVkIjoiNDg0MzIxOTYwMDI2MTAxIiwibmJmIjoxNzQ2NjI1OTgxLCJzY29wZSI6WyJiMmItYXBpLmdlbl9haSIsImIyYi1hcGkuaW1hZ2VfYXBpIl0sImlzcyI6Imh0dHBzOi8vYXBpLnBpY3NhcnQuY29tL3Rva2VuLXNlcnZpY2UiLCJvd25lcklkIjoiNDg0MzIxOTYwMDI2MTAxIiwiaWF0IjoxNzQ2NjI1OTgxLCJqdGkiOiIwNzM5YTUzMy04ZGM0LTRjYjctODI5Yy1iZDY4NjcxNzgxZjcifQ.nh6cUKrXKItV_6GbfI5z-9tPwOgE9L69YWDW7SpFmbWFfl9RqPClsvV7ZXoL52Vc28CPjOnCsKmpdRK2Q_jSBzuCpUr9Kyn7ZjikwmwCD4Y6SJfUpSY_lIjBESYID1Ik8ELD5A8oqtVgABuI-T1fWIolVhHYhBUeYLbdWal4GtnMPw-jpO8SNZVktdD5KQwcXQqRSi4wVb7hDLTSUze6OMu5hMnqpTWZByz_OlPz6PuD3BrmXkw8xStLovErZuw3Pa_QqIbGzlCcLKRagEirYLNXZj8DEDktOekD-cO6KL1HNwMSUVDWKJmMDJQojZ7cj1jnbNZiOoY317STEnW2Qg"  # Replace with your real API key

    files = {
        "image": open(image_path, "rb")
    }

    data = {
        "upscale_factor": str(upscale_factor),
        "format": output_format,
        "mode": "sync"
    }

    headers = {
        "accept": "application/json",
        "X-Picsart-API-Key": api_key
    }

    response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code == 200:
        # If you want to save the result
        result = response.json()
        output_url = result.get("data", {}).get("url")
        if output_url:
            image_data = requests.get(output_url).content
            output_path = image_path.replace(".", f"_upscaled1.{output_format.lower()}.")
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"Saved upscaled image to: {output_path}")
            return output_path
        else:
            raise Exception("Upscaled image URL not found in response.")
    else:
        raise Exception(f"Upscaling failed: {response.status_code} - {response.text}")


upscale_image("person222.jpg")









"""
LIGHTX_REMOVE_BG_URL = "https://api.lightxeditor.com/external/api/v1/remove-background"
LIGHTX_ORDER_STATUS_URL = "https://api.lightxeditor.com/external/api/v1/order-status"


def remove_background_with_polling(image_url: str ,max_retries: int = 10, retry_delay: int = 3) -> dict:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": lightx_api_key
    }
    data = {
        "imageUrl": image_url,
        "background": ""
    }
    


    try:
        logger.info("Initiating background removal with LightX API.")
        response = requests.post(LIGHTX_REMOVE_BG_URL, headers=headers, json=data)
        response_data = response.json()
        logger.info("Initial LightX API Response: %s", response_data)

        if response.status_code != 200 or response_data.get("statusCode") != 2000:
            logger.error("Failed to initiate background removal. Status Code: %d, Message: %s",
                         response.status_code, response.text)
            raise HTTPException(status_code=500, detail="Failed to initiate background removal.")

        order_id = response_data["body"]["orderId"]
        logger.info("Background removal initiated. Order ID: %s", order_id)
        
        payload = {
             "orderId": order_id
        }

        # Polling for background removal status
        for attempt in range(1, max_retries + 1):
            logger.info("Polling attempt %d/%d...", attempt, max_retries)
            poll_response = requests.get(LIGHTX_ORDER_STATUS_URL, headers=headers, json=payload)
            poll_data = poll_response.json()
            logger.debug("Polling Response: %s", poll_data)

            if poll_response.status_code != 200:
                logger.error("Polling failed. Status Code: %d, Response: %s",
                             poll_response.status_code, poll_response.text)
                raise HTTPException(status_code=500, detail="Failed to poll LightX API for status.")

            status = poll_data.get("body", {}).get("status")
            logger.info("Polling status: %s", status)

            if status == "active":
                image_url = poll_data.get("body", {}).get("output")
                if not image_url:
                    logger.error("Background removal completed but no output URL found.")
                    raise HTTPException(status_code=500, detail="No output URL found.")

                logger.info("Background removal completed successfully. Output URL: %s", image_url)
           
                return {"output_url": image_url}
            elif status == "failed":
                logger.error("Background removal failed on LightX API.")
                raise HTTPException(status_code=500, detail="Background removal failed on LightX API.")

            time.sleep(retry_delay)

        logger.error("Background removal timed out after %d attempts.", max_retries)
        raise HTTPException(status_code=500, detail="Background removal timed out.")

    except Exception as e:
        logger.exception("Error in remove_background_with_polling function: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


    
    
def save_image_from_url(url: str, save_path: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        return save_path
    else:
        raise HTTPException(status_code=500, detail="Failed to download processed image.")

def trim_image(image_path: str) -> str:
    trimmed_image_path = image_path.replace(".png", "_trimmed.png")
    
    img = Image.open(image_path).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        trimmed = img.crop(bbox)
        trimmed.save(trimmed_image_path)
        return trimmed_image_path
    else:
        raise HTTPException(status_code=500, detail="Failed to trim the image.")

@app.post("/remove-background")
async def remove_background_endpoint(
    image_file: UploadFile = File(None), 
    image_url: str = Form(None), 
    background: str = Form(None), 
):
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required.")
    
    try:
        # Step 1: Remove Background using LightX API
        response = remove_background_with_polling(image_url)
        processed_image_url = response.get("output_url")
        
        if not processed_image_url:
            raise HTTPException(status_code=500, detail="Failed to remove background.")
        
        # Step 2: Save the processed image locally
        processed_image_path = f"./static/processed_image_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
        save_image_from_url(processed_image_url, processed_image_path)

        # Step 3: Trim the processed image
        trimmed_image_path = trim_image(processed_image_path)
        logger.info(f"Trimmed image saved to: {trimmed_image_path}")

        # Step 4: If background is provided, overlay the trimmed image
        if background:
            background_image_path = f"./Background/{background}.jpg"
            if not os.path.exists(background_image_path):
                raise HTTPException(status_code=404, detail="Background image not found")

            logger.info(f"Merging with background: {background_image_path}")
            filename = f"output_img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
            public_url = overlay_person_on_background(
                trimmed_image_path, background_image_path,
                output_dir="static", output_filename=filename
            )
            logger.info(f"Final image available at: {public_url}")
            return {"url": public_url}

        # If no background is provided, return the trimmed image URL
        return FileResponse(trimmed_image_path, filename="background_removed.png")

    except Exception as e:
        logger.error(f"Error in /remove-background: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


"""