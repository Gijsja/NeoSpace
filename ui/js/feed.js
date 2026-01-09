/**
 * Sprint 21: Feed UI
 * Handles persistent feed loading, rendering, and infinite scroll.
 */

if (!window.FeedManager) {
    window.FeedManager = {
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

            // Clean up previous state if needed or reset
            this.state.loading = false;
            this.state.ended = false;
            this.state.posts = [];
            this.state.lastPostId = null;
            this.container.innerHTML = ''; // Start fresh

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
                        this.state.posts.push(...data.posts);
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
                // SCRIPT MODULE - Interactive Player
                const scriptId = `script-${post.id}`;
                const scriptCode = post.content.code ? encodeURIComponent(post.content.code) : '';
                const scriptTitle = post.content.title || "Untitled Script";

                contentHTML = `
                    <div class="relative group overflow-hidden bg-black border border-white/10 rounded-xl" id="${scriptId}-container">
                        
                        <!-- Thumbnail / Start Screen -->
                        <div class="aspect-video flex flex-col items-center justify-center p-6 relative z-10 transition-transform duration-500 group-hover:scale-[1.02]">
                            <div class="absolute inset-0 bg-gradient-to-br from-purple-900/20 to-black/80"></div>
                            
                            <!-- Icon -->
                            <div class="w-16 h-16 rounded-full bg-black/50 border border-white/20 flex items-center justify-center mb-4 transition-all duration-300 group-hover:scale-110 group-hover:border-acid-green backdrop-blur-sm shadow-xl">
                                <i class="ph-bold ph-play text-3xl text-white group-hover:text-acid-green ml-1"></i>
                            </div>
                            
                            <h3 class="relative z-20 font-black text-2xl text-white uppercase tracking-tighter shadow-black drop-shadow-md">${scriptTitle}</h3>
                            <button onclick="window.FeedManager.playScript('${scriptId}', '${scriptCode}')" 
                                    class="relative z-20 mt-4 px-6 py-2 bg-acid-green text-black font-bold uppercase tracking-widest border-2 border-black hover:bg-white transition-colors shadow-hard">
                                Run Program
                            </button>
                        </div>
                        
                        <!-- Grid Background -->
                        <div class="absolute inset-0 opacity-20 pointer-events-none" 
                             style="background-image: linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px); background-size: 20px 20px;">
                        </div>
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

            // Disconnect precious observer if exists? 
            if (this.observer) this.observer.disconnect();

            this.observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting && !this.state.loading) {
                    this.loadPosts();
                }
            }, { rootMargin: '200px' });

            this.observer.observe(this.observerTarget);
        },

        showLoader(show) {
            const el = document.getElementById('feed-loader');
            if (el) el.classList.toggle('hidden', !show);
        },

        showEmptyState() {
            this.container.innerHTML = `
                <div class="flex flex-col items-center justify-center py-20 opacity-60 animate-fade-in">
                    <div class="w-24 h-24 bg-black rounded-full flex items-center justify-center text-white text-4xl mb-4 animate-bounce">
                        <i class="ph-bold ph-broadcast"></i>
                    </div>
                    <h3 class="font-black uppercase text-xl text-center">Static Silence...</h3>
                    <p class="font-mono text-sm text-center max-w-xs mt-2 mb-6">No signals detected in the stream. Be the first to broadcast.</p>
                    <a href="/directory" class="nb-button inline-block bg-acid-green text-black border-2 border-black px-6 py-2 shadow-hard hover:bg-hot-pink transition">
                        Find Signal
                    </a>
                </div>
            `;
        },

        showEndMessage() {
            if (document.getElementById('feed-end-msg')) return;
            const msg = document.createElement('div');
            msg.id = 'feed-end-msg';
            msg.className = "text-center py-8 text-slate-500 font-mono text-xs uppercase tracking-widest";
            msg.innerText = "// END OF STREAM //";
            this.container.appendChild(msg);
        },

        checkEmpty() {
            if (this.state.posts.length === 0 && !this.state.loading) {
                this.showEmptyState();
            }
        },

        playScript(containerId, encodedCode) {
            const container = document.getElementById(containerId + '-container');
            if (!container) return;

            const code = decodeURIComponent(encodedCode);

            // iframe construction
            const iframe = document.createElement('iframe');
            iframe.className = "w-full aspect-video border-none bg-black animate-fade-in relative z-20";

            const html = `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>body { margin: 0; overflow: hidden; background: #000; }</style>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"><\/script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"><\/script>
                </head>
                <body>
                    <script>${code}<\/script>
                </body>
                </html>
            `;

            // Replace content
            container.innerHTML = '';
            container.appendChild(iframe);

            // Write to iframe
            const doc = iframe.contentWindow.document;
            doc.open();
            doc.write(html);
            doc.close();

            // Add reset button overlay
            const resetBtn = document.createElement('button');
            resetBtn.className = "absolute top-2 right-2 z-30 p-2 bg-black/50 text-white hover:text-red-400 rounded transition";
            resetBtn.innerHTML = '<i class="ph-bold ph-stop"></i>';
            resetBtn.onclick = () => {
                // Reload feed item (lazy way: just reload page or re-render post? For now, refresh feed logic)
                // Better: Store original HTML and restore it?
                // For MVP, just show a "Stopped" state
                container.innerHTML = '<div class="flex items-center justify-center h-full text-white font-mono uppercase">Terminated</div>';
            };
            container.appendChild(resetBtn);
        }
    };
}

// Always init on load (SPA re-entry)
// If script is re-run, FeedManager is already defined, but we call init() again to re-bind DOM
if (window.FeedManager) {
    // If HTMX swapped the content, the DOM elements are new, establishing new references is needed
    // HTMX 'load' event might be better?
    // Or simply call init() here since the script runs AFTER the swap
    window.FeedManager.init();
}

// Handle non-SPA legacy load
document.addEventListener('DOMContentLoaded', () => {
    if (window.FeedManager) window.FeedManager.init();
});
