import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import {proxy} from "./proxy.js";
import vue from '@vitejs/plugin-vue'
import { version } from './package.json'

export default defineConfig(({mode}) => {
	if (mode === 'electron'){
		return {
			emptyOutDir: false,
			base: './',
			plugins: [
				vue(),
			],
			resolve: {
				alias: {
					'@': fileURLToPath(new URL('./src', import.meta.url))
				}
			},
			build: {
				target: "es2022",
				outDir: '../../../../WGDashboard-Desktop',
				rollupOptions: {
					output: {
						entryFileNames: `assets/[name].js?v=${version}`,
						chunkFileNames: `assets/[name].js?v=${version}`,
						assetFileNames: `assets/[name].[ext]?v=${version}`
					}
				}
			}
		}
	}

	return {
		base: "/static/app/dist",
		plugins: [
			vue(),
		],
		resolve: {
			alias: {
				'@': fileURLToPath(new URL('./src', import.meta.url))
			}
		},
		server:{
			proxy: {
				'/api': proxy
			},
			host: '0.0.0.0'
		},
		build: {
			target: "es2022",
			outDir: 'dist',
			rollupOptions: {
				output: {
					entryFileNames: `assets/[name].js?v=${version}`,
					chunkFileNames: `assets/[name].js?v=${version}`,
					assetFileNames: `assets/[name].[ext]?v=${version}`
				}
			}
		}
	}
})
