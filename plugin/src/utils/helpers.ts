export const chunkData = (arr: Uint8Array, chunkSize = 256 * 1024) => {
	const res: Uint8Array[] = [];
	for (let i = 0; i < arr.length; i += chunkSize) {
		res.push(arr.subarray(i, i + chunkSize));
	}
	return res;
};

/**
 * Turn a Figma node id into a file-name-safe, collision-free suffix.
 * "1:23" and "12:3" must stay distinct, and instance ids like "I1:2;3:4"
 * must not end up as NaN.
 */
export const idToSuffix = (id: string) =>
	id.replace(/[^a-z0-9]+/gi, "-").replace(/^-+|-+$/g, "");
