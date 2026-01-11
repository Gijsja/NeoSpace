/**
 * ChatScripts.js
 * Handles fetching and running scripts within chat bubbles.
 */

export async function loadAndRunScript(container, id) {
    container.innerHTML = '<div class="absolute inset-0 flex items-center justify-center bg-black/80"><i class="ph-bold ph-spinner animate-spin text-white text-2xl"></i></div>';
    try {
        const res = await fetch(`/scripts/get?id=${id}`);
        const data = await res.json();
        if (data.ok) {
            const s = data.script;
            const iframe = document.createElement('iframe');
            iframe.className = "w-full h-full border-none bg-white rounded";
            // SECURITY: Removed 'allow-same-origin' to prevent access to parent DOM/Cookies
            // This treats the iframe as a unique origin (null).
            iframe.setAttribute('sandbox', 'allow-scripts allow-forms allow-pointer-lock');

            // SECURITY: Content Security Policy
            const csp = `<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none';">`;

            let html = '';
            // Simplified runner templates (similar to playground)
            if (s.script_type === 'p5') {
                html = `<!DOCTYPE html><html><head>${csp}<style>body{margin:0;overflow:hidden}</style><script src="/static/vendor/p5.min.js"><\/script></head><body><script>try{${s.content}}catch(e){document.body.innerHTML='<pre style="color:red">'+e+'</pre>'}<\/script></body></html>`;
            } else if (s.script_type === 'three') {
                html = `<!DOCTYPE html><html><head>${csp}<style>body{margin:0;overflow:hidden}</style><script src="/static/vendor/three.min.js"><\/script></head><body><script type="module">try{${s.content}}catch(e){document.body.innerHTML='<pre style="color:red">'+e+'</pre>'}<\/script></body></html>`;
            } else {
                html = `<!DOCTYPE html><html><head>${csp}</head><body><script>${s.content}<\/script></body></html>`;
            }

            iframe.srcdoc = html;
            container.innerHTML = ''; // basic reset
            container.appendChild(iframe);

        } else {
            container.innerHTML = '<div class="absolute inset-0 flex items-center justify-center bg-red-900/80 text-white text-xs">Error loading script</div>';
        }
    } catch (e) {
        container.innerHTML = '<div class="absolute inset-0 flex items-center justify-center bg-red-900/80 text-white text-xs">Network error</div>';
    }
}
