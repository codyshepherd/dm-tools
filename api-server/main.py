from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys

# append the path of the parent directory
sys.path.append("..")

from plebs import plebs, pockets

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/pockets")
async def get_pockets(number: int = 1):
    return pockets._pockets(number)


@app.get("/plebs")
async def get_plebs(number: int = 1):
    return plebs._plebs(number)
