from fastapi import FastAPI
from app.api.routes.check_link_api import router as analyze_router
from app.api.routes.check_similarity_api import router as similarity_router
from app.api.routes.check_clickbait_api import router as clickbait_router
from app.api.routes.hatespeech_api import router as hatespeech_router

app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the analyze router
app.include_router(analyze_router)

# Include the similarity router
app.include_router(similarity_router)

# Include the clickbait router
app.include_router(clickbait_router)

# Include the hatespeech router
app.include_router(hatespeech_router)

print("helloo")
