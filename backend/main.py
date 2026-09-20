from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


app = FastAPI()
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class ItemCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None


class ItemPublic(ItemCreate):
    id: int


class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int


class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float


class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"


items: dict[int, ItemPublic] = {}
next_id = 1


def ensure_unique_name(name: str, exclude_id: int | None = None) -> None:
    normalized_name = name.casefold()
    for item_id, item in items.items():
        if item_id != exclude_id and item.name.casefold() == normalized_name:
            raise HTTPException(
                status_code=409,
                detail="Item with this name already exists",
            )


@app.get("/")
def read_root():
    return {"message": "Item API is running"}


@app.get("/items", response_model=ItemListResponse)
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    filtered_items = list(items.values())

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    if q is not None:
        search_term = q.casefold()
        filtered_items = [item for item in filtered_items if search_term in item.name.casefold()]

    filtered_items.sort(key=lambda item: getattr(item, sort_by), reverse=order == "desc")
    total = len(filtered_items)
    page_items = filtered_items[skip : skip + limit]

    return ItemListResponse(items=page_items, total=total, skip=skip, limit=limit)


@app.get("/items/{item_id}", response_model=ItemPublic)
def get_item(item_id: int):
    item = items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
    global next_id

    ensure_unique_name(data.name)
    item = ItemPublic(id=next_id, **data.model_dump())
    items[next_id] = item
    next_id += 1
    return item


@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemCreate):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    ensure_unique_name(data.name, exclude_id=item_id)
    item = ItemPublic(id=item_id, **data.model_dump())
    items[item_id] = item
    return item


@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, data: ItemUpdate):
    existing_item = items.get(item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    changes = data.model_dump(exclude_unset=True)
    new_name = changes.get("name")
    if new_name is not None:
        ensure_unique_name(new_name, exclude_id=item_id)

    updated_item = existing_item.model_copy(update=changes)
    items[item_id] = updated_item
    return updated_item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    del items[item_id]
    return {"message": "Item deleted"}


@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(data: HousePriceRequest):
    price = (
        data.area_sqm * 15_000_000
        - data.distance_to_center_km * 5_000_000
        + data.bedrooms * 20_000_000
    )
    return HousePricePrediction(predicted_price=price)
