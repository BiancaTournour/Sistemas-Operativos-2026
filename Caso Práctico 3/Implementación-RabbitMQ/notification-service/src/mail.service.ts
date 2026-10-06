import { Injectable } from '@nestjs/common';
import * as nodemailer from 'nodemailer';

@Injectable()
export class MailService {
  private transporterPromise = nodemailer.createTestAccount().then((acc) =>
    nodemailer.createTransport({
      host: acc.smtp.host,
      port: acc.smtp.port,
      secure: acc.smtp.secure,
      auth: { user: acc.user, pass: acc.pass },
    }),
  );

  async sendOrderCreated(order: any) {
    const transporter = await this.transporterPromise;
    const info = await transporter.sendMail({
      from: 'tienda@ejemplo.com',
      to: order.customerEmail,
      subject: `Pedido ${order.id} creado`,
      text: `¡Gracias por tu compra! Recibimos tu pedido ${order.id}.`,
    });
    console.log('Mail enviado. Verlo en:', nodemailer.getTestMessageUrl(info));
    return info;
  }
}
