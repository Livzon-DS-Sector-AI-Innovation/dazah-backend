import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 生产构建优化
  output: "standalone",

  // 确保 CSS 正确打包
  experimental: {
    // 优化静态资源打包
    optimizePackageImports: ['antd', '@ant-design/icons'],
  },

  // 确保包含必要的静态资源
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
