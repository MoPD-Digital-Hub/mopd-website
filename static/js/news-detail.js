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

    const list = root.querySelector('[data-comment-list]');
    const empty = root.querySelector('[data-comment-empty]');
    const status = root.querySelector('[data-comment-status]');
    const countNum = root.querySelector('[data-comment-count-num]');

    function setStatus(message, kind) {
      if (!status) return;
      if (!message) {
        status.hidden = true;
        status.textContent = '';
        status.className = 'mp-article__status';
        return;
      }
      status.hidden = false;
      status.textContent = message;
      status.className = 'mp-article__status is-' + (kind || 'info');
    }

    function updateCaptcha(question) {
      if (!question) return;
      root.querySelectorAll('[data-captcha-question]').forEach((el) => {
        el.textContent = question;
      });
      root.querySelectorAll('input[name="captcha_answer"]').forEach((input) => {
        input.value = '';
      });
    }

    function updateCount(total) {
      if (typeof total !== 'number') return;
      root.dataset.commentCount = String(total);
      if (countNum) countNum.textContent = String(total);
    }

    function bindItem(item) {
      if (!item || item.dataset.bound === '1') return;
      item.dataset.bound = '1';

      item.querySelectorAll('[data-comment-like]').forEach((btn) => {
        if (btn.closest('[data-comment-item]') !== item) return;
        btn.addEventListener('click', () => {
          const countEl = btn.querySelector('[data-comment-like-count]');
          postLike(btn, countEl, btn.dataset.likeUrl);
        });
      });

      const replyBtn = item.querySelector(':scope > .mp-article__comment-actions [data-reply-btn]');
      const replyForm = item.querySelector(':scope > [data-inline-reply]');
      if (replyBtn && replyForm) {
        replyBtn.addEventListener('click', () => {
          const opening = replyForm.hidden;
          root.querySelectorAll('[data-inline-reply]').forEach((form) => {
            form.hidden = true;
          });
          root.querySelectorAll('[data-reply-btn]').forEach((btn) => {
            btn.setAttribute('aria-expanded', 'false');
          });
          if (opening) {
            replyForm.hidden = false;
            replyBtn.setAttribute('aria-expanded', 'true');
            replyForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            const name = replyForm.querySelector('input[name="name"]');
            const body = replyForm.querySelector('textarea[name="body"]');
            if (name && !name.value) name.focus();
            else if (body) body.focus();
          }
        });
      }

      const replyCancel = item.querySelector(':scope > [data-inline-reply] [data-reply-cancel]');
      if (replyCancel && replyForm && replyBtn) {
        replyCancel.addEventListener('click', () => {
          replyForm.hidden = true;
          replyBtn.setAttribute('aria-expanded', 'false');
        });
      }

      const toggle = item.querySelector(':scope > .mp-article__comment-actions [data-edit-toggle]');
      const editForm = item.querySelector(':scope > [data-edit-form]');
      const body = item.querySelector(':scope > [data-comment-body]');
      const cancelEdit = item.querySelector(':scope > [data-edit-form] [data-edit-cancel]');
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

      const deleteForm = item.querySelector(':scope > .mp-article__comment-actions [data-delete-form]');
      if (deleteForm) {
        deleteForm.addEventListener('submit', (event) => {
          if (!window.confirm('Delete this comment?')) {
            event.preventDefault();
          }
        });
      }
    }

    function insertComment(html, parentId) {
      const wrap = document.createElement('div');
      wrap.innerHTML = html.trim();
      const item = wrap.firstElementChild;
      if (!item || !list) return null;

      if (parentId) {
        const parent = root.querySelector('[data-comment-id="' + parentId + '"]');
        let replyList = parent && parent.querySelector(':scope > [data-reply-list]');
        if (parent && !replyList) {
          replyList = document.createElement('ul');
          replyList.className = 'mp-article__reply-list';
          replyList.setAttribute('data-reply-list', '');
          parent.appendChild(replyList);
        }
        if (replyList) {
          replyList.hidden = false;
          replyList.appendChild(item);
        }
      } else {
        list.appendChild(item);
      }

      list.hidden = false;
      if (empty) empty.hidden = true;
      bindItem(item);
      item.classList.add('is-new');
      item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      return item;
    }

    async function submitCommentForm(form) {
      const submitBtn = form.querySelector('[type="submit"]');
      const originalLabel = submitBtn ? submitBtn.textContent : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Posting…';
      }
      setStatus('');

      try {
        const res = await fetch(window.location.pathname + window.location.search, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrf(),
            'X-Requested-With': 'XMLHttpRequest',
            Accept: 'application/json',
          },
          credentials: 'same-origin',
          body: new FormData(form),
        });

        let data = null;
        try {
          data = await res.json();
        } catch {
          data = null;
        }

        if (!res.ok || !data || !data.ok) {
          if (data && data.captcha_question) {
            updateCaptcha(data.captcha_question);
          }
          const err = (data && data.errors && data.errors[0]) || 'Could not post comment. Please try again.';
          setStatus(err, 'error');
          return;
        }

        insertComment(data.html, data.parent_id || null);
        updateCount(data.comment_count);
        if (data.captcha_question) {
          updateCaptcha(data.captcha_question);
        }
        setStatus(data.message || 'Your comment was posted.', 'success');

        if (form.hasAttribute('data-inline-reply')) {
          const parentInput = form.querySelector('input[name="parent_id"]');
          const parentVal = parentInput ? parentInput.value : '';
          form.reset();
          if (parentInput) parentInput.value = parentVal;
          const typeInput = form.querySelector('input[name="form_type"]');
          if (typeInput) typeInput.value = 'comment';
          form.hidden = true;
          const item = form.closest('[data-comment-item]');
          const replyBtn = item && item.querySelector('[data-reply-btn]');
          if (replyBtn) replyBtn.setAttribute('aria-expanded', 'false');
        } else {
          const body = form.querySelector('textarea[name="body"]');
          const captcha = form.querySelector('input[name="captcha_answer"]');
          if (body) body.value = '';
          if (captcha) captcha.value = '';
        }

        window.setTimeout(() => setStatus(''), 4200);
      } catch {
        setStatus('Network error. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalLabel;
        }
      }
    }

    root.querySelectorAll('[data-comment-item]').forEach(bindItem);

    root.addEventListener('submit', (event) => {
      const form = event.target.closest('[data-comment-form]');
      if (!form || !root.contains(form)) return;
      event.preventDefault();
      submitCommentForm(form);
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
