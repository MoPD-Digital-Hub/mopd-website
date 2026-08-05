(function () {
  function getCsrf() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  async function postLike(btn, countEl, url) {
    if (!btn || !url || btn.disabled) return;
    btn.disabled = true;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrf(),
          Accept: 'application/json',
        },
        credentials: 'same-origin',
      });
      const data = await res.json();
      if (data && data.ok) {
        btn.classList.add('is-liked');
        btn.setAttribute('aria-pressed', 'true');
        if (countEl && typeof data.like_count === 'number') {
          countEl.textContent = String(data.like_count);
        }
      } else {
        btn.disabled = false;
      }
    } catch {
      btn.disabled = false;
    }
  }

  function initArticleLikeShare() {
    const root = document.querySelector('[data-news-engage]');
    if (!root) return;

    const likeBtn = root.querySelector('[data-like-btn]');
    const likeCount = root.querySelector('[data-like-count]');
    const likeUrl = root.dataset.likeUrl;
    const alreadyLiked = root.dataset.liked === '1';

    if (likeBtn && likeUrl) {
      likeBtn.addEventListener('click', () => {
        if (likeBtn.disabled || alreadyLiked) return;
        postLike(likeBtn, likeCount, likeUrl).then(() => {
          root.dataset.liked = '1';
        });
      });
    }

    const shareRoot = root.querySelector('[data-share-root]');
    if (!shareRoot) return;

    const toggle = shareRoot.querySelector('[data-share-toggle]');
    const menu = shareRoot.querySelector('[data-share-menu]');
    const copyBtn = shareRoot.querySelector('[data-share-copy]');
    const nativeBtn = shareRoot.querySelector('[data-share-native]');
    const pageUrl = window.location.href;
    const pageTitle = document.title;

    if (nativeBtn && navigator.share) {
      nativeBtn.hidden = false;
      nativeBtn.addEventListener('click', async () => {
        try {
          await navigator.share({ title: pageTitle, url: pageUrl });
        } catch {
          /* cancelled */
        }
      });
    }

    if (toggle && menu) {
      toggle.addEventListener('click', () => {
        const open = menu.hasAttribute('hidden');
        if (open) menu.removeAttribute('hidden');
        else menu.setAttribute('hidden', '');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });

      document.addEventListener('click', (event) => {
        if (!shareRoot.contains(event.target)) {
          menu.setAttribute('hidden', '');
          toggle.setAttribute('aria-expanded', 'false');
        }
      });
    }

    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(pageUrl);
          const original = copyBtn.textContent;
          copyBtn.textContent = 'Copied';
          setTimeout(() => {
            copyBtn.textContent = original;
          }, 1600);
        } catch {
          window.prompt('Copy this link:', pageUrl);
        }
      });
    }
  }

  function initCommentEngage() {
    const root = document.querySelector('[data-comment-root]');
    if (!root) return;

    root.querySelectorAll('[data-comment-like]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const countEl = btn.querySelector('[data-comment-like-count]');
        postLike(btn, countEl, btn.dataset.likeUrl);
      });
    });

    const closeAllReplies = (except) => {
      root.querySelectorAll('[data-inline-reply]').forEach((form) => {
        if (except && form === except) return;
        form.hidden = true;
      });
      root.querySelectorAll('[data-reply-btn]').forEach((btn) => {
        if (except && btn.closest('[data-comment-item]')?.querySelector('[data-inline-reply]') === except) {
          btn.setAttribute('aria-expanded', 'true');
          return;
        }
        btn.setAttribute('aria-expanded', 'false');
      });
    };

    root.querySelectorAll('[data-reply-btn]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const item = btn.closest('[data-comment-item]');
        const replyForm = item && item.querySelector('[data-inline-reply]');
        if (!replyForm) return;
        const opening = replyForm.hidden;
        closeAllReplies(opening ? replyForm : null);
        replyForm.hidden = !opening;
        btn.setAttribute('aria-expanded', opening ? 'true' : 'false');
        if (opening) {
          replyForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          const name = replyForm.querySelector('input[name="name"]');
          const body = replyForm.querySelector('textarea[name="body"]');
          if (name && !name.value) name.focus();
          else if (body) body.focus();
        }
      });
    });

    root.querySelectorAll('[data-reply-cancel]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const form = btn.closest('[data-inline-reply]');
        if (!form) return;
        form.hidden = true;
        const item = form.closest('[data-comment-item]');
        const replyBtn = item && item.querySelector('[data-reply-btn]');
        if (replyBtn) replyBtn.setAttribute('aria-expanded', 'false');
      });
    });

    root.querySelectorAll('[data-comment-item]').forEach((item) => {
      const toggle = item.querySelector('[data-edit-toggle]');
      const editForm = item.querySelector('[data-edit-form]');
      const body = item.querySelector('[data-comment-body]');
      const cancelEdit = item.querySelector('[data-edit-cancel]');
      if (toggle && editForm && body) {
        toggle.addEventListener('click', () => {
          editForm.hidden = false;
          body.hidden = true;
          toggle.hidden = true;
          const area = editForm.querySelector('textarea');
          if (area) area.focus();
        });
      }
      if (cancelEdit && editForm && body && toggle) {
        cancelEdit.addEventListener('click', () => {
          editForm.hidden = true;
          body.hidden = false;
          toggle.hidden = false;
        });
      }
    });

    root.querySelectorAll('[data-delete-form]').forEach((form) => {
      form.addEventListener('submit', (event) => {
        if (!window.confirm('Delete this comment?')) {
          event.preventDefault();
        }
      });
    });
  }

  function boot() {
    initArticleLikeShare();
    initCommentEngage();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
