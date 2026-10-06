"""OrdersService - consulta síncronamente a InventoryService antes de confirmar."""
import itertools

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

INVENTORY_URL = "http://localhost:8001"
TIMEOUT_SECONDS = 2.0  # en llamadas síncronas SIEMPRE definir timeout

app = FastAPI(title="OrdersService")

ORDERS: dict[int, dict] = {}
_order_id = itertools.count(1)


class OrderRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


@app.post("/orders", status_code=201)
def create_order(order: OrderRequest):
    # 1) Llamada síncrona a InventoryService (el pedido espera la respuesta)
    try:
        resp = httpx.get(
            f"{INVENTORY_URL}/inventory/{order.product_id}",
            params={"quantity": order.quantity},
            timeout=TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException:
        raise HTTPException(504, "InventoryService no respondió a tiempo")
    except httpx.RequestError:
        raise HTTPException(503, "InventoryService no disponible")

    # 2) Traducir las respuestas del servicio remoto
    if resp.status_code == 404:
        raise HTTPException(404, "El producto no existe")
    if resp.status_code != 200:
        raise HTTPException(502, "Respuesta inesperada de InventoryService")

    inventory = resp.json()

    # 3) Decisión de negocio
    if not inventory["available"]:
        raise HTTPException(
            409,
            f"Stock insuficiente (disponible: {inventory['stock']}, "
            f"pedido: {order.quantity})",
        )

    # 4) Confirmar el pedido
    order_id = next(_order_id)
    ORDERS[order_id] = {
        "id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "CONFIRMED",
    }
    return ORDERS[order_id]
