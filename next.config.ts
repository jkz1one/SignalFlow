import type { NextConfig } from "next";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  (process.env.NODE_ENV === "production"
    ? "http://api:8000"          // inside Docker: talk directly to the api service
    : "http://localhost:8000");  // local dev

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` },
    ];
  },
};

export default nextConfig;
