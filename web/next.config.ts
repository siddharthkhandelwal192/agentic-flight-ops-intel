import type { NextConfig } from "next";

/**
 * Where the Next server proxies `/afois-api/*` (server-side). Browser stays same-origin.
 * In Docker, set to `http://api:8000`. On the host, default hits a local Uvicorn.
 */
const backendOrigin = (
  process.env.AFOIS_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/afois-api/:path*",
        destination: `${backendOrigin}/:path*`,
      },
    ];
  },
};

export default nextConfig;
