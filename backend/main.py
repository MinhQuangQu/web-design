from pathlib import Path
import asyncio

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


def predict_price(area: float, bedrooms: int, location: str) -> float:
    """Return the estimated house price in VND, rounded to the nearest million."""
    total_price = 500_000_000 + (15_000_000 * area) + (50_000_000 * bedrooms)
    normalized_location = location.strip().lower()

    if normalized_location == "hanoi":
        total_price *= 1.3
    elif normalized_location == "hcmc":
        total_price *= 1.25

    return float(int(total_price / 1_000_000 + 0.5) * 1_000_000)


# This endpoint is synchronous because the calculation is plain CPU work with no I/O to await.
@app.get("/predict")
def predict_endpoint(area: float, bedrooms: int, location: str = "other"):
    return {
        "predicted_price": predict_price(area, bedrooms, location),
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
    }


class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"


@app.post("/predict")
def predict_from_body(house: HouseInput):
    return {
        "predicted_price": predict_price(house.area, house.bedrooms, house.location),
        "area": house.area,
        "bedrooms": house.bedrooms,
        "location": house.location,
    }


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
