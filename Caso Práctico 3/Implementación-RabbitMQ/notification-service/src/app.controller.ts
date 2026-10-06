import { Controller } from '@nestjs/common';
import { Ctx, EventPattern, Payload, RmqContext } from '@nestjs/microservices';
import { MailService } from './mail.service.js';

@Controller()
export class AppController {
  constructor(private mail: MailService) {
	 console.log('AppController cargado');
}

  @EventPattern('order_created')
  async onOrderCreated(@Payload() order: any, @Ctx() ctx: any) {
    const context = ctx as RmqContext;
    const channel = context.getChannelRef();
    const msg = context.getMessage();
    try {
      console.log('Pedido recibido:', order.id);
      await this.mail.sendOrderCreated(order);
      channel.ack(msg);
    } catch (e) {
      console.error('Error enviando mail, se reencola:', e);
      channel.nack(msg, false, true);
    }
  }
}