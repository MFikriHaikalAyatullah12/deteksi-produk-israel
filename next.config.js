/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    PYTHON_API_URL: process.env.PYTHON_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/detect/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

module.exports = nextConfig;