import React from "react";
import { useWebSocket } from "./useWebSocket";

export const ConnectionStatus: React.FC = () => {
  const { status } = useWebSocket();
  return <div>Connection: {status}</div>;
};
