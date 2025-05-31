from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.src.api.search_api import router as search_router

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Khởi tạo FastAPI app
app = FastAPI(
    title="Search Engine API",
    description="API cho tìm kiếm kết hợp từ khóa và ngữ nghĩa",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các origin trong môi trường development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm router
app.include_router(search_router, prefix="/api/v1", tags=["search"])

@app.get("/")
async def root():
    """
    Endpoint kiểm tra server có hoạt động không
    """
    return {
        "status": "ok",
        "message": "Search Engine API đang chạy",
        "version": "1.0.0",
        "docs_url": "/docs"  # URL đến Swagger UI
    }

# Nếu chạy trực tiếp file này
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Tự động reload khi có thay đổi code
    )

