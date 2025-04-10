# app/main.py
from fastapi import FastAPI
from app.api.routes.check_link_api import router as analyze_router

app = FastAPI()

# Include the analyze router
app.include_router(analyze_router)
print("Heelooo")