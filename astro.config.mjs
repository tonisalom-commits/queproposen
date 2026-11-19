import { defineConfig } from 'astro/config';

// GitHub Pages: https://tonisalom-commits.github.io/queproposen/
export default defineConfig({
  site: 'https://tonisalom-commits.github.io',
  base: '/queproposen',
  output: 'static',
  trailingSlash: 'always'
});
