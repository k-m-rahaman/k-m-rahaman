/* Standalone preview behavior; does not imply custom hover support in GitHub Markdown. */
(() => {
  'use strict';
  function initPreview() {
    const article = document.querySelector('article');
    if (!article || document.querySelector('.preview-toolbar')) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const fineHover = window.matchMedia('(hover: hover) and (pointer: fine)');
    const root = document.documentElement;
    let paused = false;
    let userChoseMotion = false;

    const toolbar = document.createElement('section');
    toolbar.className = 'preview-toolbar';
    toolbar.setAttribute('aria-label', 'Interactive preview controls');
    toolbar.innerHTML = '<div class="preview-toolbar__identity">INTERACTIVE PREVIEW</div>' +
      '<div class="preview-toolbar__controls"><span class="preview-toolbar__status" aria-live="polite"></span>' +
      '<button class="preview-motion-toggle" type="button" aria-pressed="false">Pause animations</button></div>' +
      '<p class="preview-toolbar__note">Hover glow and touch feedback work in this preview. On GitHub, use linked cards and tap-to-expand sections.</p>';
    article.before(toolbar);
    const motionButton = toolbar.querySelector('button');
    const motionStatus = toolbar.querySelector('.preview-toolbar__status');

    // Record original attributes once. Responsive picture selection remains native.
    const animatedImages = Array.from(article.querySelectorAll('img')).filter(image => /\.gif(?:[?#]|$)/i.test(image.getAttribute('src') || ''));
    const animationRecords = animatedImages.map(image => ({
      image,
      src: image.getAttribute('src'),
      srcset: image.getAttribute('srcset'),
      sources: Array.from(image.closest('picture')?.querySelectorAll('source') || []).map(source => ({
        element: source,
        srcset: source.getAttribute('srcset'),
        media: source.getAttribute('media') || ''
      }))
    }));

    const replaceExtension = (value, from, to) => value?.replace(new RegExp('\\.' + from + '(?=([?#][^\\s,]*)?(?:\\s|,|$))', 'gi'), '.' + to);

    function applyMotion(nextPaused, explicit = false) {
      paused = nextPaused;
      if (explicit) userChoseMotion = true;
      root.dataset.previewAnimations = paused ? 'paused' : 'playing';
      for (const record of animationRecords) {
        for (const source of record.sources) {
          let value = source.srcset;
          if (paused) value = replaceExtension(value, 'gif', 'png');
          // An explicit Play overrides the reduced-motion picture branch for GIFs,
          // while pointer tilt/ripple still honor the OS reduced-motion setting.
          else if (explicit && reducedMotion.matches && source.media.includes('prefers-reduced-motion')) value = replaceExtension(value, 'png', 'gif');
          if (value !== null) source.element.setAttribute('srcset', value);
        }
        if (record.srcset !== null) record.image.setAttribute('srcset', paused ? replaceExtension(record.srcset, 'gif', 'png') : record.srcset);
        record.image.setAttribute('src', paused ? replaceExtension(record.src, 'gif', 'png') : record.src);
      }
      motionButton.textContent = paused ? 'Play animations' : 'Pause animations';
      motionButton.setAttribute('aria-pressed', String(paused));
      motionStatus.textContent = paused ? 'Animations paused' : 'Animations playing';
      if (paused) {
        article.querySelectorAll('.preview-ripple').forEach(ripple => ripple.remove());
        article.querySelectorAll('.preview-surface').forEach(surface => {
          surface.style.removeProperty('--preview-rx');
          surface.style.removeProperty('--preview-ry');
          surface.classList.remove('preview-pressed');
        });
      }
    }

    motionButton.addEventListener('click', () => applyMotion(!paused, true));
    reducedMotion.addEventListener('change', () => {
      if (!userChoseMotion) applyMotion(reducedMotion.matches);
    });

    const surfaces = new Set();
    article.querySelectorAll('picture').forEach(picture => {
      const anchor = picture.closest('a');
      const surface = anchor || picture;
      surface.classList.add('preview-surface');
      if (anchor) surface.classList.add('preview-surface--linked', 'preview-surface--large');
      surfaces.add(surface);
    });
    article.querySelectorAll('a').forEach(anchor => {
      if (anchor.querySelector('img') && !anchor.classList.contains('preview-surface')) {
        anchor.classList.add('preview-surface', 'preview-surface--linked', 'preview-surface--compact');
        surfaces.add(anchor);
      } else if (!anchor.querySelector('img')) anchor.classList.add('preview-link');
    });

    function motionAllowed() { return !paused && !reducedMotion.matches; }

    for (const surface of surfaces) {
      let frame = 0;
      let pressTimer = 0;
      let touchTimer = 0;

      surface.addEventListener('pointermove', event => {
        if (!motionAllowed() || !fineHover.matches || event.pointerType === 'touch') return;
        if (frame) cancelAnimationFrame(frame);
        const x = event.clientX;
        const y = event.clientY;
        frame = requestAnimationFrame(() => {
          frame = 0;
          const rect = surface.getBoundingClientRect();
          const rx = -.9 * ((y - rect.top) / rect.height - .5);
          const ry = 1.8 * ((x - rect.left) / rect.width - .5);
          surface.style.setProperty('--preview-rx', rx.toFixed(2) + 'deg');
          surface.style.setProperty('--preview-ry', ry.toFixed(2) + 'deg');
        });
      }, { passive: true });

      surface.addEventListener('pointerleave', () => {
        if (frame) cancelAnimationFrame(frame);
        frame = 0;
        surface.style.removeProperty('--preview-rx');
        surface.style.removeProperty('--preview-ry');
        surface.classList.remove('preview-pressed');
      }, { passive: true });

      surface.addEventListener('pointerdown', event => {
        if (event.button !== 0) return;
        clearTimeout(pressTimer);
        surface.classList.add('preview-pressed');
        pressTimer = setTimeout(() => surface.classList.remove('preview-pressed'), 240);
        if (event.pointerType === 'touch' && !surface.matches('a')) {
          clearTimeout(touchTimer);
          surface.classList.add('preview-touched');
          touchTimer = setTimeout(() => surface.classList.remove('preview-touched'), 700);
        }
        if (!motionAllowed()) return;
        const rect = surface.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 1.4;
        const ripple = document.createElement('span');
        ripple.className = 'preview-ripple';
        ripple.setAttribute('aria-hidden', 'true');
        ripple.style.setProperty('--ripple-size', size + 'px');
        ripple.style.setProperty('--ripple-left', event.clientX - rect.left - size / 2 + 'px');
        ripple.style.setProperty('--ripple-top', event.clientY - rect.top - size / 2 + 'px');
        surface.append(ripple);
        ripple.addEventListener('animationend', () => ripple.remove(), { once: true });
        setTimeout(() => ripple.remove(), 800);
      }, { passive: true });
      surface.addEventListener('pointerup', () => surface.classList.remove('preview-pressed'), { passive: true });
      surface.addEventListener('pointercancel', () => surface.classList.remove('preview-pressed'), { passive: true });
    }

    applyMotion(paused);
    root.dataset.previewReady = 'true';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initPreview, { once: true });
  else initPreview();
})();
