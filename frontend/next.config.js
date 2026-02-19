/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  transpilePackages: [
    '@deck.gl/core',
    '@deck.gl/layers',
    '@deck.gl/geo-layers',
    '@deck.gl/react',
    '@luma.gl/core',
    '@luma.gl/webgl',
    'maplibre-gl',
  ],
  webpack: (config) => {
    // Allow WebAssembly (needed by pmtiles / deck.gl internals)
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
    };
    return config;
  },
};

module.exports = nextConfig;
