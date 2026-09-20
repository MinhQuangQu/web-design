from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class Item(BaseModel):
    name: str
    price: int
    in_stock: bool = True


class ItemResponse(Item):
    id: int


items: dict[int, ItemResponse] = {}
next_id = 1


@app.get("/")
def read_root():
    return {"message": "Item API is running"}


@app.get("/items", response_model=list[ItemResponse])
def get_items():
    return list(items.values())


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    item = items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(data: Item):
    global next_id

    item = ItemResponse(id=next_id, **data.model_dump())
    items[next_id] = item
    next_id += 1
    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, data: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    item = ItemResponse(id=item_id, **data.model_dump())
    items[item_id] = item
    return item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    del items[item_id]
    return {"message": "Item deleted"}
