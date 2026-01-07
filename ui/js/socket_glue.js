/**
 * NeoSpace Socket Client
 * Handles WebSocket communication and UI updates
 */

console.log('socket_glue.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  console.log('socket_glue.js starting...');
  let socket;
  try {
    socket = io();
    console.log('Socket initialized', socket);
  } catch (e) {
    console.error('Failed to initialize socket:', e);
  }

// DOM elements
const messagesContainer = document.getElementById('messages');
const messagesScroll = document.getElementById('messages-scroll');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('input');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const messageTemplate = document.getElementById('message-template');
const toastContainer = document.getElementById('toast-container');
const sendBtn = document.getElementById('send-btn');
const confirmModal = document.getElementById('confirm-modal');
const modalConfirmBtn = document.getElementById('modal-confirm');
const modalCancelBtn = document.getElementById('modal-cancel');
const scrollBottomBtn = document.getElementById('scroll-bottom');
const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');
const unreadBadge = document.getElementById('unread-badge');
const typingIndicator = document.getElementById('typing-indicator');
const typingUsers = document.getElementById('typing-users');
const emojiBtn = document.getElementById('emoji-btn');
const emojiPickerContainer = document.getElementById('emoji-picker-container');
const emojiPicker = document.querySelector('emoji-picker');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const dragOverlay = document.getElementById('drag-overlay');

// State
let currentUser = localStorage.getItem('neospace_username') || '';
let currentRoom = localStorage.getItem('neospace_last_room') || '# general';
let messageIds = new Set();
let isLoading = false;
let pendingDeleteId = null;
let allMessages = []; // Store messages for search
let typingTimeout = null;
let isTyping = false;
let typingUsersList = new Set();

// Typing indicator: emit when user types
messageInput.addEventListener('input', () => {
  if (!isTyping) {
    isTyping = true;
    socket.emit('typing', { user: currentUser || 'anonymous' });
  }
  clearTimeout(typingTimeout);
  typingTimeout = setTimeout(() => {
    isTyping = false;
    socket.emit('stop_typing', { user: currentUser || 'anonymous' });
  }, 2000);
});

/**
 * Format relative time
 */
function formatRelativeTime(date) {
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

/**
 * Update all timestamps (call periodically)
 */
function updateAllTimestamps() {
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

    // UX GOD: Living Wall Decay Logic
    const ageMs = Date.now() - date.getTime();
    msg.classList.remove('age-fresh', 'age-recent', 'age-old', 'age-ancient');
    
    if (ageMs < 10 * 1000) { // < 10 seconds
        msg.classList.add('age-fresh');
    } else if (ageMs < 5 * 60 * 1000) { // < 5 mins
        msg.classList.add('age-recent');
    } else if (ageMs < 60 * 60 * 1000) { // < 1 hour
        msg.classList.add('age-old');
    } else {
        msg.classList.add('age-ancient');
    }
  });
}

// Update timestamps every minute
setInterval(updateAllTimestamps, 60000);

/**
 * Show a toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toast.setAttribute('role', 'alert');
  
  toastContainer.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideOut 200ms ease-out forwards';
    setTimeout(() => toast.remove(), 200);
  }, duration);
}

/**
 * Set loading state for send button
 */
function setLoading(loading) {
  isLoading = loading;
  sendBtn.disabled = loading;
  sendBtn.textContent = loading ? '...' : 'Send';
}

/**
 * Show/hide empty state
 */
function updateEmptyState() {
  const existing = messagesContainer.querySelector('.empty-state');
  const visibleMessages = messagesContainer.querySelectorAll('.message:not(.search-hidden)');
  
  if (visibleMessages.length === 0 && messageIds.size === 0) {
    if (!existing) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.innerHTML = `
        <div class="empty-state-icon">💬</div>
        <div class="empty-state-text">No messages yet.</div>
      `;
      messagesContainer.appendChild(empty);
    }
  } else if (existing) {
    existing.remove();
  }
}

/**
 * Update scroll-to-bottom button visibility
 */
function updateScrollButton() {
  const distanceFromBottom = messagesScroll.scrollHeight - messagesScroll.scrollTop - messagesScroll.clientHeight;
  if (scrollBottomBtn) {
      if (distanceFromBottom > 200) {
          scrollBottomBtn.classList.remove('hidden');
      } else {
          scrollBottomBtn.classList.add('hidden');
      }
  }
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
  messagesScroll.scrollTop = messagesScroll.scrollHeight;
}

if (scrollBottomBtn) scrollBottomBtn.addEventListener('click', scrollToBottom);
messagesScroll.addEventListener('scroll', updateScrollButton);

/**
 * Fetch and update unread count
 */
async function updateUnreadCount() {
  try {
    const res = await fetch('/unread');
    const data = await res.json();
    if (unreadBadge) {
        if (data.count > 0) {
          unreadBadge.textContent = data.count > 99 ? '99+' : data.count;
          unreadBadge.classList.remove('hidden');
        } else {
          unreadBadge.classList.add('hidden');
        }
    }
  } catch (err) {
    console.error('Failed to fetch unread count:', err);
  }
}

updateUnreadCount();
setInterval(updateUnreadCount, 30000);

/**
 * Search messages
 */
function searchMessages(query) {
  const q = query.toLowerCase().trim();
  if (searchClear) searchClear.hidden = !q;
  
  document.querySelectorAll('.message').forEach(msg => {
    if (!q) {
      msg.classList.remove('search-hidden', 'search-match');
      return;
    }
    
    const content = msg.querySelector('.message-content')?.textContent.toLowerCase() || '';
    const user = msg.querySelector('.message-user')?.textContent.toLowerCase() || '';
    
    if (content.includes(q) || user.includes(q)) {
      msg.classList.remove('search-hidden');
      msg.classList.add('search-match');
    } else {
      msg.classList.add('search-hidden');
      msg.classList.remove('search-match');
    }
  });
}

let searchTimeout;
if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        searchMessages(searchInput.value);
      }, 200);
    });
}

if (searchClear) {
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      searchMessages('');
      searchInput.focus();
    });
}

/**
 * Show confirmation modal
 */
function showConfirmModal(messageId) {
  pendingDeleteId = messageId;
  confirmModal.classList.remove('hidden');
  modalConfirmBtn.focus();
}

function hideConfirmModal() {
  confirmModal.classList.add('hidden');
  pendingDeleteId = null;
}

modalCancelBtn.addEventListener('click', hideConfirmModal);
confirmModal.addEventListener('click', (e) => {
  if (e.target === confirmModal) hideConfirmModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !confirmModal.classList.contains('hidden')) {
    hideConfirmModal();
  }
});

modalConfirmBtn.addEventListener('click', async () => {
  if (!pendingDeleteId) return;
  const id = pendingDeleteId;
  hideConfirmModal();
  try {
    const res = await fetch('/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User': currentUser || 'anonymous'
      },
      body: JSON.stringify({ id })
    });
    
    const data = await res.json();
    if (res.ok) {
      const msgEl = document.querySelector(`[data-id="${id}"]`);
      if (msgEl) {
        msgEl.querySelector('.message-content').textContent = '[deleted]';
        msgEl.classList.add('deleted');
        const actions = msgEl.querySelector('.message-actions');
        if(actions) actions.style.display = 'none';
      }
      showToast('Message deleted', 'success');
      updateUnreadCount();
    } else {
      showToast(data.error || 'Failed to delete message', 'error');
    }
  } catch (err) {
    console.error('Delete error:', err);
    showToast('Network error', 'error');
  }
});

/**
 * Generate deterministic color class from username
 */
function getUserColorClass(username) {
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  return `user-color-${Math.abs(hash) % 8}`;
}

function getInitials(username) {
  return username.slice(0, 2).toUpperCase();
}

/**
 * Start inline editing
 */
function startEdit(article, currentContent) {
  article.classList.add('editing');
  const input = article.querySelector('.edit-input');
  if(input) {
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
        'X-User': currentUser || 'anonymous'
      },
      body: JSON.stringify({ id, content: newContent })
    });
    const data = await res.json();
    if (res.ok) {
      article.querySelector('.message-content').textContent = newContent;
      article.querySelector('.message-edited').hidden = false;
      cancelEdit(article);
      showToast('Message edited', 'success');
    } else {
      showToast(data.error || 'Failed to edit message', 'error');
    }
  } catch (err) {
    showToast('Network error', 'error');
  }
}

/**
 * Create a message element from template
 */
function createMessageElement(msg) {
  const template = messageTemplate.content.cloneNode(true);
  const article = template.querySelector('.message');
  
  article.dataset.id = msg.id;
  const timestamp = msg.created_at || Date.now();
  article.dataset.timestamp = timestamp;
  
  // UX GOD: Scribble Mode (Random Rotation)
  // Only rotate if not "own" message to keep input clean? No, let's rot all for fun.
  const rotation = Math.floor(Math.random() * 5); // 0 to 4
  if (rotation > 0) {
      article.classList.add(`scribble-${rotation}`);
  }
  
  // UX GOD: Organic Margins
  const margin = Math.floor(Math.random() * 4) + 1; // 1-4
  article.classList.add(`margin-${margin}`);
  
  // Avatar
  const avatar = article.querySelector('.message-avatar');
  avatar.textContent = getInitials(msg.user);
  avatar.classList.add(getUserColorClass(msg.user));
  
  // User name
  article.querySelector('.message-user').textContent = msg.user;
  article.querySelector('.message-time').textContent = formatRelativeTime(new Date(timestamp));
  
  // Content
  const content = article.querySelector('.message-content');
  if (msg.deleted) {
    content.textContent = '[deleted]';
    article.classList.add('deleted');
  } else {
    content.textContent = msg.content;
  }
  
  if (msg.edited) {
    article.querySelector('.message-edited').hidden = false;
  }
  
  // Own message styling
  const effectiveUser = currentUser.trim();
  if (effectiveUser && msg.user === effectiveUser) {
    article.classList.add('own');
    if (article.querySelector('.btn-edit')) {
        article.querySelector('.btn-edit').addEventListener('click', () => {
          startEdit(article, content.textContent);
        });
        article.querySelector('.btn-delete').addEventListener('click', () => {
          showConfirmModal(msg.id);
        });
        article.querySelector('.btn-save')?.addEventListener('click', () => {
          saveEdit(article, msg.id);
        });
        article.querySelector('.btn-cancel')?.addEventListener('click', () => {
          cancelEdit(article);
        });
        article.querySelector('.edit-input')?.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            saveEdit(article, msg.id);
          } else if (e.key === 'Escape') {
            cancelEdit(article);
          }
        });
    }
  } else {
    const actions = article.querySelector('.message-actions');
    if(actions) actions.classList.add('!hidden');
  }
  
  return article;
}

/**
 * Add a message to the UI
 */
function addMessage(msg) {
  if (messageIds.has(msg.id)) return;
  messageIds.add(msg.id);
  
  updateEmptyState();
  const element = createMessageElement(msg);
  const contentEl = element.querySelector('.message-content');
  const rawContent = msg.content || '';
  
  // 1. Script Card (script:ID) - NEW
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
          </div>
      `;
      contentEl.querySelector('.script-preview').addEventListener('click', (e) => {
           loadAndRunScript(e.currentTarget, scriptId);
      });
  } 
  // 2. Image handling
  else if (rawContent.startsWith('img:') || rawContent.match(/\.(jpeg|jpg|gif|png|webp)$/i)) {
      const src = rawContent.startsWith('img:') ? rawContent.substring(4) : rawContent;
      contentEl.innerHTML = `<img src="${src}" alt="Uploaded image" class="max-w-full h-auto rounded-lg border border-slate-700 mt-2 hover:shadow-lg transition" loading="lazy" />`;
  } 
  // 3. Code blocks
  else if (rawContent.includes('```')) {
      const formatted = rawContent.replace(/```([\s\S]*?)```/g, '<pre class="bg-black/50 p-2 rounded text-xs font-mono overflow-x-auto my-2 border border-white/5">$1</pre>');
      contentEl.innerHTML = formatted;
  }
  // 4. Inline code
  else if (rawContent.includes('`')) {
      const formatted = rawContent.replace(/`([^`]+)`/g, '<code class="bg-black/30 px-1 py-0.5 rounded text-xs font-mono text-green-300">$1</code>');
      contentEl.innerHTML = formatted;
  }
  
  messagesContainer.appendChild(element);
  
  if (searchInput && searchInput.value.trim()) {
    searchMessages(searchInput.value);
  }
  
  const isNearBottom = messagesScroll.scrollHeight - messagesScroll.scrollTop - messagesScroll.clientHeight < 100;
  if (isNearBottom) {
    scrollToBottom();
  }
  updateScrollButton();
  updateUnreadCount();
}

function setConnectionStatus(status) {
  if(statusDot) {
      statusDot.className = 'status-dot ' + status;
      if(statusText) {
          const labels = {connected:'Connected', disconnected:'Offline', reconnecting:'...'};
          statusText.textContent = labels[status] || status;
          statusText.hidden = (status === 'connected');
      }
  }
}

socket.on('connect', () => setConnectionStatus('connected'));
socket.on('connected', () => socket.emit('request_backfill', { after_id: 0 }));
socket.on('disconnect', () => { setConnectionStatus('disconnected'); showToast('Offline', 'warning'); });
socket.on('reconnect', () => { setConnectionStatus('connected'); showToast('Back online', 'success'); });
socket.on('reconnecting', () => setConnectionStatus('reconnecting'));
socket.on('message', msg => addMessage(msg));
socket.on('backfill', payload => {
  payload.messages.forEach(msg => addMessage(msg));
  updateEmptyState();
  updateScrollButton();
  updateUnreadCount();
});

function updateTypingUI() {
  if (typingUsersList.size === 0) {
    typingIndicator.classList.add('hidden');
    return;
  }
  typingIndicator.classList.remove('hidden');
  const users = Array.from(typingUsersList);
  typingUsers.textContent = users.length === 1 ? `${users[0]} is typing...` : `${users.length} users typing...`;
}

socket.on('typing', ({ user }) => {
  if (user !== currentUser && user) {
    typingUsersList.add(user);
    updateTypingUI();
  }
});
socket.on('stop_typing', ({ user }) => {
  typingUsersList.delete(user);
  updateTypingUI();
});

messageForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const content = messageInput.value.trim();
  if (!content || isLoading) return;
  setLoading(true);
  const user = currentUser || 'anonymous';
  try {
    socket.emit('send_message', { user, content });
    messageInput.value = '';
  } catch (err) {
    showToast('Failed to send', 'error');
  } finally {
    setLoading(false);
    messageInput.focus();
  }
});

  setConnectionStatus('connecting');
  updateEmptyState();

  if (currentRoom) {
      const roomHeader = document.getElementById('current-room-name');
      if (roomHeader) roomHeader.textContent = currentRoom;
  }

  document.querySelectorAll('.room-link').forEach(link => {
    link.addEventListener('click', () => {
      currentRoom = link.dataset.room;
      localStorage.setItem('neospace_last_room', currentRoom);
    });
  });

  if (emojiBtn && emojiPickerContainer && emojiPicker) {
    emojiBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      emojiPickerContainer.classList.toggle('hidden');
    });
    emojiPicker.addEventListener('emoji-click', (event) => {
      insertAtCursor(messageInput, event.detail.unicode);
      emojiPickerContainer.classList.add('hidden');
    });
    document.addEventListener('click', (e) => {
      if (!emojiPickerContainer.contains(e.target) && e.target !== emojiBtn && !emojiBtn.contains(e.target)) {
        emojiPickerContainer.classList.add('hidden');
      }
    });
    emojiPickerContainer.addEventListener('click', (e) => e.stopPropagation());
  }

  // File Upload
  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleUpload(fileInput.files[0]);
            fileInput.value = '';
        }
    });
  }

  const dropZone = document.body;
  if(dragOverlay) {
      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
      });
      function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
      dropZone.addEventListener('dragenter', () => dragOverlay.classList.remove('hidden'));
      dragOverlay.addEventListener('dragleave', (e) => {
          if (e.clientX <= 0 || e.clientY <= 0 || e.clientX >= window.innerWidth || e.clientY >= window.innerHeight) {
             dragOverlay.classList.add('hidden');
          }
      });
      dropZone.addEventListener('drop', (e) => {
        dragOverlay.classList.add('hidden');
        if (e.dataTransfer.files.length > 0) handleUpload(e.dataTransfer.files[0]);
      });
  }

  async function handleUpload(file) {
      if (!file.type.startsWith('image/')) {
          showToast('Only images supported', 'warning');
          return;
      }
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      try {
          const res = await fetch('/upload', {
              method: 'POST',
              body: formData,
              headers: { 'X-User': currentUser || 'anonymous' }
          });
          const data = await res.json();
          if (res.ok) {
              socket.emit('send_message', { user: currentUser || 'anonymous', content: `img:${data.url}` });
          } else {
              showToast(data.error || 'Upload failed', 'error');
          }
      } catch (err) {
          showToast('Upload error', 'error');
      } finally {
          setLoading(false);
      }
  }

}); // End DOMContentLoaded

function insertAtCursor(input, text) {
  const start = input.selectionStart;
  const end = input.selectionEnd;
  const value = input.value;
  input.value = value.substring(0, start) + text + value.substring(end);
  input.selectionStart = input.selectionEnd = start + text.length;
  input.focus();
}

/**
 * Fetch and run script in chat
 */
async function loadAndRunScript(container, id) {
    container.innerHTML = '<div class="absolute inset-0 flex items-center justify-center bg-black/80"><i class="ph ph-spinner animate-spin text-white text-2xl"></i></div>';
    try {
        const res = await fetch(`/scripts/get?id=${id}`);
        const data = await res.json();
        if(data.ok) {
            const s = data.script;
            const iframe = document.createElement('iframe');
            iframe.className = "w-full h-full border-none bg-white rounded";
            iframe.sandbox = "allow-scripts allow-forms allow-pointer-lock allow-same-origin";
            
            let html = '';
            // Simplified runner templates (similar to playground)
            if(s.script_type === 'p5') {
                 html = `<!DOCTYPE html><html><head><style>body{margin:0;overflow:hidden}</style><script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"><\/script></head><body><script>try{${s.content}}catch(e){document.body.innerHTML='<pre style="color:red">'+e+'</pre>'}<\/script></body></html>`;
            } else if(s.script_type === 'three') {
                 html = `<!DOCTYPE html><html><head><style>body{margin:0;overflow:hidden}</style></head><body><script type="module">try{${s.content}}catch(e){document.body.innerHTML='<pre style="color:red">'+e+'</pre>'}<\/script></body></html>`;
            } else {
                 html = `<!DOCTYPE html><html><body><script>${s.content}<\/script></body></html>`;
            }
            
            iframe.srcdoc = html;
            container.innerHTML = ''; // basic reset
            container.appendChild(iframe);
            // Re-add label overlay? No, let script take over.
        } else {
            container.innerHTML = '<div class="absolute inset-0 flex items-center justify-center bg-red-900/80 text-white text-xs">Error loading script</div>';
        }
    } catch(e) {
        container.innerHTML = '<div class="absolute inset-0 flex items-center justify-center bg-red-900/80 text-white text-xs">Network error</div>';
    }
}
