import atexit
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys

# append the path of the parent directory
sys.path.append("..")

from plebs import plebs, pockets
from state import AppState

app = FastAPI()
state = AppState()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def close_gracefully():
    state.close()


@app.get("/pockets")
async def get_pockets(request: Request, number: int = 1):
    global state
    client_host = request.client.host
    state.log_visit(client_host, "pockets")
    return pockets._pockets(number)


@app.get("/plebs")
async def get_plebs(request: Request, number: int = 1):
    global state
    client_host = request.client.host
    state.log_visit(client_host, "plebs")
    return plebs._plebs(number)


@app.get("/visits")
async def get_visits(request: Request):
    global state
    client_host = request.client.host
    state.log_visit(client_host, "visits")
    return state.visits

atexit.register(close_gracefully)
