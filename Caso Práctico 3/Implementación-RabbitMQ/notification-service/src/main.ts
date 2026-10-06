import amqp from 'amqplib';
import { MailService } from './mail.service.js';

const QUEUE = 'notifications_queue';

async function bootstrap() {
  const mail = new MailService();
  const conn = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await conn.createChannel();

  await channel.assertQueue(QUEUE, { durable: true });
  await channel.prefetch(1);

  console.log('NotificationService escuchando notifications_queue...');

  await channel.consume(
    QUEUE,
    async (msg) => {
      if (!msg) return;

      let evento: { pattern: string; data: any };
      try {
        evento = JSON.parse(msg.content.toString());
      } catch {
        console.error('Mensaje inválido, se descarta');
        channel.ack(msg);
        return;
      }

      if (evento.pattern !== 'order_created') {
        channel.ack(msg);
        return;
      }

      try {
        console.log('Pedido recibido:', evento.data.id);
        await mail.sendOrderCreated(evento.data);
        channel.ack(msg); // recién acá sale de la cola
      } catch (e) {
        console.error('Error enviando mail, se reencola:', e);
        channel.nack(msg, false, true); // vuelve a la cola
      }
    },
    { noAck: false },
  );
}

bootstrap();
