# biosnicar documentation

The BioSNICAR docs site, built with [Nextra](https://nextra.site/) on top of Next.js.

## Prerequisites

- **Node.js** 18.18 or later (required by Next.js 15).
- **pnpm** — install once with `npm install -g pnpm`, or via [corepack](https://nodejs.org/api/corepack.html): `corepack enable && corepack prepare pnpm@latest --activate`.
- **Git**, and a clone of this repo.

No environment variables or external services are required to run the site locally — the docs are fully static.

## Local development

```bash
pnpm i        # install dependencies
pnpm dev      # start dev server at http://localhost:3000
```

Pages hot-reload as you edit.

## Adding or updating a page

Content lives under `pages/` as MDX files. The sidebar layout is driven by `_meta.ts` files in each directory.

**To update an existing page:** edit the relevant `.mdx` file under `pages/` — for example `pages/faq.mdx` or `pages/remote-sensing/inversions.mdx`. The dev server reloads automatically.

**To add a new page:**

1. Create the MDX file in the appropriate directory, e.g. `pages/fundamentals/my-new-page.mdx`.
2. Register it in that directory's `_meta.ts` so it appears in the sidebar with the right label and order:

   ```ts
   export default {
     index: "Overview",
     inputs: "Input Parameters",
     "my-new-page": "My New Page",  // key matches the filename without .mdx
     // ...
   }
   ```

   The order of keys in `_meta.ts` is the order shown in the sidebar.

**To add a new top-level section:**

1. Create a new directory under `pages/`, e.g. `pages/my-section/`.
2. Add an `index.mdx` (this is the section's landing page) and a `_meta.ts` listing its child pages.
3. Register the section in the top-level `pages/_meta.ts`.

## Deployment

The site is deployed via Vercel and is connected to this repo. Pushes to `main` trigger a production deploy automatically; PRs get preview deploys.

Before pushing, verify the build locally:

```bash
pnpm build
```

If `pnpm build` passes, Vercel will too.

## License

This project is licensed under the MIT License.
