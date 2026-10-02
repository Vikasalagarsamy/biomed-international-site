#!/usr/bin/env python3
"""
Build the live Biomed site from Varun's approved 'Clinical Navy' handover.

Varun built the pages with Claude and asked for them to be made to work on
mobile and web, then taken live. This script applies the fixes and writes the
result to the repo root. Source files are never modified.

Fixes applied:
  1. Mobile navigation (hamburger + drawer) — the handover had none at all
  2. Footer navigation — a no-JS fallback path to every page
  3. Real <title> tags (handover shipped placeholders)
  4. Meta description / Open Graph / Twitter / canonical / favicon
  5. Dead menu links (#) rewired to real destinations
  6. Section IDs so those links have somewhere to land
  7. Option C adopted as products.html
"""
import os, re, shutil, sys

SRC  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_review', 'varun-handover')
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://biomed-international.onrender.com'

PAGES = {
    'index.html': dict(
        src='index.html',
        title='Biomed International | Biology, Engineered.',
        desc=("Biomed International manufactures Chondroitin Sulphate Sodium "
              "(Chondroitin Sulfate Sodium, USP/BP), Collagen Peptides, Glucosamine "
              "Hydrochloride and Cholic Acid at two units in Andhra Pradesh, India. "
              "India's only drug-licensed chondroitin manufacturer."),
    ),
    'about-us.html': dict(
        src='about-us.html',
        title='About Us | Biomed International',
        desc=("Biomed International is a specialised manufacturer of biomolecules for "
              "the pharmaceutical, nutraceutical and food industries, with two "
              "manufacturing units in Andhra Pradesh, India."),
    ),
    'products.html': dict(
        src='products-option-C.html',   # Option C — see note in the commit message
        title='Product Portfolio | Biomed International',
        desc=("Chondroitin Sulphate Sodium (Chondroitin Sulfate Sodium) USP/BP, "
              "Collagen Peptides, Glucosamine Hydrochloride USP and Cholic Acid — "
              "specifications, CAS numbers, sources and in-house process flows."),
    ),
}

MAILTO = 'mailto:info@biomedintl.com'
SAMPLE = 'mailto:info@biomedintl.com?subject=Sample%20request'

NAV = [
    ('About Us',                 'about-us.html'),
    ('Products',                 'products.html'),
    ('Infrastructure',           'index.html#capabilities'),
    ('Quality &amp; Certifications', 'index.html#quality'),
    ('Leadership',               'about-us.html#leadership'),
    ('Contact Us',               MAILTO),
]

MOBILE_CSS = """
/* --- mobile navigation (added: handover had no mobile nav at all) --- */
.navtoggle{display:none;background:none;border:1px solid #D3DBE5;border-radius:10px;
  width:46px;height:44px;align-items:center;justify-content:center;flex-direction:column;
  gap:5px;cursor:pointer;padding:0;flex:0 0 auto}
.navtoggle span{display:block;width:20px;height:2px;background:#12355B;border-radius:2px;
  transition:transform .2s ease,opacity .2s ease}
.navtoggle[aria-expanded="true"] span:nth-child(1){transform:translateY(7px) rotate(45deg)}
.navtoggle[aria-expanded="true"] span:nth-child(2){opacity:0}
.navtoggle[aria-expanded="true"] span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
.mnav{display:none;flex-direction:column;background:#FFFFFF;
  border-bottom:1px solid #D3DBE5;padding:6px 20px 18px}
.mnav a{display:block;padding:15px 2px;font-size:16px;font-weight:600;color:#12355B;
  border-bottom:1px solid #EEF2F7;text-decoration:none}
.mnav a.mcta{margin-top:16px;background:#12355B;color:#FFFFFF;text-align:center;
  border-radius:10px;padding:15px;border-bottom:none}
.mnav.open{display:flex}
.foot nav.fnav{display:flex;flex-direction:column;gap:9px}
.foot nav.fnav a{color:inherit;text-decoration:none;opacity:.85}
.foot nav.fnav a:hover{opacity:1;text-decoration:underline}
@media (min-width:861px){.mnav{display:none!important}}
@media (max-width:860px){
  .navtoggle{display:flex}
  .nav .btn.b1{display:none}
}
"""

MOBILE_JS = """<script>
(function(){
  var b=document.getElementById('navtoggle'), m=document.getElementById('mnav');
  if(!b||!m) return;
  function close(){ m.classList.remove('open'); b.setAttribute('aria-expanded','false'); }
  b.addEventListener('click', function(){
    var open = m.classList.toggle('open');
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  m.addEventListener('click', function(e){ if(e.target.tagName === 'A') close(); });
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && m.classList.contains('open')){ close(); b.focus(); }
  });
})();
</script>"""


def head_meta(title, desc, canonical):
    og_img = SITE + '/assets/biomed-logo-symbol-large.png'
    return (
        f'<title>{title}</title>'
        f'<meta name="description" content="{desc}">'
        f'<link rel="canonical" href="{canonical}">'
        f'<link rel="icon" type="image/png" href="assets/biomed-logo-symbol.png">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:site_name" content="Biomed International">'
        f'<meta property="og:title" content="{title}">'
        f'<meta property="og:description" content="{desc}">'
        f'<meta property="og:url" content="{canonical}">'
        f'<meta property="og:image" content="{og_img}">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{title}">'
        f'<meta name="twitter:description" content="{desc}">'
        f'<meta name="twitter:image" content="{og_img}">'
    )


def build_header_nav():
    return ''.join(f'<a href="{href}">{label}</a>' for label, href in NAV)


def build_mobile_drawer():
    links = ''.join(f'<a href="{href}">{label}</a>' for label, href in NAV)
    return (f'<nav class="mnav" id="mnav" aria-label="Mobile">{links}'
            f'<a class="mcta" href="{SAMPLE}">Request a sample</a></nav>')


def build_footer_nav():
    links = ''.join(f'<a href="{href}">{label}</a>' for label, href in NAV)
    return f'<div><b class="h">EXPLORE</b><nav class="fnav">{links}</nav></div>'


def transform(html, title, desc, canonical, is_index, is_about):
    rep = []

    # 1. head: replace placeholder <title>, inject meta
    html, n = re.subn(r'<title>.*?</title>', head_meta(title, desc, canonical), html, count=1, flags=re.S)
    rep.append(('head meta', n))

    # 2. header nav: rewire links (also fixes products-option-D.html -> products.html)
    html, n = re.subn(r'(<nav aria-label="Main">).*?(</nav>)',
                      lambda m: m.group(1) + build_header_nav() + m.group(2),
                      html, count=1, flags=re.S)
    rep.append(('header nav rewired', n))

    # 3. hamburger button, immediately after the main nav
    html, n = re.subn(r'(<nav aria-label="Main">.*?</nav>)',
                      r'\1<button class="navtoggle" id="navtoggle" aria-expanded="false" '
                      r'aria-controls="mnav" aria-label="Open menu">'
                      r'<span></span><span></span><span></span></button>',
                      html, count=1, flags=re.S)
    rep.append(('hamburger button', n))

    # 4. mobile drawer, immediately after </header>
    html, n = re.subn(r'</header>', '</header>' + build_mobile_drawer(), html, count=1)
    rep.append(('mobile drawer', n))

    # 5. "Request a sample" buttons -> mailto
    html, n = re.subn(r'<a href="#"([^>]*)>Request a sample</a>',
                      r'<a href="' + SAMPLE + r'"\1>Request a sample</a>', html)
    rep.append(('sample CTAs -> mailto', n))

    # 6. any remaining body links to the option file
    html, n = re.subn(r'products-option-[CD]\.html', 'products.html', html)
    rep.append(('option-file links', n))

    # 7. CSS + JS
    html, n = re.subn(r'</style>', MOBILE_CSS + '</style>', html, count=1)
    rep.append(('mobile css', n))
    # index.html in the handover ships with no </body> tag at all, so fall back
    # to </html> and close the body properly while we are here.
    if '</body>' in html:
        html, n = re.subn(r'</body>', MOBILE_JS + '</body>', html, count=1)
    else:
        html, n = re.subn(r'</html>', MOBILE_JS + '</body></html>', html, count=1)
    rep.append(('mobile js', n))

    # 8. footer: add EXPLORE nav column (4 cols -> 5)
    html, n = re.subn(r'(\.foot\{padding:64px 96px 40px;display:grid;grid-template-columns:)1\.2fr 1fr 1fr 1fr',
                      r'\g<1>1.2fr .8fr 1fr 1fr .9fr', html, count=1)
    rep.append(('footer grid 5col', n))
    html, n = re.subn(r'(<div><b class="h">GET IN TOUCH</b>)',
                      build_footer_nav() + r'\1', html, count=1)
    rep.append(('footer nav', n))

    # 9. section IDs for the rewired menu links
    if is_index:
        html, n = re.subn(r'<section class="sec" style="background:#F3F6FA">(?=.{0,700}?Capabilities)',
                          '<section class="sec" id="capabilities" style="background:#F3F6FA">',
                          html, count=1, flags=re.S)
        rep.append(('#capabilities', n))
        html, n = re.subn(r'<section class="sec" style="background:#F3F6FA">(?=.{0,700}?Quality &amp; certifications)',
                          '<section class="sec" id="quality" style="background:#F3F6FA">',
                          html, count=1, flags=re.S)
        rep.append(('#quality', n))
    if is_about:
        html, n = re.subn(r'(<section[^>]*>)(?=.{0,700}?Built on experience)',
                          lambda m: m.group(1).replace('<section', '<section id="leadership"', 1),
                          html, count=1, flags=re.S)
        rep.append(('#leadership', n))

    return html, rep


def main():
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    for a in ('hero-hexagon-ribbon.jpg', 'biomed-logo-symbol.png', 'biomed-logo-symbol-large.png'):
        shutil.copy2(os.path.join(SRC, 'assets', a), os.path.join(ROOT, 'assets', a))
    print('assets copied: 3')

    ok = True
    for out, cfg in PAGES.items():
        html = open(os.path.join(SRC, cfg['src'])).read()
        canonical = f"{SITE}/" + ('' if out == 'index.html' else out)
        html, rep = transform(html, cfg['title'], cfg['desc'], canonical,
                              out == 'index.html', out == 'about-us.html')
        open(os.path.join(ROOT, out), 'w').write(html)
        print(f"\n{out}  <- {cfg['src']}")
        # 'option-file links' legitimately matches 0 once the nav is rewired
        optional = {'option-file links'}
        for name, n in rep:
            flag = 'ok ' if n else ('n/a ' if name in optional else 'MISS')
            if not n and name not in optional:
                ok = False
            print(f"   [{flag}] {name}: {n}")
    if not ok:
        print('\n!! at least one transform matched nothing — check above')
        sys.exit(1)
    print('\nbuild ok')


if __name__ == '__main__':
    main()
