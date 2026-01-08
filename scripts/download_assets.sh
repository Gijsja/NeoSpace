#!/bin/bash

# Create vendor directories
mkdir -p static/vendor
mkdir -p static/vendor/phosphor

# Helper to download
download() {
    url=$1
    filename=$2
    echo "Downloading $filename..."
    curl -L -s -o "static/vendor/$filename" "$url"
}

# Core libs
download "https://cdn.socket.io/4.7.4/socket.io.min.js" "socket.io.min.js"
download "https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js" "alpine.min.js"
download "https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js" "htmx.min.js"
download "https://cdn.tailwindcss.com" "tailwindcss.js"

# UI Libs
# Skipping emoji-picker (complex ESM tree), keeping CDN

# Phosphor Icons (Manual download of weights)
echo "Downloading Phosphor assets..."
base_url="https://unpkg.com/@phosphor-icons/web@2.1.1/src"
for weight in regular bold fill; do
    # Download CSS
    # Note: The CSS references font files. We need to ensure paths match or edit CSS.
    # The default CSS usually expects font at current dir or similar.
    download "$base_url/$weight/style.css" "phosphor/phosphor-$weight.css"
    
    # Download Font
    cap_weight=$(echo "$weight" | sed 's/./\u&/') # Capitalize first letter
    font_name="Phosphor-$cap_weight.woff2"
    if [ "$weight" == "regular" ]; then font_name="Phosphor.woff2"; fi # Regular is just Phosphor.woff2 sometimes? Checking...
    # Checking source: regular uses Phosphor.woff2, others use Phosphor-Bold.woff2 etc.
    # Actually checking the style.css content would be best.
    # We will verify after download.
    
    download "$base_url/$weight/$font_name" "phosphor/$font_name"
done

# Wall/Editor Libs
download "https://cdn.jsdelivr.net/npm/mobile-drag-drop@2.3.0-rc.2/index.min.js" "mobile-drag-drop.min.js"
download "https://cdn.jsdelivr.net/npm/marked/marked.min.js" "marked.min.js"
download "https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js" "purify.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css" "highlight-atom-one-dark.min.css"
download "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js" "highlight.min.js"

# Scripting
download "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" "three.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js" "p5.min.js"

echo "Download complete."
ls -R static/vendor
