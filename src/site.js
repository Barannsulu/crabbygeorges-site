(function () {
  var $ = function (s) { return document.querySelector(s); };
  var $$ = function (s) { return [].slice.call(document.querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Today's hours (restaurant time zone)
  var hrs = { 0: '12:00–9:30 PM', 1: '3:30–9:00 PM', 2: '3:30–9:00 PM', 3: '3:30–9:00 PM', 4: '3:30–9:00 PM', 5: '2:00–9:30 PM', 6: '12:00–10:00 PM' };
  try {
    var d = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/New_York' })).getDay();
    if ($('#todayHours')) $('#todayHours').textContent = hrs[d];
    var row = $('.hours tr[data-d="' + d + '"]'); if (row) row.classList.add('today');
  } catch (e) {}

  function play(v) { v.preload = 'auto'; var p = v.play(); if (p && p.catch) p.catch(function () {}); }

  // Sticky media frame: swap as each step reaches mid-screen; only the visible video plays
  var fx = $$('.frame .fx'), count = $('#count');
  if (fx.length) {
    fx.forEach(function (m, j) { m.style.zIndex = j; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = +e.target.dataset.i;
        fx.forEach(function (m, j) {
          m.classList.toggle('on', j <= i);
          if (m.tagName === 'VIDEO') { if (j === i && !reduce) play(m); else m.pause(); }
        });
        if (count) count.textContent = '0' + (i + 1) + ' / 0' + fx.length;
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    $$('.step').forEach(function (s) { io.observe(s); });
  }

  // Narrow screens: step cards play their own video while on screen
  if (!reduce && $$('video.m-img').length) {
    var io3 = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target; if (getComputedStyle(v).display === 'none') return;
        if (e.isIntersecting) play(v); else v.pause();
      });
    }, { threshold: 0.35 });
    $$('video.m-img').forEach(function (v) { io3.observe(v); });
  }

  // Hero video pause control
  var hv = $('#heroVid'), pb = $('#pauseBtn');
  if (hv && pb) {
    if (reduce) { hv.removeAttribute('autoplay'); hv.pause(); pb.textContent = 'Play'; }
    pb.addEventListener('click', function () { if (hv.paused) { hv.play(); pb.textContent = 'Pause'; } else { hv.pause(); pb.textContent = 'Play'; } });
  }

  // Menu: active category
  var cats = $$('.cats a');
  if (cats.length) {
    var io2 = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) cats.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); }); });
    }, { rootMargin: '-40% 0px -55% 0px' });
    $$('.msec').forEach(function (s) { io2.observe(s); });
  }

  // Menu: photo peek on hover (mouse only)
  var peek = $('#peek');
  if (peek && matchMedia('(pointer:fine)').matches) {
    var pimg = peek.querySelector('img');
    $$('.item[data-img]').forEach(function (it) {
      it.addEventListener('mouseenter', function () { pimg.src = it.dataset.img; peek.classList.add('on'); });
      it.addEventListener('mouseleave', function () { peek.classList.remove('on'); });
    });
    addEventListener('mousemove', function (e) { peek.style.transform = 'translate(' + (e.clientX + 24) + 'px,' + (e.clientY - 90) + 'px)'; });
  }

  if (reduce || !window.gsap) return;
  gsap.registerPlugin(ScrollTrigger);
  if ($('#reel')) {
    var tl = gsap.timeline({ defaults: { ease: 'power4.out' } });
    tl.fromTo('#reel', { clipPath: 'inset(46% 0% 46% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.1, ease: 'expo.inOut' }, 0)
      .fromTo('#heroVid', { scale: 1.3 }, { scale: 1, duration: 2.2, ease: 'power3.out' }, 0)
      .from('#h1 .line > span', { yPercent: 110, duration: 1, stagger: 0.12 }, 0.55)
      .from('#heroClaim,#heroEyebrow,#heroLede,#heroCtas,#heroFacts', { y: 20, opacity: 0, duration: 0.7, stagger: 0.08 }, 0.95);
    gsap.to('#reel', { yPercent: 8, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  }
  if ($('.band')) {
    gsap.fromTo('#bandImg', { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: '.band', start: 'top bottom', end: 'bottom top', scrub: true } });
    gsap.from('.band .over p', { scale: 0.86, opacity: 0, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: '.band', start: 'top 75%' } });
  }
})();
