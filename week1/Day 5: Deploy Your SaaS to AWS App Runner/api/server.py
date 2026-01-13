from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from openai import OpenAI

app = FastAPI()

# Initialize OpenAI Client safely
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/consultation")
async def consultation(request: Request):
    print("Request received at /api/consultation")
    if not client:
        return {"error": "OpenAI API Key not configured"}
        
    try:
        body = await request.json()
        symptoms = body.get("symptoms", "No symptoms provided")
        
        async def generate():
            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Analyze: {symptoms}"}],
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        # FIXED LINE BELOW (Added the missing } after 'text')
                        yield f"data: {json.dumps({'text': text})}\n\n"
            except Exception as inner_e:
                print(f"STREAM ERROR: {inner_e}")
                yield f"data: {json.dumps({'text': 'AI processing error'})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        print(f"GENERAL ERROR: {e}")
        return {"error": str(e)}

# Serve static files
if os.path.exists("./static"):
    app.mount("/_next", StaticFiles(directory="./static/_next"), name="nextjs-assets")
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path): return FileResponse(file_path)
        html_file = os.path.join("static", f"{full_path}.html")
        if os.path.isfile(html_file): return FileResponse(html_file)
        return FileResponse("static/index.html")