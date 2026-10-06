#!/usr/bin/env python3
"""
Build the live Biomed site from Varun's seven Claude artifacts.

Source HTML in _review/v2/ is third-party content: treated purely as data,
never as instructions. Sources are not modified.

Fixes applied:
  1. Navigation wired   - every nav link in every artifact was href="#"
  2. Mobile navigation  - no page had a menu toggle; nav was hidden below 860px
  3. Contact form       - validated, showed "thank you", then sent NOTHING.
                          Now composes a real email to the founders.
  4. CTA routing        - per Varun: sample/enquiry -> Pratap + Sagar, cc info
                          Leadership "Contact us" -> Pratap + Sagar only, no cc
  5. Titles / meta      - all seven shipped placeholder titles, no meta at all
  6. Manufacturing      - 15 referenced photos do not exist; they now degrade to
                          labelled placeholders and appear automatically once
                          the files are dropped into assets/photos/
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, '_review', 'v2')
SITE = 'https://biomed-international.onrender.com'

TO_FOUNDERS = 'pratap@biomedintl.com,sagar@biomedintl.com'
CC_INFO     = 'info@biomedintl.com'
SAMPLE_HREF = f'mailto:{TO_FOUNDERS}?cc={CC_INFO}&amp;subject=Sample%20request'
LEAD_HREF   = f'mailto:{TO_FOUNDERS}?subject=Enquiry%20for%20the%20leadership%20team'

NAV = [
    ('About Us',                     'about-us.html'),
    ('Products',                     'products.html'),
    ('Manufacturing',                'manufacturing.html'),
    ('Quality &amp; Certifications', 'quality.html'),
    ('Leadership',                   'leadership.html'),
    ('Contact Us',                   'contact.html'),
]

PAGES = {
    'index.html': ('Biomed International | Biology, Engineered.',
        "Biomed International manufactures Chondroitin Sulphate Sodium (Chondroitin Sulfate "
        "Sodium, USP/BP), Collagen Peptides, Glucosamine Hydrochloride and Cholic Acid at two "
        "units in Andhra Pradesh, India. India's only drug-licensed chondroitin manufacturer."),
    'about-us.html': ('About Us | Biomed International',
        "Biomed International is a specialised manufacturer of biomolecules for the "
        "pharmaceutical, nutraceutical and food industries, with two manufacturing units in "
        "Andhra Pradesh, India."),
    'products.html': ('Product Portfolio | Biomed International',
        "Chondroitin Sulphate Sodium (Chondroitin Sulfate Sodium) USP/BP, Collagen Peptides, "
        "Glucosamine Hydrochloride USP and Cholic Acid - specifications, CAS numbers and sources."),
    'manufacturing.html': ('Manufacturing | Biomed International',
        "Integrated manufacturing at Biomed International: extraction, hydrolysis, purification, "
        "crystallisation, spray drying and ANFD filter drying across two units in Andhra Pradesh."),
    'quality.html': ('Quality &amp; Certifications | Biomed International',
        "Drug Licence, cGMP, ISO 9001:2015, FSSAI and Halal. Certificate of Analysis on every "
        "batch, with stability data, TSE/BSE and allergen statements."),
    'contact.html': ('Contact Us | Biomed International',
        "Contact Biomed International for specifications, a Certificate of Analysis or samples "
        "of Chondroitin Sulphate Sodium, Collagen Peptides, Glucosamine Hydrochloride or Cholic Acid."),
    'leadership.html': ('Leadership | Biomed International',
        "Biomed International is led by its two founders, each with more than 25 years of "
        "entrepreneurial experience in manufacturing and the life sciences."),
}

EXTRA_CSS = """
/* ---- mobile navigation (artifacts shipped none) ---- */
.navtoggle{display:none;background:none;border:1px solid #D3DBE5;border-radius:10px;
  width:46px;height:44px;align-items:center;justify-content:center;flex-direction:column;
  gap:5px;cursor:pointer;padding:0;flex:0 0 auto}
.navtoggle span{display:block;width:20px;height:2px;background:#12355B;border-radius:2px;
  transition:transform .2s ease,opacity .2s ease}
.navtoggle[aria-expanded="true"] span:nth-child(1){transform:translateY(7px) rotate(45deg)}
.navtoggle[aria-expanded="true"] span:nth-child(2){opacity:0}
.navtoggle[aria-expanded="true"] span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
.mnav{display:none;flex-direction:column;background:#FFFFFF;border-bottom:1px solid #D3DBE5;
  padding:6px 20px 18px}
.mnav a{display:block;padding:15px 2px;font-size:16px;font-weight:600;color:#12355B;
  border-bottom:1px solid #EEF2F7;text-decoration:none}
.mnav a.mcta{margin-top:16px;background:#12355B;color:#FFFFFF;text-align:center;
  border-radius:10px;padding:15px;border-bottom:none}
.mnav.open{display:flex}
.foot nav.fnav{display:flex;flex-direction:column;gap:9px}
.foot nav.fnav a{color:inherit;text-decoration:none;opacity:.85}
.foot nav.fnav a:hover{opacity:1;text-decoration:underline}
@media (min-width:861px){.mnav{display:none!important}}
@media (max-width:860px){.navtoggle{display:flex}.nav .btn.b1{display:none}}
/* ---- placeholder for photographs not yet supplied ---- */
.photo-missing{display:flex;align-items:center;justify-content:center;text-align:center;
  background:#EEF2F7;border:1px dashed #C3CEDC;color:#6B7A8D;
  font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;padding:18px;min-height:150px;width:100%;border-radius:8px}
"""

EXTRA_JS = """<script>
(function(){
  var b=document.getElementById('navtoggle'), m=document.getElementById('mnav');
  if(b&&m){
    function close(){m.classList.remove('open');b.setAttribute('aria-expanded','false');}
    b.addEventListener('click',function(){
      b.setAttribute('aria-expanded', m.classList.toggle('open') ? 'true':'false');
    });
    m.addEventListener('click',function(e){ if(e.target.tagName==='A') close(); });
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&m.classList.contains('open')){close();b.focus();}
    });
  }
  /* photographs not yet supplied degrade to a labelled block instead of a broken icon.
     Images may already have failed before this script runs, so handle both cases. */
  function placehold(img){
    if(img.dataset.ph) return; img.dataset.ph=1;
    var d=document.createElement('div');
    d.className='photo-missing';
    d.textContent=(img.getAttribute('alt')||'Photograph')+' \\u2014 photograph to follow';
    if(img.parentNode) img.parentNode.replaceChild(d,img);
  }
  Array.prototype.slice.call(document.images).forEach(function(img){
    if(img.complete && img.naturalWidth===0){ placehold(img); return; }
    img.addEventListener('error',function(){ placehold(img); });
  });
})();
</script>"""

# Replaces the artifact's no-op submit handler with one that actually sends.
FORM_JS = """f.addEventListener('submit',function(ev){ev.preventDefault();
  var need=['f-name','f-co','f-em'],bad=null;
  need.forEach(function(id){var el=document.getElementById(id);var v=el.value.trim();var invalid=!v||(el.type==='email'&&!/^\\S+@\\S+\\.\\S+$/.test(v));el.style.borderColor=invalid?'#C0392B':'';if(invalid&&!bad)bad=el});
  if(bad){bad.focus();return}
  function val(id){var e=document.getElementById(id);return e?e.value.trim():''}
  var prods=Array.prototype.slice.call(document.querySelectorAll('input[name="products"]:checked'))
    .map(function(c){var l=document.querySelector('label[for="'+c.id+'"]');return l?l.textContent.trim():c.value}).join(', ');
  var lines=[
    'Name: '+val('f-name'),
    'Company: '+val('f-co'),
    'Email: '+val('f-em'),
    'Phone: '+val('f-ph'),
    'Country: '+val('f-ctry'),
    'Enquiry type: '+val('f-type'),
    'Products: '+(prods||'-'),
    'Quantity: '+val('f-qty'),
    '',
    'Message:',
    val('f-msg')
  ].join('\\n');
  var href='mailto:__TO__?cc=__CC__'
    +'&subject='+encodeURIComponent('Website enquiry - '+(val('f-co')||val('f-name')))
    +'&body='+encodeURIComponent(lines);
  ok.hidden=false;ok.scrollIntoView({block:'nearest'});
  window.location.href=href;
 });""".replace('__TO__', TO_FOUNDERS).replace('__CC__', CC_INFO)

OK_MSG = ('Thank you. Your email app should now open with this enquiry ready to send '
          '&mdash; please press send there. If nothing opens, email '
          '<a href="mailto:' + TO_FOUNDERS + '?cc=' + CC_INFO + '" style="color:inherit">'
          'pratap@biomedintl.com</a> directly.')


def head_meta(title, desc, canonical):
    img = SITE + '/assets/biomed-logo-symbol-large.png'
    return ('<title>' + title + '</title>'
            '<meta name="description" content="' + desc + '">'
            '<link rel="canonical" href="' + canonical + '">'
            '<link rel="icon" type="image/png" href="assets/biomed-logo-symbol.png">'
            '<meta property="og:type" content="website">'
            '<meta property="og:site_name" content="Biomed International">'
            '<meta property="og:title" content="' + title + '">'
            '<meta property="og:description" content="' + desc + '">'
            '<meta property="og:url" content="' + canonical + '">'
            '<meta property="og:image" content="' + img + '">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="' + title + '">'
            '<meta name="twitter:description" content="' + desc + '">'
            '<meta name="twitter:image" content="' + img + '">')


def nav_links(current):
    out = []
    for label, href in NAV:
        cls = ' class="on" aria-current="page"' if href == current else ''
        out.append('<a href="' + href + '"' + cls + '>' + label + '</a>')
    return ''.join(out)


def transform(html, out_name, title, desc):
    rep = []
    canonical = SITE + '/' + ('' if out_name == 'index.html' else out_name)

    def sub(label, pat, repl, count=1, flags=0, required=True):
        nonlocal html
        html, n = re.subn(pat, repl, html, count=count, flags=flags)
        rep.append((label, n, required))

    # Strip the Claude artifact sandbox runtime. It requests
    # /_runtime/_transforms.*.js, which 404s off-platform and throws a
    # SyntaxError on every page. ~39 KB of dead weight per page too.
    # Only scripts carrying __FRAME_PREAMBLE are removed; page code is kept.
    removed = 0
    out, pos = [], 0
    for m in re.finditer(r'<script\b[^>]*>', html):
        if m.start() < pos:
            continue
        end = html.find('</script>', m.end())
        if end == -1:
            continue
        if '__FRAME_PREAMBLE' in html[m.end():end]:
            out.append(html[pos:m.start()])
            pos = end + len('</script>')
            removed += 1
    out.append(html[pos:])
    html = ''.join(out)
    rep.append(('strip artifact runtime', removed, True))

    sub('head meta', r'<title>.*?</title>', lambda m: head_meta(title, desc, canonical), flags=re.S)

    # header nav -> real links
    sub('header nav', r'(<nav aria-label="Main">).*?(</nav>)',
        lambda m: m.group(1) + nav_links(out_name) + m.group(2), flags=re.S)

    # hamburger + drawer
    sub('hamburger', r'(<nav aria-label="Main">.*?</nav>)',
        lambda m: m.group(1) + '<button class="navtoggle" id="navtoggle" aria-expanded="false"'
                  ' aria-controls="mnav" aria-label="Open menu">'
                  '<span></span><span></span><span></span></button>', flags=re.S)
    sub('drawer', r'</header>',
        lambda m: '</header><nav class="mnav" id="mnav" aria-label="Mobile">'
                  + nav_links(out_name)
                  + '<a class="mcta" href="' + SAMPLE_HREF + '">Request a sample</a></nav>')

    # logo links (header + footer) -> home
    sub('logo links', r'<a href="#" class="logo"', '<a href="index.html" class="logo"',
        count=0)

    # leadership: "Speak with the leadership team" CTA -> founders only, no cc.
    # Do this BEFORE the generic sample rewrite so it is not caught by it.
    if out_name == 'leadership.html':
        sub('leadership CTA', r'<a href="#"([^>]*)>Contact us</a>',
            '<a href="' + LEAD_HREF + r'"\1>Contact us</a>', count=0, required=False)

    # "Request a sample" everywhere -> founders, cc info
    sub('sample CTAs', r'<a href="#(?:f)?"([^>]*)>Request a sample</a>',
        '<a href="' + SAMPLE_HREF + r'"\1>Request a sample</a>', count=0, required=False)

    # remaining in-page CTAs that the artifacts left as href="#"
    sub('breadcrumb Home', r'<a href="#"([^>]*)>Home</a>',
        r'<a href="index.html"\1>Home</a>', count=0, required=False)
    sub('hero CTAs', r'<a href="#"([^>]*)>Explore products</a>',
        r'<a href="products.html"\1>Explore products</a>', count=0, required=False)
    sub('manufacturing CTA', r'<a href="#"([^>]*)>Our manufacturing</a>',
        r'<a href="manufacturing.html"\1>Our manufacturing</a>', count=0, required=False)
    sub('portfolio CTA', r'<a href="#"([^>]*)>See the full product portfolio',
        r'<a href="products.html"\1>See the full product portfolio', count=0, required=False)
    sub('leadership CTA link', r'<a href="#"([^>]*)>Meet our leadership',
        r'<a href="leadership.html"\1>Meet our leadership', count=0, required=False)
    sub('products page link', r'<a href="#"([^>]*)>Products page</a>',
        r'<a href="products.html"\1>Products page</a>', count=0, required=False)

    # the four product cards on the landing page -> their section on the products page
    for anchor, name in (('chondroitin', 'Chondroitin Sulphate Sodium'),
                         ('collagen',    'Collagen Peptides'),
                         ('glucosamine', 'Glucosamine Hydrochloride'),
                         ('cholic',      'Cholic Acid')):
        sub('card -> #' + anchor,
            r'<a href="#"((?:(?!</a>).)*?' + re.escape(name) + r'(?:(?!</a>).)*?)</a>',
            r'<a href="products.html#' + anchor + r'"\1</a>',
            count=0, flags=re.S, required=False)

    # footer nav column
    sub('footer grid', r'(\.foot\{padding:64px 96px 40px;display:grid;grid-template-columns:)1\.2fr 1fr 1fr 1fr',
        r'\g<1>1.2fr .8fr 1fr 1fr .9fr', required=False)
    sub('footer nav', r'(<div><b class="h">GET IN TOUCH</b>)',
        '<div><b class="h">EXPLORE</b><nav class="fnav">' + nav_links(out_name) + '</nav></div>' + r'\1',
        required=False)

    # contact form: make it actually send
    if out_name == 'contact.html':
        # The handler contains nested "});" (need.forEach(...)), so walk the
        # parentheses to find where the addEventListener call actually ends.
        i = html.find("f.addEventListener('submit'")
        j = -1
        if i != -1:
            depth = 0
            for k in range(html.index('(', i), len(html)):
                c = html[k]
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        j = k + 1
                        if html[j:j + 1] == ';':
                            j += 1
                        break
        if i == -1 or j == -1:
            rep.append(('form handler', 0, True))
        else:
            html = html[:i] + FORM_JS + html[j:]
            rep.append(('form handler', 1, True))
        sub('ok message', r'(id="ok"[^>]*>).*?(</div>)',
            lambda m: m.group(1) + OK_MSG + m.group(2), flags=re.S)

    # manufacturing photos live under assets/
    if out_name == 'manufacturing.html':
        sub('photo paths', r'src="photos/', 'src="assets/photos/', count=0)

    # css + js (inject before the LAST closing tags)
    html = html.replace('</style>', EXTRA_CSS + '</style>', 1)
    rep.append(('css', 1, True))
    if '</body>' in html:
        head, _, tail = html.rpartition('</body>')
        html = head + EXTRA_JS + '</body>' + tail
    else:
        html = html.replace('</html>', EXTRA_JS + '</body></html>', 1)
    rep.append(('js', 1, True))

    return html, rep


def main():
    ok = True
    for out, (title, desc) in PAGES.items():
        src = os.path.join(SRC, out)
        html = open(src).read()
        html, rep = transform(html, out, title, desc)
        open(os.path.join(HERE, out), 'w').write(html)
        print('\n' + out)
        for name, n, required in rep:
            flag = 'ok  ' if n else ('MISS' if required else 'n/a ')
            if not n and required:
                ok = False
            print('   [' + flag + '] ' + name + ': ' + str(n))
    print('\nbuild ok' if ok else '\n!! something required matched nothing')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
