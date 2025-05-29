import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
	base: "/static/client/dist",
	plugins: [
		vue(),
		vueDevTools(),
		{
			name: 'rename',
			enforce: 'post',
			generateBundle(options, bundle) {
				bundle['index.html'].fileName = bundle['index.html'].fileName.replace('index.html', 'client.html')
			}
		}
	],
	resolve: {
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url))
		},
	}
})
