
from fastapi import FastAPI

app = FastAPI(
    title="Company Document AI",
    description="API for company document management and intelligent search",
    version="0.1.0",
)


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

