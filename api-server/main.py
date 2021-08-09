from fastapi import FastAPI
import sys

# append the path of the parent directory
sys.path.append("..")

from plebs import plebs, pockets

app = FastAPI()


@app.get("/pockets")
async def get_pockets(number: int = 1):
    return pockets._pockets(number)


@app.get("/plebs")
async def get_plebs(number: int = 1):
    return plebs._plebs(number)
