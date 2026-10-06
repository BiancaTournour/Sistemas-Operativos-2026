# Ejercicio 1 – Comunicación síncrona con REST
 
Prototipo con dos microservicios en Python (FastAPI). **OrdersService** consulta a **InventoryService** por REST si hay stock antes de confirmar un pedido.
 
```
Cliente ──POST /orders──▶ OrdersService (:8000) ──GET /inventory/{id}──▶ InventoryService (:8001)
                                   ◀────────── { available: true/false } ──────────┘
```
 
## Estructura
 
```
Implementación-REST/
├── inventory_service.py                      # InventoryService (puerto 8001)
├── orders_service.py                         # OrdersService (puerto 8000)
├── requirements.txt
├── orders_inventory.postman_collection.json  # Colección para Postman
└── README.md
```
 
## Requisitos
 
- Python 3.9 o superior
- Postman (opcional)
## Instalación
 
```powershell
cd C:\Users\bmtou\VScode\SO\CP3\Implementación-REST
pip install -r requirements.txt
```
 
## Ejecución
 
Abre **dos terminales** en la carpeta del proyecto y deja ambas corriendo.
 
**Terminal 1: InventoryService**
```powershell
python -m uvicorn inventory_service:app --port 8001
```
 
**Terminal 2: OrdersService**
```powershell
python -m uvicorn orders_service:app --port 8000
```
 
Documentación interactiva (Swagger):
- Orders: http://localhost:8000/docs
- Inventory: http://localhost:8001/docs
## Datos de prueba (stock en memoria)
 
| Producto | Nombre | Stock |
|---|---|---|
| `P001` | Teclado mecánico | 10 |
| `P002` | Mouse gamer | 0 |
| `P003` | Monitor 24" | 3 |
 
## API
 
### `POST /orders` (OrdersService)
 
Body:
```json
{ "product_id": "P001", "quantity": 2 }
```
 
| Código | Significado |
|---|---|
| `201` | Pedido confirmado (`status: CONFIRMED`) |
| `404` | El producto no existe |
| `409` | Stock insuficiente |
| `422` | Body inválido (p. ej. `quantity` ≤ 0) |
| `502` | Respuesta inesperada de InventoryService |
| `503` | InventoryService no disponible |
| `504` | InventoryService no respondió en 2 s |
 
### `GET /inventory/{product_id}?quantity=N` (InventoryService)
 
Respuesta:
```json
{ "product_id": "P001", "name": "Teclado mecánico", "stock": 10, "requested": 2, "available": true }
```
 
## Cómo probar
 
### Opción A: PowerShell
 
> En PowerShell `curl` es un alias de `Invoke-WebRequest`; usa `Invoke-RestMethod` o `curl.exe`.
 
```powershell
# Pedido con stock (201)
Invoke-RestMethod -Method Post -Uri http://localhost:8000/orders `
  -ContentType "application/json" `
  -Body '{"product_id":"P001","quantity":2}'
 
# Sin stock (409): mostrar solo el detalle del error
try {
  Invoke-RestMethod -Method Post -Uri http://localhost:8000/orders `
    -ContentType "application/json" `
    -Body '{"product_id":"P002","quantity":1}'
} catch { $_.ErrorDetails.Message }
 
# Consultar Inventory directamente
Invoke-RestMethod "http://localhost:8001/inventory/P003?quantity=2"
```
 
Alternativa con curl real:
```powershell
curl.exe -X POST http://localhost:8000/orders -H "Content-Type: application/json" -d '{\"product_id\":\"P001\",\"quantity\":2}'
```
 
### Opción B: Postman
 
1. **Import** → seleccionar `orders_inventory.postman_collection.json`.
2. Ejecutar cada request o usar **Run collection**. Incluye pruebas automáticas para `201`, `409` y `404`.
### Opción C: Swagger
 
Abrir http://localhost:8000/docs → `POST /orders` → **Try it out**.
 
## Probar fallas de red (acoplamiento síncrono)
 
1. Detén InventoryService (`Ctrl+C` en la Terminal 1).
2. Envía un pedido a OrdersService.
3. Resultado esperado: `503 InventoryService no disponible`.
Esto muestra la principal desventaja de la comunicación síncrona: **OrdersService depende de que InventoryService esté disponible en ese momento**.
 
## Comparación gRPC vs REST (para este escenario)
 
| Aspecto | REST (JSON/HTTP) | gRPC (Protobuf/HTTP2) |
|---|---|---|
| Contrato | Informal (OpenAPI opcional) | Estricto (`.proto`) con código generado |
| Rendimiento | Texto, más pesado | Binario, más compacto y rápido |
| Simplicidad | Muy alta (`curl`, navegador, Postman) | Requiere generar código y herramientas específicas |
| Depuración | Fácil de leer | Más difícil (binario) |
| Streaming | Limitado | Nativo, bidireccional |
| Compatibilidad | Universal | Limitada en navegadores (grpc-web) |
| Timeouts | Manuales | *Deadlines* integrados |
 
**Conclusión:** la consulta de stock es pequeña y simple, por lo que REST es suficiente y más práctico para un prototipo. gRPC se justificaría con muy alto volumen de llamadas, muchos servicios internos encadenados o necesidad de contratos fuertemente tipados.
 
## Limitaciones del prototipo
 
- **Acoplamiento temporal:** si Inventory cae, no se confirman pedidos.
- **Condición de carrera:** entre consultar y confirmar, otro pedido puede consumir el stock. En producción se usaría un endpoint de **reserva** (`POST /inventory/{id}/reserve`).
- **Sin persistencia:** stock y pedidos viven en memoria y se pierden al reiniciar.
- **Latencia acumulada** si la cadena de llamadas entre servicios crece.
 