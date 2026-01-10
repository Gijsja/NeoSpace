/**
 * Sprint 19: Search UI
 * Handles client-side search against /search API
 */

const SearchUI = {
    state: {
        query: '',
        type: 'users', // 'users' or 'posts'
        results: []
    },

    init() {
        const input = document.querySelector('input[name="search"]');
        const resultsContainer = document.getElementById('search-results');
        const typeToggles = document.querySelectorAll('.search-type-toggle');

        if (!input || !resultsContainer) return;

        // Debounced Input
        let timeout;
        input.addEventListener('input', (e) => {
            this.state.query = e.target.value.trim();
            clearTimeout(timeout);
            timeout = setTimeout(() => this.performSearch(), 300);
        });

        // Type Toggles
        typeToggles.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                typeToggles.forEach(b => b.classList.remove('bg-black', 'text-white'));
                typeToggles.forEach(b => b.classList.add('bg-white', 'text-black'));

                btn.classList.remove('bg-white', 'text-black');
                btn.classList.add('bg-black', 'text-white');

                this.state.type = btn.dataset.type;
                this.performSearch();
            });
        });

        // Check URL params for initial search OR load directory
        const urlParams = new URLSearchParams(window.location.search);
        const initialQ = urlParams.get('q');

        if (initialQ) {
            input.value = initialQ;
            this.state.query = initialQ;
            this.performSearch();
        } else {
            // New: Load generic directory listing
            this.loadDirectory();
        }
    },

    async loadDirectory() {
        const container = document.getElementById('search-results');

        // Loading State
        // Skeleton Loading State
        container.innerHTML = Array(8).fill(0).map(() => `
                <div class="nb-card p-4 flex flex-col items-center gap-3 animate-pulse">
                    <div class="w-20 h-20 rounded-full bg-gray-200 border-2 border-gray-300"></div>
                    <div class="h-4 w-32 bg-gray-200 rounded"></div>
                    <div class="h-3 w-20 bg-gray-200 rounded"></div>
                    <div class="h-8 w-full bg-gray-200 rounded mt-2"></div>
                </div>
            `).join('');

        try {
            // Hit the Directory API instead of Search API
            const res = await fetch('/users/');
            const data = await res.json();

            if (data.users) {
                // Determine if we need to adapt structure?
                // Search expects: id, username, display_name, avatar_path, is_following
                // Directory returns: id, username, display_name, avatar_path, is_following (now added)
                // So we can feed it directly
                this.renderResults(data.users);
            }
        } catch (e) {
            console.error(e);
            container.innerHTML = `<p class="text-red-500">Failed to load directory.</p>`;
        }
    },

    async performSearch() {
        const container = document.getElementById('search-results');

        if (this.state.query.length < 1) {
            container.innerHTML = `
                <div class="col-span-full text-center p-8 opacity-50">
                    <i class="ph-bold ph-magnifying-glass text-4xl mb-2"></i>
                    <p>Start typing to search...</p>
                </div>
            `;
            return;
        }

        // Loading State
        container.innerHTML = `
            <div class="col-span-full text-center p-8">
                <i class="ph-bold ph-spinner animate-spin text-4xl mb-2"></i>
                <p>SEARCHING...</p>
            </div>
        `;

        try {
            const res = await fetch(`/search/?q=${encodeURIComponent(this.state.query)}&type=${this.state.type}`);
            const data = await res.json();

            if (data.ok) {
                this.renderResults(data.results);
            } else {
                container.innerHTML = `<p class="text-red-500">Error: ${data.error}</p>`;
            }
        } catch (e) {
            console.error(e);
            container.innerHTML = `<p class="text-red-500">Search failed</p>`;
        }
    },

    renderResults(results) {
        const container = document.getElementById('search-results');

        if (results.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center p-8 opacity-50">
                    <p>NO MATCHES FOUND</p>
                </div>
            `;
            return;
        }

        if (this.state.type === 'users') {
            container.innerHTML = results.map(user => `
                <div class="nb-card p-4 flex flex-col items-center text-center gap-3 group relative overflow-hidden">
                    <a href="/wall?user_id=${user.id}" class="block relative">
                        <img src="${user.avatar_path || '/static/img/default_avatar.png'}" 
                             class="w-20 h-20 rounded-full border-2 border-black object-cover group-hover:scale-105 transition-transform bg-gray-100">
                    </a>
                    <div class="min-w-0 w-full px-2">
                        <a href="/wall?user_id=${user.id}" class="font-bold text-lg hover:underline truncate block">
                            ${user.display_name || user.username}
                        </a>
                        <p class="text-sm text-gray-500 font-mono truncate">@${user.username}</p>
                    </div>
                    
                    <!-- Follow Button -->
                    <button class="w-full h-8 border-2 border-black font-bold text-sm uppercase transition-all active:translate-y-1 active:shadow-none shadow-hard-sm flex items-center justify-center gap-2 ${user.is_following ? 'bg-white text-black hover:bg-gray-100' : 'bg-black text-white hover:bg-gray-800'}" 
                            data-user-id="${user.id}"
                            data-status="${user.is_following ? 'following' : 'not_following'}"
                            onclick="FriendManager.toggleFollow(this)">
                        ${user.is_following ? '<i class="ph-bold ph-check"></i> FOLLOWING' : '<i class="ph-bold ph-plus"></i> FOLLOW'}
                    </button>
                </div>
            `).join('');
        } else {
            // Posts
            container.innerHTML = results.map(post => `
                <div class="nb-card p-4">
                    <div class="flex items-center gap-3 mb-3">
                        <img src="${post.author_avatar}" class="w-8 h-8 rounded-full border border-black">
                        <div>
                            <span class="font-bold text-sm">${post.author_name}</span>
                            <span class="text-xs text-gray-500 ml-1">@${post.author_username}</span>
                        </div>
                    </div>
                    <div class="prose prose-sm mb-3">
                        ${post.content.text || '(No text)'}
                    </div>
                    <div class="text-xs text-gray-400">
                        ${new Date(post.created_at).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    SearchUI.init();
});
