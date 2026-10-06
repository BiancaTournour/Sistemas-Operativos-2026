"""InventoryService - responde si un producto tiene stock suficiente."""
from fastapi import FastAPI, HTTPException

app = FastAPI(title="InventoryService")

# "Base de datos" en memoria
STOCK = {
    "P001": {"name": "Teclado mecánico", "stock": 10},
    "P002": {"name": "Mouse gamer", "stock": 0},
    "P003": {"name": "Monitor 24\"", "stock": 3},
}


@app.get("/inventory/{product_id}")
def check_availability(product_id: str, quantity: int = 1):
    item = STOCK.get(product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Producto inexistente")

    return {
        "product_id": product_id,
        "name": item["name"],
        "stock": item["stock"],
        "requested": quantity,
        "available": item["stock"] >= quantity,
    }
