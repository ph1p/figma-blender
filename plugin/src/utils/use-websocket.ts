import { useEffect, useRef, useState } from "react";

import { useStore } from "../store";
import { ConnectionEnum } from "./interfaces";

type MessageHandler = (event: MessageEvent<string>, ws: WebSocket) => void;

export const useWebSocket = ({
	url,
	onmessage,
}: {
	url: string;
	onmessage: MessageHandler;
}) => {
	const store = useStore();
	const [socket, setSocket] = useState<WebSocket | null>(null);
	const onmessageRef = useRef(onmessage);

	// Keep the latest onmessage callback without reconnecting
	useEffect(() => {
		onmessageRef.current = onmessage;
	}, [onmessage]);

	useEffect(() => {
		let timeout: ReturnType<typeof setTimeout> | undefined;
		// Aborting removes every listener and prevents reconnection on cleanup
		const controller = new AbortController();
		const { signal } = controller;

		const connect = () => {
			if (signal.aborted) return;

			const ws = new WebSocket(url);

			ws.addEventListener("message", (e) => onmessageRef.current(e, ws), {
				signal,
			});

			ws.addEventListener(
				"open",
				() => {
					store.setStatus(ConnectionEnum.CONNECTED);
					setSocket(ws);
					clearTimeout(timeout);
				},
				{ signal },
			);

			ws.addEventListener(
				"close",
				() => {
					store.setStatus(ConnectionEnum.CONNECTING);
					setSocket(null);
					timeout = setTimeout(connect, 1000);
				},
				{ signal },
			);

			ws.addEventListener(
				"error",
				() => {
					store.setStatus(ConnectionEnum.ERROR);
					setSocket(null);
					ws.close();
				},
				{ signal },
			);

			signal.addEventListener("abort", () => ws.close());
		};

		connect();

		return () => {
			controller.abort();
			clearTimeout(timeout);
		};
	}, [store, url]);

	return { socket };
};
