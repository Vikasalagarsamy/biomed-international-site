// Shared chrome (nav + footer) injected into every page.
(function(){
  var page = document.body.getAttribute('data-page') || '';
  function active(p){ return p===page ? ' class="active"' : ''; }

  var nav =
  '<header class="nav"><div class="wrap nav-inner">'+
    '<a href="/" class="brand"><img src="/assets/brand/logo.jpg" alt="Biomed International logo"/>'+
      '<div><div class="bt">Biomed International</div><div class="bs">Bioceutical Manufacturing</div></div></a>'+
    '<nav class="links" id="navLinks">'+
      '<a href="/about.html"'+active('about')+'>About Us</a>'+
      '<a href="/products.html"'+active('products')+'>Products</a>'+
      '<a href="/infrastructure.html"'+active('infrastructure')+'>Infrastructure</a>'+
      '<a href="/careers.html"'+active('careers')+'>Careers</a>'+
      '<a href="/contact.html"'+active('contact')+'>Contact</a>'+
    '</nav>'+
    '<div class="nav-right">'+
      '<a href="/contact.html" class="btn btn-primary nav-quote">Contact Us</a>'+
      '<button class="menu-toggle" aria-label="Toggle menu" onclick="document.body.classList.toggle(\'nav-open\')">☰</button>'+
    '</div>'+
  '</div></header>';

  var footer =
  '<footer><div class="wrap"><div class="foot-grid">'+
    '<div><h5>Biomed International</h5><p class="tag">Leading life science manufacturing since 2014 — Chondroitin Sulfate Sodium and Collagen for pharma, nutraceutical and food industries.</p></div>'+
    '<div><div class="fh">Navigate</div><ul>'+
      '<li><a href="/about.html">About Us</a></li>'+
      '<li><a href="/products.html">Products</a></li>'+
      '<li><a href="/infrastructure.html">Infrastructure</a></li>'+
      '<li><a href="/careers.html">Careers</a></li>'+
      '<li><a href="/contact.html">Contact</a></li></ul></div>'+
    '<div><div class="fh">Products</div><ul>'+
      '<li><a href="/products.html#chondroitin">Chondroitin Sulfate Sodium</a></li>'+
      '<li><a href="/products.html#collagen">Collagen</a></li></ul></div>'+
    '<div><div class="fh">Get in touch</div><ul>'+
      '<li>Mekanuru Village, Guduru Mandal, Tirupati District, Andhra Pradesh – 524410</li>'+
      '<li><a href="tel:+919791154650">+91 97911 54650</a></li>'+
      '<li><a href="mailto:info@biomedintl.com">info@biomedintl.com</a></li></ul></div>'+
  '</div><div class="foot-bottom"><span>© 2026 Biomed International. All rights reserved.</span><span>Tirupati District, Andhra Pradesh · India</span></div></div></footer>';

  document.body.insertAdjacentHTML('afterbegin', nav);
  document.body.insertAdjacentHTML('beforeend', footer);

  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold:.12});
  document.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });

  var navEl = document.querySelector('header.nav');
  function onScroll(){ navEl.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
})();
