const { Kafka } = require("kafkajs");

const kafka = new Kafka({
  clientId: "notification-service",
  brokers: ["localhost:9092"],
});
const consumer = kafka.consumer({ groupId: "notification-service" });

const messages = {
  CREATED: "Recibimos tu pedido",
  CONFIRMED: "Tu pedido fue confirmado",
  SHIPPED: "Tu pedido está en camino",
};

async function main() {
  await consumer.connect();
  await consumer.subscribe({ topic: "order-events", fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ partition, message }) => {
      const event = JSON.parse(message.value.toString());
      console.log(
        `[Notification] (p${partition}) Enviando correo: "${messages[event.status]}" -> pedido ${event.orderId}`,
      );
    },
  });
}

main().catch(console.error);
