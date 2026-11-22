type Emit = (name: string, data?: unknown) => void;
// oxlint-disable-next-line typescript/no-explicit-any -- listener payloads are typed by the caller
type Listener<T = any> = (data: T, emit: Emit) => void;

interface PluginMessage {
	name: string;
	data: unknown;
	/** Set on "ask" requests and echoed back by the answer */
	requestId?: number;
}

/**
 * An structured way to handle renderer and main messages
 */
class EventEmitter {
	messageEvent = new Map<string, Listener>();
	// Keyed by request id, so concurrent asks for the same name cannot steal
	// each other's answers.
	pending = new Map<number, (data: unknown) => void>();
	nextRequestId = 1;
	post: (message: PluginMessage) => void;

	constructor() {
		if (typeof figma !== "undefined") {
			// MAIN PROCESS
			this.post = (message) => figma.ui.postMessage(message, { origin: "*" });

			figma.ui.on("message", (message: PluginMessage) => this.receive(message));
		} else {
			// RENDERER PROCESS
			this.post = (message) =>
				parent.postMessage({ pluginMessage: message }, "*");

			window.addEventListener(
				"message",
				(event: MessageEvent<{ pluginMessage?: PluginMessage }>) => {
					if (event.data.pluginMessage) {
						this.receive(event.data.pluginMessage);
					}
				},
			);
		}
	}

	private receive({ name, data, requestId }: PluginMessage) {
		const resolve =
			requestId === undefined ? undefined : this.pending.get(requestId);

		if (resolve) {
			this.pending.delete(requestId!);
			resolve(data);
			return;
		}

		const reply: Emit = (replyName, replyData) =>
			this.post({ name: replyName, data: replyData ?? null, requestId });

		this.messageEvent.get(name)?.(data, reply);
	}

	emit: Emit = (name, data) => {
		this.post({ name, data: data ?? null });
	};

	/**
	 * Listen to a message
	 * @param name string
	 * @param callback function
	 */
	on<T>(name: string, callback: Listener<T>) {
		this.messageEvent.set(name, callback);

		return () => this.remove(name);
	}

	/**
	 * Ask for data
	 * @param name
	 */
	ask<R>(name: string, data?: unknown) {
		const requestId = this.nextRequestId++;

		return new Promise<R>((resolve) => {
			this.pending.set(requestId, resolve as (data: unknown) => void);
			this.post({ name, data: data ?? null, requestId });
		});
	}

	/**
	 * Answer data from "ask"
	 * @param name
	 * @param functionOrValue
	 */
	answer<T, R>(
		name: string,
		functionOrValue: ((data: T) => R | Promise<R>) | R,
	) {
		this.on<T>(name, (incomingData, reply) => {
			if (typeof functionOrValue === "function") {
				void Promise.resolve(
					(functionOrValue as (data: T) => R | Promise<R>)(incomingData),
				).then((data) => reply(name, data));
			} else {
				reply(name, functionOrValue);
			}
		});
	}

	/**
	 * Remove an active listener
	 * @param name
	 */
	remove(name: string) {
		this.messageEvent.delete(name);
	}
}

export default new EventEmitter();
