# app/main.py

from fastapi import FastAPI
from app.scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Alarm Notification System!"}
