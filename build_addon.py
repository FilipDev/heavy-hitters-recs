#!/usr/bin/env python3
"""Build the static Stremio catalog addon from the dashboard dataset.

Source of truth: the FILMS array embedded in the dashboard source
(~/workspace/ts-spaces/movie-recommendations-dashboard/index.html),
which carries the verified IMDb IDs. Output: a purely static addon
(manifest.json + catalog JSON files paginated at 100/page, the way
Stremio's core requests them) that any static HTTPS host can serve.
"""
import json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.expanduser('~/workspace/ts-spaces/movie-recommendations-dashboard/index.html')
PAGE = 100

s = open(DASH).read()
i = s.find('var FILMS = ') + len('var FILMS = ')
films, _ = json.JSONDecoder().raw_decode(s[i:])
assert len(films) == 192, len(films)
assert len({f['imdb'] for f in films}) == 192

def meta(f):
    tt = f['imdb']
    return {
        'id': tt,
        'type': 'movie',
        'name': f['t'],
        'poster': f'https://images.metahub.space/poster/medium/{tt}/img',
        'background': f'https://images.metahub.space/background/medium/{tt}/img',
        'genres': f['g'],
        'releaseInfo': str(f['y']),
        'year': f['y'],
        'runtime': f"{f['m']} min",
        'director': f['d'],
        'description': f['desc'],
    }

def write_catalog(cid, items):
    base = os.path.join(HERE, 'catalog', 'movie')
    os.makedirs(base, exist_ok=True)
    pages = [items[k:k + PAGE] for k in range(0, len(items), PAGE)] or [[]]
    with open(os.path.join(base, f'{cid}.json'), 'w') as fh:
        json.dump({'metas': pages[0]}, fh, ensure_ascii=False, indent=1)
    for pno, page_items in enumerate(pages[1:], start=1):
        d = os.path.join(base, cid)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f'skip={pno * PAGE}.json'), 'w') as fh:
            json.dump({'metas': page_items}, fh, ensure_ascii=False, indent=1)
    return len(pages)

allm = [meta(f) for f in films]
am = [meta(f) for f in films if f['list'] == 'A']
bm = [meta(f) for f in films if f['list'] == 'B']
assert len(am) == 18 and len(bm) == 174

# Clean previous catalog output so stale pages cannot linger
shutil.rmtree(os.path.join(HERE, 'catalog'), ignore_errors=True)
p_all = write_catalog('recommendations-192', allm)
p_a = write_catalog('recommendations-a', am)
p_b = write_catalog('recommendations-b', bm)

manifest = {
    'id': 'community.recommendations192',
    'version': '1.0.0',
    'name': '192 Movie Recommendations',
    'description': 'A personally curated list of 192 films — diverse plots and emotional intensities, each one chosen because it powerfully captures something specific. Catalog only: streams come from your other Stremio addons, and every film can be played, cast and added to your library natively in Stremio.',
    'resources': ['catalog'],
    'types': ['movie'],
    'idPrefixes': ['tt'],
    'catalogs': [
        {'type': 'movie', 'id': 'recommendations-192', 'name': 'All 192 Recommendations'},
        {'type': 'movie', 'id': 'recommendations-a', 'name': 'List A — First Picks (18)'},
        {'type': 'movie', 'id': 'recommendations-b', 'name': 'The Numbered List (174)'},
    ],
    'behaviorHints': {'adult': False, 'p2p': False, 'configurable': False, 'configurationRequired': False},
}
with open(os.path.join(HERE, 'manifest.json'), 'w') as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=1)

print(f'films=192 A={len(am)} B={len(bm)} pages: all={p_all} a={p_a} b={p_b}')
