"""Generate static GAMS browsing pages from the portable software catalog."""
from html import escape
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

from catalog_export import BASE_URL, ROOT
from xpackage_gams import ancestors, class_order


def e(value):
    return escape(str(value), quote=True)


def link(url, label, **attrs):
    attributes = ''.join(f' {key}="{e(value)}"' for key, value in attrs.items())
    return f'<a href="{e(url)}"{attributes}>{e(label)}</a>'


def generate_gams_site(destination, feed, *, asset_version=None):
    """Render the already validated feed; no service calls or package builds."""
    destination = Path(destination)
    tree = feed['taxonomies']['gams']['classes']
    projects = sorted(feed['projects'], key=lambda p: p['name'].casefold())
    by_class = {code: [p for p in projects if code in p['curation']['gams_codes']] for code in tree}
    demos = feed.get('demonstrations', [])
    written = []
    written_paths = set()

    def package_path(project):
        return 'packages/' + quote(project.get('playground', {}).get('package_id', project['id']), safe='') + '/'

    def page(path, title, description, body, depth=0):
        prefix = '../' * depth
        asset_suffix = '?v=' + asset_version if asset_version else ''
        url = BASE_URL + '/gams/' + path
        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'">
  <meta name="description" content="{e(description)}">
  <title>{e(title)} | Fortran GAMS catalog</title>
  <link rel="canonical" href="{e(url)}">
  <link rel="stylesheet" href="{prefix}catalog.css{asset_suffix}">
  <script type="module" src="{prefix}search.mjs{asset_suffix}"></script>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="masthead"><div class="shell">
  <a class="brand" href="{prefix or './'}">FORTRAN SOFTWARE CATALOG</a>
  <nav aria-label="Main navigation">{link(prefix or './', 'Browse GAMS')} {link(prefix+'../fpm/', 'FPM playground')} {link(prefix+'../', 'Fortran playground')}</nav>
</div></header>
<main id="content" class="shell">{body}</main>
<footer class="shell"><p>Classifications maintained by the playground, using the {link('https://gams.nist.gov/cgi-bin/serve.cgi', 'NIST GAMS scheme')} and {link('https://netlib.org/misc/gams.html', 'Netlib detailed taxonomy')}.</p>
<p>{link(prefix+'../catalog/catalog-v1.json', 'Download catalog data')} · {link('https://github.com/Beliavsky/fortran-playground', 'Source and corrections')}</p></footer>
</body></html>
'''
        target = destination / path / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
        written_paths.add(target)
        written.append(url)

    def class_links(codes, prefix):
        return ' '.join(link(prefix + code + '/', code, title=tree[code]['label']) for code in codes)

    def card(project, prefix, code=None):
        curation = project['curation']
        records = curation.get('procedures', [])
        matched = [p for p in records if code is None or any(code in ancestors(tree, c) for c in p['gams_codes'])]
        search = ' '.join([project['name'], project['repository']['owner'], project['repository']['name'],
                           project['description'], *project.get('categories', []),
                           *project.get('github', {}).get('topics', []), *curation.get('topics', []),
                           *[code+' '+tree[code]['label'] for code in curation['gams_codes']],
                           *[p['module']+' '+p['procedure'] for p in records]])
        procedures = ''
        if code and matched:
            procedures = '<p class="procedures"><span class="label">Matching APIs:</span> ' + e('; '.join(p['procedure'] for p in matched)) + '</p>'
        actions = [link(prefix+package_path(project), 'Package details'), link(project['repository']['url'], 'Repository')]
        playground = project.get('playground')
        if playground:
            actions.append(link(playground['url'], 'Try in playground'))
        return f'''<article class="package" data-search="{e(search)}">
<h3>{link(prefix+package_path(project), project['name'])}</h3>
<p class="owner">{e(project['repository']['owner'])} / {e(project['repository']['name'])}</p>
<p>{e(project['description'])}</p>{procedures}
<p class="codes">{class_links(curation['gams_codes'], prefix)}</p>
<p class="actions">{' · '.join(actions)}</p></article>'''

    def listing(items, prefix, code=None):
        return f'''<section class="package-section" aria-labelledby="packages-heading">
<div class="section-heading"><h2 id="packages-heading">Packages</h2><span id="result-count" role="status">{len(items)} packages</span></div>
<div id="search-controls" class="search-controls" hidden><label for="package-search">Search these packages</label>
<input id="package-search" type="search" placeholder="Name, author, topic or procedure" autocomplete="off">
<button id="clear-search" type="button">Clear</button></div>
<p id="no-results" hidden>No packages match. Try fewer words or clear the search.</p>
<div class="package-grid">{''.join(card(p, prefix, code) for p in items)}</div>
</section>'''

    def children(parent, prefix):
        codes = sorted((c for c, info in tree.items() if info['parent'] == parent), key=class_order)
        if not codes:
            return ''
        heading = 'Main classifications' if parent is None else 'Subclasses'
        items = ''.join(f'<li>{link(prefix+c+"/", c+" — "+tree[c]["label"])} <span class="count">{len(by_class[c])}</span></li>' for c in codes)
        return f'<section class="class-section"><h2>{heading}</h2><ul class="class-list">{items}</ul></section>'

    page('', 'Fortran software by GAMS classification',
         'Browse Fortran packages by mathematical problem, with reviewed procedure mappings and runnable examples.',
         '<section class="intro"><p class="eyebrow">BROWSE BY MATHEMATICAL PROBLEM</p>'
         '<h1>Fortran software by GAMS classification</h1>'
         f'<p class="lede">Explore {len(projects)} selected packages, from linear algebra and optimization to statistics and software tools.</p>'
         '<p>Each package has a checked example in the FPM playground with GNU Fortran 16. '
         'Browse here without running code, then open a package to try it.</p></section>'
         + children(None, '') + listing(projects, ''))

    for code in sorted(tree, key=class_order):
        lineage = list(reversed(ancestors(tree, code)))
        crumbs = link('../', 'All classes') + ''.join(' / ' + link('../'+c+'/', c+' — '+tree[c]['label']) for c in lineage[:-1])
        intro = (f'<nav class="breadcrumbs" aria-label="Breadcrumb">{crumbs}</nav>'
                 f'<section class="intro"><p class="eyebrow">GAMS {e(code)}</p><h1>{e(tree[code]["label"])}</h1>'
                 f'<p class="lede">{len(by_class[code])} matching packages</p>'
                 '<p>Includes packages assigned to this class and its descendants. A package may cover only part of a class.</p>'
                 f'<p>{link("https://gams.nist.gov/cgi-bin/serve.cgi/Class/"+code, "GAMS definition")}</p></section>')
        empty = '<p class="empty">No selected package is currently classified here. This does not imply that no Fortran implementation exists.</p>' if not by_class[code] else ''
        page(code+'/', 'GAMS '+code+' — '+tree[code]['label'],
             'Fortran packages for '+tree[code]['label']+', classified as GAMS '+code+'.',
             intro+children(code, '../')+empty+listing(by_class[code], '../', code), depth=1)

    for project in projects:
        curation = project['curation']
        repository = project['repository']['url']
        revision = curation['reviewed_revision']
        source = repository + '/tree/' + revision
        playground = project.get('playground')
        actions = [link(repository, 'Repository'), link(source, 'Pinned source ('+revision[:12]+')')]
        if playground:
            actions.append(link(playground['url'], 'Try in playground'))
            actions.append(link('https://github.com/Beliavsky/fortran-playground/blob/main/'+playground['example']['path'], 'Checked package example'))
        intro = (f'<nav class="breadcrumbs" aria-label="Breadcrumb">{link("../../", "All classes")}</nav>'
                 f'<section class="intro"><p class="eyebrow">{e(project["repository"]["owner"])}</p><h1>{e(project["name"])}</h1>'
                 f'<p class="lede">{e(project["description"])}</p><p class="actions">{" · ".join(actions)}</p></section>')
        codes = '<section><h2>GAMS classifications</h2><ul class="classification-list">' + ''.join(
            '<li>'+link('../../'+code+'/', code+' — '+tree[code]['label'])+'</li>' for code in curation['gams_codes']) + '</ul></section>'
        topics = sorted(set(curation.get('topics', []) + project.get('github', {}).get('topics', [])))
        details = '<section><h2>About this package</h2><dl><dt>Category</dt><dd>'+e(', '.join(project.get('categories', [])))+'</dd><dt>License</dt><dd>'+e(project.get('license', {}).get('label') or 'See repository')+'</dd></dl>'
        if topics:
            details += '<p><span class="label">Topics:</span> '+e(', '.join(topics))+'</p>'
        if curation.get('gams_notes'):
            details += '<details><summary>Classification scope and review notes</summary><p>'+e(curation['gams_notes'])+'</p></details>'
        details += '</section>'
        procedures = '<section><h2>Reviewed procedures</h2><p>These mappings have pinned source evidence. A checked package example may exercise only some of them; source review is not a numerical benchmark.</p>'
        for record in curation.get('procedures', []):
            base = repository+'/blob/'+record['revision']+'/'
            sources = [link(base+quote(item['path'], safe='/')+'#L'+str(item['line']), item['path']) for item in record['evidence']]
            examples = [link(base+quote(item['path'], safe='/'), item['path']) for item in record.get('author_examples', [])]
            procedure_demos = [d for d in demos if d['procedure_id'] == record['id']]
            procedures += (f'<article class="procedure" id="{e(record["id"])}"><h3>{e(record["procedure"])}</h3>'
                           f'<p><span class="label">Module:</span> <code>{e(record["module"])}</code></p>'
                           f'<p class="codes">{class_links(record["gams_codes"], "../../")}</p>'
                           f'<p><span class="label">Derivatives / callbacks:</span> {e(record["derivatives"])}</p>'
                           f'<p>{e(record["notes"])}</p><p><span class="label">Pinned source:</span> {" · ".join(sources)}</p>')
            if examples:
                procedures += '<p><span class="label">Author examples/tests:</span> '+' · '.join(examples)+'</p>'
            for demo in procedure_demos:
                procedures += '<p>'+link(demo['url'], 'Run checked GAMS driver: '+demo['name'])+'</p>'
            procedures += '</article>'
        if not curation.get('procedures'):
            procedures += '<p>No procedure-level mapping is recorded yet. The classifications describe package capabilities.</p>'
        procedures += '</section>'
        page(package_path(project), project['name'], project['description'], intro+codes+details+procedures, depth=2)

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += ''.join('<url><loc>'+xml_escape(url)+'</loc></url>\n' for url in written) + '</urlset>\n'
    (destination/'sitemap.xml').write_text(sitemap, encoding='utf-8')
    # Only remove obsolete generated HTML, retaining hand-maintained assets.
    for old in [*destination.glob('*/index.html'), *destination.glob('packages/*/index.html')]:
        if old not in written_paths:
            old.unlink()
    return len(written)


if __name__ == '__main__':
    site = ROOT / '_site'
    # Use the normal builder so the catalog's CSS, search and playground links work.
    from xsite import build_site
    print('Built site with GAMS catalog:', build_site(ROOT/'site', site))
