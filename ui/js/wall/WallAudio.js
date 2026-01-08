/**
 * WallAudio.js
 * Handles Audio Anthem logic.
 */

let anthemMuted = false;
const anthemPlayer = document.getElementById('anthem-player');
const anthemToggle = document.getElementById('anthem-toggle');
const anthemIcon = document.getElementById('anthem-icon');

export function setupAnthem(url, autoplay) {
    if (!url) {
        if (anthemToggle) anthemToggle.classList.add('hidden');
        if (anthemPlayer) {
            anthemPlayer.pause();
            anthemPlayer.src = '';
        }
        return;
    }
    
    if (anthemPlayer) anthemPlayer.src = url;
    if (anthemToggle) anthemToggle.classList.remove('hidden');
    
    // Set up click handler once
    if (anthemToggle && !anthemToggle.onclick) {
        anthemToggle.onclick = toggleAnthem;
    }
    
    if (autoplay) {
        if (anthemPlayer) {
            anthemPlayer.play().then(() => {
                updateAnthemIcon(false);
            }).catch(() => {
                anthemMuted = true;
                updateAnthemIcon(true);
            });
        }
    } else {
        anthemMuted = true;
        updateAnthemIcon(true);
    }
}

function updateAnthemIcon(muted) {
    if (!anthemIcon || !anthemToggle) return;
    if (muted) {
        anthemIcon.className = 'ph-bold ph-speaker-x text-xl';
        anthemToggle.classList.add('bg-slate-600/80');
        anthemToggle.classList.remove('bg-purple-600/80');
    } else {
        anthemIcon.className = 'ph-bold ph-speaker-high text-xl';
        anthemToggle.classList.remove('bg-slate-600/80');
        anthemToggle.classList.add('bg-purple-600/80');
    }
}

function toggleAnthem() {
    anthemMuted = !anthemMuted;
    if (anthemMuted) {
        anthemPlayer.pause();
    } else {
        anthemPlayer.play().catch(() => {});
    }
    updateAnthemIcon(anthemMuted);
}
