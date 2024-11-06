import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import {proxy} from "./proxy.js";
import vue from '@vitejs/plugin-vue'
import {v4} from "uuid";

const hash = () => {
    return Math.floor(Math.random() * 90000) + 10000
}

// https://vitejs.dev/config/
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
            entryFileNames: `assets/[name]-${v4()}.js`,
            chunkFileNames: `assets/[name]-${v4()}.js`,
            assetFileNames: `assets/[name]-${v4()}.[ext]`
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
          entryFileNames: `assets/[name]-${v4()}.js`,
          chunkFileNames: `assets/[name]-${v4()}.js`,
          assetFileNames: `assets/[name]-${v4()}.[ext]`
        }
      }
    }
  }
})
