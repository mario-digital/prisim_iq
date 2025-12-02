import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  
  // Enable experimental features
  experimental: {
    // Enable React 19 features
    reactCompiler: false,
  },
  
  // Transpile shared package
  transpilePackages: ['@prismiq/shared'],
  
  // Environment variables available on the client
  env: {
    NEXT_PUBLIC_APP_NAME: 'PrismIQ',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },
};

export default nextConfig;

