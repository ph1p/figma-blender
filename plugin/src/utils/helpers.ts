export const sleep = (time) =>
  new Promise((resolve) => setTimeout(resolve, time));

export const chunkData = (arr, chunkSize = 256 * 1024) => {
  const res = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    const chunk = arr.slice(i, i + chunkSize);
    res.push(chunk);
  }
  return res;
};
