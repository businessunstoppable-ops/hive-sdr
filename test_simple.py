from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def home(request: Request):
    return HTMLResponse("<h1>HIVE-SDR is running</h1><p>If you see this, the server is fine.</p>")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=54609)
