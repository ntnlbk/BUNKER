from fastapi import FastAPI, Depends # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from dataclasses import asdict  

app = FastAPI(title="Bunker Game API")

@app.get("/")
def read_root():
    return JSONResponse(
        content={"message": "Bunker is live!"},
        media_type="application/json; charset=utf-8"
    )