(function () {
  const loader = document.getElementById('mpPageLoader');
  if (!loader) return;

  const MIN_MS = 450;
  const MAX_MS = 4000;
  const started = Date.now();
  let finished = false;

  function finish() {
    if (finished) return;
    finished = true;
    const elapsed = Date.now() - started;
    const wait = Math.max(0, MIN_MS - elapsed);
    window.setTimeout(() => {
      document.documentElement.classList.remove('mp-loading');
      document.documentElement.classList.add('mp-page-ready');
      document.body.classList.add('mp-page-ready');
      loader.classList.add('is-done');
      loader.setAttribute('aria-busy', 'false');
      window.setTimeout(() => {
        if (loader.parentNode) loader.parentNode.removeChild(loader);
      }, 550);
    }, wait);
  }

  function imageReady(img) {
    if (img.complete && img.naturalWidth > 0) return Promise.resolve();
    if (img.complete && img.naturalWidth === 0) return Promise.resolve();
    return new Promise((resolve) => {
      const done = () => resolve();
      img.addEventListener('load', done, { once: true });
      img.addEventListener('error', done, { once: true });
    });
  }

  function waitForVisibleImages() {
    const images = Array.prototype.slice.call(document.images || []).filter((img) => {
      if (!img || img.closest('#mpPageLoader')) return false;
      if (img.loading === 'lazy') return false;
      // Skip tiny tracking/spacer pixels
      if (img.width === 1 && img.height === 1) return false;
      return true;
    });
    if (!images.length) return Promise.resolve();
    return Promise.all(images.map(imageReady));
  }

  function waitForDom() {
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      document.addEventListener('DOMContentLoaded', resolve, { once: true });
    });
  }

  const ready = waitForDom().then(waitForVisibleImages);
  const timeout = new Promise((resolve) => window.setTimeout(resolve, MAX_MS));

  Promise.race([ready, timeout]).then(finish);

  // Safety if something blocks forever before race settles oddly
  window.setTimeout(finish, MAX_MS + 300);
})();
