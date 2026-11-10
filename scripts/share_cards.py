"""Branded sharing artwork. HTML/SVG is rendered to PNG by render_share_cards.py."""
from pathlib import Path
from html import escape
import json
from site_experience import product_visual

ROOT = Path(__file__).resolve().parents[1]

def card_data():
    hardware=json.loads((ROOT/'content/hardware.json').read_text(encoding='utf-8'))
    blog=json.loads((ROOT/'content/blog-latest.json').read_text(encoding='utf-8'))
    data=[
        dict(key='home',path='/',title='Intelligence.\nMade physical.',eyebrow='The total solution',summary='AI models, software, and robotics.\nOne connected product ecosystem.',kind='ecosystem',alt='Realworld Labs: RealBrain, RealStudio, RealHand, RealArm, and RealBot in one product ecosystem.'),
        dict(key='products',path='/products/',title='One ecosystem.\nFive product families.',eyebrow='Our products',summary='Explore RealHand, RealArm, RealStudio,\nRealBot, and RealBrain.',kind='ecosystem',alt='The five Realworld Labs product families, from AI models and software to robotic hardware.')
    ]
    for p in hardware:
        family='RealArm' if p['slug']=='p7' else 'RealHand'
        data.append(dict(key=p['slug'],path='/products/'+p['slug']+'/',title=p['name'],eyebrow=family+' / '+p['category'],summary=p['subtitle'],kind='hardware',image=p['hero'],alt=p['name']+' by '+family+': '+p['subtitle']))
    data.extend([
        dict(key='realstudio',path='/products/realstudio/',title='RealStudio',eyebrow='Embodied AI platform',summary='One platform from robot control\nto on-site deployment.',kind='realstudio',alt='RealStudio: Control, Collect, Train, and Deploy, with the original blue logo and abstract software workflow.'),
        dict(key='realbot',path='/products/realbot/',title='RealBot',eyebrow='Robot series',summary='Humanoid and quadruped.\nOne robot family.',kind='realbot',status='Coming soon',alt='RealBot upcoming robot series: humanoid and quadruped robots.'),
        dict(key='realbrain',path='/products/realbrain/',title='RealBrain',eyebrow='AI model',summary='Our upcoming\nAI model.',kind='realbrain',status='Coming soon',alt='RealBrain, the forthcoming Realworld Labs AI model, with its blue brand logo.'),
        dict(key='blogs',path='/blogs/',title='Ideas in motion.',eyebrow='Research / Engineering / Stories',summary='Explore research and progress\nacross our robotics ecosystem.',kind='blog',image=blog['hero'],alt='Realworld Labs Blogs: robotics research, engineering, and stories.'),
        dict(key='blog-'+blog['slug'],path='/blogs/'+blog['slug']+'/',title='Agent as Policy\non RoboDojo',eyebrow='Research / '+blog['dateLabel'],summary='42 Tasks.\nOne General-Purpose Agent.',kind='blog',image=blog['hero'],alt=blog['title']+' — originally published by '+blog['author']+'.')
    ])
    return data

def ecosystem_art():
    nodes=[('RealBrain','AI MODEL',28,40),('RealStudio','PLATFORM',245,40),('RealHand','DEXTEROUS HANDS',20,254),('RealArm','ROBOTIC ARMS',253,254),('RealBot','ROBOT SERIES',135,326)]
    lines=''.join(f'<path d="M220 190 Q220 {y+25} {x+65} {y+25}"/>' for name,category,x,y in nodes)
    boxes=''.join(f'<g transform="translate({x} {y})"><rect width="130" height="58" rx="12" fill="#f8fbff" stroke="#bccfe7"/><text x="14" y="18" font-size="6.8" letter-spacing=".9" fill="#748bac">{category}</text><text x="14" y="40" font-size="18" fill="#29466c">{name}</text></g>' for name,category,x,y in nodes)
    return '<svg class="share-map" viewBox="0 0 440 400" aria-hidden="true"><g fill="none" stroke="#b7cce6" stroke-width="1">'+lines+'<ellipse cx="220" cy="215" rx="185" ry="70" opacity=".35"/><ellipse cx="220" cy="215" rx="145" ry="50" opacity=".25"/><circle cx="220" cy="190" r="65" stroke-dasharray="2 7" opacity=".65"/></g><circle cx="220" cy="190" r="55" fill="#edf4fe" stroke="#b2cceb"/><g text-anchor="middle" font-family="Space Grotesk, sans-serif" fill="#304e77"><text x="220" y="184" font-size="14" letter-spacing="1.5">TOTAL</text><text x="220" y="204" font-size="14" letter-spacing="1.5">SOLUTION</text></g><g font-family="Space Grotesk, sans-serif">'+boxes+'</g></svg>'

def render_document(card, origin):
    title='<br>'.join(escape(line) for line in card['title'].split('\n'))
    summary='<br>'.join(escape(line) for line in card['summary'].split('\n'))
    kind=card['kind']
    if kind=='ecosystem':
        artwork=ecosystem_art()
    elif kind in ['realstudio','realbot','realbrain']:
        artwork=product_visual(kind)
    else:
        artwork='<div class="share-photo share-'+kind+'"><img src="'+escape(card['image'],quote=True)+'" alt=""></div>'
    status='<span class="share-status">'+escape(card['status'])+'</span>' if card.get('status') else ''
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><base href="'''+origin+'''/"><link rel="stylesheet" href="/pages.css"><link rel="stylesheet" href="/ecosystem.css"><style>
html,body{width:1200px!important;height:630px!important;overflow:hidden!important;scrollbar-width:none;margin:0;padding:0}
body{background:#edf1f7;color:#29364b;font-family:Inter,sans-serif}
.share-frame{position:relative;isolation:isolate;width:1200px;height:630px;padding:45px 56px;background:radial-gradient(ellipse at 83% 40%,#fff8,transparent 50%),linear-gradient(120deg,#f6f8fb,#e4ebf6)}
.share-frame:after{content:"";position:absolute;inset:18px;border:1px solid #c9d6e8;border-radius:24px;pointer-events:none}
.share-header{height:54px;display:flex;justify-content:space-between;align-items:center}
.share-header img{width:285px;height:auto}.share-header span{font-size:11px;letter-spacing:.13em;color:#7890af}
.share-body{height:414px;display:grid;grid-template-columns:1.28fr 1fr;gap:26px;align-items:center;margin-top:22px}
.share-eyebrow{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#7188a8;margin:0 0 20px;line-height:1.5}
.share-copy h1{font:400 64px/1.07 'Space Grotesk',sans-serif;letter-spacing:-.055em;margin:0;color:#29374c}
.share-copy p.share-summary{font-size:20px;line-height:1.6;margin:25px 0 0;color:#6b819e}
.share-status{display:inline-flex;margin:0 0 17px;padding:6px 11px;border:1px solid #b7cae3;border-radius:7px;font-size:10px;color:#617dA5;letter-spacing:.05em}
.share-art{min-width:0;height:390px;display:grid;place-items:center;border:1px solid #d1ddec;border-radius:22px;overflow:hidden;background:linear-gradient(140deg,#f7faff90,#e0eaf7)}
.share-art>.product-scene{height:390px;border-radius:0}
.share-photo{height:100%;width:100%;display:grid;place-items:center}
.share-hardware img{height:90%;width:90%;object-fit:contain}
.share-blog img{height:100%;width:100%;object-fit:cover}
.share-map{width:100%;height:100%}
.share-footer{position:absolute;left:56px;right:56px;bottom:40px;display:flex;justify-content:space-between;gap:20px;border-top:1px solid #c6d2e3;padding-top:16px;color:#7c91ae;font-size:11px}
.share-footer span:first-child{letter-spacing:.03em}.share-footer span:last-child{font-size:10px}
.share-product .share-copy h1{font-size:76px}
.share-home .share-copy h1{font-size:76px}
.share-products .share-copy h1{font-size:57px}
.share-blog .share-copy h1{font-size:62px}
.studio-signal{animation:none!important}
</style></head><body><main class="share-frame share-'''+escape(card['key'])+(' share-product' if kind=='hardware' else '')+'''"><header class="share-header"><img src="/assets/brand/realworld-labs.png" alt="Realworld Labs"><span>INTELLIGENCE. MADE PHYSICAL.</span></header><div class="share-body"><div class="share-copy"><p class="share-eyebrow">'''+escape(card['eyebrow'])+'''</p>'''+status+'''<h1>'''+title+'''</h1><p class="share-summary">'''+summary+'''</p></div><div class="share-art">'''+artwork+'''</div></div><footer class="share-footer"><span>RealHand · RealArm · RealStudio · RealBot · RealBrain</span><span>realworldlabs.com</span></footer></main></body></html>'''

def icon_svg():
    import xml.etree.ElementTree as ET
    source=ET.parse(ROOT/'public/assets/brand/realworld-labs-white.svg').getroot()
    symbol=list(source)[0].get('d')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64"><rect width="64" height="64" rx="12" fill="#f1f3f7"/><path transform="translate(10.3 3.9) scale(.28)" fill="#153a91" fill-rule="evenodd" d="'+symbol+'"/></svg>'
