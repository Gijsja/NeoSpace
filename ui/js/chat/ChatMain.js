/**
 * ChatMain.js
 * Entry point for Chat UI.
 */
import * as Socket from './ChatSocket.js';
import * as UI from './ChatUI.js';
import * as Input from './ChatInput.js';
import { state, cleanupChat } from './ChatState.js';

// Init
function init() {
    // 1. Cleanup previous instance
    if (window.CurrentChatCleanup) {
        window.CurrentChatCleanup();
    }
    
    // 2. Setup UI
    UI.setConnectionStatus('connecting');
    UI.updateEmptyState();
    UI.updateUnreadCount();
    UI.setupConfirmModal();
    
    // 3. Setup Socket with callbacks
    Socket.initSocket({
        onConnect: () => UI.setConnectionStatus('connected'),
        onDisconnect: () => {
             UI.setConnectionStatus('disconnected');
             UI.showToast('Offline', 'warning');
        },
        onReconnect: () => UI.setConnectionStatus('connected'),
        onMessage: (msg) => {
            console.log('[ChatMain] Msg received', msg);
            UI.addMessage(msg);
        },
        onBackfill: (payload) => {
            console.log('[ChatMain] Backfill received', payload.messages.length);
            payload.messages.forEach(msg => UI.addMessage(msg));
            UI.updateEmptyState();
            UI.updateScrollButton();
            UI.updateUnreadCount();
        },
        onTyping: ({ user }) => {
            if (user !== state.currentUser && user) {
                state.typingUsersList.add(user);
                UI.updateTypingUI();
            }
        },
        onStopTyping: ({ user }) => {
            state.typingUsersList.delete(user);
            UI.updateTypingUI();
        }
    });
    
    // 4. Setup Input
    console.log('[ChatMain] Setting up Input...');
    Input.setupChatInput();
    
    // 5. Update Loops
    setInterval(UI.updateAllTimestamps, 60000);
    setInterval(UI.updateUnreadCount, 30000);
    
    // 6. Global listeners
    const messagesScroll = document.getElementById('messages-scroll');
    if (messagesScroll) {
        messagesScroll.addEventListener('scroll', UI.updateScrollButton);
    }
    const scrollBottomBtn = document.getElementById('scroll-bottom');
    if (scrollBottomBtn) {
        scrollBottomBtn.addEventListener('click', UI.scrollToBottom);
    }
    
    // 7. Room Header
    console.log('[ChatMain] Setting Room Header for:', state.currentRoom);
    if (state.currentRoom) {
      const roomHeader = document.getElementById('current-room-name');
      if (roomHeader) {
          roomHeader.textContent = '# ' + state.currentRoom;
          console.log('[ChatMain] Room header updated');
      } else {
          console.warn('[ChatMain] Room header element not found');
      }
    }
    
    // 8. Room Links
    document.querySelectorAll('.room-link').forEach(link => {
       link.addEventListener('click', () => {
         localStorage.setItem('neospace_last_room', link.dataset.room);
       });
    });

    // Register Cleanup
    window.CurrentChatCleanup = cleanupChat;

    console.log('[ChatMain] Initialization complete.');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
