from database import Base, engine
from fastapi import FastAPI, Response, Request
from routers import router_items, router_users, router_authentication
import time, json

Base.metadata.create_all(engine)

# Initialize app
app = FastAPI()

app.include_router(router_users.router_user)
app.include_router(router_items.router_items)
app.include_router(router_authentication.router_auth)

@app.middleware("http")
async def test_middleware(request: Request, call_next):
    start_time = time.time()
    request = json.loads(await request.body())
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response