const { Kafka } = require("kafkajs");
const { randomUUID } = require("crypto");

const kafka = new Kafka({
  clientId: "orders-service",
  brokers: ["localhost:9092"],
});
const producer = kafka.producer();

async function publishOrderEvent(orderId, status, data = {}) {
  const event = {
    eventId: randomUUID(),
    orderId,
    status, // CREATED | CONFIRMED | SHIPPED
    occurredAt: new Date().toISOString(),
    ...data,
  };

  await producer.send({
    topic: "order-events",
    messages: [{ key: String(orderId), value: JSON.stringify(event) }],
  });

  console.log(`[Orders] Evento publicado: ${status} (pedido ${orderId})`);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  await producer.connect();

  // Simulación del ciclo de vida de dos pedidos
  for (const orderId of [101, 102]) {
    await publishOrderEvent(orderId, "CREATED", {
      customerEmail: "cliente@mail.com",
      total: 15000,
    });
    await sleep(1000);
    await publishOrderEvent(orderId, "CONFIRMED");
    await sleep(1000);
    await publishOrderEvent(orderId, "SHIPPED");
  }

  await producer.disconnect();
}

main().catch(console.error);
