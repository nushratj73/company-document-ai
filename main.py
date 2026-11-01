
from fastapi import FastAPI
from routers.auth import router as auth_router

app = FastAPI(
    title="Company Document AI",
    description="API for company document management and intelligent search",
    version="0.1.0",
)

# Register authentication routes
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Company Document AI API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "company-doc-ai"
    }