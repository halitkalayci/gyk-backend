from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="GYK Backend API", description="Örnek CRUD API", version="1.0.0")

@app.get("/")
async def root():
    """API ana sayfası"""
    return {"message": "GYK Backend API'ye hoş geldiniz!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)