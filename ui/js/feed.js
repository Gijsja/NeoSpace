/**
 * Sprint 21: Feed UI
 * Handles persistent feed loading, rendering, and infinite scroll.
 */

const FeedManager = {
    state: {
        posts: [],
        loading: false,
        ended: false,
        limit: 10,
        lastPostId: null
    },

    init() {
        this.container = document.getElementById('feed-container');
        this.observerTarget = document.getElementById('load-more-trigger');
        
        if (!this.container) return;
        
        // Initial Load
        this.loadPosts();
        
        // Infinite Scroll
        this.setupObserver();
    },

    async loadPosts() {
        if (this.state.loading || this.state.ended) return;
        this.state.loading = true;
        
        this.showLoader(true);
        
        try {
            let url = `/feed/?limit=${this.state.limit}`;
            if (this.state.lastPostId) {
                url += `&before_id=${this.state.lastPostId}`;
            }
            
            const res = await fetch(url);
            const data = await res.json();
            
            if (data.ok) {
                if (data.posts.length < this.state.limit) {
                    this.state.ended = true;
                    this.showEndMessage();
                }
                
                if (data.posts.length > 0) {
                    this.renderPosts(data.posts);
                    this.state.lastPostId = data.posts[data.posts.length - 1].id;
                } else if (this.state.posts.length === 0) {
                     this.showEmptyState();
                }
            }
        } catch (e) {
            console.error(e);
            this.container.innerHTML += `<div class="text-red-500 text-center p-4">Failed to load feed.</div>`;
        } finally {
            this.state.loading = false;
            this.showLoader(false);
        }
    },

    renderPosts(posts) {
        // Reuse similar logic to Wall but with Author Header
        const html = posts.map(post => this.createPostHTML(post)).join('');
        
        // Append before the loader/trigger
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        this.container.appendChild(wrapper);
        
        // Initialize interactive elements (like audio players) if needed
        // For now, simpler than Wall (no edit specific logic yet)
    },
    
    createPostHTML(post) {
        // Safe defaults
        const author = post.author_name || "Unknown";
        const username = post.author_username || "anon";
        const avatar = post.author_avatar || "/static/img/default_avatar.png";
        const time = new Date(post.created_at).toLocaleDateString();
        
        let contentHTML = "";
        
        // -- Render Logic based on Module Type --
        if (post.module_type === 'text') {
            // Basic text rendering, maybe reuse Markdown helper if available
            // For feed, plain text or simple markdown is good
            // Use window.marked if available, else textContent
            let text = post.content.text || "";
            if (typeof marked !== 'undefined') text = marked.parse(text);
            contentHTML = `<div class="prose prose-sm prose-invert max-w-none text-slate-300 break-words">${text}</div>`;
            
        } else if (post.module_type === 'image') {
            contentHTML = `<img src="${post.content.url}" class="w-full h-auto rounded border border-white/10" loading="lazy">`;
            
        } else if (post.module_type === 'link') {
            contentHTML = `
                <a href="${post.content.url}" target="_blank" class="block p-4 bg-slate-800 rounded border border-white/10 hover:bg-slate-700 transition">
                    <div class="flex items-center gap-3">
                        <i class="ph-bold ph-link text-slate-400"></i>
                        <div class="min-w-0">
                             <div class="font-bold text-sky-400 truncate">${post.content.title || post.content.url}</div>
                             <div class="text-xs text-slate-500 truncate">${post.content.url}</div>
                        </div>
                    </div>
                </a>
            `;
        } else if (post.module_type === 'audio') {
            contentHTML = `
                <div class="p-3 bg-slate-800 rounded border border-white/10">
                    <div class="flex items-center gap-3 mb-2">
                         <div class="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center text-purple-400">
                            <i class="ph-fill ph-music-notes"></i>
                         </div>
                         <div class="text-sm font-bold text-slate-200">${post.content.title || "Audio Track"}</div>
                    </div>
                    <audio controls src="${post.content.url}" class="w-full h-8"></audio>
                </div>
            `;
        } else if (post.module_type === 'script') {
             // Simplified script card for feed
             contentHTML = `
                <div class="aspect-video bg-black rounded border border-white/10 flex items-center justify-center relative group overflow-hidden">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-4">
                        <div class="font-mono text-xs text-acid-green mb-1">SCRIPT</div>
                        <div class="font-bold text-white">${post.script_details?.title || "Untitled Script"}</div>
                    </div>
                    <a href="/wall?user_id=${post.user_id}" class="absolute inset-0 z-10"></a>
                    <i class="ph-fill ph-code text-4xl text-slate-700 group-hover:text-white transition"></i>
                </div>
             `;
        }

        return `
            <div class="nb-card p-0 mb-6 overflow-hidden animate-fade-in relative group">
                 <!-- Author Header -->
                 <div class="flex items-center gap-3 p-4 border-b border-black/10 bg-slate-50 dark:bg-slate-900/50">
                    <a href="/wall?user_id=${post.user_id}" class="shrink-0">
                        <img src="${avatar}" class="w-10 h-10 rounded-full border border-black/20 object-cover">
                    </a>
                    <div class="min-w-0 flex-1">
                        <a href="/wall?user_id=${post.user_id}" class="block font-bold text-sm hover:underline truncate">
                            ${author}
                        </a>
                        <div class="text-xs text-slate-500">@${username} • ${time}</div>
                    </div>
                    <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition">
                         <a href="/wall?user_id=${post.user_id}" class="text-xs font-bold uppercase tracking-wider text-black border border-black px-2 py-1 bg-white hover:bg-black hover:text-white transition">
                            View Wall
                         </a>
                    </div>
                 </div>
                 
                 <!-- Content -->
                 <div class="p-4 bg-white dark:bg-slate-900">
                    ${contentHTML}
                 </div>
            </div>
        `;
    },

    setupObserver() {
        if (!this.observerTarget) return;
        
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && !this.state.loading) {
                this.loadPosts();
            }
        }, { rootMargin: '200px' });
        
        observer.observe(this.observerTarget);
    },
    
    showLoader(show) {
        const el = document.getElementById('feed-loader');
        if (el) el.classList.toggle('hidden', !show);
    },
    
    showEmptyState() {
        this.container.innerHTML = `
            <div class="text-center py-20 px-4">
                <i class="ph-bold ph-globe-hemisphere-west text-6xl mb-4 opacity-20"></i>
                <h2 class="text-xl font-black uppercase mb-2">Your Feed is Quiet</h2>
                <p class="text-slate-500 mb-6 max-w-md mx-auto">Follow more people to see their updates here.</p>
                <a href="/directory" class="nb-button inline-block bg-black text-white px-6 py-2">
                    Find People
                </a>
            </div>
        `;
    },
    
    showEndMessage() {
        if (document.getElementById('feed-end')) return;
        const el = document.createElement('div');
        el.id = "feed-end";
        el.className = "text-center py-10 opacity-50 font-mono text-sm uppercase tracking-widest";
        el.innerText = "End of Transmission";
        this.container.appendChild(el);
        
        // Hide trigger
        if (this.observerTarget) this.observerTarget.style.display = 'none';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    FeedManager.init();
});
