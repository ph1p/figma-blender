import React, { FunctionComponent } from 'react';

interface Props {
  socket: WebSocket | null;
  children: any;
}

const SocketContext = React.createContext<WebSocket | null>(null);

export const SocketProvider: FunctionComponent<Props> = (props) => (
  <SocketContext.Provider value={props.socket}>
    {props.children}
  </SocketContext.Provider>
);

export const useSocket = (): WebSocket | null => {
  const socket = React.useContext(SocketContext);

  if (socket === undefined) {
    throw new Error('useSocket must be used within a SocketProvider.');
  }

  return socket;
};

export const withSocketContext = (Component: any) => (props: any) =>
  (
    <SocketContext.Consumer>
      {(socket) => <Component {...(props as unknown)} socket={socket} />}
    </SocketContext.Consumer>
  );
