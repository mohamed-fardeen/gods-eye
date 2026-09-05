import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import basicSsl from '@vitejs/plugin-basic-ssl';
import path from "path";

const cesiumSource = "node_modules/cesium/Build/Cesium";

export default defineConfig({
  define: {
    // Define the base URL where Cesium static assets will be served
    CESIUM_BASE_URL: JSON.stringify("/cesium/"),
  },
  plugins: [
    basicSsl(),
    viteStaticCopy({
      targets: [
        {
          src: `${cesiumSource}/Workers`,
          dest: "cesium",
        },
        {
          src: `${cesiumSource}/ThirdParty`,
          dest: "cesium",
        },
        {
          src: `${cesiumSource}/Assets`,
          dest: "cesium",
        },
        {
          src: `${cesiumSource}/Widgets`,
          dest: "cesium",
        },
      ],
    }),
  ],
  server: {
    port: 5173,
    host: true, // Listen on all local IPs
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true
      }
    }
  },
});
