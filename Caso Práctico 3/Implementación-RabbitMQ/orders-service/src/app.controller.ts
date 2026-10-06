import { Body, Controller, Post } from '@nestjs/common';
import { AppService } from './app.service.js';

@Controller('orders')
export class AppController {
  constructor(private readonly service: AppService) {}

  @Post()
  create(@Body() dto: { customerEmail: string; product: string }) {
    return this.service.createOrder(dto);
  }
}