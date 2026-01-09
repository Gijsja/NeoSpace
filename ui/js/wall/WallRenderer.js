/**
 * WallRenderer.js
 * Renders the main profile sections (Header, Bio, Stickers, Top8).
 */

import { state, themes } from './WallState.js';
import { setupAnthem } from './WallAudio.js';
import { openEditModal } from './WallEdit.js';
import { renderWallModules, appendWallModules } from './WallModules.js';
import { fetchMorePosts } from './WallNetwork.js';

export function renderProfile(data) {
    document.title = `${data.display_name}'s Wall`;

    // Text fields
    setText('display-name', data.display_name);
    setText('username-handle', `@${data.username}`);
    setText('status-message', data.status_message || "Just setting up my space...");
    setText('status-emoji', data.status_emoji || "👋");
    setText('now-activity', data.now_activity || "Just chilling...");

    // Icon mapping
    const activityIcons = {
        'listening': 'ph-headphones',
        'working': 'ph-laptop',
        'playing': 'ph-game-controller',
        'reading': 'ph-book-open',
        'thinking': 'ph-brain',
        'watching': 'ph-monitor-play'
    };
    const iconClass = activityIcons[data.now_activity_type] || 'ph-star';
    const nowIconEl = document.getElementById('now-activity-type-icon');
    if (nowIconEl) nowIconEl.innerHTML = `<i class="ph-fill ${iconClass}"></i>`;

    const memberSinceEl = document.getElementById('member-since');
    if (memberSinceEl) memberSinceEl.textContent = new Date(data.member_since).toLocaleDateString(undefined, { year: 'numeric', month: 'short' });

    // Avatar
    const avatarEl = document.getElementById('avatar-container');
    const initialEl = document.getElementById('avatar-initial');
    if (avatarEl && initialEl) {
        if (data.avatar_path) {
            avatarEl.style.backgroundImage = `url('${data.avatar_path}')`;
            initialEl.classList.add('hidden');
        } else {
            avatarEl.style.backgroundImage = '';
            initialEl.classList.remove('hidden');
            initialEl.textContent = data.display_name.charAt(0).toUpperCase();
        }
    }

    // Voice Intro
    renderVoiceIntro(data);

    // Audio Anthem
    setupAnthem(data.anthem_url, data.anthem_autoplay);

    // Theme Application (Sprint 24: Hacker Terminal)
    applyTheme(data.theme_preset);
    document.documentElement.style.setProperty('--color-accent', data.accent_color);

    // Interaction
    if (data.is_own) {
        ['edit-avatar-btn', 'edit-profile-btn', 'edit-now-btn'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('hidden');
                el.onclick = openEditModal;
            }
        });
        const addModBtn = document.getElementById('add-module-btn');
        if (addModBtn) addModBtn.classList.remove('hidden');
    }

    if (data.show_online_status) {
        const onlineEl = document.getElementById('online-indicator');
        if (onlineEl) onlineEl.classList.remove('hidden');
    }

    renderWallModules(data.wall_modules);
    renderLoadMore(data);
    renderTop8(data.top8);
    renderFollowBtn(data);

    // Stickers
    if (state.stickerManager) state.stickerManager.setStickers(data.stickers);
}

function renderLoadMore(data) {
    const container = document.getElementById('wall-load-more-container');
    const btn = document.getElementById('btn-load-more');
    const loader = document.getElementById('loader-more');

    if (!container || !btn || !loader) return;

    // Pagination state is in data.wall_pagination { page, has_more }
    const pag = data.wall_pagination || { page: 1, has_more: false };

    if (pag.has_more) {
        container.classList.remove('hidden');
        btn.classList.remove('hidden');
        loader.classList.add('hidden');

        // Remove old listener to prevent duplicates (using onclick works for valid HTML elements, one handler)
        btn.onclick = async () => {
            btn.classList.add('hidden');
            loader.classList.remove('hidden');

            const nextPage = pag.page + 1;
            const res = await fetchMorePosts(data.user_id, nextPage);

            loader.classList.add('hidden');

            if (res && res.posts) {
                appendWallModules(res.posts);

                // Update local state
                pag.page = res.page;
                pag.has_more = res.has_more;

                if (res.has_more) {
                    btn.classList.remove('hidden');
                } else {
                    container.classList.add('hidden');
                }
            } else {
                // Error handled silently or retry
                btn.classList.remove('hidden');
                alert("Failed to load posts.");
            }
        };
    } else {
        container.classList.add('hidden');
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function renderVoiceIntro(data) {
    const voiceSection = document.getElementById('voice-intro-section');
    if (voiceSection) {
        if (data.voice_intro_path) {
            voiceSection.classList.remove('hidden');
            let waveform = [];
            try {
                waveform = JSON.parse(data.voice_waveform_json || '[]');
            } catch (e) { }

            if (typeof VoicePlayer !== 'undefined') {
                new VoicePlayer('voice-intro-section', data.voice_intro_path, waveform);
            }
        } else {
            voiceSection.classList.add('hidden');
            voiceSection.innerHTML = '';
        }
    }
}

function renderTop8(friends) {
    const section = document.getElementById('top8-section');
    const grid = document.getElementById('top8-grid');
    if (!section || !grid) return;

    if (!friends || friends.length === 0) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');
    grid.innerHTML = friends.map(f => `
        <a href="/wall?user_id=${f.id}" class="block group relative" title="${f.display_name}">
            <img src="${f.avatar_path || '/static/img/default_avatar.png'}" 
                 class="w-full aspect-square object-cover border-2 border-black group-hover:scale-105 transition-transform bg-white">
            <div class="absolute inset-x-0 bottom-0 bg-black text-white text-[10px] font-bold truncate px-1 opacity-0 group-hover:opacity-100 transition-opacity">
                ${f.username}
            </div>
        </a>
    `).join('');
}

function renderFollowBtn(data) {
    const followBtn = document.getElementById('follow-btn');
    if (followBtn) {
        if (!data.is_own && data.viewer_id) {
            followBtn.classList.remove('hidden');
            followBtn.dataset.userId = data.user_id;

            const isFollowing = data.viewer_is_following;
            followBtn.dataset.status = isFollowing ? 'following' : 'not_following';

            if (window.FriendManager) {
                window.FriendManager.updateButtonState(followBtn, isFollowing, false);
                followBtn.onclick = () => window.FriendManager.toggleFollow(followBtn);
            }
        } else {
            followBtn.classList.add('hidden');
        }
    }
}

export function setupPalette() {
    const palette = document.getElementById('sticker-palette');
    if (palette) palette.classList.remove('hidden');

    if (palette && window.STICKERS_PRESETS) {
        palette.innerHTML = '';
        window.STICKERS_PRESETS.forEach(char => {
            const el = document.createElement('div');
            el.className = 'text-3xl hover:scale-125 transition cursor-grab active:cursor-grabbing p-2 shrink-0';
            el.innerText = char;
            el.draggable = true;
            el.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    type: 'new',
                    sticker: char,
                    offsetX: 20,
                    offsetY: 20
                }));
            });
            palette.appendChild(el);
        });
    }
}

// Theme Logic
function applyTheme(preset) {
    const container = document.getElementById('wall-container');
    const hackerLink = document.getElementById('theme-hacker-css');

    // Reset state
    if (container) {
        container.classList.remove('theme-hacker');
        container.style.background = ''; // Clear inline styles
    }
    if (hackerLink) hackerLink.setAttribute('disabled', 'true');

    // Apply specific theme
    if (preset === 'hacker') {
        if (container) container.classList.add('theme-hacker');
        if (hackerLink) hackerLink.removeAttribute('disabled');
    } else if (themes[preset]) {
        // Legacy/Simple background gradients from WallState.js
        if (container) container.style.background = themes[preset];
    }
}
