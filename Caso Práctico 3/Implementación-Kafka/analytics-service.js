const { Kafka } = require("kafkajs");

const kafka = new Kafka({
  clientId: "analytics-service",
  brokers: ["localhost:9092"],
});
const consumer = kafka.consumer({ groupId: "analytics-service" });

const countByStatus = { CREATED: 0, CONFIRMED: 0, SHIPPED: 0 };
const createdAt = {};

async function main() {
  await consumer.connect();
  await consumer.subscribe({ topic: "order-events", fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ message }) => {
      const event = JSON.parse(message.value.toString());
      countByStatus[event.status]++;

      if (event.status === "CREATED")
        createdAt[event.orderId] = new Date(event.occurredAt);
      if (event.status === "SHIPPED" && createdAt[event.orderId]) {
        const secs =
          (new Date(event.occurredAt) - createdAt[event.orderId]) / 1000;
        console.log(
          `[Analytics] Pedido ${event.orderId}: de creado a enviado en ${secs}s`,
        );
      }

      console.log("[Analytics] Totales:", countByStatus);
    },
  });
}

main().catch(console.error);
