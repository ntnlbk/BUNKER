from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Bunker Game API")

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("app/UI/index.html", "r", encoding="utf-8") as f:
        return f.read()