from fastapi import FastAPI
from api.routes.analyze import router as analyze_router

app = FastAPI()

# Include the analyze router
app.include_router(analyze_router)