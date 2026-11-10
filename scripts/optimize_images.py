
"""Optional authoring tool: losslessly encode large active PNGs as WebP.
Requires Pillow with WebP support. Original PNG files remain the source assets.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from hashlib import sha256
from PIL import Image
import json

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public'
REPORT=ROOT/'content/image-optimizations.json'

class Images(HTMLParser):
    def __init__(self):super().__init__();self.refs=set()
    def handle_starttag(self,tag,attrs):
        if tag=='img':
            src=dict(attrs).get('src','')
            if src.startswith('/'):self.refs.add(unquote(urlsplit(src).path))

def main():
    existing=json.loads(REPORT.read_text(encoding='utf-8'))['images'] if REPORT.exists() else []
    known={row['source']:row for row in existing}
    refs=set(known)
    for page in PUBLIC.rglob('*.html'):
        reader=Images();reader.feed(page.read_text(encoding='utf-8'));refs.update(reader.refs)
    selected=[url for url in sorted(refs) if url.endswith('.png') and (PUBLIC/url.lstrip('/')).stat().st_size>300000]
    if '/assets/hardware/p7/hero.png' in selected:
        selected.remove('/assets/hardware/p7/hero.png');selected.insert(0,'/assets/hardware/p7/hero.png')
    results=[];mapping={};by_digest={}
    for url in selected:
        source=PUBLIC/url.lstrip('/')
        original=source.read_bytes();digest=sha256(original).hexdigest()
        if digest in by_digest:
            row={**by_digest[digest],'source':url}
            results.append(row);mapping[url]=row['served'];continue
        if url in known:
            prior=known[url];cached=PUBLIC/prior['served'].lstrip('/')
            if prior['source_sha256']==digest and cached.exists() and sha256(cached.read_bytes()).hexdigest()==prior['served_sha256']:
                results.append(prior);mapping[url]=prior['served'];by_digest[digest]=prior
                print('Verified existing lossless output:',url,flush=True)
                continue
        target=PUBLIC/known[url]['served'].lstrip('/') if url in known else source.with_suffix('.webp')
        if target.exists() and url not in known:target=source.with_name(source.stem+'-lossless.webp')
        assert target.resolve().is_relative_to(PUBLIC.resolve())
        with Image.open(source) as image:
            if image.mode not in ['RGB','RGBA']:raise ValueError('Unsupported source mode: '+str(source))
            expected=sha256(image.convert('RGBA').tobytes()).hexdigest()
            image.save(target,format='WEBP',lossless=True,exact=True,quality=100,method=6,icc_profile=image.info.get('icc_profile',b''),exif=image.info.get('exif',b''))
            size=image.size
        with Image.open(target) as encoded:
            assert encoded.size==size and sha256(encoded.convert('RGBA').tobytes()).hexdigest()==expected,'Pixel mismatch: '+url
        if target.stat().st_size>=len(original)*.95:
            if url not in known:target.unlink()
            print('Kept PNG; no meaningful saving:',url,flush=True);continue
        served='/'+target.relative_to(PUBLIC).as_posix()
        row=dict(source=url,served=served,source_bytes=len(original),served_bytes=target.stat().st_size,width=size[0],height=size[1],source_sha256=digest,served_sha256=sha256(target.read_bytes()).hexdigest(),rgba_sha256=expected)
        results.append(row);mapping[url]=served;by_digest[digest]=row
        print(round(len(original)/1024),'KB ->',round(target.stat().st_size/1024),'KB',url,flush=True)
    for name in ['content/hardware.json','content/blog-latest.json','scripts/build_site.py','scripts/site_experience.py']:
        path=ROOT/name;text=path.read_text(encoding='utf-8')
        for old,new in mapping.items():text=text.replace(old,new)
        if name=='scripts/site_experience.py' and '/assets/products/p7.png' in mapping:
            old="asset='l30-silver-palm.webp' if node['key']=='realhand' else 'p7.png'"
            new="asset='/assets/products/l30-silver-palm.webp' if node['key']=='realhand' else '"+mapping['/assets/products/p7.png']+"'"
            if old in text:text=text.replace(old,new).replace('src="/assets/products/{asset}"','src="{asset}"')
        path.write_bytes(text.encode('utf-8'))
    REPORT.write_bytes((json.dumps(dict(images=results),indent=2)+'\n').encode('utf-8'))
    before=sum(row['source_bytes'] for row in results)
    after=sum(row['served_bytes'] for row in results)
    print(json.dumps(dict(references=len(results),unique_images=len({row['served'] for row in results}),before_mb=round(before/1048576,2),after_mb=round(after/1048576,2),reduction_percent=round((1-after/before)*100,1),pixel_validation='exact RGBA match')),flush=True)

if __name__=='__main__':main()
