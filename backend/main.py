from pathlib import Path
import asyncio

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/")
def read_root():
    return FileResponse(FRONTEND_DIR / "house_form.html")

@app.get('/hello/{name}')
def hello(name: str):
    return {"Greeting": f"Hello {name}"}

@app.get("/add")
async def add(a: int, b: int):
    await asyncio.sleep(3)      # delay
    return {"a": a, "b": b, "sum": a + b}

@app.get("/predict")
async def predict_price(area: float, bedrooms: int, location: str):
    base_price = 500
    area_price = 15 * area
    bedroom_price = 50 * bedrooms
    total_price = base_price + area_price + bedroom_price

    if location == "hanoi":
        total_price *= 1.3
    elif location == "hcmc":
        total_price *= 1.25

    return {
        "predicted_price": total_price,
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
    }


# Phải đặt sau các API routes để /predict vẫn được FastAPI xử lý.
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
