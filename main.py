from fastapi import FastAPI
from bonna_simulation import api_calistir

app = FastAPI()

@app.post("/paletle")
def paletle(data: dict):

    palet = data["palet"]
    urunler = data["urunler"]

    return api_calistir(
        urunler,
        palet["en"],
        palet["boy"],
        palet["yukseklik"]
    )