import { DocsThemeConfig } from 'nextra-theme-docs';
import { biosnicarLogo } from './components/logo';

const config: DocsThemeConfig = {
  logo: biosnicarLogo,
  project: {
    link: 'https://github.com/jmcook1186/biosnicar-py',
  },
  docsRepositoryBase: 'https://github.com/jmcook1186/biosnicar-website/tree/main',
  footer: {
    text: 'Nextra Docs Template',
  }
}

export default config
