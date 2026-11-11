# crabbygeorges.com

Static website for Crabby George's Seafood Buffet, 7904 N Kings Hwy, Myrtle Beach, SC.

- `src/` – content: page sections (`src/partials/*.html`), styles (`src/site.css`, `src/extra.css`), script (`src/site.js`)
- `build.py` – page list, titles/descriptions, FAQ, drinks, schema.org data, sitemap, robots.txt, llms.txt
- `site/` – the generated website that Netlify publishes (no build step on Netlify)

To change something: edit `src/` or `build.py`, run `python3 build.py`, commit and push. Netlify deploys automatically.

Keep these the same everywhere (site, Google Business Profile, Yelp, TripAdvisor, Apple Maps, Bing Places):
name, address, phone (843) 839-4044, hours.
