"""Validate generated HTML, share cards, crawl files, and the static deployment contract."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
from hashlib import sha256
import json
import re
import struct
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://www.realworldlabs.com'

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.references=[];self.meta={};self.links=[];self.jsonld=[]
        self.h1=0;self.title='';self.in_title=False;self.in_schema=False;self.schema='';self.lang=None
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='html':self.lang=d.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='title':self.in_title=True
        if 'id' in d:self.ids.append(d['id'])
        if tag=='meta':self.meta[d.get('property',d.get('name',''))]=d.get('content','')
        if tag=='link':self.links.append(d)
        if tag=='script' and d.get('type')=='application/ld+json':self.in_schema=True;self.schema=''
        for name in ['href','src','poster','data-lightbox']:
            if d.get(name):self.references.append(d[name])
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='script' and self.in_schema:
            self.jsonld.append(json.loads(self.schema));self.in_schema=False
    def handle_data(self,data):
        if self.in_title:self.title+=data
        if self.in_schema:self.schema+=data

def png_dimensions(path):
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n',str(path)+' is not a PNG'
    return struct.unpack('>II',data[16:24])

def validate(public=None):
    public=Path(public or ROOT/'public').resolve()
    documents={p:Document(p.read_text(encoding='utf-8')) for p in public.rglob('*.html')}
    errors=[];canonicals=[];references=0;shares=set()
    def require(condition,message):
        if not condition:errors.append(message)
    def local_target(reference,source):
        url=urlsplit(reference)
        if url.scheme and (url.scheme!='https' or url.netloc!='www.realworldlabs.com'):return None,url
        if url.netloc and url.netloc!='www.realworldlabs.com':return None,url
        if not url.path:return source,url
        target=public/unquote(url.path.lstrip('/')) if url.path.startswith('/') else source.parent/unquote(url.path)
        if target.is_dir():target=target/'index.html'
        return target.resolve(),url
    required_meta=['description','og:type','og:title','og:description','og:url','og:image','og:image:alt','og:image:width','og:image:height','og:site_name','twitter:card','twitter:image','twitter:image:alt']
    for path,doc in documents.items():
        label=path.relative_to(public).as_posix()
        require(doc.lang=='en',label+': language missing')
        require(doc.h1==1,label+': expected exactly one h1')
        require(bool(doc.title.strip()),label+': missing title')
        require(len(doc.ids)==len(set(doc.ids)),label+': duplicate ids')
        canonical=[x.get('href') for x in doc.links if x.get('rel')=='canonical']
        if label=='404.html':
            require(not canonical,'404 must not canonicalize to another page')
            require('noindex' in doc.meta.get('robots',''),'404 must be noindex')
            require(not doc.jsonld,'404 should not declare a normal indexed page')
        else:
            require(len(canonical)==1,label+': missing or duplicate canonical')
            if canonical:
                url=canonical[0];canonicals.append(url)
                require(url.startswith(ORIGIN+'/') and url.endswith('/') and not urlsplit(url).query,label+': canonical format')
                require(doc.meta.get('og:url')==url,label+': OG URL differs from canonical')
                expected='/' if label=='index.html' else '/'+label[:-len('index.html')]
                require(url==ORIGIN+expected,label+': canonical points to a different page')
            for name in required_meta:require(bool(doc.meta.get(name)),label+': missing '+name)
            require(doc.meta.get('twitter:card')=='summary_large_image',label+': missing large share card')
            require('noindex' not in doc.meta.get('robots',''),label+': public page accidentally noindex')
            require(doc.meta.get('og:image')==doc.meta.get('twitter:image'),label+': share card mismatch')
            require(doc.meta.get('og:image:width')=='1200' and doc.meta.get('og:image:height')=='630',label+': share dimensions')
            image=doc.meta.get('og:image','')
            require(image.startswith(ORIGIN+'/assets/share/'),label+': share image must be absolute and local')
            target,parsed=local_target(image,path)
            if target and target.exists():
                require(png_dimensions(target)==(1200,630),label+': incorrect share raster size')
                shares.add(target)
                require(parse_qs(parsed.query).get('v')==[sha256(target.read_bytes()).hexdigest()[:12]],label+': stale share image version')
            else:errors.append(label+': missing share image')
            require(len(doc.jsonld)==1,label+': expected structured metadata')
            if doc.jsonld:
                graph=doc.jsonld[0].get('@graph',[])
                require(doc.jsonld[0].get('@context')=='https://schema.org',label+': schema context')
                require(any(x.get('@type')=='Organization' and x.get('email')=='sales@realworldlabs.com' for x in graph),label+': organization contact')
                if '/blogs/' in '/'+label and label!='blogs/index.html':
                    posts=[x for x in graph if x.get('@type')=='BlogPosting']
                    require(len(posts)==1 and posts[0].get('isBasedOn','').startswith('https://www.realhand.com/'),label+': article attribution')
                    require(doc.meta.get('og:type')=='article',label+': article OG type')
        for reference in doc.references:
            if reference.startswith('mailto:'):
                require(reference[7:].split('?')[0]=='sales@realworldlabs.com',label+': unexpected email')
                continue
            target,parsed=local_target(reference,path)
            if not target:continue
            references+=1
            require(target.is_relative_to(public),label+': reference escapes public')
            require(target.exists(),label+': missing '+reference)
            if target in documents and parsed.fragment:require(unquote(parsed.fragment) in documents[target].ids,label+': broken anchor '+reference)
    urls=[node.text for node in ET.parse(public/'sitemap.xml').getroot().findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    require(len(urls)==12 and len(set(urls))==12,'Expected 12 unique sitemap URLs')
    require(set(urls)==set(canonicals),'Sitemap must exactly match the public canonicals')
    require(not any('404' in url or '?' in url or '#' in url for url in urls),'Sitemap contains noncanonical URLs')
    robots=(public/'robots.txt').read_text(encoding='utf-8')
    require('User-agent: *' in robots and 'Allow: /' in robots and 'Disallow: /' not in robots,'Production robots must allow crawling')
    require('Sitemap: '+ORIGIN+'/sitemap.xml' in robots,'Robots sitemap location')
    manifest=json.loads((public/'site.webmanifest').read_text(encoding='utf-8'))
    for icon in manifest['icons']:
        target=public/icon['src'].lstrip('/')
        require(target.exists() and png_dimensions(target)==tuple(map(int,icon['sizes'].split('x'))),'Invalid manifest icon')
    require(png_dimensions(public/'assets/brand/apple-touch-icon.png')==(180,180),'Apple touch icon size')
    for path in (public/'assets/build').iterdir():
        match=re.fullmatch(r'(pages|ecosystem)\.([a-f0-9]{12})\.(css|js)',path.name)
        require(bool(match),'Unexpected build asset '+path.name)
        if match:require(sha256(path.read_bytes()).hexdigest()[:12]==match.group(2),'Build asset fingerprint mismatch '+path.name)
    config=json.loads((ROOT/'vercel.json').read_text(encoding='utf-8'))
    require(config.get('outputDirectory')=='public' and config.get('cleanUrls') and config.get('trailingSlash'),'Static deployment route settings')
    require(not config.get('rewrites'),'Do not rewrite unknown pages to successful homepage responses')
    require(config.get('buildCommand')=='npm run verify:build','Deployment must verify generated artifacts')
    require(len(shares)==12,'Expected page-specific share images for all 12 public pages')
    image_rows=json.loads((ROOT/'content/image-optimizations.json').read_text(encoding='utf-8'))['images']
    for row in image_rows:
        for field,digest in [('source','source_sha256'),('served','served_sha256')]:
            target=public/row[field].lstrip('/')
            require(target.exists(),row[field]+': missing optimized image source/output')
            if target.exists():require(sha256(target.read_bytes()).hexdigest()==row[digest],row[field]+': image changed; rerun optimize_images.py')
        require(row['served_bytes']<row['source_bytes'] and len(row['rgba_sha256'])==64,row['served']+': missing lossless proof')
    if errors:raise AssertionError('\n'.join(errors))
    return dict(html_pages=len(documents),indexed_pages=len(canonicals),sitemap_urls=len(urls),share_images=len(shares),local_references=references,status='passed')

def main():
    print(json.dumps(validate(),indent=2))

if __name__=='__main__':main()
