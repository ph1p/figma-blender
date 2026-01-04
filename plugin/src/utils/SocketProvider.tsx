import React, { type FunctionComponent } from "react";

interface Props {
	socket: WebSocket | null;
	children: React.ReactNode;
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
		throw new Error("useSocket must be used within a SocketProvider.");
	}

	return socket;
};

export const withSocketContext =
	<P extends object>(
		Component: React.ComponentType<P & { socket: WebSocket | null }>,
	) =>
	(props: P) => (
		<SocketContext.Consumer>
			{(socket) => <Component {...props} socket={socket} />}
		</SocketContext.Consumer>
	);
