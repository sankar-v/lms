from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import users, modules, progress, recommendations, chat

app = FastAPI(
    title="LMS API",
    description="Learning Management System API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(modules.router, prefix="/api/v1/modules", tags=["modules"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "LMS API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
