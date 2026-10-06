import { Inject, Injectable } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import { randomUUID } from 'crypto';

@Injectable()
export class AppService {
  constructor(@Inject('NOTIFICATIONS_SERVICE') private client: ClientProxy) {}

  createOrder(dto: { customerEmail: string; product: string }) {
    const order = { id: randomUUID(), ...dto, createdAt: new Date() };
    this.client.emit('order_created', order);
    return order;
  }
}