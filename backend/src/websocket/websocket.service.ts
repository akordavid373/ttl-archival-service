import { Injectable } from '@nestjs/common';
import { Socket } from 'socket.io';

@Injectable()
export class WebsocketService {
  private clients: Map<string, Socket> = new Map();
  private messageQueue: Map<string, any[]> = new Map();

  registerClient(client: Socket) {
    this.clients.set(client.id, client);
    this.messageQueue.set(client.id, []);
  }

  removeClient(clientId: string) {
    this.clients.delete(clientId);
    this.messageQueue.delete(clientId);
  }

  queueMessage(clientId: string, message: any) {
    if (this.clients.has(clientId)) {
      this.clients.get(clientId).emit('message', message);
    } else {
      const queue = this.messageQueue.get(clientId) || [];
      queue.push(message);
      this.messageQueue.set(clientId, queue);
    }
  }

  flushQueue(clientId: string) {
    const queue = this.messageQueue.get(clientId) || [];
    queue.forEach(msg => this.clients.get(clientId)?.emit('message', msg));
    this.messageQueue.set(clientId, []);
  }
}
