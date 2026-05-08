from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
db = {}

#req model
class ItemCreate(BaseModel):
    name: str
    price: float

#res model
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

#create 
@app.post("/items/{item_id}", response_model=ItemResponse)
async def create(item_id: int, item: ItemCreate):
    db[item_id] = item
    return {"id": item_id, **item.model_dump()}

#read
@app.get("/items/{item_id}", response_model=ItemResponse)
async def read(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    item = db[item_id]
    return {"id": item_id, **item.model_dump()}

#update
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update(item_id: int, item: ItemCreate):
    if item_id not in db:
        raise HTTPException(status_code=404, details="Item not found")
    db[item_id] = item
    return {"id": item_id, **item.model_dump()}

#delete
@app.delete("/items/{item_id}", response_model=ItemResponse)
async def delete(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, details="Item not found")
    del db[item_id]
    return {"msg": "deleted item"}