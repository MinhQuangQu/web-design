from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Web!"}

@app.get('/hello/{name}')
def hello(name: str):
    return {"Greeting": f"Hello {name}"}

@app.get("/add")
async def add(a: int, b: int):
    await asyncio.sleep(3)      # delay
    return {"a": a, "b": b, "sum": a + b}