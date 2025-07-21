from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ImageGetterAPI import app as ImageGetterApp
from image_tools.MockupApi import app as mockupApiApp

api = FastAPI()

# Mount both FastAPI apps inside the single /api path
api.mount("/mockup", mockupApiApp)
api.mount("/parts", ImageGetterApp)

app = FastAPI()

# Mount backend
app.mount("/api", api)

# Serve frontend static files (HTML, CSS, JS)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
