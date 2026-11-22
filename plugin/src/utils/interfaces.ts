export enum ConnectionEnum {
	NOT_ALLOWED = "NOT_ALLOWED",
	CONNECTED = "CONNECTED",
	ERROR = "ERROR",
	CONNECTING = "CONNECTING",
}

export interface FigmaElement {
	id: string;
	name: string;
}

export interface FigmaFrame extends FigmaElement {
	width: number;
	height: number;
	data?: Uint8Array;
}
