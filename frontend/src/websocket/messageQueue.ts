const offlineQueue: any[] = [];

export function queueMessage(msg: any) {
  offlineQueue.push(msg);
}

export function flushQueue(socket: any) {
  while (offlineQueue.length > 0) {
    socket.emit("message", offlineQueue.shift());
  }
}
