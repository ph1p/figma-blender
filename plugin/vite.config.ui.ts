import path from "node:path";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig(({ mode }) => ({
	build: {
		emptyOutDir: false,
		sourcemap: mode === "production" ? false : "inline",
		rollupOptions: {
			input: path.resolve("index.html"),
		},
		outDir: path.resolve("dist"),
		assetsInlineLimit: Infinity,
		minify: mode === "production",
	},
	plugins: [react(), viteSingleFile()],
}));
