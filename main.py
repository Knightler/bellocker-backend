from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "meta-llama/llama-3-8b-instruct"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class AnalyzeRequest(BaseModel):
    html_chunk: str

@app.post("/analyze")
async def analyze_ad(request: AnalyzeRequest):
    prompt = f"""
    You are an AI ad detector. Based on the following HTML content, determine if it is an advertisement, native ad, or promotional content. Reply only with `ad` or `not ad`.

    HTML:
    {request.html_chunk}
    """

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        result = response.json()
        print(result)  # ✅ Add this line

        # Add this block to avoid crashing
        if "choices" not in result:
            return {"error": "AI call failed", "details": result}

        content = result['choices'][0]['message']['content'].strip().lower()
        return {"classification": content}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)