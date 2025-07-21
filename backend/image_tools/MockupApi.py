from pydantic_core import Url
from MockupGen import generate_mug_mockup
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
import requests
import io
import uvicorn

app = FastAPI()

# Enable CORS so frontend JS can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/mockup")
async def create_mockup(image: UploadFile = File(...), text: str = Form(...)):
    image_bytes = await image.read()

    user_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    
    # Your existing image processing here (remove bg, add text, generate mockup)
    img_bytes = generate_mug_mockup(user_img,'backend/image_tools/mug_base.png',text)
    
    return StreamingResponse(img_bytes, media_type="image/png")

@app.post("/api/mockupurl")
async def create_mockup(image_url: str = Form(...), text: str = Form(...)):
    try:
        # Download the image from the provided URL
        headers = {
            'User-Agent': 'My User Agent 1.0',
            'From': 'youremail@domain.example'  # This is another valid field
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

    try:
        # Convert to PIL image
        user_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    # Generate mug mockup (your existing function)
    img_bytes = generate_mug_mockup(user_img, 'backend/image_tools/mug_base.png', text)

    return StreamingResponse(img_bytes, media_type="image/png")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
