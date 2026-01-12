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
            this.renderSkeletons();
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
            const avatar = post.author_avatar || "/static/images/cats/null.png";
            const time = new Date(post.created_at).toLocaleDateString();

            let contentHTML = "";

            // -- Render Logic based on Module Type --
            if (post.module_type === 'text') {
                let text = post.content.text || "";
                if (typeof marked !== 'undefined') text = marked.parse(text);
                contentHTML = `<div class="prose prose-sm prose-black max-w-none font-mono text-sm leading-relaxed">${text}</div>`;

            } else if (post.module_type === 'image') {
                contentHTML = `<img src="${post.content.url}" class="w-full h-auto border-4 border-black box-shadow-hard" loading="lazy">`;

            } else if (post.module_type === 'link') {
                contentHTML = `
                    <a href="${post.content.url}" target="_blank" class="block p-4 bg-white border-4 border-black hover:bg-yellow-200 transition shadow-hard">
                        <div class="flex items-center gap-3">
                            <i class="ph-bold ph-link text-2xl"></i>
                            <div class="min-w-0">
                                 <div class="font-black uppercase truncate">${post.content.title || post.content.url}</div>
                                 <div class="text-xs font-mono truncate">${post.content.url}</div>
                            </div>
                        </div>
                    </a>
                `;
            } else if (post.module_type === 'audio') {
                contentHTML = `
                    <div class="p-3 bg-white border-4 border-black shadow-hard">
                        <div class="flex items-center gap-3 mb-2">
                             <div class="w-10 h-10 bg-hot-pink border-4 border-black flex items-center justify-center text-white">
                                <i class="ph-fill ph-music-notes text-xl"></i>
                             </div>
                             <div class="text-sm font-black uppercase">${post.content.title || "Audio Track"}</div>
                        </div>
                        <audio controls src="${post.content.url}" class="w-full h-8 border-2 border-black"></audio>
                    </div>
                `;
            } else if (post.module_type === 'script') {
                // SCRIPT MODULE - Interactive Player
                const scriptId = `script-${post.id}`;
                const scriptCode = post.content.code ? encodeURIComponent(post.content.code) : '';
                const scriptTitle = post.content.title || "Untitled Script";

                contentHTML = `
                    <div class="relative group overflow-hidden bg-black border-4 border-black shadow-hard" id="${scriptId}-container">
                        
                        <!-- Thumbnail / Start Screen -->
                        <div class="aspect-video flex flex-col items-center justify-center p-6 relative z-10">
                            <div class="absolute inset-0 bg-white opacity-10" style="background-image: radial-gradient(#000 1px, transparent 1px); background-size: 10px 10px;"></div>
                            
                            <!-- Icon -->
                            <div class="w-16 h-16 bg-acid-green border-4 border-black flex items-center justify-center mb-4 shadow-hard transition-transform group-hover:scale-110">
                                <i class="ph-bold ph-play text-3xl text-black"></i>
                            </div>
                            
                            <h3 class="relative z-20 font-black text-2xl text-white uppercase tracking-tighter mix-blend-difference">${scriptTitle}</h3>
                            <button onclick="window.FeedManager.playScript('${scriptId}', '${scriptCode}')" 
                                    class="relative z-20 mt-4 px-6 py-2 bg-white text-black font-bold uppercase tracking-widest border-4 border-black hover:bg-neon-green transition-colors shadow-hard">
                                Run Program
                            </button>
                        </div>
                    </div>
                 `;
            }

            return `
                <div class="nb-card p-0 mb-6 overflow-hidden animate-fade-in relative group transition hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-xl">
                     <!-- Author Header -->
                     <div class="flex items-center gap-3 p-4 border-b-4 border-black bg-white">
                        <a href="/wall?user_id=${post.user_id}" class="shrink-0 relative">
                            <div class="absolute inset-0 bg-black translate-x-1 translate-y-1 rounded-none"></div>
                            <img src="${avatar}" class="relative w-12 h-12 border-4 border-black object-cover bg-gray-200 z-10">
                        </a>
                        <div class="min-w-0 flex-1">
                            <a href="/wall?user_id=${post.user_id}" class="block font-black text-sm uppercase hover:underline truncate">
                                ${author}
                            </a>
                            <div class="text-xs font-mono font-bold text-gray-500">@${username} • ${time}</div>
                        </div>
                        <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition">
                             <a href="/wall?user_id=${post.user_id}" class="text-xs font-bold uppercase tracking-wider text-black border-2 border-black px-2 py-1 bg-white hover:bg-black hover:text-white transition shadow-hard-sm">
                                View Wall
                             </a>
                        </div>
                     </div>
                     
                     <!-- Content -->
                     <div class="p-6 bg-white">
                        ${contentHTML}
                     </div>

                     <!-- Actions Footer -->
                     <div class="border-t-4 border-black p-3 flex gap-4 bg-gray-50">
                        <button class="flex items-center gap-2 text-xs font-bold uppercase hover:bg-hot-pink hover:text-white px-2 py-1 border-2 border-transparent hover:border-black transition">
                            <i class="ph-bold ph-heart"></i> Like
                        </button>
                        <button class="flex items-center gap-2 text-xs font-bold uppercase hover:bg-neon-green hover:text-black px-2 py-1 border-2 border-transparent hover:border-black transition">
                            <i class="ph-bold ph-chat-circle"></i> Comment
                        </button>
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
                    <script src="/static/vendor/three.min.js"><\/script>
                    <script src="/static/vendor/p5.min.js"><\/script>
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
        },

        renderSkeletons() {
            // Render 3 skeleton posts
            this.container.innerHTML = Array(3).fill(0).map(() => `
                <div class="nb-card p-0 mb-6 animate-pulse bg-white border-4 border-black shadow-hard">
                    <div class="flex items-center gap-3 p-4 border-b-4 border-black bg-white">
                        <div class="w-12 h-12 bg-gray-200 border-4 border-black"></div>
                        <div class="flex-1">
                            <div class="h-4 w-32 bg-gray-200 mb-2"></div>
                            <div class="h-3 w-20 bg-gray-200"></div>
                        </div>
                    </div>
                    <div class="p-6 space-y-3">
                        <div class="h-4 w-3/4 bg-gray-200"></div>
                        <div class="h-4 w-1/2 bg-gray-200"></div>
                        <div class="h-32 w-full bg-gray-100 border-4 border-black mt-4"></div>
                    </div>
                </div>
            `).join('');
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

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.FeedManager) window.FeedManager.init();
    });
} else {
    if (window.FeedManager) window.FeedManager.init();
}
