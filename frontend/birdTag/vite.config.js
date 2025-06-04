import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import rollupNodePolyFill from 'rollup-plugin-node-polyfills';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      buffer: 'buffer',
      process: 'process',
    },
  },
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ['buffer', 'process'],
  },
  build: {
    rollupOptions: {
      plugins: [rollupNodePolyFill()],
    },
  },
  server: {
    proxy: {
      '/bird': {
        target: 'https://voe9xiqt31.execute-api.us-east-1.amazonaws.com/version1',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/bird/, ''),
      },
    },
  },
});
