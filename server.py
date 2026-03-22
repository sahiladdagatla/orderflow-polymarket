from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from find_signals import find_signals

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/scan")
def scan():
    results = find_signals(max_markets=25)
    return {"markets": results}