# capture_bridge.py

from fastapi import WebSocket


image_futures = {}
clients = []

def register_client(ws: WebSocket):
    """Register a new client connection."""
    clients.append(ws)

def unregister_client(ws: WebSocket):
    """Unregister a client connection."""
    if ws in clients:
        clients.remove(ws)

def resolve_image(tool_call_id: str, image_data: str):
    """Resolve the image capture and fulfill the corresponding future."""
    if tool_call_id in image_futures:
        future = image_futures.pop(tool_call_id)
        future.set_result(image_data)

async def broadcast_capture_request(tool_call_id: str):
    """Broadcast an image capture request to all connected clients."""
    for client in clients:
        await client.send_json({
            "type": "capture_image",
            "tool_call_id": tool_call_id
        })