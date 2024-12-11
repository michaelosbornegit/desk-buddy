import react from '@vitejs/plugin-react-swc';
import dns from 'dns';
import { defineConfig } from 'vite';

// dns.setDefaultResultOrder('verbatim');

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    outDir: 'build',
    emptyOutDir: true,
    sourcemap: true,
  },
  plugins: [react()],
  types: ['node'],
});
