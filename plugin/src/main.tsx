import { observer } from "mobx-react-lite";
import { useEffect } from "react";
import ReactDOM from "react-dom/client";
import { Route, MemoryRouter as Router, Routes } from "react-router-dom";
import slugify from "slugify";
import styled from "styled-components";

import EventEmitter from "./shared/EventEmitter";
import { StoreProvider, useStore } from "./store";
import { chunkData } from "./utils/helpers";
import type { FigmaElement, FigmaFrame } from "./utils/interfaces";

import "./style.css";

import { SocketProvider } from "./utils/SocketProvider";
import { useWebSocket } from "./utils/use-websocket";
import HomeView from "./views/Home";

const AppWrapper = styled.div`
	overflow: hidden;
`;

const App = observer(() => {
	const store = useStore();
	const { socket } = useWebSocket({
		url: store.url,
		onmessage: (e, ws) => {
			const data = JSON.parse(e.data);

			const sendElement = async (id: string) => {
				const frame = await EventEmitter.ask<FigmaFrame | null>("frame", {
					id,
					scaling: store.scaling,
				});

				if (!frame?.data) {
					ws.send(
						JSON.stringify({
							event: "element_data",
							type: "FILE_ERROR",
						}),
					);
					return;
				}

				for (const chunk of chunkData(frame.data)) {
					ws.send(
						JSON.stringify({
							event: "element_data",
							type: "FILE_DATA",
							data: Array.from(chunk),
						}),
					);
				}

				ws.send(
					JSON.stringify({
						event: "element_data",
						type: "FILE_END",
						name: `${slugify(frame.name)}-${(+frame.id.replace(":", "")).toString(16)}`,
						width: frame.width,
						height: frame.height,
					}),
				);
			};

			if (data.event === "get_element") {
				sendElement(data.id);
			} else if (data.event === "not_allowed") {
				store.setNotAllowed();
			} else if (data.event === "init") {
				EventEmitter.emit("get data");
			}
		},
	});

	useEffect(() => {
		if (socket) {
			const cleanup = EventEmitter.on(
				"data",
				({
					elements,
					page_name,
				}: {
					elements: FigmaElement[] | undefined;
					page_name: string;
				}) => {
					store.setElements(elements || []);
					store.setPageName(page_name);
					socket.send(
						JSON.stringify({
							event: "data",
							elements: elements || [],
							page_name,
						}),
					);
				},
			);

			return () => {
				cleanup();
				EventEmitter.remove("frames");
			};
		}
	}, [socket, store]);

	// Figma fires no event when a frame is added, renamed or deleted, so ask the
	// main thread to re-check while we are connected.
	useEffect(() => {
		if (!socket) return;

		const interval = setInterval(
			() => EventEmitter.emit("refresh elements"),
			2000,
		);

		return () => clearInterval(interval);
	}, [socket]);

	return (
		<AppWrapper>
			<SocketProvider socket={socket}>
				<Router>
					<Routes>
						<Route path="/" element={<HomeView />} />
					</Routes>
				</Router>
			</SocketProvider>
		</AppWrapper>
	);
});

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

ReactDOM.createRoot(root).render(
	<StoreProvider>
		<App />
	</StoreProvider>,
);
