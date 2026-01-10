/**
 * ChatUI.js
 * Core rendering logic for the chat interface.
 */

import { state } from './ChatState.js';
import { loadAndRunScript } from './ChatScripts.js';

// --- Timestamps ---
export function formatRelativeTime(date) {
  const now = new Date();
  const diff = now - date;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function updateAllTimestamps() {
  document.querySelectorAll('.message[data-timestamp]').forEach(msg => {
    let date;
    const ts = msg.dataset.timestamp;

    if (ts && (ts.includes('T') || ts.includes('-') || ts.includes(':'))) {
      date = new Date(ts.endsWith('Z') ? ts : ts + 'Z');
    } else {
      date = new Date(parseInt(ts, 10));
    }

    const timeEl = msg.querySelector('.message-time');

    if (timeEl && !isNaN(date.getTime())) {
      timeEl.textContent = formatRelativeTime(date);
      timeEl.title = date.toLocaleString();
    }

    // Decay Logic & Styling
    const ageMs = Date.now() - date.getTime();
    msg.classList.remove('age-fresh', 'age-recent', 'age-old', 'age-ancient');

    if (ageMs < 10 * 1000) msg.classList.add('age-fresh');
    else if (ageMs < 5 * 60 * 1000) msg.classList.add('age-recent');
    else if (ageMs < 60 * 60 * 1000) msg.classList.add('age-old');
    else msg.classList.add('age-ancient');
  });
}

// --- Rendering ---
function createMessageElement(msg) {
  const messageTemplate = document.getElementById('message-template');
  if (!messageTemplate) {
    console.error('[ChatUI] Template not found');
    return null;
  }

  const template = messageTemplate.content.cloneNode(true);
  const article = template.querySelector('.message');

  if (!article) {
    console.error('[ChatUI] Article not found in template');
    return null;
  }

  article.dataset.id = msg.id;
  const timestamp = msg.created_at || Date.now();
  article.dataset.timestamp = timestamp;

  // UX GOD: Visual Flavor
  const rotation = Math.floor(Math.random() * 5);
  if (rotation > 0) article.classList.add(`scribble-${rotation}`);

  const margin = Math.floor(Math.random() * 4) + 1;
  article.classList.add(`margin-${margin}`);

  // Avatar
  const avatar = article.querySelector('.message-avatar');
  if (avatar) {
    avatar.textContent = (msg.user || '?').slice(0, 2).toUpperCase();
    avatar.classList.add(getUserColorClass(msg.user || ''));
  }

  // User name
  const userEl = article.querySelector('.message-user');
  if (userEl) userEl.textContent = msg.user;

  const timeEl = article.querySelector('.message-time');
  if (timeEl) timeEl.textContent = formatRelativeTime(new Date(timestamp));

  // Content
  const content = article.querySelector('.message-content');
  if (msg.deleted) {
    if (content) content.textContent = '[deleted]';
    article.classList.add('deleted');
  } else {
    if (content) content.textContent = msg.content;
  }

  if (msg.edited) {
    const editedEl = article.querySelector('.message-edited');
    if (editedEl) editedEl.hidden = false;
  }

  // Own message logic & Actions
  const effectiveUser = state.currentUser ? state.currentUser.trim() : '';
  if (effectiveUser && msg.user === effectiveUser) {
    article.classList.add('own');
    setupMessageActions(article, msg, content);
  } else {
    // Hide actions for others
    const actions = article.querySelector('.message-actions');
    if (actions) actions.classList.add('!hidden');
  }

  return article;
}

function setupMessageActions(article, msg, contentEl) {
  if (!contentEl) return;
  const editBtn = article.querySelector('.btn-edit');
  const deleteBtn = article.querySelector('.btn-delete');

  if (editBtn) {
    editBtn.addEventListener('click', () => {
      startEdit(article, contentEl.textContent.trim());
    });
  }
  if (deleteBtn) {
    deleteBtn.addEventListener('click', () => {
      showConfirmModal(msg.id);
    });
  }

  // Edit Mode Actions
  article.querySelector('.btn-save')?.addEventListener('click', () => saveEdit(article, msg.id));
  article.querySelector('.btn-cancel')?.addEventListener('click', () => cancelEdit(article));
  article.querySelector('.edit-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      saveEdit(article, msg.id);
    } else if (e.key === 'Escape') {
      cancelEdit(article);
    }
  });
}

export function addMessage(msg) {
  console.log('[ChatUI] addMessage called', msg.id);
  if (state.messageIds.has(msg.id)) return;
  state.messageIds.add(msg.id);

  updateEmptyState();

  const element = createMessageElement(msg);
  if (!element) {
    console.error('[ChatUI] Failed to create message element');
    return;
  }

  const contentEl = element.querySelector('.message-content');
  const rawContent = msg.content || '';

  // Content Processing
  // ... (keeping content processing logic implies we trust it, or I should guard it too?)
  // Guarding contentEl
  if (contentEl) {
    // 1. Script
    const scriptMatch = rawContent.match(/^script:(\d+)$/);
    if (scriptMatch) {
      const scriptId = scriptMatch[1];
      contentEl.innerHTML = `
              <div class="script-card bg-black/30 border border-slate-700/50 rounded-lg p-2 w-full max-w-[280px]">
                  <div class="flex items-center gap-2 mb-2 text-slate-300">
                      <i class="ph-duotone ph-cube text-blue-400"></i>
                      <span class="text-[10px] font-bold uppercase tracking-wider">Sketch #${scriptId}</span>
                  </div>
                  <div class="aspect-video bg-black/80 rounded flex items-center justify-center cursor-pointer hover:bg-slate-900 transition group script-preview relative overflow-hidden" data-id="${scriptId}">
                      <i class="ph-fill ph-play text-3xl text-white opacity-90 group-hover:scale-110 transition z-10"></i>
                      <div class="absolute inset-0 bg-gradient-to-tr from-blue-900/20 to-purple-900/20"></div>
                  </div>
              </div>`;
      const preview = contentEl.querySelector('.script-preview');
      if (preview) {
        preview.addEventListener('click', (e) => {
          loadAndRunScript(e.currentTarget, scriptId);
        });
      }
    }
    // 2. Image
    else if (rawContent.startsWith('img:') || rawContent.match(/\.(jpeg|jpg|gif|png|webp)$/i)) {
      const src = rawContent.startsWith('img:') ? rawContent.substring(4).trim() : rawContent;
      contentEl.innerHTML = '';
      const img = document.createElement('img');
      img.src = src;
      img.alt = "Uploaded image";
      img.className = "max-w-full h-auto rounded-lg border border-slate-700 mt-2 hover:shadow-lg transition";
      img.loading = "lazy";
      contentEl.appendChild(img);
    }
    // 3. Code Block
    else if (rawContent.includes('```')) {
      const escapeHtml = (text) => text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]);
      const formatted = rawContent.replace(/```([\s\S]*?)```/g, (match, code) => {
        return `<pre class="bg-black/50 p-2 rounded text-xs font-mono overflow-x-auto my-2 border border-white/5">${escapeHtml(code)}</pre>`;
      });
      contentEl.innerHTML = formatted;
    }
    // 4. Inline Code
    else if (rawContent.includes('`')) {
      const escapeHtml = (text) => text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]);
      const formatted = rawContent.replace(/`([^`]+)`/g, (match, code) => {
        return `<code class="bg-black/30 px-1 py-0.5 rounded text-xs font-mono text-green-300">${escapeHtml(code)}</code>`;
      });
      contentEl.innerHTML = formatted;
    }
  }

  const messagesContainer = document.getElementById('messages');
  if (messagesContainer) {
    messagesContainer.appendChild(element);
    console.log('[ChatUI] Appended message', msg.id);

    const messagesScroll = document.getElementById('messages-scroll');
    if (messagesScroll) {
      const isNearBottom = messagesScroll.scrollHeight - messagesScroll.scrollTop - messagesScroll.clientHeight < 100;
      if (isNearBottom) scrollToBottom();
    }
    updateScrollButton();
    updateUnreadCount();
  } else {
    console.error('[ChatUI] messages container not found');
  }
}

// --- UI Helpers ---
export function setConnectionStatus(status) {
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  if (statusDot) {
    statusDot.className = 'status-dot ' + status;
    if (statusText) {
      const labels = { connected: 'Connected', disconnected: 'Offline', reconnecting: '...' };
      statusText.textContent = labels[status] || status;
      statusText.hidden = (status === 'connected');
    }
  }
}

export function updateTypingUI() {
  const typingIndicator = document.getElementById('typing-indicator');
  const typingUsers = document.getElementById('typing-users');
  if (!typingIndicator || !typingUsers) return;

  if (state.typingUsersList.size === 0) {
    typingIndicator.classList.add('hidden');
    return;
  }
  typingIndicator.classList.remove('hidden');
  const users = Array.from(state.typingUsersList);
  typingUsers.textContent = users.length === 1 ? `${users[0]} is typing...` : `${users.length} users typing...`;
}

export function scrollToBottom() {
  const messagesScroll = document.getElementById('messages-scroll');
  if (messagesScroll) messagesScroll.scrollTop = messagesScroll.scrollHeight;
}

export function updateScrollButton() {
  const messagesScroll = document.getElementById('messages-scroll');
  const scrollBottomBtn = document.getElementById('scroll-bottom');
  if (!messagesScroll || !scrollBottomBtn) return;

  const distanceFromBottom = messagesScroll.scrollHeight - messagesScroll.scrollTop - messagesScroll.clientHeight;
  if (distanceFromBottom > 200) scrollBottomBtn.classList.remove('hidden');
  else scrollBottomBtn.classList.add('hidden');
}

export function updateEmptyState() {
  const messagesContainer = document.getElementById('messages');
  if (!messagesContainer) return;
  const existing = messagesContainer.querySelector('.empty-state');
  const visibleMessages = messagesContainer.querySelectorAll('.message:not(.search-hidden)');

  if (visibleMessages.length === 0 && state.messageIds.size === 0) {
    if (!existing) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.innerHTML = `<div class="empty-state-icon">💬</div><div class="empty-state-text">No messages yet.</div>`;
      messagesContainer.appendChild(empty);
    }
  } else if (existing) {
    existing.remove();
  }
}

// --- Unread & Toasts ---
export async function updateUnreadCount() {
  try {
    const res = await fetch('/unread');
    const data = await res.json();
    const unreadBadge = document.getElementById('unread-badge');
    if (unreadBadge) {
      if (data.count > 0) {
        unreadBadge.textContent = data.count > 99 ? '99+' : data.count;
        unreadBadge.classList.remove('hidden');
      } else {
        unreadBadge.classList.add('hidden');
      }
    }
  } catch (err) {
    // silent fail
  }
}

export function showToast(message, type = 'info', duration = 3000) {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 200ms ease-out forwards';
    setTimeout(() => toast.remove(), 200);
  }, duration);
}

// --- Utils ---
function getUserColorClass(username) {
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  return `user-color-${Math.abs(hash) % 8}`;
}

// --- Editing Logic ---
function startEdit(article, currentContent) {
  article.classList.add('editing');
  const input = article.querySelector('.edit-input');
  if (input) {
    input.value = currentContent;
    input.focus();
    input.select();
  }
}

function cancelEdit(article) {
  article.classList.remove('editing');
}

async function saveEdit(article, id) {
  const input = article.querySelector('.edit-input');
  const newContent = input.value.trim();

  if (!newContent) {
    showToast('Message cannot be empty', 'warning');
    return;
  }

  try {
    const res = await fetch('/edit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User': state.currentUser || 'anonymous'
      },
      body: JSON.stringify({ id, content: newContent })
    });

    if (res.ok) {
      article.querySelector('.message-content').textContent = newContent;
      article.querySelector('.message-edited').hidden = false;
      cancelEdit(article);
      showToast('Message edited', 'success');
    } else {
      const data = await res.json();
      showToast(data.error || 'Failed', 'error');
    }
  } catch (err) {
    showToast('Network error', 'error');
  }
}

// --- Delete Modal ---
export function setupConfirmModal() {
  const confirmModal = document.getElementById('confirm-modal');
  const modalConfirmBtn = document.getElementById('modal-confirm');
  const modalCancelBtn = document.getElementById('modal-cancel');

  if (!confirmModal) return;

  function hide() {
    confirmModal.classList.add('hidden');
    state.pendingDeleteId = null;
  }

  modalCancelBtn?.addEventListener('click', hide);
  confirmModal.addEventListener('click', (e) => {
    if (e.target === confirmModal) hide();
  });

  modalConfirmBtn?.addEventListener('click', async () => {
    if (!state.pendingDeleteId) return;
    const id = state.pendingDeleteId;
    hide();

    try {
      const res = await fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User': state.currentUser || 'anonymous' },
        body: JSON.stringify({ id })
      });
      if (res.ok) {
        const msgEl = document.querySelector(`[data-id="${id}"]`);
        if (msgEl) {
          msgEl.querySelector('.message-content').textContent = '[deleted]';
          msgEl.classList.add('deleted');
          const actions = msgEl.querySelector('.message-actions');
          if (actions) actions.style.display = 'none';
        }
        showToast('Message deleted', 'success');
        updateUnreadCount();
      } else {
        showToast('Failed to delete', 'error');
      }
    } catch (e) {
      showToast('Network error', 'error');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !confirmModal.classList.contains('hidden')) {
      hide();
    }
  });
}

export function showConfirmModal(id) {
  state.pendingDeleteId = id;
  const m = document.getElementById('confirm-modal');
  if (m) {
    m.classList.remove('hidden');
    const btn = document.getElementById('modal-confirm');
    if (btn) btn.focus();
  }
}
