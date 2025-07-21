from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from DigikeyImageFinder import DigikeyImageFinder
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

@app.get("/api/part-image")
def get_part_image(mpn: str = Query(...)):
    part_info = image_finder.get_part_image(mpn)
    print(part_info)
    if part_info['image_url']:
        return {"image_url": part_info['image_url']}
    return {"error": "Image not found"}



if __name__ == "__main__":
    image_finder = DigikeyImageFinder()
    uvicorn.run(app, host="0.0.0.0", port=8001)
