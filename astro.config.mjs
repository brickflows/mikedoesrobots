import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://mikedoesrobots.com',
  trailingSlash: 'always',
  redirects: {
    '/portfolio_mahle': '/portfolio-mahle/',
  },
});
