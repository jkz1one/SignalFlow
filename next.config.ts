import type { NextConfig } from "next";

// Resolve backend base URL for rewrites.
// In Docker prod, talk to the "api" service by name.
// In local dev, use localhost:8000.
const BACKEND_URL =
  process.env.BACKEND_URL ||
  (process.env.NODE_ENV === "production"
    ? "http://api:8000"
    : "http://localhost:8000");

const nextConfig: NextConfig = {
  // Be explicit about redirects so bare domain works.
  async redirects() {
    return [
      { source: "/", destination: "/tracker", permanent: false },
    ];
  },

  // Route all REST requests through Next to the FastAPI backend.
  // Note: WebSockets (/ws/*) are handled at the Caddy proxy, not here.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` },
    ];
  },

  // Optional hardening/sanity flags you can keep or drop:
  reactStrictMode: true,
  poweredByHeader: false,
};

export default nextConfig;
