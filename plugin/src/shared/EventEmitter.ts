type Emit = (name: string, data?: unknown) => void;
// oxlint-disable-next-line typescript/no-explicit-any -- listener payloads are typed by the caller
type Listener<T = any> = (data: T, emit: Emit) => void;

interface PluginMessage {
	name: string;
	data: unknown;
}

/**
 * An structured way to handle renderer and main messages
 */
class EventEmitter {
	messageEvent = new Map<string, Listener>();
	emit: Emit;

	constructor() {
		if (typeof figma !== "undefined") {
			// MAIN PROCESS
			this.emit = (name, data) => {
				figma.ui.postMessage({ name, data: data || null }, { origin: "*" });
			};

			figma.ui.on("message", (event: PluginMessage) => {
				this.messageEvent.get(event.name)?.(event.data, this.emit);
			});
		} else {
			// RENDERER PROCESS
			window.addEventListener(
				"message",
				(event: MessageEvent<{ pluginMessage?: PluginMessage }>) => {
					const message = event.data.pluginMessage;
					if (message) {
						this.messageEvent.get(message.name)?.(message.data, this.emit);
					}
				},
			);

			this.emit = (name = "", data = {}) => {
				parent.postMessage(
					{ pluginMessage: { name, data: data || null } },
					"*",
				);
			};
		}
	}

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
	 * Listen to a message once
	 * @param name
	 * @param callback
	 */
	once<T>(name: string, callback: Listener<T>) {
		const remove = this.on<T>(name, (data, emit) => {
			callback(data, emit);
			remove();
		});
	}

	/**
	 * Ask for data
	 * @param name
	 */
	ask<R>(name: string, data?: unknown) {
		this.emit(name, data);

		return new Promise<R>((resolve) => this.once<R>(name, resolve));
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
		this.on<T>(name, (incomingData, emit) => {
			if (typeof functionOrValue === "function") {
				void Promise.resolve(
					(functionOrValue as (data: T) => R | Promise<R>)(incomingData),
				).then((data) => emit(name, data));
			} else {
				emit(name, functionOrValue);
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
