import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { WebsocketService } from './websocket.service';

@WebSocketGateway({ cors: true })
export class WebsocketGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  constructor(private readonly wsService: WebsocketService) {}

  handleConnection(client: Socket) {
    this.wsService.registerClient(client);
    this.server.emit('status', { clientId: client.id, status: 'connected' });
  }

  handleDisconnect(client: Socket) {
    this.wsService.removeClient(client.id);
    this.server.emit('status', { clientId: client.id, status: 'disconnected' });
  }

  @SubscribeMessage('message')
  handleMessage(client: Socket, payload: any) {
    this.wsService.queueMessage(client.id, payload);
  }
}
