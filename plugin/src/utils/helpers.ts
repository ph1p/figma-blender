export const sleep = (time: number) =>
	new Promise((resolve) => setTimeout(resolve, time));

export const chunkData = (arr: Uint8Array, chunkSize = 256 * 1024) => {
	const res: Uint8Array[] = [];
	for (let i = 0; i < arr.length; i += chunkSize) {
		const chunk = arr.slice(i, i + chunkSize);
		res.push(chunk);
	}
	return res;
};
