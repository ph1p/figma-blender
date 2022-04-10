import React, { useEffect } from 'react';
import { useStore } from '../store';
import { ConnectionEnum } from './interfaces';

export const useWebSocket = ({ url, onmessage }) => {
  const store = useStore();
  const [socket, _setSocket] = React.useState<WebSocket>(null);

  const socketRef = React.useRef(socket);
  const setSocket = (data) => {
    socketRef.current = data;
    _setSocket(data);
  };

  useEffect(() => {
    let timeout;

    const connect = () => {
      const ws = new WebSocket(url);

      ws.onmessage = (e) => onmessage(e, ws);

      ws.onopen = () => {
        store.setStatus(ConnectionEnum.CONNECTED);
        setSocket(ws);
        clearTimeout(timeout);
      };

      ws.onclose = () => {
        store.setStatus(ConnectionEnum.CONNECTING);
        setSocket(null);
        timeout = setTimeout(() => {
          connect();
        }, 1000);
      };

      ws.onerror = () => {
        store.setStatus(ConnectionEnum.ERROR);
        setSocket(null);
        ws.close();
      };
    };

    connect();
  }, []);

  return {
    socket: socketRef.current,
  };
};
