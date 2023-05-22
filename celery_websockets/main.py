from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from celery import Celery
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="static")
import os
from pathlib import Path

BASEDIR = Path(__file__).resolve().parent

fast_app = FastAPI()
fast_app.mount("/static", StaticFiles(directory=os.path.join(BASEDIR, "static")), name="static")

# Configure Celery
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Replace with your Redis broker URL
    backend='redis://localhost:6379/0'  # Replace with your Redis backend URL
)

connected_websockets = set()


@celery.task
def upload_image(image_path: str):
    # Your image upload logic here
    # Simulating a delay for demonstration purposes
    import time
    time.sleep(2)
    message = f"Image uploaded: {image_path}"
    notify_progress.delay(message)


@celery.task
def notify_progress(message: str):
    for websocket in connected_websockets:
        websocket.send_text(message)


@fast_app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@fast_app.post("/upload")
async def upload_images(background_tasks: BackgroundTasks):
    images = ["image1.jpg", "image2.jpg", "image3.jpg"]  # Replace with your list of image paths
    for image_path in images:
        upload_image.delay(image_path)
    return {"message": "Upload process started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fast_app)
