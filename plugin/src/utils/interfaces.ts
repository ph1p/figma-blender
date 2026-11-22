export enum ConnectionEnum {
	NOT_ALLOWED = "NOT_ALLOWED",
	CONNECTED = "CONNECTED",
	ERROR = "ERROR",
	CONNECTING = "CONNECTING",
}

/**
 * Wire format version this plugin speaks. The addon announces its own with
 * "init"; addons from before versioning send none and count as 1.
 *   1: image chunks as JSON FILE_DATA messages
 *   2: image chunks as raw binary frames
 */
export const PROTOCOL_VERSION = 2;

export interface FigmaElement {
	id: string;
	name: string;
}

export interface FigmaFrame extends FigmaElement {
	width: number;
	height: number;
	data?: Uint8Array;
}
