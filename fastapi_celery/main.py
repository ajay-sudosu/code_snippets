from fastapi import FastAPI, BackgroundTasks
from celery_task_app.main import task_test

app = FastAPI()


@app.get("/")
async def index():
    return {"message": "Hello world."}


@app.get("/background")
async def check(data: BackgroundTasks):
    try:
        result = {"name": "Hello"}
        data.add_task(check_celery_function)
        return {"message": "Success."}
    except Exception as e:
        return {"message": "Failed."}


def check_celery_function():
    task_test.delay()
