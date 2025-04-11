from fastapi import FastAPI
from app.api.routes.check_link_api import router as analyze_router
from app.api.routes.check_similarity_api import router as similarity_router

app = FastAPI()

# Include the analyze router
app.include_router(analyze_router)

# Include the similarity router
app.include_router(similarity_router)  # Register the similarity router


print("helloo")