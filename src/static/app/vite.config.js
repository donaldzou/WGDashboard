import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import {proxy} from "./proxy.js";
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({mode}) => {
  
 
  if (mode === 'electron'){
    return {
      define: {
        'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api')
      },
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
        outDir: '../../../../WGDashboard-Desktop',
        rollupOptions: {
          output: {
            entryFileNames: `assets/[name].js`,
            chunkFileNames: `assets/[name].js`,
            assetFileNames: `assets/[name].[ext]`
          }
        }
      }
    }
  }

  return {
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api')
    },
    base: "./",
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
      outDir: 'dist',
      rollupOptions: {
        output: {
          entryFileNames: `assets/[name].js`,
          chunkFileNames: `assets/[name].js`,
          assetFileNames: `assets/[name].[ext]`
        }
      }
    }
  }
})
