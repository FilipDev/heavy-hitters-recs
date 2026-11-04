# Heavy Hitters — static Stremio catalog addon

A purely static Stremio addon (no server code) that publishes the
recommendation list as ONE catalog, **Heavy Hitters**
(`recommendations-192`). The manifest declares a `genre` extra with all
23 genres in the list, so Stremio's Discover page offers a genre selector
for the catalog; each genre view is a pre-generated static file
(`catalog/movie/recommendations-192/genre=<Genre>.json`, plus
`&skip=` pages for genres over 100 — Drama paginates to three pages,
Documentary to two, and the base catalog to four).

Every entry carries its verified IMDb ID, poster/backdrop (via
images.metahub.space), year, genres, runtime, director and the
“powerfully captures…” description from the dashboard. The addon also
serves each film's detail page (the `meta` resource, one static file per
film under `meta/movie/<tt>.json`): the description there combines the
“powerfully captures…” note with the IMDb synopsis, and the remaining
detail data (rating, cast, links) is Cinemeta's own meta, preserved
as-is. Streams and casting are Stremio's own — this addon provides the
catalog and film details only.

## Files

- `manifest.json` — the addon manifest. Its hosted URL is what you paste
  into Stremio to install.
- `catalog/movie/<catalog-id>.json` — first page (100 items) of each catalog.
- `catalog/movie/<catalog-id>/skip=100.json` — second page, requested by
  Stremio when scrolling (pagination is 100/page).
- `index.html` — landing page with an Install button; it builds the
  manifest URL from wherever the files are hosted.
- `build_addon.py` — regenerates all JSON from the dashboard dataset
  (`var FILMS` in the dashboard source). Re-run after any list change.

## Hosting requirements

Any static host works, provided:

1. The files are served over **HTTPS** at fixed paths (Stremio clients
   fetch `…/manifest.json` and `…/catalog/movie/…` exactly).
2. Responses send **`Access-Control-Allow-Origin: *`** (needed by
   Stremio Web; GitHub Pages does this by default).

## Install

Open the hosted `index.html` and tap **Install in the Stremio app**, or
paste the manifest URL into Stremio → Addons → Community Add-ons.
