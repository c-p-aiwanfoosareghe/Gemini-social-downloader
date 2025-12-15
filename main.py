# app/main.py
from fastapi import FastAPI
from app.api.router import router

app = FastAPI(
    title="Public Content Downloader API", 
    version="1.0.0",
    description="Backend server to download publicly available content from Instagram and Facebook."
)

# Include the router to add all defined endpoints to the application
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Public Content Downloader API is running. Check /docs for endpoints."}
