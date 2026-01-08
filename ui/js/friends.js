/**
 * Sprint 20: Social Actions UI
 * Client-side logic for Friend interactions (Follow/Unfollow)
 */

const FriendManager = {
    async toggleFollow(btn) {
        // Prevent double clicks
        if (btn.classList.contains('processing')) return;
        
        const userId = btn.dataset.userId;
        const currentStatus = btn.dataset.status; // 'following' or 'not_following'
        const isFollowing = currentStatus === 'following';
        
        // Optimistic UI Update
        btn.classList.add('processing');
        this.updateButtonState(btn, !isFollowing, true); // true = loading style
        
        try {
            const endpoint = isFollowing ? '/friends/unfollow' : '/friends/follow';
            
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // CSRF Token if needed (Sprint 18 added Flask-WTF, likely need to extract from DOM or cookie)
                    // For now, assuming fetch wrapper or relaxed checking in some envs, 
                    // but standard Flask-WTF requires X-CSRFToken.
                    // We will add a helper to get it.
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ user_id: userId })
            });

            const data = await res.json();
            
            if (data.ok) {
                // Success - Commit Update
                btn.dataset.status = isFollowing ? 'not_following' : 'following';
                this.updateButtonState(btn, !isFollowing, false); // false = not loading
            } else {
                throw new Error(data.error);
            }
        } catch (e) {
            console.error(e);
            alert("Action failed: " + e.message);
            // Revert State
            this.updateButtonState(btn, isFollowing, false);
        } finally {
            btn.classList.remove('processing');
        }
    },
    
    updateButtonState(btn, isFollowing, isLoading) {
        if (isLoading) {
            btn.style.opacity = '0.5';
            btn.innerText = '...';
            return;
        }
        
        btn.style.opacity = '1';
        
        if (isFollowing) {
            // "Following" State
            btn.innerText = 'UNFOLLOW';
            btn.classList.remove('bg-black', 'text-white');
            btn.classList.add('bg-white', 'text-black', 'border', 'border-black');
        } else {
            // "Not Following" State
            btn.innerText = 'FOLLOW';
            btn.classList.remove('bg-white', 'text-black', 'border', 'border-black');
            btn.classList.add('bg-black', 'text-white');
        }
    },
    
    getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }
};

// Global Exposure for inline onclicks
window.FriendManager = FriendManager;
