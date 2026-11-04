#!/usr/bin/env python3
"""Build the static Stremio catalog addon from the dashboard dataset.

Source of truth: the FILMS array embedded in the dashboard source
(~/workspace/ts-spaces/movie-recommendations-dashboard/index.html),
which carries the verified IMDb IDs.

Design (v1.1.0, per Filip 2026-11-04): ONE catalog, not split into
List A / List B. The manifest declares a `genre` extra with all
genres present in the list, so Stremio's Discover page offers a genre
selector for the catalog. Stremio requests a genre view as
/catalog/movie/recommendations-192/genre=<Genre>.json (plus
genre=<Genre>&skip=100.json for pagination past 100), so those files
are pre-generated statically for every genre.
"""
import json, os, shutil, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.expanduser('~/workspace/ts-spaces/movie-recommendations-dashboard/index.html')
PAGE = 100
CID = 'recommendations-192'

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

genres = sorted({g for f in films for g in f['g']})

def dump(path, metas):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        json.dump({'metas': metas}, fh, ensure_ascii=False, indent=1)

base = os.path.join(HERE, 'catalog', 'movie')
sub = os.path.join(base, CID)
shutil.rmtree(os.path.join(HERE, 'catalog'), ignore_errors=True)
os.makedirs(sub, exist_ok=True)

allm = [meta(f) for f in films]

# Main catalog: page 1 at <CID>.json, page 2 at <CID>/skip=100.json
dump(os.path.join(base, f'{CID}.json'), allm[:PAGE])
if len(allm) > PAGE:
    dump(os.path.join(sub, f'skip={PAGE}.json'), allm[PAGE:])

# One static file per genre view (+ a &skip= page when a genre tops 100)
genre_counts = {}
for g in genres:
    gm = [meta(f) for f in films if g in f['g']]
    genre_counts[g] = len(gm)
    dump(os.path.join(sub, f'genre={g}.json'), gm[:PAGE])
    if len(gm) > PAGE:
        dump(os.path.join(sub, f'genre={g}&skip={PAGE}.json'), gm[PAGE:])

manifest = {
    'id': 'community.recommendations192',
    'version': '1.1.0',
    'name': '192 Movie Recommendations',
    'description': 'A personally curated list of 192 films — diverse plots and emotional intensities, each one chosen because it powerfully captures something specific. One catalog, browsable by genre in Stremio\'s Discover. Catalog only: streams come from your other Stremio addons, and every film can be played, cast and added to your library natively in Stremio.',
    'resources': ['catalog'],
    'types': ['movie'],
    'idPrefixes': ['tt'],
    'catalogs': [
        {
            'type': 'movie',
            'id': CID,
            'name': '192 Movie Recommendations',
            'extra': [{'name': 'genre', 'options': genres, 'isRequired': False}],
        },
    ],
    'behaviorHints': {'adult': False, 'p2p': False, 'configurable': False, 'configurationRequired': False},
}
with open(os.path.join(HERE, 'manifest.json'), 'w') as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=1)

print(f'films=192 genres={len(genres)}')
print('genre counts:', json.dumps(genre_counts, ensure_ascii=False))
