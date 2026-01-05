/**
 * LocalBBS Socket Client
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
const usernameInput = document.getElementById('username');
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

// State
let currentUser = localStorage.getItem('localbbs_username') || '';
let currentRoom = localStorage.getItem('localbbs_last_room') || '# general';
let messageIds = new Set();
let isLoading = false;
let pendingDeleteId = null;
let allMessages = []; // Store messages for search
let typingTimeout = null;
let isTyping = false;
let typingUsersList = new Set();

// Initialize username from localStorage
usernameInput.value = currentUser;

// Username persistence
usernameInput.addEventListener('change', () => {
  currentUser = usernameInput.value.trim() || 'anonymous';
  localStorage.setItem('localbbs_username', currentUser);
});

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
    const timestamp = parseInt(msg.dataset.timestamp, 10);
    const timeEl = msg.querySelector('.message-time');
    if (timeEl && timestamp) {
      timeEl.textContent = formatRelativeTime(new Date(timestamp));
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
  sendBtn.textContent = loading ? 'Sending...' : 'Send';
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
        <div class="empty-state-text">No messages yet. Start the conversation!</div>
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
  scrollBottomBtn.classList.toggle('visible', distanceFromBottom > 200);
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
  messagesScroll.scrollTop = messagesScroll.scrollHeight;
}

// Scroll button click handler
scrollBottomBtn.addEventListener('click', scrollToBottom);

// Monitor scroll position
messagesScroll.addEventListener('scroll', updateScrollButton);

/**
 * Fetch and update unread count
 */
async function updateUnreadCount() {
  try {
    const res = await fetch('/unread');
    const data = await res.json();
    if (data.count > 0) {
      unreadBadge.textContent = data.count > 99 ? '99+' : data.count;
      unreadBadge.hidden = false;
    } else {
      unreadBadge.hidden = true;
    }
  } catch (err) {
    console.error('Failed to fetch unread count:', err);
  }
}

// Update unread count on load and periodically
updateUnreadCount();
setInterval(updateUnreadCount, 30000);

/**
 * Search messages
 */
function searchMessages(query) {
  const q = query.toLowerCase().trim();
  searchClear.hidden = !q;
  
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

// Search input handler with debounce
let searchTimeout;
searchInput.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchMessages(searchInput.value);
  }, 200);
});

// Clear search button
searchClear.addEventListener('click', () => {
  searchInput.value = '';
  searchMessages('');
  searchInput.focus();
});

// Escape to clear search
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    searchInput.value = '';
    searchMessages('');
  }
});

/**
 * Show confirmation modal
 */
function showConfirmModal(messageId) {
  pendingDeleteId = messageId;
  confirmModal.classList.remove('hidden');
  modalConfirmBtn.focus();
}

/**
 * Hide confirmation modal
 */
function hideConfirmModal() {
  confirmModal.classList.add('hidden');
  pendingDeleteId = null;
}

// Modal event handlers
modalCancelBtn.addEventListener('click', hideConfirmModal);
confirmModal.addEventListener('click', (e) => {
  if (e.target === confirmModal) hideConfirmModal();
});

// Escape key to close modal
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
        msgEl.querySelector('.message-actions').style.display = 'none';
      }
      showToast('Message deleted', 'success');
      updateUnreadCount();
    } else {
      showToast(data.error || 'Failed to delete message', 'error');
    }
  } catch (err) {
    console.error('Delete error:', err);
    showToast('Network error. Please try again.', 'error');
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

/**
 * Get initials from username
 */
function getInitials(username) {
  return username.slice(0, 2).toUpperCase();
}

/**
 * Start inline editing
 */
function startEdit(article, currentContent) {
  article.classList.add('editing');
  const input = article.querySelector('.edit-input');
  input.value = currentContent;
  input.focus();
  input.select();
}

/**
 * Cancel inline editing
 */
function cancelEdit(article) {
  article.classList.remove('editing');
}

/**
 * Save inline edit
 */
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
    console.error('Edit error:', err);
    showToast('Network error. Please try again.', 'error');
  }
}

/**
 * Create a message element from template
 */
function createMessageElement(msg) {
  const template = messageTemplate.content.cloneNode(true);
  const article = template.querySelector('.message');
  
  article.dataset.id = msg.id;
  
  // Add timestamp for relative time updates
  const timestamp = Date.now();
  article.dataset.timestamp = timestamp;
  
  // Avatar
  const avatar = article.querySelector('.message-avatar');
  avatar.textContent = getInitials(msg.user);
  avatar.classList.add(getUserColorClass(msg.user));
  
  // User name
  article.querySelector('.message-user').textContent = msg.user;
  
  // Timestamp
  article.querySelector('.message-time').textContent = formatRelativeTime(new Date(timestamp));
  
  // Content
  const content = article.querySelector('.message-content');
  if (msg.deleted) {
    content.textContent = '[deleted]';
    article.classList.add('deleted');
  } else {
    content.textContent = msg.content;
  }
  
  // Edited indicator
  if (msg.edited) {
    article.querySelector('.message-edited').hidden = false;
  }
  
  // Own message styling
  const effectiveUser = currentUser.trim();
  if (effectiveUser && msg.user === effectiveUser) {
    article.classList.add('own');
    
    // Edit button - start inline edit
    article.querySelector('.btn-edit').addEventListener('click', () => {
      startEdit(article, content.textContent);
    });
    
    // Delete button - show modal
    article.querySelector('.btn-delete').addEventListener('click', () => {
      showConfirmModal(msg.id);
    });
    
    // Inline editor save button
    article.querySelector('.btn-save').addEventListener('click', () => {
      saveEdit(article, msg.id);
    });
    
    // Inline editor cancel button
    article.querySelector('.btn-cancel').addEventListener('click', () => {
      cancelEdit(article);
    });
    
    // Enter to save, Escape to cancel
    article.querySelector('.edit-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        saveEdit(article, msg.id);
      } else if (e.key === 'Escape') {
        cancelEdit(article);
      }
    });
  } else {
    // Hide actions for messages from other users
    article.querySelector('.message-actions').classList.add('!hidden');
  }
  
  return article;
}

/**
 * Add a message to the UI
 */
function addMessage(msg) {
  if (messageIds.has(msg.id)) return;
  messageIds.add(msg.id);
  allMessages.push(msg);
  
  updateEmptyState();
  
  const element = createMessageElement(msg);
  messagesContainer.appendChild(element);
  
  // Apply current search filter
  if (searchInput.value.trim()) {
    searchMessages(searchInput.value);
  }
  
  // Auto-scroll if near bottom
  const isNearBottom = messagesScroll.scrollHeight - messagesScroll.scrollTop - messagesScroll.clientHeight < 100;
  if (isNearBottom) {
    scrollToBottom();
  }
  
  updateScrollButton();
  updateUnreadCount();
}

/**
 * Update connection status indicator
 */
function setConnectionStatus(status) {
  statusDot.className = 'status-dot ' + status;
  const labels = {
    connected: 'Connected',
    disconnected: 'Disconnected',
    reconnecting: 'Reconnecting...'
  };
  statusText.textContent = labels[status] || status;
}

// Socket event handlers
socket.on('connect', () => {
  setConnectionStatus('connected');
});

socket.on('connected', () => {
  socket.emit('request_backfill', { after_id: 0 });
});

socket.on('disconnect', () => {
  setConnectionStatus('disconnected');
  showToast('Connection lost', 'warning');
});

socket.on('reconnect', () => {
  setConnectionStatus('connected');
  showToast('Reconnected', 'success');
});

socket.on('reconnecting', () => {
  setConnectionStatus('reconnecting');
});

socket.on('message', msg => {
  addMessage(msg);
});

socket.on('backfill', payload => {
  payload.messages.forEach(msg => addMessage(msg));
  updateEmptyState();
  updateScrollButton();
  updateUnreadCount();
});

// Typing indicator event handlers
function updateTypingUI() {
  if (typingUsersList.size === 0) {
    typingIndicator.classList.add('hidden');
    return;
  }
  
  typingIndicator.classList.remove('hidden');
  const users = Array.from(typingUsersList);
  if (users.length === 1) {
    typingUsers.textContent = `${users[0]} is typing...`;
  } else if (users.length === 2) {
    typingUsers.textContent = `${users[0]} and ${users[1]} are typing...`;
  } else {
    typingUsers.textContent = `${users.length} people are typing...`;
  }
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

// Form submission
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
    showToast('Failed to send message', 'error');
  } finally {
    setLoading(false);
    messageInput.focus();
  }
});

  // Initialize
  setConnectionStatus('connecting');
  updateEmptyState();

  // Restore last room
  if (currentRoom) {
    document.getElementById('current-room-name').textContent = currentRoom;
    document.querySelectorAll('.room-link').forEach(l => {
      if (l.dataset.room === currentRoom) {
        l.classList.add('bg-bbs-accent/20', 'text-bbs-accent');
        l.classList.remove('text-slate-400');
      } else {
        l.classList.remove('bg-bbs-accent/20', 'text-bbs-accent');
        l.classList.add('text-slate-400');
      }
    });
  }

  // Persist room selection
  document.querySelectorAll('.room-link').forEach(link => {
    link.addEventListener('click', () => {
      currentRoom = link.dataset.room;
      localStorage.setItem('localbbs_last_room', currentRoom);
    });
  });

  // Emoji Picker Logic
  if (emojiBtn && emojiPickerContainer && emojiPicker) {
    // Toggle picker
    emojiBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      emojiPickerContainer.classList.toggle('hidden');
    });

    // Handle emoji selection
    emojiPicker.addEventListener('emoji-click', (event) => {
      const emoji = event.detail.unicode;
      insertAtCursor(messageInput, emoji);
      emojiPickerContainer.classList.add('hidden');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!emojiPickerContainer.contains(e.target) && e.target !== emojiBtn && !emojiBtn.contains(e.target)) {
        emojiPickerContainer.classList.add('hidden');
      }
    });

    // Stop closing when clicking inside picker
    emojiPickerContainer.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }
}); // End DOMContentLoaded

/**
 * Insert text at cursor position
 */
function insertAtCursor(input, text) {
  const start = input.selectionStart;
  const end = input.selectionEnd;
  const value = input.value;
  input.value = value.substring(0, start) + text + value.substring(end);
  input.selectionStart = input.selectionEnd = start + text.length;
  input.focus();
}
