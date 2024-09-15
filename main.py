from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ここを必要に応じて適切なURLに設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルを提供する設定
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 テンプレートの設定
templates = Jinja2Templates(directory="templates")

# WebSocket接続を保持するためのリスト
connections: List[WebSocket] = []

class TimeData(BaseModel):
    time: str

@app.post("/update_time")
async def update_time(data: TimeData):
    for connection in connections:
        await connection.send_text(data.time)
    return {"message": "Time updated"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data from websocket: {data}")
    except WebSocketDisconnect:
        connections.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    # テンプレートを使って動的なデータを渡す
    return templates.TemplateResponse("index.html", {"request": request, "time": "2024-09-15T12:00:00Z"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)