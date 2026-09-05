import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import path from "path";

const cesiumSource = "node_modules/cesium/Build/Cesium";

export default defineConfig({
  define: {
    // Define the base URL where Cesium static assets will be served
    CESIUM_BASE_URL: JSON.stringify("/cesium/"),
  },
  plugins: [
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
    port: 3000,
    open: false,
  },
});
