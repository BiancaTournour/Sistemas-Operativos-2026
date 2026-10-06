# Ejercicio 2 – Comunicación asíncrona con RabbitMQ

Dos microservicios NestJS que se comunican mediante una cola de RabbitMQ:

- **orders-service** (productor): expone `POST /orders`, crea el pedido y publica el evento `order_created`.
- **notification-service** (consumidor): lee la cola `notifications_queue` y envía un correo al cliente.
- **RabbitMQ**: corre en Docker y actúa como intermediario (broker).

```
Cliente ──POST /orders──> orders-service ──order_created──> RabbitMQ ──> notification-service ──> mail
```

## Estructura

```
ejercicio2/
├── docker-compose.yml
├── orders-service/
│   └── src/ (main.ts, app.module.ts, app.controller.ts, app.service.ts)
└── notification-service/
    └── src/ (main.ts, mail.service.ts)
```

## Requisitos

- Node.js 20 o superior
- Docker Desktop (abierto y corriendo)
- Conexión a internet (el correo de prueba usa Ethereal)

## 1. Levantar RabbitMQ

Desde la carpeta donde está `docker-compose.yml`:

```
docker compose up -d
docker compose ps
```

El contenedor `rabbitmq` debe figurar como *running*.

- Panel de administración: http://localhost:15672
- Usuario: `guest` / Contraseña: `guest`
- Puerto AMQP: `5672`

## 2. Instalar dependencias (una sola vez)

```
cd orders-service
npm install
cd ..\notification-service
npm install
```

Si faltan paquetes:

```
:: orders-service
npm i @nestjs/microservices amqplib amqp-connection-manager

:: notification-service
npm i amqplib nodemailer
npm i -D @types/amqplib @types/nodemailer
```

## 3. Ejecutar los servicios

Abrir **tres terminales** (cmd).

**Terminal 1 – notification-service**

```
cd notification-service
npm run build
npm run start
```

Debe mostrar: `NotificationService escuchando notifications_queue...`

**Terminal 2 – orders-service**

```
cd orders-service
npm run build
npm run start
```

Debe terminar con: `Nest application successfully started` (puerto 3000).

**Terminal 3 – enviar pedidos**

```
curl -X POST http://localhost:3000/orders -H "Content-Type: application/json" -d "{\"customerEmail\":\"cliente@test.com\",\"product\":\"Teclado\"}"
```

## 4. Resultado esperado

- La terminal 3 devuelve el pedido en JSON con su `id`.
- La terminal 1 muestra:

```
Pedido recibido: <id>
Mail enviado. Verlo en: https://ethereal.email/message/...
```

- Al abrir ese link en el navegador se ve el correo enviado.

## 5. Prueba: ¿qué pasa si NotificationService está caído?

1. En la terminal 1, detener `notification-service` con `Ctrl + C` (si pregunta por el trabajo por lotes, responder `S`).
2. Enviar 3 pedidos con el `curl` anterior. `orders-service` responde con normalidad.
3. Abrir http://localhost:15672 → **Queues** → `notifications_queue`. Deben verse **3 mensajes en *Ready*** y **0 consumers**.
4. Volver a iniciar `notification-service` (`npm run start`).
5. Los 3 mensajes se consumen, llegan los 3 correos y la cola vuelve a **0**.

**Conclusión:** no se pierde ningún mensaje. La cola es *durable* y los mensajes *persistentes*, por lo que RabbitMQ los guarda hasta que el consumidor vuelve. Además, el consumidor usa confirmación manual (`ack`): si falla a mitad de procesamiento, el mensaje vuelve a la cola. La entrega es *at-least-once*, por lo que puede haber duplicados y conviene que el consumidor sea idempotente.

## 6. Detener todo

```
Ctrl + C          :: en cada terminal de Node
docker compose down
```

## Notas técnicas

- El proyecto usa módulos ESM: los imports relativos terminan en `.js` (por ejemplo `'./app.module.js'`).
- `notification-service` consume la cola directamente con `amqplib` (en lugar de `@EventPattern`). El mensaje publicado por `orders-service` tiene el formato `{ "pattern": "order_created", "data": { ... } }`.
- Los correos se envían con una cuenta de prueba de **Ethereal** (se crea al iniciar el servicio), por lo que no se envían mails reales.

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `Failed to connect to localhost:3000` | `orders-service` no está corriendo. Iniciarlo con `npm run start`. |
| `ECONNREFUSED 127.0.0.1:5672` | RabbitMQ no está levantado. Abrir Docker Desktop y ejecutar `docker compose up -d`. |
| `Cannot find module './app.service'` | Falta la extensión `.js` en el import, o el archivo no se guardó. |
| El mensaje se consume pero no hay mail | Revisar la conexión a internet (Ethereal) y los errores en la terminal de `notification-service`. |
| Mensajes que no bajan de *Ready* | `notification-service` no está corriendo, o hay otra copia abierta. Ver **Consumers** en el panel. |
