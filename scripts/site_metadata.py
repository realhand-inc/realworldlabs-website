"""Production metadata, discoverability files, and fingerprinted static assets."""
from pathlib import Path
from html import escape
from hashlib import sha256
from functools import lru_cache
import json
import re
from share_cards import card_data

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public'
ORIGIN='https://www.realworldlabs.com'
SITE_NAME='Realworld Labs'
EMAIL='sales@realworldlabs.com'
ASSETS={}
ROUTES=[]
CARDS={}

def prepare_assets():
    ASSETS.clear();ROUTES.clear();CARDS.clear();resource_url.cache_clear()
    folder=(PUBLIC/'assets/build').resolve()
    assert folder.parent==(PUBLIC/'assets').resolve()
    folder.mkdir(parents=True,exist_ok=True)
    keep=set()
    for name in ['pages.css','pages.js','ecosystem.css','ecosystem.js']:
        content=(PUBLIC/name).read_bytes().replace(b'\r\n',b'\n')
        stem,suffix=name.rsplit('.',1)
        filename=stem+'.'+sha256(content).hexdigest()[:12]+'.'+suffix
        target=folder/filename
        target.write_bytes(content)
        keep.add(filename)
        ASSETS['/'+name]='/assets/build/'+filename
    for target in folder.iterdir():
        if target.is_file() and re.fullmatch(r'(?:pages|ecosystem)\.[0-9a-f]{12}\.(?:css|js)',target.name) and target.name not in keep:
            assert target.resolve().parent==folder
            target.unlink()
    for card in card_data():
        image='/assets/share/'+card['key']+'.png'
        if not (PUBLIC/image.lstrip('/')).is_file():
            raise FileNotFoundError('Missing share image '+image+'. Run scripts/render_share_cards.py.')
        CARDS[card['path']]=(image,card['alt'])

def asset_url(path):
    return ASSETS[path]

@lru_cache(maxsize=None)
def resource_url(path):
    content=(PUBLIC/path.lstrip('/')).read_bytes()
    return path+'?v='+sha256(content).hexdigest()[:12]

def _json_script(value):
    text=json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    return '<script type="application/ld+json">'+text+'</script>'

def _structured_data(title,description,path,image,image_alt,article):
    canonical=ORIGIN+path
    organization={'@type':'Organization','@id':ORIGIN+'/#organization','name':SITE_NAME,'url':ORIGIN+'/','email':EMAIL,'logo':{'@type':'ImageObject','url':ORIGIN+'/assets/brand/realworld-labs.png','width':1094,'height':201}}
    website={'@type':'WebSite','@id':ORIGIN+'/#website','url':ORIGIN+'/','name':SITE_NAME,'inLanguage':'en','publisher':{'@id':ORIGIN+'/#organization'}}
    webpage={'@type':'CollectionPage' if path in ['/products/','/blogs/'] else 'WebPage','@id':canonical+'#webpage','url':canonical,'name':title+' | '+SITE_NAME,'description':description,'inLanguage':'en','isPartOf':{'@id':ORIGIN+'/#website'},'primaryImageOfPage':{'@type':'ImageObject','contentUrl':image,'width':1200,'height':630,'caption':image_alt}}
    graph=[organization,website,webpage]
    if path!='/':
        crumbs=[('Home',ORIGIN+'/')]
        if path.startswith('/products/'):
            crumbs.append(('Products',ORIGIN+'/products/'))
        elif path.startswith('/blogs/'):
            crumbs.append(('Blogs',ORIGIN+'/blogs/'))
        if path not in ['/products/','/blogs/']:
            crumbs.append((title.split(' — ')[0],canonical))
        graph.append({'@type':'BreadcrumbList','@id':canonical+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':i+1,'name':label,'item':url} for i,(label,url) in enumerate(crumbs)]})
        webpage['breadcrumb']={'@id':canonical+'#breadcrumb'}
    if article:
        graph.append({'@type':'BlogPosting','@id':canonical+'#article','headline':article['title'],'description':description,'url':canonical,'mainEntityOfPage':{'@id':canonical+'#webpage'},'image':[image],'datePublished':article['published'],'author':{'@type':'Organization','name':article['author']},'publisher':{'@id':ORIGIN+'/#organization'},'isBasedOn':article['sourceUrl'],'articleSection':article.get('category','Research'),'inLanguage':'en'})
        webpage['mainEntity']={'@id':canonical+'#article'}
    return _json_script({'@context':'https://schema.org','@graph':graph})

def page_head(title,description,path,noindex=False,article=None):
    e=lambda value:escape(str(value),quote=True)
    canonical=ORIGIN+path
    parts=[
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="theme-color" content="#f1f3f7">',
        '<title>'+e(title)+' | '+SITE_NAME+'</title>',
        '<meta name="description" content="'+e(description)+'">',
        '<meta name="robots" content="'+('noindex,follow' if noindex else 'index,follow,max-image-preview:large')+'">',
        '<link rel="icon" href="'+resource_url('/assets/brand/favicon.svg')+'" type="image/svg+xml">',
        '<link rel="icon" href="'+resource_url('/assets/brand/favicon-32.png')+'" sizes="32x32" type="image/png">',
        '<link rel="icon" href="'+resource_url('/assets/brand/favicon-16.png')+'" sizes="16x16" type="image/png">',
        '<link rel="apple-touch-icon" href="'+resource_url('/assets/brand/apple-touch-icon.png')+'" sizes="180x180">',
        '<link rel="manifest" href="/site.webmanifest">',
        '<link rel="preload" href="/assets/fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="stylesheet" href="'+asset_url('/pages.css')+'">',
        '<link rel="stylesheet" href="'+asset_url('/ecosystem.css')+'">',
        '<script src="'+asset_url('/pages.js')+'" defer></script>'
    ]
    if not noindex:
        ROUTES.append(path)
        image,image_alt=CARDS[path]
        image=ORIGIN+resource_url(image)
        parts.extend([
            '<link rel="canonical" href="'+e(canonical)+'">',
            '<meta property="og:site_name" content="'+SITE_NAME+'">',
            '<meta property="og:locale" content="en_US">',
            '<meta property="og:type" content="'+('article' if article else 'website')+'">',
            '<meta property="og:title" content="'+e(title)+' | '+SITE_NAME+'">',
            '<meta property="og:description" content="'+e(description)+'">',
            '<meta property="og:url" content="'+e(canonical)+'">',
            '<meta property="og:image" content="'+e(image)+'">',
            '<meta property="og:image:secure_url" content="'+e(image)+'">',
            '<meta property="og:image:type" content="image/png">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:image:alt" content="'+e(image_alt)+'">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:title" content="'+e(title)+' | '+SITE_NAME+'">',
            '<meta name="twitter:description" content="'+e(description)+'">',
            '<meta name="twitter:image" content="'+e(image)+'">',
            '<meta name="twitter:image:alt" content="'+e(image_alt)+'">'
        ])
        if article:
            parts.append('<meta property="article:published_time" content="'+e(article['published'])+'">')
        parts.append(_structured_data(title,description,path,image,image_alt,article))
    return '\n'.join(parts)

def write_discovery():
    paths=list(dict.fromkeys(ROUTES))
    assert len(paths)==12 and set(paths)==set(CARDS),paths
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap+=''.join('  <url><loc>'+escape(ORIGIN+path)+'</loc></url>\n' for path in paths)
    sitemap+='</urlset>\n'
    (PUBLIC/'sitemap.xml').write_bytes(sitemap.encode('utf-8'))
    (PUBLIC/'robots.txt').write_bytes(('User-agent: *\nAllow: /\n\nSitemap: '+ORIGIN+'/sitemap.xml\n').encode('utf-8'))
    manifest={'name':SITE_NAME,'short_name':SITE_NAME,'start_url':'/','display':'browser','background_color':'#f1f3f7','theme_color':'#f1f3f7','icons':[{'src':'/assets/brand/icon-192.png','sizes':'192x192','type':'image/png','purpose':'any'},{'src':'/assets/brand/icon-512.png','sizes':'512x512','type':'image/png','purpose':'any'}]}
    (PUBLIC/'site.webmanifest').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf-8'))

TEXT_EXTENSIONS={'.py','.json','.js','.mjs','.css','.html','.xml','.txt','.svg','.webmanifest'}

def file_digest(path):
    content=path.read_bytes()
    if path.suffix in TEXT_EXTENSIONS:content=content.replace(b'\r\n',b'\n')
    return sha256(content).hexdigest()

def record_build_state():
    inputs=[
        'scripts/build_site.py','scripts/site_experience.py','scripts/site_metadata.py',
        'scripts/share_cards.py','scripts/render_share_cards.py','scripts/validate_site.py','scripts/check_build.mjs','scripts/preview_site.py','scripts/optimize_images.py',
        'content/hardware.json','content/realstudio.json','content/blog-latest.json','content/image-optimizations.json',
        'public/pages.css','public/pages.js','public/ecosystem.css','public/ecosystem.js',
        'package.json','vercel.json','.gitattributes'
    ]
    image_rows=json.loads((ROOT/'content/image-optimizations.json').read_text(encoding='utf-8'))['images']
    inputs += ['public'+row['source'] for row in image_rows]
    outputs=list(PUBLIC.rglob('*.html'))+list((PUBLIC/'assets/build').iterdir())+list((PUBLIC/'assets/share').glob('*.png'))
    outputs += [PUBLIC/'sitemap.xml',PUBLIC/'robots.txt',PUBLIC/'site.webmanifest',PUBLIC/'favicon.ico']
    outputs += [PUBLIC/'assets/brand'/name for name in ['favicon.svg','favicon-16.png','favicon-32.png','apple-touch-icon.png','icon-192.png','icon-512.png']]
    outputs += list({PUBLIC/row['served'].lstrip('/') for row in image_rows})
    state={'version':1,'inputs':{name:file_digest(ROOT/name) for name in inputs},'outputs':{p.relative_to(ROOT).as_posix():file_digest(p) for p in sorted(outputs)}}
    (ROOT/'content/build-state.json').write_bytes((json.dumps(state,indent=2)+'\n').encode('utf-8'))
