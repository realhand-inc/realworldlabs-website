"""Build the static, multi-page Realworld Labs website from local product content."""
from pathlib import Path
from html import escape
import json
import re
from site_experience import ecosystem_section, product_visual, upcoming_content
from site_metadata import prepare_assets, asset_url, resource_url, page_head, write_discovery, record_build_state
from validate_site import validate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
EMAIL = 'sales@realworldlabs.com'

def e(value):
    return escape(str(value), quote=True)

def read_json(name):
    return json.loads((ROOT / 'content' / name).read_text(encoding='utf-8'))

def product_url(slug):
    return f'/products/{slug}/'

def header(active=''):
    current_products = ' aria-current="true"' if active == 'products' else ''
    current_blog = ' aria-current="page"' if active == 'blogs' else ''
    hand_links = ''.join(f'<a href="{product_url(slug)}">{slug.upper()}</a>' for slug in ['l6','o6','l20','l30'])
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><nav class="nav-shell container" aria-label="Main navigation">
  <a class="brand" href="/" aria-label="Realworld Labs home"><img src="/assets/brand/realworld-labs.png" alt="Realworld Labs" width="253" height="45"></a>
  <div class="desktop-nav">
    <div class="nav-dropdown"><button class="nav-link products-toggle" aria-expanded="false" aria-controls="products-menu"{current_products}>Products</button>
      <div class="products-menu" id="products-menu" hidden>
        <div class="menu-intro"><span>Our product ecosystem</span><a href="/products/">View all products</a></div>
        <div class="menu-columns"><div><p>Dexterous hands</p>{hand_links}</div><div><p>Robotic arms</p><a href="/products/p7/">P7</a><p class="menu-second-label">Robot series</p><a href="/products/realbot/">RealBot <small>Coming soon</small></a></div><div><p>Software platform</p><a href="/products/realstudio/">RealStudio<small>Embodied AI platform</small></a><p class="menu-second-label">Core model</p><a href="/products/realbrain/">RealBrain <small>Coming soon</small></a></div></div>
      </div>
    </div>
    <a class="nav-link" href="/blogs/"{current_blog}>Blogs</a><a class="nav-link" href="/#about">About us</a>
  </div>
  <a class="button button-small nav-contact" href="/#contact">Let’s talk</a>
  <button class="menu-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="mobile-nav">Menu</button>
</nav><div class="mobile-nav" id="mobile-nav" hidden><a class="mobile-all" href="/products/">All products</a><div class="mobile-product-group"><p>Dexterous hands</p><div>{hand_links}</div></div><div class="mobile-product-group"><p>Robotic arms</p><a href="/products/p7/">P7</a></div><div class="mobile-product-group"><p>Software platform</p><a href="/products/realstudio/">RealStudio</a></div><div class="mobile-product-group"><p>Robot series</p><a href="/products/realbot/">RealBot <span class="status-inline">Coming soon</span></a></div><div class="mobile-product-group"><p>Core model</p><a href="/products/realbrain/">RealBrain <span class="status-inline">Coming soon</span></a></div><a href="/blogs/">Blogs</a><a href="/#about">About us</a><a href="/#contact">Get in touch</a></div></header>'''

def footer():
    return f'''<footer class="site-footer"><div class="container footer-main"><div class="footer-brand"><a class="brand" href="/"><img src="/assets/brand/realworld-labs.png" alt="Realworld Labs" width="253" height="45" loading="lazy"></a><p>Embodied intelligence.<br>Real-world possibilities.</p></div><div class="footer-links"><div><h2>Products</h2><a href="/products/#hands">RealHand</a><a href="/products/p7/">RealArm</a><a href="/products/realstudio/">RealStudio</a><a href="/products/realbot/">RealBot · Coming soon</a><a href="/products/realbrain/">RealBrain · Coming soon</a></div><div><h2>Explore</h2><a href="/blogs/">Blogs</a><a href="/#about">About us</a><a href="mailto:{EMAIL}">{EMAIL}</a></div></div></div><div class="container footer-bottom"><span>© <span id="copyright-year">2026</span> Realworld Labs. All rights reserved.</span><a href="#top">Back to top</a></div></footer>'''

def page(title, description, body, active='', path='/', extra='', noindex=False, article=None):
    head=page_head(title,description,path,noindex,article)+extra
    return f'''<!doctype html>
<html lang="en"><head>{head}</head>
<body id="top" data-page="{e(active or 'home')}">{header(active)}<main id="main">{body}</main>{footer()}<dialog id="image-viewer" class="image-dialog" aria-label="Product image"><button class="dialog-close" aria-label="Close image">Close</button><img alt=""><p></p></dialog></body></html>'''

def write(path, html):
    target = PUBLIC / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(html.encode('utf-8'))

def contact(title='Your next idea.<br>Made real.', subject='', identifier=''):
    href = f'mailto:{EMAIL}' + ('?subject=' + subject.replace(' ', '%20') if subject else '')
    return f'''<section class="contact-section" {f'id="{identifier}"' if identifier else ''}><div class="container contact-grid"><div><p class="eyebrow">Build with us</p><h2>{title}</h2></div><div class="contact-copy"><p>Talk to our team about your application, hardware, or robotics workflow.</p><a class="button" href="{e(href)}">Talk to our team</a><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a></div></div></section>'''

def breadcrumb(label, parent='Products', href='/products/'):
    return f'<nav class="breadcrumbs container" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="{href}">{parent}</a><span>/</span><span aria-current="page">{e(label)}</span></nav>'

def hand_card(product):
    return f'''<a class="hardware-card" href="{product_url(product['slug'])}"><div class="hardware-card-image"><img src="{e(product['hero'])}" alt="{e(product['heroAlt'])}" loading="lazy"></div><div class="hardware-card-copy"><h3>{e(product['name'])}</h3><p>{e(product['subtitle'])}</p><span>Explore product</span></div></a>'''

def family_cards():
    return '''<div class="family-grid">
<a class="family-card" href="/products/#hands"><div class="family-visual"><img src="/assets/products/l30-silver-palm.webp" alt="L30 dexterous robotic hand" loading="lazy"></div><div class="family-copy"><p class="eyebrow">01 / Dexterity</p><h3>RealHand</h3><p>L6 / O6 / L20 / L30</p><span class="card-link">Explore the range</span></div></a>
<a class="family-card" href="/products/p7/"><div class="family-visual"><img src="/assets/hardware/p7/hero.webp" alt="P7 robotic arm" loading="lazy"></div><div class="family-copy"><p class="eyebrow">02 / Motion</p><h3>RealArm</h3><p>P7 / RealArm</p><span class="card-link">Explore the P7</span></div></a>
<a class="family-card" href="/products/realstudio/"><div class="family-visual">'''+product_visual('realstudio',True)+'''</div><div class="family-copy"><p class="eyebrow">03 / Platform</p><h3>RealStudio</h3><p>Control / Collect / Train / Deploy</p><span class="card-link">Explore the platform</span></div></a>
<a class="family-card" href="/products/realbot/"><div class="family-visual">'''+product_visual('realbot',True)+'''</div><div class="family-copy"><p class="eyebrow">04 / Robot series</p><h3>RealBot</h3><p>Humanoid &amp; quadruped robots</p><span class="card-link">Coming soon</span></div></a>
<a class="family-card" href="/products/realbrain/"><div class="family-visual">'''+product_visual('realbrain',True)+'''</div><div class="family-copy"><p class="eyebrow">05 / Core model</p><h3>RealBrain</h3><p>The intelligence at our core.</p><span class="card-link">Coming soon</span></div></a></div>'''

def blog_card(blog, compact=False):
    return f'''<a class="blog-feature {'is-compact' if compact else ''}" href="/blogs/{e(blog['slug'])}/"><div class="blog-feature-image"><img src="{e(blog['hero'])}" alt="{e(blog.get('heroAlt', blog['title']))}" loading="lazy"></div><div class="blog-feature-copy"><p class="eyebrow">{e(blog.get('category','Research'))} <span>·</span> {e(blog['dateLabel'])}</p><h3>{e(blog['title'])}</h3><p>{e(blog['excerpt'])}</p><span class="text-link">Read the story</span></div></a>'''

def home(blog):
    body = ecosystem_section() + '''<section class="section-space container home-products" id="products"><div class="section-heading"><div><p class="eyebrow">Our ecosystem</p><h2>Five product families.<br>One embodied future.</h2></div><a class="text-link" href="/products/">View all products</a></div>'''+family_cards()+'''</section>
<section class="about-section container" id="about" aria-labelledby="about-title">
  <div class="about-opening"><div class="about-heading"><p class="eyebrow">About Realworld Labs</p><h2 id="about-title">Intelligence, made<br>for the <span>real world.</span></h2><a class="text-link" href="/products/">Explore our product ecosystem</a></div><div class="about-story"><p class="about-lead">We build the hardware and software that connect embodied intelligence with physical action.</p><p>Our work spans dexterous hands, robotic arms, and an embodied AI software platform. We bring these capabilities into one product ecosystem, helping researchers and developers move between physical interaction, data collection, model training, and deployment.</p></div></div>
  <div class="about-approach"><article><p class="about-index">01 / Physical interaction</p><h3>Start with the real world.</h3><p>RealHand dexterous hands and the RealArm P7 provide the hardware for manipulation, motion, and interaction with the world.</p></article><article><p class="about-index">02 / Connected development</p><h3>Bring the workflow together.</h3><p>RealStudio brings Control, Collect, Train, and Deploy into one platform, supporting a connected workflow from robot operation to on-site deployment.</p></article><article><p class="about-index">03 / What comes next</p><h3>Build toward a fuller ecosystem.</h3><p>Our roadmap includes RealBot humanoid and quadruped robots and RealBrain, our core model. Both product families are coming soon.</p></article></div>
</section>
<section class="section-space container home-blog"><div class="section-heading"><div><p class="eyebrow">From the blog</p><h2>Ideas in motion.</h2></div><a class="text-link" href="/blogs/">All stories</a></div>'''+blog_card(blog, True)+'''</section>'''+contact(identifier='contact')
    write('index.html', page('Intelligence. Made physical.', 'Dexterous hands, P7 robotic arms, RealStudio software, RealBot humanoid and quadruped robots, and the RealBrain core model. Explore the Realworld Labs ecosystem.', body, extra=f'<script src="{asset_url("/ecosystem.js")}" defer></script>'))

def products_index(hardware):
    hands = [p for p in hardware if p['slug']!='p7']
    p7 = next(p for p in hardware if p['slug']=='p7')
    body = '''<section class="page-heading container"><p class="eyebrow">Our products</p><h1>Hardware to software.<br>Idea to action.</h1><p>Core models, a software platform, dexterous hands, robotic arms, and robot series. One product ecosystem.</p></section>
<div class="container"><div class="product-filters" role="group" aria-label="Filter products">'''+''.join(f'<button data-product-filter="{key}" aria-pressed="{str(key=="all").lower()}" class="filter-button {"is-active" if key=="all" else ""}">{label}</button>' for key,label in [('all','All products'),('hands','Dexterous hands'),('arms','Robotic arms'),('software','Platform'),('robots','Robot series'),('models','Core model')])+'''</div><p class="sr-only" id="filter-status" role="status" aria-live="polite">Showing all products.</p>
<section class="catalog-section" id="hands" data-category="hands"><div class="section-heading"><div><p class="eyebrow">01 / Dexterous hands</p><h2>A hand for your next idea.</h2></div><p class="section-intro">Four models for robotic manipulation.<br>Explore the details of each hand.</p></div><div class="hardware-grid">'''+''.join(hand_card(p) for p in hands)+'''</div></section>
<section class="catalog-section" id="arms" data-category="arms"><div class="catalog-feature"><div class="catalog-feature-copy"><p class="eyebrow">02 / Robotic arms</p><h2>P7</h2><p>'''+e(p7['description'])+'''</p><a class="button" href="/products/p7/">Explore the P7</a></div><div class="catalog-feature-image"><img src="'''+e(p7['hero'])+'''" alt="'''+e(p7['heroAlt'])+'''" loading="lazy"></div></div></section>
<section class="catalog-section" id="platform" data-category="software"><div class="catalog-feature studio-promo"><div class="catalog-feature-copy"><p class="eyebrow">03 / Embodied AI platform</p><h2>RealStudio</h2><p>One platform from robot control to on-site deployment. Control, collect, train, and deploy in one connected ecosystem.</p><a class="button" href="/products/realstudio/">Explore RealStudio</a></div><div class="catalog-art">'''+product_visual('realstudio')+'''</div></div></section>
<section class="catalog-section" id="robots" data-category="robots"><div class="catalog-feature"><div class="catalog-feature-copy"><span class="status">Coming soon</span><p class="eyebrow">04 / Robot series</p><h2>RealBot</h2><p>A robot series spanning humanoid and quadruped robots. Discover our next chapter in physical embodiment.</p><a class="button" href="/products/realbot/">Discover RealBot</a></div><div class="catalog-art">'''+product_visual('realbot')+'''</div></div></section>
<section class="catalog-section" id="models" data-category="models"><div class="catalog-feature"><div class="catalog-feature-copy"><span class="status">Coming soon</span><p class="eyebrow">05 / Core model</p><h2>RealBrain</h2><p>Our forthcoming core model. The model layer of the Realworld Labs product ecosystem.</p><a class="button" href="/products/realbrain/">Discover RealBrain</a></div><div class="catalog-art">'''+product_visual('realbrain')+'''</div></div></section></div>'''+contact()
    write('products/index.html', page('Products', 'Explore L6, O6, L20, and L30 dexterous hands, the P7 robotic arm, and RealStudio. RealBot robot series and the RealBrain core model are coming soon.', body, 'products', '/products/'))

def hardware_page(product, hardware):
    slug=product['slug']
    features=''.join(f'<article><span class="feature-number">0{i+1}</span><h3>{e(f["title"])}</h3><p>{e(f["description"])}</p></article>' for i,f in enumerate(product['features']))
    specs=''.join(f'<tr><th scope="row">{e(s["label"])}</th><td>{e(s["value"])}</td></tr>' for s in product['specs'])
    gallery=''.join(f'<figure><button class="gallery-image" data-lightbox="{e(g["src"])}" data-caption="{e(g.get("caption",g["alt"]))}" aria-label="Enlarge {e(g["alt"])}"><img src="{e(g["src"])}" alt="{e(g["alt"])}" loading="lazy"></button><figcaption>{e(g.get("caption", ""))}</figcaption></figure>' for g in product.get('gallery',[]))
    downloads=''.join(f'<a class="text-link" href="{e(d["url"])}" target="_blank" rel="noopener">{e(d["label"])}</a>' for d in product.get('downloads',[]))
    related=''.join(hand_card(p) for p in hardware if p['slug']!=slug)
    notes=product.get('notes',[])
    if isinstance(notes,str):notes=[notes]
    notes_html=''.join(f'<p>{e(note)}</p>' for note in notes)
    body=breadcrumb(product['name'])+f'''<section class="product-hero container"><div class="product-hero-copy"><p class="eyebrow">{e(product['category'])}</p><h1>{e(product['name'])}</h1><h2>{e(product['subtitle'])}</h2><p>{e(product['description'])}</p><div class="product-actions"><a class="button" href="mailto:{EMAIL}?subject={e(product['name'])}%20enquiry">Discuss {e(product['name'])}</a><a class="text-link" href="#specifications">Technical specifications</a></div></div><div class="product-hero-visual"><img src="{e(product['hero'])}" alt="{e(product['heroAlt'])}" fetchpriority="high"><span>{e(product['name'])} / {e(product['category'])}</span></div></section>
<nav class="product-subnav container" aria-label="On this product page"><a href="#features">Overview</a><a href="#specifications">Specifications</a>{'<a href="#gallery">Gallery</a>' if gallery else ''}<a href="#product-contact">Enquire</a></nav>
<section class="container section-space" id="features"><div class="section-heading"><div><p class="eyebrow">Designed for the task</p><h2>Explore {e(product['name'])}.</h2></div></div><div class="feature-grid">{features}</div></section>
<section class="spec-section container" id="specifications"><div><p class="eyebrow">The details</p><h2>Technical<br>specifications.</h2><p>Product information and specifications from RealHand.</p>{downloads}</div><div class="spec-panel"><table class="spec-table"><caption class="sr-only">{e(product['name'])} technical specifications</caption><tbody>{specs}</tbody></table><div class="spec-notes">{notes_html}</div></div></section>
{f'<section class="container section-space" id="gallery"><div class="section-heading"><div><p class="eyebrow">A closer look</p><h2>Form meets function.</h2></div></div><div class="product-gallery">{gallery}</div></section>' if gallery else ''}
<section class="container section-space related-products"><div class="section-heading"><div><p class="eyebrow">The connected ecosystem</p><h2>Explore more hardware.</h2></div><a class="text-link" href="/products/">All products</a></div><div class="hardware-grid">{related}</div></section>'''+contact(subject=product['name']+' enquiry', identifier='product-contact')
    write(f'products/{slug}/index.html',page(product['name']+' — '+product['subtitle'],product['description'],body,'products',product_url(slug)))

def studio_page(studio):
    capabilities=studio['capabilities']
    first=capabilities[0]
    tabs=''.join(f'<button class="studio-tab {"is-active" if i==0 else ""}" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="studio-panel" id="tab-{c["key"]}" data-capability="{c["key"]}" tabindex="{0 if i==0 else -1}">{e(c["label"])}</button>' for i,c in enumerate(capabilities))
    editions=''.join(f'<article><span class="edition-stage">{e(ed["stage"])}</span><h3>{e(ed["name"])}</h3><p>{e(ed["description"])}</p><ul>{"".join(f"<li>{e(f)}</li>" for f in ed["features"])}</ul></article>' for ed in studio['editions'])
    rows=''
    for group in studio['matrix']:
        rows+=f'<tr class="matrix-group"><th colspan="6">{e(group["title"])}</th></tr>'
        for label in group['rows']:
            rows+=f'<tr><th scope="row">{e(label)}</th>'
            for edition in ['free','data','training','deployment','enterprise']:
                included=group['key']=='free' or edition==group['key'] or edition=='enterprise'
                cell = 'Included' if included else '<span aria-label="Not included">—</span>'
                rows+=f'<td class="{"included" if included else "not-included"}">{cell}</td>'
            rows+='</tr>'
    body=breadcrumb('RealStudio')+f'''<section class="studio-hero container"><div><p class="eyebrow">Software / {e(studio['category'])}</p><h1>RealStudio</h1><h2>{e(studio['tagline'])}</h2><p>{e(studio['description'])}</p><div class="product-actions"><a class="button" href="#editions">Choose your edition</a><a class="text-link" href="mailto:{EMAIL}?subject=RealStudio%20enquiry">Discuss RealStudio</a></div></div><div class="studio-hero-art">{product_visual("realstudio")}</div></section>
<nav class="product-subnav container" aria-label="On this product page"><a href="#capabilities">Capabilities</a><a href="#editions">Editions</a><a href="#feature-matrix">Feature matrix</a><a href="#resources">Resources</a></nav>
<section class="container section-space" id="capabilities"><div class="section-heading"><div><p class="eyebrow">Four core capabilities</p><h2>Control. Collect.<br>Train. Deploy.</h2></div></div><div class="capability-layout"><div class="studio-tabs" role="tablist" aria-label="RealStudio capabilities">{tabs}</div><div class="studio-panel" id="studio-panel" role="tabpanel" aria-labelledby="tab-control" tabindex="0"><div><span class="panel-number">01 / CONTROL</span><h3>{e(first['heading'])}</h3><p class="panel-description">{e(first['description'])}</p><p class="panel-availability">{e(first['availability'])}</p></div><ul>{''.join(f'<li>{e(f)}</li>' for f in first['features'])}</ul></div></div></section>
<section class="container section-space editions-section" id="editions"><div class="section-heading"><div><p class="eyebrow">RealStudio editions</p><h2>Choose your edition.</h2></div><p class="section-intro">Data, Training, and Deployment each include Free.<br>Choose the capabilities your workflow needs.</p></div><div class="edition-grid">{editions}<article class="enterprise-edition"><div><h3>Enterprise</h3><p>Every capability in a single edition.</p></div><div class="enterprise-includes"><span>Free</span><b>+</b><span>Data</span><b>+</b><span>Training</span><b>+</b><span>Deployment</span></div></article></div><p class="edition-note">{e(studio['editionNote'])}</p></section>
<section class="container section-space matrix-section" id="feature-matrix"><div class="section-heading"><div><p class="eyebrow">Compare editions</p><h2>Every feature.<br>A clear view.</h2></div><p class="section-intro">Compare the features included in each edition.</p></div><p class="table-hint">Scroll the table horizontally to compare all editions.</p><div class="matrix-scroll" tabindex="0" role="region" aria-label="Scrollable RealStudio feature comparison"><table class="feature-matrix"><caption class="sr-only">RealStudio feature availability by edition</caption><thead><tr><th scope="col">Feature</th>{''.join(f'<th scope="col">{name}</th>' for name in ['Free','Data','Training','Deployment','Enterprise'])}</tr></thead><tbody>{rows}</tbody></table></div><p class="edition-note">{e(studio['editionNote'])}</p></section>
<section class="resources-section container" id="resources"><div><p class="eyebrow">Product resources</p><h2>Take a closer look.</h2></div><div><a href="{resource_url('/assets/documents/realstudio-overview.pdf')}" target="_blank" rel="noopener"><span>Editions overview</span><small>PDF</small></a><a href="{resource_url('/assets/documents/realstudio-feature-matrix.pdf')}" target="_blank" rel="noopener"><span>Full feature matrix</span><small>PDF</small></a></div></section>'''+contact(subject='RealStudio enquiry')+f'<script type="application/json" id="studio-content">{json.dumps(capabilities,ensure_ascii=False).replace("<", chr(92)+"u003c")}</script>'
    write('products/realstudio/index.html',page('RealStudio — Embodied AI platform',studio['tagline'],body,'products','/products/realstudio/'))

def bot_page():
    body=breadcrumb('RealBot')+upcoming_content('realbot')
    write('products/realbot/index.html',page('RealBot — Robot series · Coming soon','RealBot is our upcoming robot series, including humanoid and quadruped robots.',body,'products','/products/realbot/'))

def brain_page():
    body=breadcrumb('RealBrain')+upcoming_content('realbrain')
    write('products/realbrain/index.html',page('RealBrain — Core model · Coming soon','RealBrain is the forthcoming core model from Realworld Labs.',body,'products','/products/realbrain/'))

def blogs(blog):
    body='''<section class="page-heading container"><p class="eyebrow">Blogs</p><h1>Ideas, experiments.<br>Real-world progress.</h1><p>Research, engineering, and stories from our robotics ecosystem.</p></section><section class="container blog-list">'''+blog_card(blog)+'''</section>'''+contact()
    write('blogs/index.html',page('Blogs','Research, engineering, and stories from the Realworld Labs robotics ecosystem.',body,'blogs','/blogs/'))
    author=f'<span>{e(blog["author"])}</span>' if blog.get('author') else ''
    body=breadcrumb(blog['title'],'Blogs','/blogs/')+f'''<article class="blog-article"><header class="article-header container"><p class="eyebrow">{e(blog.get('category','Research'))}</p><h1>{e(blog['title'])}</h1><div class="article-meta"><time datetime="{e(blog['published'])}">{e(blog['dateLabel'])}</time>{author}<a href="{e(blog['sourceUrl'])}" target="_blank" rel="noopener">Originally published on RealHand</a></div><p>{e(blog['excerpt'])}</p></header><div class="article-cover container"><img src="{e(blog['hero'])}" alt="{e(blog.get('heroAlt',blog['title']))}" fetchpriority="high"></div><div class="article-body">{blog['bodyHtml']}</div><div class="article-end"><a class="text-link" href="/blogs/">Back to all stories</a><a class="text-link" href="{e(blog['sourceUrl'])}" target="_blank" rel="noopener">Read the original on RealHand</a></div></article>'''+contact()
    write(f'blogs/{blog["slug"]}/index.html',page(blog['title'],blog['excerpt'],body,'blogs',f'/blogs/{blog["slug"]}/',article=blog))

def main():
    prepare_assets()
    hardware=read_json('hardware.json')
    if isinstance(hardware,dict):hardware=hardware.get('products',list(hardware.values()))
    blog=read_json('blog-latest.json')
    studio=read_json('realstudio.json')
    assert len(hardware)==5 and {p['slug'] for p in hardware}=={'l6','o6','l20','l30','p7'}
    home(blog);products_index(hardware)
    for product in hardware:hardware_page(product,hardware)
    studio_page(studio);bot_page();brain_page();blogs(blog)
    write('404.html',page('Page not found','Explore products and stories from Realworld Labs.','<section class="page-heading container not-found"><p class="eyebrow">404</p><h1>Let’s find your<br>next connection.</h1><p>This page could not be found.</p><a class="button" href="/products/">Explore our products</a></section>',path='/404.html',noindex=True))
    write_discovery()
    report=validate(PUBLIC)
    record_build_state()
    print('Launch checks: '+json.dumps(report))
    print('Built homepage, product overview, 8 product pages, blog listing, latest article, and 404 page.')

if __name__=='__main__':main()
