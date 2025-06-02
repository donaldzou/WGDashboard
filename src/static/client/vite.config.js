import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import {proxy} from "./proxy.js";


export default defineConfig({
	plugins: [
		vue(),
		vueDevTools(),
		{
			name: 'rename',
			enforce: 'post',
			generateBundle(options, bundle) {
				bundle['index.html'].fileName = "client.html"
			}
		}
	],
	resolve: {
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url))
		},
	},
	server:{
		proxy: {
			'/client': proxy,
		},
		host: '0.0.0.0'
	},
	base: '/static/client/dist'
})
