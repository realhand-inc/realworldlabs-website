"""Product artwork and an interactive, conceptual product ecosystem."""
from math import sin, cos, sqrt, pi
import json

NODES = [
    {'key':'realbrain','name':'RealBrain','layer':'model','category':'AI model','status':'Coming soon','summary':'Our forthcoming AI model. RealBrain adds the model layer to the Realworld Labs product ecosystem.','href':'/products/realbrain/','link':'Discover RealBrain','position':[.18,.22,-45]},
    {'key':'realstudio','name':'RealStudio','layer':'platform','category':'Embodied AI platform','status':'','summary':'One platform from robot control to on-site deployment. Control, collect, train, and deploy with RealStudio.','href':'/products/realstudio/','link':'Explore RealStudio','position':[.52,.17,20]},
    {'key':'realhand','name':'RealHand','layer':'hardware','category':'Dexterous hands','status':'','summary':'L6, O6, L20, and L30: four dexterous hands for robotic manipulation and physical interaction.','href':'/products/#hands','link':'Explore dexterous hands','position':[.18,.71,60]},
    {'key':'realarm','name':'RealArm','layer':'hardware','category':'Robotic arms','status':'','summary':'The P7 robotic arm brings reach and motion to arm-hand systems and robotic manipulation.','href':'/products/p7/','link':'Explore the P7','position':[.52,.82,50]},
    {'key':'realbot','name':'RealBot','layer':'robots','category':'Robot series','status':'Coming soon','summary':'Our upcoming robot series spans humanoid and quadruped robots. Two forms of embodiment in the RealBot family.','href':'/products/realbot/','link':'Discover RealBot','position':[.83,.49,0]}
]

_brain_count = 0

def brain_visual(compact=False):
    global _brain_count
    _brain_count += 1
    gradient_id = 'brain-sphere-' + str(_brain_count)
    points=[]
    for i in range(110):
        y=1-2*(i+.5)/110
        r=sqrt(1-y*y)
        theta=pi*(3-sqrt(5))*i
        x=cos(theta)*r
        z=sin(theta)*r
        xr=x*.88+z*.47
        zr=-x*.47+z*.88
        scale=1+zr*.15
        points.append((200+xr*104*scale,150+y*104*scale,zr))
    lines=[]
    for i,(x,y,z) in enumerate(points):
        neighbours=sorted(((sqrt((x-x2)**2+(y-y2)**2),j) for j,(x2,y2,z2) in enumerate(points) if j>i))[:2]
        for dist,j in neighbours:
            if dist<41:
                x2,y2,z2=points[j]
                lines.append(f'<path d="M{x:.1f},{y:.1f} L{x2:.1f},{y2:.1f}" opacity="{.12+(z+1)*.10:.2f}"/>')
    dots=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.1+(z+1)*.6:.1f}" opacity="{.35+(z+1)*.3:.2f}"/>' for x,y,z in points)
    return '<div class="brain-art" aria-hidden="true"><div class="brain-halo"></div><svg viewBox="0 0 400 320" focusable="false"><defs><radialGradient id="'+gradient_id+'"><stop stop-color="#b9e7ff" stop-opacity=".4"/><stop offset="1" stop-color="#6aa5ed" stop-opacity="0"/></radialGradient></defs><circle cx="200" cy="150" r="130" fill="url(#'+gradient_id+')"/><g fill="none" stroke="#598bd2" stroke-width=".65">'+''.join(lines)+'</g><g fill="#548dd8">'+dots+'</g><ellipse cx="200" cy="150" rx="151" ry="45" transform="rotate(-28 200 150)" fill="none" stroke="#a6c6ef" stroke-width=".7"/><ellipse cx="200" cy="150" rx="140" ry="47" transform="rotate(56 200 150)" fill="none" stroke="#7ca6de" stroke-width=".5"/></svg><span class="brain-art-label">AI MODEL</span></div>'

def studio_visual_art():
    grid=[]
    for i in range(1,9):
        t=i/9
        grid.append(f'<path d="M{320+198*t:.1f},{105+100*t:.1f} l-198,100 M{320-198*t:.1f},{105+100*t:.1f} l198,100"/>')
    return '<svg class="studio-flow-art" viewBox="0 0 640 420" aria-hidden="true" focusable="false"><ellipse class="studio-floor-shadow" cx="320" cy="331" rx="180" ry="24" fill="#557da8" opacity=".10"/><path d="M320 155 518 255 320 355 122 255Z" fill="#cfdef0" fill-opacity=".14" stroke="#9db7d7" stroke-opacity=".28"/><path d="M320 130 518 230 320 330 122 230Z" fill="#e8f1fc" fill-opacity=".24" stroke="#a4bedf" stroke-opacity=".45"/><path d="M320 105 518 205 320 305 122 205Z" fill="#fff" fill-opacity=".38" stroke="#98b8df" stroke-opacity=".65"/><g fill="none" stroke="#a2bddf" stroke-width=".7" opacity=".4">'+''.join(grid)+'</g><g class="studio-circuit" fill="none" stroke="#749acc" stroke-width="1.1"><path d="M122 205 220 155 320 205 420 155 518 205"/><path d="M320 105 420 155 320 205 420 255 320 305"/><path d="M320 105 220 155 320 205 220 255 320 305"/></g><g class="studio-signal" fill="none" stroke="#fafdff" stroke-width="2"><path d="M122 205 220 155 320 205 420 155 518 205"/><path d="M320 105 420 155 320 205 420 255 320 305"/></g><g class="studio-kernel"><path d="M320 174 390 209 320 244 250 209Z" fill="#b5d0ee" fill-opacity=".65" stroke="#87a9d4"/><path d="M320 158 390 193 320 228 250 193Z" fill="#e2effd" fill-opacity=".8" stroke="#9ab9df"/><path d="M320 142 390 177 320 212 250 177Z" fill="#fbfdff" fill-opacity=".9" stroke="#aac7e8"/><path d="M320 156 362 177 320 198 278 177Z" fill="none" stroke="#95b8e2" stroke-width=".8"/><path d="M320 165 344 177 320 189 296 177Z" fill="#b9d4f4" fill-opacity=".6" stroke="#87aedf" stroke-width=".7"/></g><g fill="#f9fcff" stroke="#8aacd7" stroke-width=".9"><path d="M320 98 333 105 320 112 307 105Z"/><path d="M518 198 531 205 518 212 505 205Z"/><path d="M320 298 333 305 320 312 307 305Z"/><path d="M122 198 135 205 122 212 109 205Z"/></g><g fill="#9dbfe8"><circle cx="220" cy="155" r="2"/><circle cx="420" cy="155" r="2"/><circle cx="220" cy="255" r="2"/><circle cx="420" cy="255" r="2"/></g></svg>'

def product_visual(key, compact=False):
    size=' is-compact' if compact else ''
    if key=='realstudio':
        return f'''<div class="product-scene studio-scene{size}" role="img" aria-label="Abstract RealStudio workflow: Control, Collect, Train, and Deploy"><div class="preview-grid"></div><img class="preview-wordmark" src="/assets/brand/realstudio-blue.svg" alt="RealStudio">{studio_visual_art()}<div class="preview-step step-control"><span>01</span>Control</div><div class="preview-step step-collect"><span>02</span>Collect</div><div class="preview-step step-train"><span>03</span>Train</div><div class="preview-step step-deploy"><span>04</span>Deploy</div><span class="preview-caption">ONE PLATFORM. FOUR CAPABILITIES.</span></div>'''
    if key=='realbot':
        return f'''<div class="product-scene bot-scene{size}" role="img" aria-label="RealBot upcoming robot series: humanoid and quadruped robots"><div class="preview-grid"></div><div class="bot-orbit orbit-one"></div><div class="bot-orbit orbit-two"></div><span class="preview-coming">Coming soon</span><img class="bot-wordmark" src="/assets/brand/realbot-blue.svg" alt="RealBot"><div class="bot-formats"><span>Humanoid</span><span>Quadruped</span></div></div>'''
    if key=='realbrain':
        return f'<div class="product-scene brain-scene{size}" role="img" aria-label="Abstract visualization of the forthcoming RealBrain AI model"><span class="preview-coming">Coming soon</span>'+brain_visual(compact)+'<img class="brain-wordmark brain-logo" src="/assets/brand/realbrain-blue.svg" alt="RealBrain" width="749" height="176" decoding="async"></div>'
    return ''

def ecosystem_section():
    buttons=[]
    previews=[]
    for i,node in enumerate(NODES):
        x,y,z=node['position']
        status=f'<span class="eco-node-status">{node["status"]}</span>' if node['status'] else ''
        buttons.append(f'''<button class="eco-node" data-eco-node="{node['key']}" data-layer="{node['layer']}" aria-pressed="false" aria-controls="ecosystem-detail" style="left:{x*100}%;top:{y*100}%"><span class="eco-node-category">{node['category']}</span><strong>{node['name']}</strong>{status}</button>''')
        if node['key'] in ['realstudio','realbot','realbrain']:
            artwork=product_visual(node['key'],True)
        else:
            asset='/assets/products/l30-silver-palm.webp' if node['key']=='realhand' else '/assets/hardware/p7/hero.webp'
            artwork=f'<div class="eco-hardware-preview"><img src="{asset}" alt="{node["name"]}" loading="lazy"></div>'
        previews.append(f'<div class="eco-product-preview" data-eco-preview="{node["key"]}" hidden>{artwork}</div>')
    layers=''.join(f'<button data-eco-layer="{key}" aria-pressed="{str(key=="all").lower()}" class="{ "is-active" if key=="all" else ""}">{label}</button>' for key,label in [('all','All layers'),('model','Model'),('platform','Platform'),('hardware','Hardware'),('robots','Robots')])
    data=json.dumps(NODES,ensure_ascii=False).replace('<','\\u003c')
    return f'''<section class="ecosystem-section ecosystem-hero container" id="ecosystem" aria-labelledby="ecosystem-title"><div class="section-heading"><div><p class="eyebrow">The total solution</p><h1 id="ecosystem-title">Intelligence to action.<br>Every layer connected.</h1></div><p class="section-intro">AI models, a software platform, dexterous hardware, and robot series. Explore the complete Realworld Labs product ecosystem.</p></div>
<div class="ecosystem-experience"><div class="eco-topbar"><div class="eco-layer-controls" role="group" aria-label="Explore an ecosystem layer">{layers}</div><span class="eco-live-label">REALWORLD LABS / PRODUCT ECOSYSTEM</span></div><div class="eco-workspace"><div class="eco-map" tabindex="0" aria-label="Interactive product ecosystem. Select a product node, or drag the background to change the view."><canvas class="eco-canvas" aria-hidden="true"></canvas><div class="eco-center" aria-hidden="true"><span>REALWORLD LABS</span><strong>TOTAL<br>SOLUTION</strong><small>Intelligence. Made physical.</small></div>{''.join(buttons)}<span class="eco-axis-label axis-model">INTELLIGENCE</span><span class="eco-axis-label axis-hardware">EMBODIMENT</span></div><aside class="eco-detail" id="ecosystem-detail"><div class="eco-preview-area"><div class="eco-product-preview eco-overview-preview" data-eco-preview="all"><div class="eco-overview-core">{brain_visual(True)}</div><img src="/assets/brand/realworld-labs-white.svg" alt="Realworld Labs" class="eco-overview-mark"></div>{''.join(previews)}</div><div class="eco-detail-copy" aria-live="polite" aria-atomic="true"><p class="eco-detail-category">One connected ecosystem</p><h3 class="eco-detail-title">The complete picture.</h3><span class="eco-detail-status" hidden></span><p class="eco-detail-description">From AI models to physical embodiment, our product families bring the layers of a robotics solution together.</p><div class="eco-model-links" hidden><a href="/products/l6/">L6</a><a href="/products/o6/">O6</a><a href="/products/l20/">L20</a><a href="/products/l30/">L30</a></div><a class="eco-detail-link" href="/products/">Explore all products</a></div></aside></div><div class="eco-bottom-bar"><p>Drag to change perspective <span>·</span> Select a product to explore</p><div class="eco-playback"><button class="eco-tour" aria-pressed="false">Play tour</button><button class="eco-motion" aria-pressed="true">Pause motion</button><button class="eco-reset">Reset view</button></div></div></div><script type="application/json" id="ecosystem-data">{data}</script></section>'''

def upcoming_content(key):
    is_bot=key=='realbot'
    name='RealBot' if is_bot else 'RealBrain'
    category='Robot series' if is_bot else 'AI model'
    headline='Humanoid and quadruped.<br>One robot family.' if is_bot else 'Our upcoming<br>AI model.'
    description='RealBot is our upcoming robot series, spanning humanoid and quadruped robots. Contact our team for future product updates.' if is_bot else 'RealBrain is our forthcoming AI model. Contact our team for future product updates.'
    return f'''<section class="coming-page upcoming-page container"><div class="coming-copy"><span class="status">Coming soon</span><p class="eyebrow">{category}</p><h1>{name}</h1><h2>{headline}</h2><p>{description}</p><div class="product-actions"><a class="button" href="mailto:sales@realworldlabs.com?subject={name}%20updates">Contact us for updates</a><a class="text-link" href="/#ecosystem">Explore our ecosystem</a></div></div><div class="upcoming-art">{product_visual(key)}</div></section>'''
