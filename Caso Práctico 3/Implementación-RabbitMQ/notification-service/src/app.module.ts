import { Module } from '@nestjs/common';
import { AppController } from './app.controller.js';
import { MailService } from './mail.service.js';

@Module({
  controllers: [AppController],
  providers: [MailService],
})
export class AppModule {}