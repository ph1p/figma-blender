import fs from "node:fs";
import path from "node:path";
import { defineConfig, type PluginOption } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const manifestPlugin: PluginOption = {
	name: "generate-manifest",
	buildStart() {
		const packageJsonPath = path.resolve("package.json");
		if (fs.existsSync(packageJsonPath)) {
			const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf-8"));

			if (packageJson.figma) {
				this.emitFile({
					type: "asset",
					fileName: "manifest.json",
					source: JSON.stringify(packageJson.figma, null, 2),
				});
			}
		}
	},
};

export default defineConfig(({ mode }) => ({
	build: {
		emptyOutDir: false,
		target: "es2017",
		sourcemap: mode === "production" ? false : "inline",
		rollupOptions: {
			input: "src/main/code.ts",
			output: {
				assetFileNames: "[name].[ext]",
				chunkFileNames: "[name].js",
				entryFileNames: "[name].js",
			},
		},
		assetsInlineLimit: Infinity,
		minify: mode === "production",
	},
	plugins: [viteSingleFile(), manifestPlugin],
}));
