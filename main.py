from fastapi import FastAPI
from bonna_simulation import api_calistir

app = FastAPI()

@app.post("/paletle")
def paletle(data: dict):
    palet_en = data["palet"]["en"]
    palet_boy = data["palet"]["boy"]
    palet_yuk = data["palet"]["yukseklik"]

    wms_emri = data["urunler"]

    sonuc = api_calistir(
        wms_emri,
        palet_en,
        palet_boy,
        palet_yuk
    )

    return sonuc