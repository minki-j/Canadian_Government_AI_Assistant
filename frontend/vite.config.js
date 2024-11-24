import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

console.log("process.env.DOCKER_ENV:", process.env.DOCKER_ENV);
const running_on_docker = process.env.DOCKER_ENV === "true";
const backendUrl = running_on_docker
  ? "http://fastapi:8000"
  : "http://localhost:8000";

const proxyEndpoints = ["/health", "/fetch_website_content"];

const proxyConfig = Object.fromEntries(
  proxyEndpoints.map((endpoint) => [
    endpoint,
    {
      target: backendUrl,
      changeOrigin: true,
    },
  ])
);

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: proxyConfig,
    host: true,
    port: 3001,
  },
});
