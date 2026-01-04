import React, { useEffect } from "react";
import { useStore } from "../store";
import { ConnectionEnum } from "./interfaces";

export const useWebSocket = ({ url, onmessage }) => {
	const store = useStore();
	const [socket, _setSocket] = React.useState<WebSocket>(null);

	const socketRef = React.useRef(socket);
	const onmessageRef = React.useRef(onmessage);

	// Keep the ref updated with the latest onmessage callback
	useEffect(() => {
		onmessageRef.current = onmessage;
	}, [onmessage]);

	const setSocket = React.useCallback((data) => {
		socketRef.current = data;
		_setSocket(data);
	}, []);

	useEffect(() => {
		let timeout: NodeJS.Timeout | undefined;
		let ws: WebSocket | null = null;
		let shouldReconnect = true;

		const connect = () => {
			// Don't connect if we're cleaning up
			if (!shouldReconnect) return;

			ws = new WebSocket(url);

			ws.onmessage = (e) => onmessageRef.current(e, ws);

			ws.onopen = () => {
				store.setStatus(ConnectionEnum.CONNECTED);
				setSocket(ws);
				clearTimeout(timeout);
			};

			ws.onclose = () => {
				// Only reconnect if we should and we're not cleaning up
				if (!shouldReconnect) return;

				store.setStatus(ConnectionEnum.CONNECTING);
				setSocket(null);
				timeout = setTimeout(() => {
					if (shouldReconnect) {
						connect();
					}
				}, 1000);
			};

			ws.onerror = () => {
				store.setStatus(ConnectionEnum.ERROR);
				setSocket(null);
				ws?.close();
			};
		};

		connect();

		// Cleanup function to close connection and prevent reconnection
		return () => {
			shouldReconnect = false;
			clearTimeout(timeout);
			if (ws) {
				ws.onclose = null; // Prevent reconnection
				ws.onerror = null;
				ws.onmessage = null;
				ws.onopen = null;
				ws.close();
			}
		};
	}, [setSocket, store.setStatus, url]);

	return {
		socket: socketRef.current,
	};
};
