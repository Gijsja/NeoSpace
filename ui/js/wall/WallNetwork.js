/**
 * WallNetwork.js
 * API calls for the Wall.
 * Pure module - returns data, does not render.
 */

import { state, setCurrentUserData } from './WallState.js';

const loadingEl = document.getElementById('loading');
const wallContainer = document.getElementById('wall-container');

export async function fetchProfileData() {
    const endpoint = state.userId ? `/profile?user_id=${state.userId}` : '/profile';
    try {
        const res = await fetch(endpoint);
        if (res.status === 401) {
            window.location.href = '/auth/login';
            return null;
        }
        
        let data;
        try {
            data = await res.json();
        } catch (jsonErr) {
             throw new Error("Invalid JSON response from server");
        }
        
        if (data.error) {
            if(loadingEl) loadingEl.innerHTML = `<div class="text-red-400 font-bold border-2 border-red-500 p-4 bg-white shadow-hard">${data.error}</div>`;
            return null;
        }

        setCurrentUserData(data);
        
        if(loadingEl) loadingEl.classList.add('hidden');
        if(wallContainer) wallContainer.classList.remove('hidden');

        return data;

    } catch (err) {
        console.error(err);
        if(loadingEl) loadingEl.innerHTML = `
            <div class="text-red-500 font-bold border-2 border-red-500 p-4 bg-white shadow-hard flex flex-col items-center gap-2">
                <i class="ph-bold ph-warning-octagon text-3xl"></i>
                <span>CONNECTION LOST</span>
                <span class="text-xs font-mono text-black">${err.message || 'Unknown Error'}</span>
                <button onclick="window.location.reload()" class="mt-2 px-4 py-1 bg-black text-white text-xs font-bold uppercase hover:bg-gray-800">Retry</button>
            </div>`;
        return null;
    }
}

export async function deleteModule(moduleId) {
    try {
        const res = await fetch('/wall/post/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id: moduleId })
        });
        const data = await res.json();
        return data;
    } catch(e) {
        console.error(e);
        return { ok: false, error: 'Network error' };
    }
}

export async function fetchScriptContent(scriptId) {
     const res = await fetch(`/scripts/get?id=${scriptId}`);
     return await res.json();
}
