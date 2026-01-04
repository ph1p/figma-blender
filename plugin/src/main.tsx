import { observer } from "mobx-react-lite";
import { useEffect } from "react";
import ReactDOM from "react-dom/client";
import { Route, MemoryRouter as Router, Routes } from "react-router-dom";
import slugify from "slugify";
import styled from "styled-components";
import { StoreProvider, useStore } from "./store";
import { SocketProvider } from "./utils/SocketProvider";
import HomeView from "./views/Home";
import "./style.css";

import EventEmitter from "./shared/EventEmitter";
import { chunkData } from "./utils/helpers";
import { useWebSocket } from "./utils/use-websocket";

const AppWrapper = styled.div`
  overflow: hidden;
`;

const App = observer(() => {
	const store = useStore();
	const { socket } = useWebSocket({
		url: store.url,
		onmessage: (e, ws) => {
			const data = JSON.parse(e.data);

			const sendElement = async (id) => {
				await EventEmitter.ask("frame", { id, scaling: store.scaling }).then(
					(frame: unknown) => {
						const typedFrame = frame as {
							data?: Uint8Array;
							name: string;
							id: string;
							width: number;
							height: number;
						} | null;
						if (typedFrame?.data) {
							let chunks = chunkData(typedFrame.data);

							for (const chunk of chunks) {
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
									name: `${slugify(typedFrame.name)}-${(
										+typedFrame.id.replace(":", "")
									).toString(16)}`,
									width: typedFrame.width,
									height: typedFrame.height,
								}),
							);

							chunks = [];
							delete typedFrame.data;
						} else {
							ws.send(
								JSON.stringify({
									event: "element_data",
									type: "FILE_ERROR",
								}),
							);
						}
					},
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
				({ elements, page_name }: { elements: unknown; page_name: string }) => {
					store.setElements(elements);
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
