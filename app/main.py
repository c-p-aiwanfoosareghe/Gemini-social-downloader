# app/main.py

import os # Needed for general environment handling (though not strictly for this version)
from fastapi import FastAPI
from fastapi.responses import JSONResponse
# 1. Imports for CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
# 2. Imports for Rate Limiting (fastapi-throttle uses no separate init)
# from fastapi_throttle import RateLimiter # Not needed here, only in router

from app.api.router import router

# --- CORS Configuration ---
# Allows requests from any origin for easy local testing. 
# For production, replace "*" with your specific frontend domain.
origins = [
    "*", 
]

# --- Application Setup ---

app = FastAPI(
    title="Public Content Downloader API", 
    version="1.0.0",
    description="Backend server to download publicly available content from Instagram and Facebook."
    # NOTE: The 'lifespan' argument for Redis/fastapi-limiter is REMOVED 
    # since we are using the in-memory fastapi-throttle solution.
)

# 💥 CRITICAL: Add the CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers
)

# Include the router to add all defined endpoints to the application
app.include_router(router)

@app.get("/")
async def root():
    return JSONResponse(
        content={"message": "Public Content Downloader API is running. Check /docs for endpoints."}
    )
