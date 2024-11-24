import os
import subprocess
import tempfile
import uuid
from typing import Dict, List, Optional
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from fastapi.responses import HTMLResponse

from agents.llm_models import chat_model
from agents.main_graph import main_graph

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

app = FastAPI(title="Canadian Government AI Assistant Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WebsiteRequest(BaseModel):
    url: str = Field(..., description="URL of the website to fetch")

@app.post("/fetch_website_content")
async def fetch_website_content(request: WebsiteRequest):
    try:
        base_url = "https://www.canada.ca"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(request.url)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch website")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove header
            header = soup.find("header")
            if header:
                header.decompose()

            # Remove footer
            footer = soup.find("footer")
            if footer:
                footer.decompose()

            # Remove all images
            for img in soup.find_all("img"):
                img.decompose()

            # remove div with class alert-warning
            for div in soup.find_all("div", class_="alert-warning"):
                div.decompose()

            # Fix image sources
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    if src.startswith('/'):
                        img['src'] = f"{base_url}{src}"
                    elif not src.startswith(('http://', 'https://')):
                        img['src'] = f"{base_url}/{src}"

            # Fix other assets (CSS, JS, etc.)
            for tag in soup.find_all(['link', 'script']):
                for attr in ['src', 'href']:
                    if tag.get(attr) and not tag.get(attr).startswith(('http://', 'https://', '//')):
                        if tag.get(attr).startswith('/'):
                            tag[attr] = f"{base_url}{tag[attr]}"
                        else:
                            tag[attr] = f"{base_url}/{tag[attr]}"

            return HTMLResponse(content=str(soup), status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
