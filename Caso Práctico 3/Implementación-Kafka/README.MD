## Descripción

Extensión del sistema de pedidos del Ejercicio 2: cada cambio de estado de un pedido (`CREATED`, `CONFIRMED`, `SHIPPED`) se publica como evento en un topic de Kafka (`order-events`) y es consumido de forma independiente por dos servicios:

- **NotificationService:** simula el envío de un correo al cliente según el estado.
- **AnalyticsService:** cuenta los eventos por estado y calcula el tiempo entre la creación y el envío de cada pedido.

## Arquitectura

```
OrdersService ──► topic "order-events" ──┬─► NotificationService (group: notification-service)
 (producer)        (3 particiones)       └─► AnalyticsService    (group: analytics-service)
```

- Cada servicio consume con un **consumer group distinto**, por lo que ambos reciben todos los eventos.
- La **key** de cada mensaje es el `orderId`: los eventos de un mismo pedido van a la misma partición y se procesan en orden.

## Tecnologías

- Node.js
- [kafkajs](https://kafka.js.org/)
- Apache Kafka 3.9 (modo KRaft, sin Zookeeper)
- Docker Compose

## Estructura del proyecto

```
punto3/
├── docker-compose.yml
├── orders-service.js
├── notification-service.js
├── analytics-service.js
├── package.json
└── README.md
```

## Formato del evento

```json
{
  "eventId": "uuid",
  "orderId": 101,
  "status": "CREATED",
  "occurredAt": "2026-10-05T12:00:00.000Z",
  "customerEmail": "cliente@mail.com",
  "total": 15000
}
```

`customerEmail` y `total` se envían solo en el evento `CREATED`.

## Requisitos

- Node.js
- Docker Desktop

## Cómo ejecutarlo

Desde la carpeta del proyecto, en cmd:

1. Levantar Kafka y crear el topic:

```cmd
docker compose up -d
docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --topic order-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

2. Instalar dependencias:

```cmd
npm install
```

3. Ejecutar cada servicio en su propia terminal, en este orden:

```cmd
node notification-service.js
node analytics-service.js
node orders-service.js
```

## Resultado esperado

Notification y Analytics muestran los eventos `CREATED`, `CONFIRMED` y `SHIPPED` de los pedidos 101 y 102.

## Pruebas realizadas

- **Consumidor caído:** se detuvo NotificationService, se publicaron eventos y al reiniciarlo recibió los eventos pendientes gracias al offset de su consumer group.
- **Reprocesamiento:** al usar un `groupId` nuevo con `fromBeginning: true`, el servicio leyó todo el historial del topic.

## Kafka vs RabbitMQ en este escenario

| Aspecto                    | RabbitMQ                                                    | Kafka                                                                   |
| -------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------- |
| Modelo                     | Broker de mensajes: el mensaje se elimina al ser confirmado | Log de eventos: los mensajes se retienen según la política de retención |
| Varios consumidores        | Exchange `fanout`/`topic` y una cola por servicio           | Un consumer group por servicio sobre el mismo topic                     |
| Nuevo servicio (Analytics) | Solo ve mensajes desde que se enlaza su cola                | Puede leer todo el historial                                            |
| Reprocesamiento            | No es natural                                               | Se pueden reubicar los offsets                                          |
| Orden                      | Por cola                                                    | Por partición (con `orderId` como key)                                  |
| Ideal para                 | Tareas y comandos                                           | Streams de eventos y analítica                                          |

**Conclusión:** los cambios de estado son hechos que ocurrieron y que varios servicios necesitan leer, incluso uno futuro que requiera el histórico, por lo que Kafka encaja mejor.
